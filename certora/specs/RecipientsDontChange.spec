import "./Basic.spec";

using AuctionManager as auctionManager;

methods {
    // These have low-level calls that otherwise havoc
    // the recipient addresses for the rule that these do not change
    function _.upgradeToAndCall(address newImplementation, bytes memory data) external => NONDET;
    function _.forwardCall(address _to, bytes calldata _data) external  => NONDET;
}


rule recipientsDoNotChange (method f) filtered { f->
    // createBid does change the BidOwner and it is meant to
    f.selector != sig:AuctionManager.createBid(uint256,uint256).selector
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