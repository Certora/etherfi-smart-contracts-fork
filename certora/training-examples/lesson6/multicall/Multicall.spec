/* Batch calls verification example */
methods {
    function sumOfThree(address, address, address) external returns (uint256) envfree;
    function getBalance(address) external returns (uint256) envfree;

    // Dispatch summary - for unresolved calls in `multicall`
    function _._ external => DISPATCH [
        getBalance(address)
    ] default HAVOC_ECF;
}


/// @title A `sumOfThree` example to see the call trace
rule exampleSumOfThree() {
    calldataarg args;
    uint256 total = sumOfThree(args);
    satisfy true;
}


/// @title Verify correctness of `sumOfThree` function
rule testSumOfThree(address userA, address userB, address userC) {
    uint256 balanceA = getBalance(userA);
    uint256 balanceB = getBalance(userB);
    uint256 balanceC = getBalance(userC);

    uint256 total = sumOfThree(userA, userB, userC);
    assert to_mathint(total) == balanceA + balanceB + balanceC;
}
