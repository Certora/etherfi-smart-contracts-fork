methods {
    // Main contract `LiquidityPool`
    function owner() external returns (address) envfree;
    function admins(address) external returns (bool) envfree;

    // `EtherFiNode` dispatching
    function _.initialize(address) external => DISPATCHER(true);
    function _.withdrawFunds(
        address, uint256, address, uint256, address, uint256, address, uint256
    ) external => DISPATCHER(true);
    function _.claimQueuedWithdrawals(uint256, bool) external => DISPATCHER(true);
    function _.createEigenPod() external => DISPATCHER(true);
    function _.processNodeExit() external => DISPATCHER(true);
    function _.queueRestakedWithdrawal() external => DISPATCHER(true);
    function _.updateNumberOfAssociatedValidators(uint16, uint16) external => DISPATCHER(true);
    function _.updateNumExitedValidators(uint16 _up, uint16 _down) external => DISPATCHER(true);
    function _.registerValidator(uint256, bool) external => DISPATCHER(true);
    function _.unRegisterValidator(
        uint256, IEtherFiNodesManager.ValidatorInfo
    ) external => DISPATCHER(true);
    function _.updateNumExitRequests(uint16, uint16) external => DISPATCHER(true);
    function _.migrateVersion(
        uint256, IEtherFiNodesManager.ValidatorInfo
    ) external => DISPATCHER(true);
    function _.callEigenPod(bytes) external => DISPATCHER(true);
    function _.forwardCall(address, bytes) external => DISPATCHER(true);
    function _.moveFundsToManager(uint256) external => DISPATCHER(true);

    // `ERC721ReceiverMockUpgradeable` dispatching
    function _.onERC721Received(address, address, uint256, bytes) external => DISPATCHER(true);

    // `IDepositContract` dispatching
    function _.deposit(bytes, bytes, bytes, bytes32) external =>  DISPATCHER(true);
}


definition isUUPSUpgradeableFunc(method f) returns bool = (
    f.selector == sig:upgradeToAndCall(address, bytes).selector
);


/// @title Simple sanity rule to check sanity and call resolution
rule sanity(method f) {
    env e;
    calldataarg args;
    f(e, args);
    satisfy true;
}


/// @title Only the owner can change admin
rule onlyOwnerCanChangeAdmin(address a, method f) filtered {
    f -> !isUUPSUpgradeableFunc(f)
} {
    bool preStatus = admins(a);

    env e;
    calldataarg args;
    f(e, args);

    bool postStatus = admins(a);
    assert (preStatus != postStatus) => e.msg.sender == owner();
}
