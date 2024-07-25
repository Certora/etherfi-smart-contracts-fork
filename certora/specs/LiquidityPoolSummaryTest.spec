import "LiquidityPoolMock.spec";

using LiquidityPool as Pool;

methods {
    /// LiquidityPool
    function Pool.reduceEthAmountLockedForWithdrawal(uint128) external;
    function Pool.addEthAmountLockedForWithdrawal(uint128) external;
    function Pool.withdraw(address, uint256) external returns (uint256);

    function Pool.amountForShare(uint256) external returns (uint256) envfree;
    function Pool.sharesForAmount(uint256) external returns (uint256) envfree;
    function Pool.getTotalPooledEther() external returns (uint256) envfree;
    function Pool.getTotalEtherClaimOf(address) external returns (uint256) envfree;
    function Pool.ethAmountLockedForWithdrawal() external returns (uint128) envfree;
    function Pool.sharesForWithdrawalAmount(uint256) external returns (uint256) envfree;
}

persistent ghost address WithdrawRequestNFT {
    axiom WithdrawRequestNFT == Pool.withdrawRequestNFT;
}

function isEquivalentState() returns bool {
    return 
        getEthAmountLockedForWithdrawalCVL() == Pool.ethAmountLockedForWithdrawal() &&
        getTotalPooledEtherCVL() == Pool.getTotalPooledEther();
}

rule Equivalence_getTotalEtherClaim(address user) {
    require isEquivalentState();
    assert Pool.getTotalEtherClaimOf(user) == getTotalEtherClaimOfCVL(user);
}

rule Equivalence_sharesForAmount(uint256 amount) {
    require isEquivalentState();
    assert Pool.sharesForAmount(amount) == sharesForAmountCVL(amount);
}

rule Equivalence_amountForShare(uint256 shares) {
    require isEquivalentState();
    assert Pool.amountForShare(shares) == amountForShareCVL(shares);
}

rule Equivalence_sharesForWithdrawalAmount(uint256 amount) {
    require isEquivalentState();
    assert Pool.sharesForWithdrawalAmount(amount) == sharesForWithdrawalAmountCVL(amount);
}

rule Equivalence_withdraw(address recipient, uint256 amount) {
    storage initState = lastStorage;
    env e;
    require e.msg.sender == WithdrawRequestNFT;
    require isEquivalentState();
    bool reverted_cond = withdrawRevertCondition(amount);

    withdrawCVL(e.msg.sender, recipient, amount);

    withdraw(e, recipient, amount);

    assert !reverted_cond;
    assert isEquivalentState();
}

rule Equivalence_reduceEthAmount(uint128 amount) {
    env e;
    require isEquivalentState();

    reduceEthAmount(amount);

    Pool.reduceEthAmountLockedForWithdrawal(e, amount);

    assert isEquivalentState();
}

rule Equivalence_addEthAmount(uint128 amount) {
    env e;
    require isEquivalentState();

    addEthAmount(amount);

    Pool.addEthAmountLockedForWithdrawal(e, amount);

    assert isEquivalentState();
}