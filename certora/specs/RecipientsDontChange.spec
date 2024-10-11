import "./Basic.spec";

using AuctionManager as auctionManager;

methods {
    // These have low-level calls that otherwise havoc
    // the recipient addresses for the rule that these do not change
    function _.upgradeToAndCall(address newImplementation, bytes data) external => NONDET;
    // cannot NONDET this
    // function _.functionCall(address target, bytes memory data) internal => NONDET;
    // function _.functionCallWithValue(
    //     address target, bytes data,
    //     uint256 value, string errorMessage) internal => NONDET;
}


rule recipientsDoNotChange (method f) filtered { f->
    // createBid does change the BidOwner and it is meant to
    f.selector != sig:AuctionManager.createBid(uint256,uint256).selector &&
    // Sets EtherFiNodesManager for the first time which will affect
    // the bnft and tnft values
    f.selector != sig:EtherFiNodeA.initialize(address).selector &&
    f.selector != sig:EtherFiNodeB.initialize(address).selector &&
    // This just directly does an external call which will havoc.
    // These also return bytes so we cannot NONDET them.
    f.selector != sig:EtherFiNodeA.forwardCall(address,bytes).selector &&
    f.selector != sig:EtherFiNodeB.forwardCall(address,bytes).selector &&
    // Also directly does an external and returns bytes
    f.selector != sig:EtherFiNodeA.callEigenPod(bytes).selector &&
    f.selector != sig:EtherFiNodeB.callEigenPod(bytes).selector &&
    // Another direct external call
    f.selector != sig:AuctionManager.upgradeToAndCall(address,bytes).selector &&
    f.selector != sig:EtherFiNodesManager.upgradeToAndCall(address,bytes).selector &&
    // Sets bnft / tnft directly so clearly will change these
    f.selector != sig:EtherFiNodesManager.initialize(
        address,address,address,address,address,address,
        address,address).selector &&
    // Deprecated method not worth checking
    f.selector != sig:EtherFiNodeA.DEPRECATED_claimDelayedWithdrawalRouterWithdrawals(uint256).selector &&
    f.selector != sig:EtherFiNodeB.DEPRECATED_claimDelayedWithdrawalRouterWithdrawals(uint256).selector &&
    // Calls a whole bunch of deprecated functions so seems on its way out
    f.selector != sig:EtherFiNodesManager.initializeV2dot5(address).selector
}{
    uint256 validatorId;
    env e;
    calldataarg args;

    address nodeOperator_before = auctionManager.getBidOwner(e, validatorId);
    address bnftHolder_before = currentContract.bnft.ownerOf(e, validatorId);
    address tnftHolder_before = currentContract.tnft.ownerOf(e, validatorId);

    f(e, args);

    assert nodeOperator_before == auctionManager.getBidOwner(e, validatorId);
    assert bnftHolder_before == currentContract.bnft.ownerOf(e, validatorId);
    assert tnftHolder_before == currentContract.tnft.ownerOf(e, validatorId);

}