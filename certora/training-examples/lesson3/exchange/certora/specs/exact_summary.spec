/* Example that exact entry has precedence over wild card */

using ERC20DummyA as _ERC20DummyA;

methods {
    function balanceA() external returns (uint256) envfree;
    function balanceB() external returns (uint256) envfree;
    function tokenA() external returns (address) envfree;

    // Exact function entry
    function ERC20DummyA.balanceOf(address) external returns (uint256) => ALWAYS(0);

    // Using a dispatcher
    function _.balanceOf(address) external => DISPATCHER(true);
}


/// @title Exact function entry has precedence over wild card
rule exactEntryPrecedence() {
    require tokenA() == _ERC20DummyA;

    // This will force the Prover to use `ERC20DummyB` for `tokenB`
    satisfy balanceA() != balanceB();
}
