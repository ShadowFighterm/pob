"""
Consensus algorithm implementations.

Functions:
- select_validator_pob: Proof of Behavior (behavior score + uptime)
- select_validator_pow: Proof of Work (hash power)
- select_validator_pos: Proof of Stake (weighted random by stake)
"""

from __future__ import annotations

import random
from typing import Iterable

from models import NodeState


def select_validator_pob(nodes: Iterable[NodeState]) -> NodeState:
    """
    Proof of Behavior: Select validator based on behavior score and uptime.
    
    Higher behavior scores and uptime = higher chance of selection.
    Deterministic: always picks the same node with highest score.
    
    Args:
        nodes: Iterable of NodeState objects
        
    Returns:
        The selected validator node
        
    Raises:
        ValueError: If no nodes available
    """
    candidates = list(nodes)
    if not candidates:
        raise ValueError("No nodes available for validator selection")

    return max(
        candidates,
        key=lambda node: (
            node.consensus_score(),
            -node.node_id,
        ),
    )


def select_validator_pow(nodes: Iterable[NodeState]) -> NodeState:
    """
    Proof of Work: Select validator based on hash power (computing power).
    
    Highest hash power always wins.
    Deterministic: always picks the same node (least fair).
    
    Args:
        nodes: Iterable of NodeState objects
        
    Returns:
        The selected validator node
        
    Raises:
        ValueError: If no nodes available
    """
    candidates = list(nodes)
    if not candidates:
        raise ValueError("No nodes available for validator selection")

    return max(
        candidates,
        key=lambda node: (
            node.hash_power,
            -node.node_id,
        ),
    )


def select_validator_pos(nodes: Iterable[NodeState]) -> NodeState:
    """
    Proof of Stake: Select validator randomly, weighted by stake.
    
    Nodes with higher stake have higher probability of selection.
    Probabilistic: different nodes selected over time (more fair than PoW).
    
    Args:
        nodes: Iterable of NodeState objects
        
    Returns:
        The selected validator node
        
    Raises:
        ValueError: If no nodes available
    """
    candidates = list(nodes)
    if not candidates:
        raise ValueError("No nodes available for validator selection")

    total_stake = sum(node.stake for node in candidates)
    if total_stake == 0:
        return random.choice(candidates)

    selection_point = random.uniform(0, total_stake)
    current_stake = 0
    for node in candidates:
        current_stake += node.stake
        if current_stake >= selection_point:
            return node
    return candidates[-1]
