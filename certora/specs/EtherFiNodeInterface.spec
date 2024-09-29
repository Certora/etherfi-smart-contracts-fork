using EtherFiNodeA as NodeA;
using EtherFiNodeB as NodeB;

methods {
    function _.numAssociatedValidators() external  => DISPATCHER(true);
    function _.numExitRequestsByTnft() external => DISPATCHER(true);
    function _.numExitedValidators() external => DISPATCHER(true);
    function _.version() external => DISPATCHER(true);
    function _.eigenPod() external => DISPATCHER(true);
    function _.calculateTVL(uint256, IEtherFiNodesManager.ValidatorInfo, IEtherFiNodesManager.RewardsSplit, bool) external => DISPATCHER(true);
    function _.getNonExitPenalty(uint32, uint32) external => DISPATCHER(true);
    function _.getRewardsPayouts(uint32, IEtherFiNodesManager.RewardsSplit) external => DISPATCHER(true);
    function _.getFullWithdrawalPayouts(IEtherFiNodesManager.ValidatorInfo, IEtherFiNodesManager.RewardsSplit) external => DISPATCHER(true);
    function _.associatedValidatorIds(uint256) external => DISPATCHER(true);
    function _.associatedValidatorIndices(uint256) external => DISPATCHER(true);
    function _.validatePhaseTransition(IEtherFiNode.VALIDATOR_PHASE, IEtherFiNode.VALIDATOR_PHASE) external => DISPATCHER(true);

    function _.DEPRECATED_exitRequestTimestamp() external => DISPATCHER(true);
    function _.DEPRECATED_exitTimestamp() external => DISPATCHER(true);
    function _.DEPRECATED_phase() external => DISPATCHER(true);

    // Non-VIEW functions
    function _.initialize(address) external => DISPATCHER(true);
    function _.DEPRECATED_claimDelayedWithdrawalRouterWithdrawals(uint256) external => DISPATCHER(true);
    function _.createEigenPod() external => DISPATCHER(true);
    function _.isRestakingEnabled() external => DISPATCHER(true);
    function _.processNodeExit(uint256) external => DISPATCHER(true);
    function _.processFullWithdraw(uint256) external => DISPATCHER(true);
    function _.queueEigenpodFullWithdrawal() external => DISPATCHER(true);
    function _.completeQueuedWithdrawals(IDelegationManager.Withdrawal[], uint256[], bool) external => DISPATCHER(true);
    function _.completeQueuedWithdrawal(IDelegationManager.Withdrawal, uint256, bool) external => DISPATCHER(true);
    function _.updateNumberOfAssociatedValidators(uint16, uint16) external => DISPATCHER(true);
    function _.updateNumExitedValidators(uint16, uint16) external => DISPATCHER(true);
    function _.registerValidator(uint256, bool) external => DISPATCHER(true);
    function _.unRegisterValidator(uint256, IEtherFiNodesManager.ValidatorInfo) external => DISPATCHER(true);
    function _.splitBalanceInExecutionLayer() external => DISPATCHER(true);
    function _.totalBalanceInExecutionLayer() external => DISPATCHER(true);
    function _.withdrawableBalanceInExecutionLayer() external => DISPATCHER(true);
    function _.updateNumExitRequests(uint16, uint16) external => DISPATCHER(true);
    function _.migrateVersion(uint256, IEtherFiNodesManager.ValidatorInfo) external => DISPATCHER(true);

    function _.withdrawFunds(address,uint256,address,uint256,address,uint256,address,uint256) external => DISPATCHER(true);

    function _.moveFundsToManager(uint256) external => DISPATCHER(true);

    function EtherFiNode._calculateSplits(uint256 totalAmount, IEtherFiNodesManager.RewardsSplit memory) internal returns (uint256,uint256,uint256,uint256) => RewardsSplitCVL(totalAmount);

    function NodeA.getNonExitPenalty(uint32 _tNftExitRequestTimestamp, uint32 _bNftExitRequestTimestamp) internal returns (uint256) => NonExitPenaltyCVL(_tNftExitRequestTimestamp, _bNftExitRequestTimestamp);
    function NodeB.getNonExitPenalty(uint32 _tNftExitRequestTimestamp, uint32 _bNftExitRequestTimestamp) internal returns (uint256) => NonExitPenaltyCVL(_tNftExitRequestTimestamp, _bNftExitRequestTimestamp);
    function NodeA.getNonExitPenalty(uint32 _tNftExitRequestTimestamp, uint32 _bNftExitRequestTimestamp) external returns (uint256) => NonExitPenaltyCVL(_tNftExitRequestTimestamp, _bNftExitRequestTimestamp);
    function NodeB.getNonExitPenalty(uint32 _tNftExitRequestTimestamp, uint32 _bNftExitRequestTimestamp) external returns (uint256) => NonExitPenaltyCVL(_tNftExitRequestTimestamp, _bNftExitRequestTimestamp);
}

/// Enforcing the EtherFiNode to be post-upgrade:
/// Can cause unreachability for some initialization methods.

definition NodeVersion() returns uint16 = 1;

hook Sload uint16 _version EtherFiNodeA.version { require _version == NodeVersion();}

hook Sload uint16 _version EtherFiNodeB.version { require _version == NodeVersion();}


/// Splits over-approximation:
function RewardsSplitCVL(uint256 totalAmount) returns (uint256,uint256,uint256,uint256) {
    uint256 toNodeOperator; uint256 toTnft; uint256 toBnft; uint256 toTreasury;
    /// Could be verified easily by manual code review. Worth having a formal rule.
    require toNodeOperator + toTnft + toBnft + toTreasury == totalAmount;

    return (toNodeOperator, toTnft, toBnft, toTreasury);
}

/// Non-exit penalty over approximation
function NonExitPenaltyCVL(uint32 tNft_TS, uint32 bNft_TS) returns uint256 {
    if (tNft_TS == 0) return 0;

    uint128 penaltyPrinciple = NodesManager.nonExitPenaltyPrincipal();
    /*
    uint64 dailyPenalty = NodesManager.nonExitPenaltyDailyRate();
    uint256 daysElapsed = _getDaysPassedSince(tNft_TS, bNft_TS);
    if (daysElapsed > 365) {
        return _penaltyPrinciple;
    }
    */
    uint256 remaining;

    return require_uint256(penaltyPrinciple - remaining);
}