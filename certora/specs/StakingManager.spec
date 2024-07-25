// using NodeOperatorManager as NodeOperatorManager;
/* Verification of `AuctionManager` */
methods {
    function _.upgradeToAndCall(address,bytes) external => NONDET;
}

/// @title Verifies that all functions can be called
rule sanity(method f) {
    env e;
    calldataarg args;
    f(e, args);
    satisfy true;
}