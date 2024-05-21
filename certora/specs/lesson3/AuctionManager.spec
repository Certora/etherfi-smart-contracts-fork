/* Verification of `AuctionManager` */
methods {
    function getBidOwner(uint256) external returns (address) envfree;
    function numberOfBids() external returns (uint256) envfree;
}


/// @title Verifies that all functions can be called
rule sanity(method f) {
    env e;
    calldataarg args;
    f(e, args);
    satisfy true;
}


/// @title Functions filtered out since they use `delegatecall`
definition isFilteredFunc(method f) returns bool = (
    f.selector == sig:upgradeToAndCall(address, bytes).selector
);


/// @title The contact is set as initialized in the constructor -- seems a bug?
invariant alwaysInitialized()
    currentContract._initialized > 0
    filtered {f -> !isFilteredFunc(f)}
