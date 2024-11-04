using EtherFiNodesManager as NodesManager;
using RoleRegistry as RR;

methods {
    // Getters:
    function NodesManager.numberOfValidators() external returns (uint64) envfree; // # of validators in LIVE or WAITING_FOR_APPROVAL phases
    function NodesManager.nonExitPenaltyPrincipal() external returns (uint64) envfree;
    function NodesManager.nonExitPenaltyDailyRate() external returns (uint64) envfree;
    function NodesManager.SCALE() external returns (uint64) envfree;
    function NodesManager.treasuryContract() external returns (address) envfree;
    function NodesManager.stakingManagerContract() external returns (address) envfree;
    function NodesManager.auctionManager() external returns (address) envfree;
    function NodesManager.eigenPodManager() external returns (address) envfree;
    function NodesManager.etherfiNodeAddress(uint256) external returns (address) envfree; // validatorId == bidId -> withdrawalSafeAddress
    function NodesManager.unusedWithdrawalSafes(uint256) external returns (address) envfree;

    function _.instantiateEtherFiNode(bool) external => NONDET;

    // delegationManager summaries:
    function _.delegationManager() external => NONDET;
    function _.beaconChainETHStrategy() external => NONDET;
    function _.queueWithdrawals(IDelegationManager.QueuedWithdrawalParams[]) external => NONDET;
    function _.completeQueuedWithdrawals(IDelegationManager.Withdrawal[],address[][],uint256[],bool[]) external => NONDET; // external call only.

    // Auction manager summaries:
    function _.getBidOwner(uint256) external => NONDET;

    // Deprecated and penalty functions:
    function _.DEPRECATED_delayedWithdrawalRouter() external => NONDET;

    function _.getClaimableUserDelayedWithdrawals(address) external => NONDET;

    function _.proxiableUUID() external => PER_CALLEE_CONSTANT;

    /// Role Registry
    function NodesManager.NODE_ADMIN_ROLE() external returns (bytes32) envfree;
    function RR.hasRole(bytes32,address) external returns (bool) envfree;
}

// FILTERING-OUT THE FOLLOWING CALLS:
definition ignoreMethods_NodesManager(method f) returns bool =
    /// Forward to EigenPod
    f.selector != sig:EtherFiNodesManager.forwardEigenpodCall(uint256[],bytes[]).selector &&
    /// Forward to EtherFiNode
    f.selector != sig:EtherFiNodesManager.forwardExternalCall(uint256[],bytes[],address).selector &&
    /// Upgrade function
    f.selector != sig:EtherFiNodesManager.upgradeToAndCall(address, bytes).selector &&
    /// Initialization (we assume we already are post-update).
    f.selector != sig:EtherFiNodesManager.initializeV2dot5(address).selector &&
    /// Same as calling `fullWithdraw(uint256` multiple times.
    f.selector != sig:EtherFiNodesManager.batchFullWithdraw(uint256[]).selector;