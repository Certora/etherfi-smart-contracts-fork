using EETH as eETH;
using FallbackCaller as FallbackCaller;

methods {
    /// eETH
    function eETH.totalShares() external returns (uint256) envfree;
    function eETH.shares(address) external returns (uint256) envfree;
    function eETH.balanceOf(address) external returns (uint256) envfree;
    //function eETH.name() external returns (string memory) => NONDET DELETE;
    //function eETH.symbol() external returns (string memory) => NONDET DELETE;
}

ghost uint128 _ethAmountLockedForWithdrawal {
    init_state axiom _ethAmountLockedForWithdrawal ==0;
}

ghost uint256 _totalPooledEther {
    init_state axiom _totalPooledEther ==0;
}

function getEthAmountLockedForWithdrawalCVL() returns uint128 {
    return _ethAmountLockedForWithdrawal;
}

function getTotalPooledEtherCVL() returns uint256 {
    return _totalPooledEther;
}

/// We assume that _ethAmountLockedForWithdrawal > sum of withdrawal amounts.
function reduceEthAmount(uint128 amount) {
    _ethAmountLockedForWithdrawal = require_uint128(_ethAmountLockedForWithdrawal - amount);
}

function addEthAmount(uint128 amount) {
    /// We assume no overflow
    _ethAmountLockedForWithdrawal = require_uint128(_ethAmountLockedForWithdrawal + amount);
}

function amountForShareCVL(uint256 shares) returns uint256 {
    uint256 totalShares = eETH.totalShares();
    if (totalShares == 0) return 0;
    /// We assume no overflow
    return require_uint256((shares * getTotalPooledEtherCVL()) / totalShares);
}

function sharesForWithdrawalAmountCVL(uint256 amount) returns uint256 {
    uint256 totalPooledEther = getTotalPooledEtherCVL();
    if (totalPooledEther == 0) return 0;
    /// We assume no overflow
    return require_uint256((amount * eETH.totalShares() + totalPooledEther - 1) / totalPooledEther);
}

function sharesForAmountCVL(uint256 amount) returns uint256 {
    uint256 totalPooledEther = getTotalPooledEtherCVL();
    if (totalPooledEther == 0) return 0;
    /// We assume no overflow
    return require_uint256( amount * eETH.totalShares() / totalPooledEther);
}

function getTotalEtherClaimOfCVL(address user) returns uint256 {
    uint256 totalShares = eETH.totalShares();
    if (totalShares == 0) return 0;
    /// We assume no overflow
    return require_uint256(getTotalPooledEtherCVL() * eETH.shares(user) / totalShares);
}

function withdrawCVL(address caller, address recipient, uint256 amount) returns uint256 {
    assert caller == WithdrawRequestNFT;
    require !withdrawRevertCondition(amount);

    uint256 share = sharesForWithdrawalAmountCVL(amount);
    require share > 0;

    _totalPooledEther = assert_uint128(_totalPooledEther - amount);
    reduceEthAmount(assert_uint128(amount));

    env e1;
    require e1.msg.sender == Pool;
    eETH.burnShares(e1, caller, share);

    env e2;
    require e2.msg.sender == Pool;
    FallbackCaller.callFallback(e2, recipient, amount);

    return share;
}

function withdrawRevertCondition(uint256 amount) returns bool {
    //if (totalValueInLp < _amount ||
    // (msg.sender == address(withdrawRequestNFT) && ethAmountLockedForWithdrawal < _amount)
    // || eETH.balanceOf(WithdrawRequestNFT) < _amount) revert InsufficientLiquidity()
    return amount > max_uint128 || amount == 0 ||
        _totalPooledEther - amount < 0 || _totalPooledEther - amount > max_uint128; 
}