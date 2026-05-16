// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * Proof of Behavior (PoB) Validator Reputation Contract
 * 
 * This smart contract stores and manages validator metrics on Ethereum Sepolia.
 * It tracks:
 * - Valid transaction count
 * - Invalid transaction count
 * - Uptime score
 * - Behavior score (computed off-chain, stored here)
 * - Reputation ranking
 */

contract ValidatorReputation {
    
    // ==================== DATA STRUCTURES ====================
    
    struct ValidatorMetrics {
        address validator_address;
        uint256 valid_transactions;
        uint256 invalid_transactions;
        uint256 uptime_score;  // 0-100 (percentage)
        uint256 behavior_score;  // stored as integer (multiply by 100 for decimals)
        uint256 reputation_score;  // PoB score (multiply by 10000 for decimals)
        uint256 last_updated;
        bool is_active;
    }
    
    // ==================== STATE VARIABLES ====================
    
    address public owner;
    mapping(address => ValidatorMetrics) public validators;
    address[] public validator_list;
    uint256 public validator_count;
    
    // ==================== EVENTS ====================
    
    event ValidatorRegistered(address indexed validator, uint256 timestamp);
    event ValidatorUpdated(
        address indexed validator,
        uint256 valid_txs,
        uint256 invalid_txs,
        uint256 behavior_score,
        uint256 timestamp
    );
    event ValidatorDeactivated(address indexed validator, uint256 timestamp);
    
    // ==================== MODIFIERS ====================
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    // ==================== CONSTRUCTOR ====================
    
    constructor() {
        owner = msg.sender;
        validator_count = 0;
    }
    
    // ==================== VALIDATOR REGISTRATION ====================
    
    /**
     * Register a new validator
     */
    function registerValidator(address validator_address) public onlyOwner {
        require(validator_address != address(0), "Invalid validator address");
        require(!validators[validator_address].is_active, "Validator already registered");
        
        validators[validator_address] = ValidatorMetrics({
            validator_address: validator_address,
            valid_transactions: 0,
            invalid_transactions: 0,
            uptime_score: 100,  // Start with 100%
            behavior_score: 100,  // Start with 1.0 (stored as 100)
            reputation_score: 0,
            last_updated: block.timestamp,
            is_active: true
        });
        
        validator_list.push(validator_address);
        validator_count += 1;
        
        emit ValidatorRegistered(validator_address, block.timestamp);
    }
    
    /**
     * Deactivate a validator
     */
    function deactivateValidator(address validator_address) public onlyOwner {
        require(validators[validator_address].is_active, "Validator not active");
        validators[validator_address].is_active = false;
        emit ValidatorDeactivated(validator_address, block.timestamp);
    }
    
    // ==================== METRICS UPDATE ====================
    
    /**
     * Update validator metrics (called by Python backend)
     * 
     * Args:
     *   validator_address: Address of validator
     *   valid_txs: Total valid transactions
     *   invalid_txs: Total invalid transactions
     *   behavior_score: Computed behavior score (multiply by 100, so 1.5 = 150)
     *   uptime_score: Uptime percentage (0-100)
     */
    function updateValidatorMetrics(
        address validator_address,
        uint256 valid_txs,
        uint256 invalid_txs,
        uint256 behavior_score,
        uint256 uptime_score
    ) public onlyOwner {
        require(validators[validator_address].is_active, "Validator not active");
        require(uptime_score <= 100, "Uptime must be 0-100");
        
        ValidatorMetrics storage vm = validators[validator_address];
        vm.valid_transactions = valid_txs;
        vm.invalid_transactions = invalid_txs;
        vm.behavior_score = behavior_score;  // stored as integer
        vm.uptime_score = uptime_score;
        vm.last_updated = block.timestamp;
        
        // Calculate PoB reputation score
        // Formula: behavior_score + (uptime * 0.35)
        // Stored as integer (multiply by 10000)
        uint256 uptime_factor = (uptime_score * 35) / 100;  // 0.35 * uptime
        vm.reputation_score = behavior_score + uptime_factor;
        
        emit ValidatorUpdated(
            validator_address,
            valid_txs,
            invalid_txs,
            behavior_score,
            block.timestamp
        );
    }
    
    // ==================== GETTER FUNCTIONS ====================
    
    /**
     * Get validator metrics
     */
    function getValidatorMetrics(address validator_address)
        public
        view
        returns (ValidatorMetrics memory)
    {
        return validators[validator_address];
    }
    
    /**
     * Get all validators
     */
    function getAllValidators() public view returns (address[] memory) {
        return validator_list;
    }
    
    /**
     * Get top N validators by reputation score
     */
    function getTopValidators(uint256 count) public view returns (address[] memory) {
        require(count > 0, "Count must be greater than 0");
        
        uint256 limit = count < validator_list.length ? count : validator_list.length;
        address[] memory top_validators = new address[](limit);
        
        // Simple sorting: bubble sort
        // In production, use off-chain sorting
        address[] memory sorted = new address[](validator_list.length);
        for (uint i = 0; i < validator_list.length; i++) {
            sorted[i] = validator_list[i];
        }
        
        for (uint i = 0; i < sorted.length; i++) {
            for (uint j = i + 1; j < sorted.length; j++) {
                if (validators[sorted[j]].reputation_score > validators[sorted[i]].reputation_score) {
                    address temp = sorted[i];
                    sorted[i] = sorted[j];
                    sorted[j] = temp;
                }
            }
        }
        
        for (uint i = 0; i < limit; i++) {
            top_validators[i] = sorted[i];
        }
        
        return top_validators;
    }
    
    /**
     * Get validator count
     */
    function getValidatorCount() public view returns (uint256) {
        return validator_count;
    }
    
    /**
     * Check if validator is active
     */
    function isValidatorActive(address validator_address) public view returns (bool) {
        return validators[validator_address].is_active;
    }
}
