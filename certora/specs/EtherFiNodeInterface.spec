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
    // EigenPod function:
    function _.startCheckpoint(bool) external => NONDET;
    function _.setProofSubmitter(address) external => NONDET;
    function _.callEigenPod(bytes) external => NONDET;
    function _.forwardCall(address, bytes) external => NONDET;

    function _.withdrawFunds(address,uint256,address,uint256,address,uint256,address,uint256) external => DISPATCHER(true);

    function _.moveFundsToManager(uint256) external => DISPATCHER(true);
}