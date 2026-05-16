"""
Blockchain Transaction Analyzer

This module fetches real Ethereum Sepolia transactions and analyzes
validator behavior to compute PoB scores.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict
from eth_connector import EthereumConnector
import time


@dataclass
class ValidatorBehavior:
    """Stores validator behavioral metrics."""
    validator_address: str
    block_count: int
    valid_transactions: int
    failed_transactions: int
    gas_efficiency: float
    uptime_score: float
    behavior_score: float
    pob_score: float
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'validator': self.validator_address,
            'blocks_mined': self.block_count,
            'valid_txs': self.valid_transactions,
            'failed_txs': self.failed_transactions,
            'gas_efficiency': round(self.gas_efficiency, 4),
            'uptime_score': round(self.uptime_score, 4),
            'behavior_score': round(self.behavior_score, 4),
            'pob_score': round(self.pob_score, 4),
        }


class BlockchainAnalyzer:
    """
    Analyzes Ethereum blockchain transaction data to compute
    validator fairness metrics and PoB scores.
    """
    
    def __init__(self, eth_connector: EthereumConnector):
        """
        Initialize analyzer.
        
        Args:
            eth_connector: Connected EthereumConnector instance
        """
        self.eth = eth_connector
        self.validators: Dict[str, ValidatorBehavior] = {}
    
    def analyze_blocks(self, start_block: int, end_block: int) -> Dict[str, ValidatorBehavior]:
        """
        Analyze blocks in range and compute validator metrics.
        
        Args:
            start_block: Starting block number
            end_block: Ending block number
            
        Returns:
            Dictionary mapping validator address to ValidatorBehavior
        """
        print(f"\n📊 Analyzing blocks {start_block} to {end_block}...")
        print(f"   Total blocks to analyze: {end_block - start_block + 1}\n")
        
        # Dictionary to accumulate metrics per validator
        validator_stats: Dict[str, dict] = {}
        
        # Process each block
        for block_num in range(start_block, end_block + 1):
            if block_num % 10 == 0:
                print(f"   Processing block {block_num}...", end='\r')
            
            try:
                block = self.eth.w3.eth.get_block(block_num)
                validator = block['miner'].lower()
                
                # Initialize validator stats if not seen before
                if validator not in validator_stats:
                    validator_stats[validator] = {
                        'block_count': 0,
                        'valid_txs': 0,
                        'failed_txs': 0,
                        'total_gas_used': 0,
                        'total_gas_limit': 0,
                        'blocks': [],
                    }
                
                validator_stats[validator]['block_count'] += 1
                validator_stats[validator]['total_gas_used'] += block['gasUsed']
                validator_stats[validator]['total_gas_limit'] += block['gasLimit']
                validator_stats[validator]['blocks'].append(block_num)
                
                # Analyze transactions in block
                tx_count = len(block['transactions'])
                
                # Fetch transaction receipts to check success/failure
                for tx_hash in block['transactions']:
                    try:
                        tx_receipt = self.eth.w3.eth.get_transaction_receipt(tx_hash)
                        if tx_receipt['status'] == 1:
                            validator_stats[validator]['valid_txs'] += 1
                        else:
                            validator_stats[validator]['failed_txs'] += 1
                    except:
                        # If receipt unavailable, count as valid (conservative)
                        validator_stats[validator]['valid_txs'] += 1
            
            except Exception as e:
                print(f"   Error processing block {block_num}: {e}")
                continue
        
        print(f"\n   ✅ Analyzed {end_block - start_block + 1} blocks")
        print(f"   Found {len(validator_stats)} unique validators\n")
        
        # Compute fairness metrics
        self._compute_metrics(validator_stats)
        
        return self.validators
    
    def _compute_metrics(self, validator_stats: Dict[str, dict]) -> None:
        """
        Compute fairness and PoB metrics from raw statistics.
        
        Args:
            validator_stats: Raw validator statistics
        """
        if not validator_stats:
            return
        
        # Compute total blocks for percentage calculations
        total_blocks = sum(v['block_count'] for v in validator_stats.values())
        
        print("📈 Computing Fairness Metrics\n")
        print("   Validator                            Blocks  Block%  Valid  Failed  PoB Score")
        print("   " + "-" * 85)
        
        for validator, stats in sorted(
            validator_stats.items(),
            key=lambda x: x[1]['block_count'],
            reverse=True
        ):
            # Block percentage (fairness measure)
            block_percentage = (stats['block_count'] / total_blocks) * 100
            
            # Transaction success rate
            total_txs = stats['valid_txs'] + stats['failed_txs']
            success_rate = (stats['valid_txs'] / total_txs * 100) if total_txs > 0 else 100
            
            # Gas efficiency (used / limit)
            gas_efficiency = (stats['total_gas_used'] / stats['total_gas_limit']) if stats['total_gas_limit'] > 0 else 0
            
            # Uptime score (based on consistent block production)
            # Higher block count = better uptime
            uptime_score = min(100, (stats['block_count'] / (total_blocks / len(validator_stats)) * 100))
            
            # Behavior score based on transaction quality
            # Formula: 1.0 + (success_rate/100 * 0.5)
            behavior_score = 1.0 + (success_rate / 100 * 0.5)
            
            # PoB score = behavior_score + (uptime_score * 0.35) / 100
            pob_score = behavior_score + (uptime_score * 0.35 / 100)
            
            # Create ValidatorBehavior object
            self.validators[validator] = ValidatorBehavior(
                validator_address=validator,
                block_count=stats['block_count'],
                valid_transactions=stats['valid_txs'],
                failed_transactions=stats['failed_txs'],
                gas_efficiency=gas_efficiency,
                uptime_score=uptime_score,
                behavior_score=behavior_score,
                pob_score=pob_score,
            )
            
            # Print metrics
            print(f"   {validator[:34]}  {stats['block_count']:5d}  {block_percentage:5.1f}%  {stats['valid_txs']:5d}  {stats['failed_txs']:5d}  {pob_score:7.4f}")
        
        print("\n   ✅ Metrics computed\n")
    
    def get_validator_ranking(self, method: str = 'pob') -> List[tuple]:
        """
        Get validators ranked by specified method.
        
        Args:
            method: 'pob' (PoB score), 'pow' (block count), 'pos' (random by count)
            
        Returns:
            List of (validator_address, score) tuples
        """
        if method == 'pob':
            return sorted(
                [(v.validator_address, v.pob_score) for v in self.validators.values()],
                key=lambda x: x[1],
                reverse=True
            )
        elif method == 'pow':
            return sorted(
                [(v.validator_address, v.block_count) for v in self.validators.values()],
                key=lambda x: x[1],
                reverse=True
            )
        else:
            return [(v.validator_address, v.block_count) for v in self.validators.values()]
    
    def calculate_fairness_metric(self) -> float:
        """
        Calculate fairness metric (Gini coefficient).
        
        Higher value = more centralized (unfair)
        Lower value = more distributed (fair)
        
        Returns:
            Fairness score (0 to 1)
        """
        if not self.validators:
            return 0.0
        
        blocks = [v.block_count for v in self.validators.values()]
        total = sum(blocks)
        
        # Sort blocks
        blocks.sort()
        
        # Gini coefficient
        n = len(blocks)
        numerator = sum((2 * i - n - 1) * blocks[i] for i in range(n))
        denominator = n * total
        
        gini = numerator / denominator if denominator > 0 else 0
        
        return max(0, gini)  # Gini is 0-1
    
    def print_summary(self) -> None:
        """Print analysis summary."""
        if not self.validators:
            print("No validators found")
            return
        
        print("\n" + "="*70)
        print("📊 BLOCKCHAIN ANALYSIS SUMMARY")
        print("="*70)
        
        total_blocks = sum(v.block_count for v in self.validators.values())
        total_validators = len(self.validators)
        fairness = self.calculate_fairness_metric()
        
        # Top validator
        top_validator = max(self.validators.values(), key=lambda v: v.block_count)
        
        print(f"\n📈 Overall Statistics:")
        print(f"   Total Blocks Analyzed: {total_blocks}")
        print(f"   Total Validators: {total_validators}")
        print(f"   Avg Blocks per Validator: {total_blocks / total_validators:.1f}")
        print(f"   Fairness Score (Gini): {fairness:.4f}")
        print(f"   PoW Concentration: {(top_validator.block_count / total_blocks * 100):.1f}%")
        
        print(f"\n🏆 Top 3 Validators (by PoB score):")
        rankings = self.get_validator_ranking('pob')
        for i, (addr, score) in enumerate(rankings[:3], 1):
            v = self.validators[addr]
            print(f"   {i}. {addr[:10]}... - PoB: {score:.4f} (Blocks: {v.block_count})")
        
        print(f"\n" + "="*70 + "\n")
