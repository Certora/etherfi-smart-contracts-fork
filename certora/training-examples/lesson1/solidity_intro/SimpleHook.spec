/* The most basic example of a hook.
*/

hook Sstore _hasVoted[KEY address voter] bool newVal (bool oldVal) {
    assert newVal && !oldVal;
}

/// @title `_hasVoted` can only change from false to true
rule hasVotedOnlyOneWayChange(method f) {
    env e;
    calldataarg args;
    f(e, args);
    assert true;
}
