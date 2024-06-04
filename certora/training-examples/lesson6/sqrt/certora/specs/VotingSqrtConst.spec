/* Spec for Square Root Voting Strength - CONSTANT summary */

using ERC20 as _ERC20;

methods
{
    function totalVotes() external returns (uint256) envfree;
    function votesInFavor() external returns (uint256) envfree;
    function votesAgainst() external returns (uint256) envfree;
    function hasVoted(address) external returns (bool) envfree;
    function votingPower(address) external returns (uint256) envfree;

    // Using constant summary
    // Note: summarizing the internal function!
    function sqrt(uint256) internal returns (uint256) => CONSTANT;

    function ERC20.balanceOf(address) external returns (uint256) envfree;
}


/// @title Sum results is total votes
invariant sumResultsEqualsTotalVotes()
    votesInFavor() + votesAgainst() == to_mathint(totalVotes());


/// @title Voting power function properties (can be an invariant)
rule votingPowerProperties(address a, address b) {

    uint256 balanceA = _ERC20.balanceOf(a);
    uint256 powerA = votingPower(a);

    uint256 balanceB = _ERC20.balanceOf(b);
    uint256 powerB = votingPower(b);

    assert balanceA == 0 => powerA == 0, "Voting power preserves zero";
    assert (
        balanceA <= balanceB => powerA <= powerB,
        "Voting power weakly monotonic increasing"
    );
}


/// @title Vote integrity
rule voteIntegrity(address voter, bool isInFavor) {

    uint256 power = votingPower(voter);
    uint256 totalBefore = totalVotes();
    uint256 inFavorBefore = votesInFavor();
    uint256 againstBefore = votesAgainst();

    env e;
    require e.msg.sender == voter;
    vote(e, isInFavor);

    assert (
        to_mathint(totalVotes()) == totalBefore + power,
        "Total votes increased by power"
    );
    assert (
        (isInFavor => to_mathint(votesInFavor()) == inFavorBefore + power) &&
        (!isInFavor => to_mathint(votesAgainst()) == againstBefore + power),
        "Votes in favor or against tally increased by power"
    );
}
