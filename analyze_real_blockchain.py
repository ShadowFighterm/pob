"""
Real Blockchain Analysis: Compare PoW vs PoB Validator Selection

This script:
1. Fetches real Sepolia blockchain data
2. Analyzes validator behavior
3. Compares PoW (actual) vs PoB (what should happen) selection
4. Measures fairness improvement
"""

from eth_connector import EthereumConnector
from blockchain_analyzer import BlockchainAnalyzer
import json


def main():
    print("\n" + "="*70)
    print("🔍 REAL BLOCKCHAIN ANALYSIS - PoW vs PoB COMPARISON")
    print("="*70)
    
    try:
        # Connect to Sepolia
        print("\n🔗 Connecting to Ethereum Sepolia...")
        eth = EthereumConnector()
        
        # Get latest block
        latest_block = eth.w3.eth.get_block('latest')
        latest_block_num = latest_block['number']
        
        print(f"✅ Connected! Latest block: {latest_block_num}\n")
        
        # Analyze last 50 blocks (manageable size)
        start_block = max(0, latest_block_num - 50)
        end_block = latest_block_num
        
        print(f"📊 Analyzing blocks {start_block} to {end_block}\n")
        
        # Create analyzer
        analyzer = BlockchainAnalyzer(eth)
        
        # Analyze blocks
        validators = analyzer.analyze_blocks(start_block, end_block)
        
        if not validators:
            print("❌ No validators found in this block range")
            return
        
        # Print summary
        analyzer.print_summary()
        
        # Compare PoW vs PoB
        print("\n" + "="*70)
        print("⚖️  PoW vs PoB VALIDATOR SELECTION COMPARISON")
        print("="*70)
        
        # PoW ranking (by block count - current system)
        print("\n📊 PROOF OF WORK (Current System)")
        print("   Validators ranked by: Block Count (Hash Power)")
        print("   Characteristic: Always selects same validator (most centralized)\n")
        
        pow_ranking = analyzer.get_validator_ranking('pow')
        print("   Rank  Validator                          Blocks  Fairness")
        print("   " + "-" * 65)
        for i, (addr, blocks) in enumerate(pow_ranking[:10], 1):
            percentage = (blocks / sum(v.block_count for v in validators.values())) * 100
            fairness = "✅ Fair" if blocks < 5 else ("⚠️  Moderate" if blocks < 10 else "❌ Unfair")
            print(f"   {i:2d}.  {addr[:34]}  {blocks:5d}   {percentage:5.1f}%")
        
        # PoB ranking (by PoB score - proposed system)
        print("\n\n💡 PROOF OF BEHAVIOR (Proposed System)")
        print("   Validators ranked by: PoB Score (Behavior + Uptime)")
        print("   Characteristic: Selects based on transaction quality & reliability\n")
        
        pob_ranking = analyzer.get_validator_ranking('pob')
        print("   Rank  Validator                          PoB Score  Change")
        print("   " + "-" * 65)
        for i, (addr, score) in enumerate(pob_ranking[:10], 1):
            v = validators[addr]
            pow_pos = next((j for j, (a, _) in enumerate(pow_ranking, 1) if a == addr), None)
            change = f"↑ {pow_pos - i}" if pow_pos and pow_pos > i else (f"↓ {i - pow_pos}" if pow_pos and pow_pos < i else "→ Same")
            print(f"   {i:2d}.  {addr[:34]}  {score:9.4f}   {change}")
        
        # Fairness comparison
        print("\n\n📈 FAIRNESS METRICS")
        print("   " + "-" * 65)
        
        total_blocks = sum(v.block_count for v in validators.values())
        
        # PoW concentration (Herfindahl index)
        pow_hhi = sum((v.block_count / total_blocks) ** 2 for v in validators.values())
        
        # PoB concentration (weighted by PoB scores)
        pob_total_score = sum(v.pob_score for v in validators.values())
        pob_hhi = sum((v.pob_score / pob_total_score) ** 2 for v in validators.values())
        
        fairness_improvement = ((pow_hhi - pob_hhi) / pow_hhi) * 100
        
        print(f"   PoW Concentration Index (HHI): {pow_hhi:.4f}")
        print(f"   PoB Concentration Index (HHI): {pob_hhi:.4f}")
        print(f"   Fairness Improvement:          {fairness_improvement:+.1f}%")
        print(f"\n   Interpretation:")
        if fairness_improvement > 0:
            print(f"   ✅ PoB IMPROVES FAIRNESS by {fairness_improvement:.1f}%")
        else:
            print(f"   ⚠️  PoB slightly decreases fairness by {abs(fairness_improvement):.1f}%")
        
        # Save results
        print("\n\n💾 Saving Analysis Results...")
        results = {
            'analysis_date': str(__import__('datetime').datetime.now()),
            'blockchain': 'Ethereum Sepolia',
            'blocks_analyzed': end_block - start_block + 1,
            'validators_found': len(validators),
            'pow_metrics': {
                'concentration_index': float(pow_hhi),
                'top_validator_percentage': (pow_ranking[0][1] / total_blocks * 100) if pow_ranking else 0,
            },
            'pob_metrics': {
                'concentration_index': float(pob_hhi),
                'fairness_improvement_percent': float(fairness_improvement),
            },
            'top_validators_pow': [{'address': addr, 'blocks': blocks} for addr, blocks in pow_ranking[:5]],
            'top_validators_pob': [{'address': addr, 'score': float(score)} for addr, score in pob_ranking[:5]],
        }
        
        with open('blockchain_analysis_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("✅ Results saved to: blockchain_analysis_results.json")
        
        print("\n" + "="*70)
        print("✅ ANALYSIS COMPLETE")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
