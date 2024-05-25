/* Initial setup for `LiquidityPool` - with a rule */
methods {
    function owner() external returns (address) envfree;
    function admins(address) external returns (bool) envfree;
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
