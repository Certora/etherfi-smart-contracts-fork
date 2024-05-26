/* Initial setup for `LiquidityPool` */
methods {
}


/// @title Simple sanity rule to check sanity and call resolution
rule sanity(method f) {
    env e;
    calldataarg args;
    f(e, args);
    satisfy true;
}
