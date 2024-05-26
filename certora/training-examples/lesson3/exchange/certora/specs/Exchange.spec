/* Verification of Exchange contract */
methods {
    function balanceA() external returns (uint256) envfree;
    function balanceB() external returns (uint256) envfree;
}


/// @title Integrity of `transferAtoB` (w.r.t. current contract)
rule transferIntegrity(uint256 amount) {
    mathint preA = balanceA();
    mathint preB = balanceB();

    require preA + amount <= max_uint256;

    env e;
    require e.msg.sender != currentContract;  // Why is this needed?
    transferAtoB(e, amount);
    
    mathint postA = balanceA();
    mathint postB = balanceB();

    assert postA - preA == to_mathint(amount);
    assert preB - postB == to_mathint(amount);
}
