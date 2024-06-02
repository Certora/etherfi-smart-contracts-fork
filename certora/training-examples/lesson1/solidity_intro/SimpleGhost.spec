/* The most basic example of a ghost.
*/

ghost bool someoneVoted;

hook Sstore _hasVoted[KEY address voter] bool newVal (bool oldVal) {
    someoneVoted = true;
}

/// @title If someone voted, then the vote function was called
rule someoneVotesUsingVote(method f) {
    require !someoneVoted;

    env e;
    calldataarg args;
    f(e, args);

    assert someoneVoted => f.selector == sig:vote(bool).selector;
}
