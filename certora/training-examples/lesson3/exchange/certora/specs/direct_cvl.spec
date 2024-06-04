/* Example that direct calls from CVL are never summarized */

using ERC20DummyA as _ERC20DummyA;

methods {
    function balanceA() external returns (uint256) envfree;
    function tokenA() external returns (address) envfree;

    // Exact function entry
    function ERC20DummyA.balanceOf(address) external returns (uint256) => NONDET;
}


/// @title Direct calls from CVL are never summarized
rule callsFromCVLNotSummarized() {
    env e;
    
    // This call is not summarized
    uint256 directBalanceA = _ERC20DummyA.balanceOf(e, currentContract);

    require tokenA() == _ERC20DummyA;
    uint256 indirectBalanceA = balanceA();

    satisfy directBalanceA != indirectBalanceA;
}
