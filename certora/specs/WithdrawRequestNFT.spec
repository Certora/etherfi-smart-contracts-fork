import "LiquidityPoolSummary.spec";
import "ERC721Receiver.spec";

using WithdrawRequestNFT as WithdrawRequestNFT;
use builtin rule sanity;

methods {
    function WithdrawRequestNFT.liquidityPool() external returns (address) envfree;
    function WithdrawRequestNFT.name() external returns (string memory) => NONDET DELETE;
    function WithdrawRequestNFT.symbol() external returns (string memory) => NONDET DELETE;

    /// IERC1822
    function _.proxiableUUID() external => PER_CALLEE_CONSTANT;
}

persistent ghost address Pool {
    axiom Pool == currentContract.liquidityPool;
}

definition isRequestWithdraw(method f) returns bool = 
    f.selector == sig:requestWithdraw(uint96,uint96,address,uint256).selector;

definition isUpgradeMethod(method f) returns bool = 
    f.selector == sig:upgradeToAndCall(address,bytes).selector;

rule cannot_frontrun_requestWithdraw(method f) filtered{f->!isRequestWithdraw(f) && !isUpgradeMethod(f)} {
    env e1;
    calldataarg args1;
    /// The liquidityPool doesn't pass any ETH when calling requestWithdraw (check!)
    require e1.msg.value == 0;

    env e2;
    calldataarg args2;
    storage initState = lastStorage;

    requestWithdraw(e1, args1);

    f(e2, args2) at initState;
    requestWithdraw@withrevert(e1, args1);

    assert e1.msg.sender != e2.msg.sender => !lastReverted;
}

rule requestWithdraw_is_user_indepednent(address user1, address user2) {
    env e1;
    env e2;
    /// Both callers are liquidityPool.
    require e1.msg.sender == e2.msg.sender;
    /// LiquidityPool is the caller and isn't the WithdrawRequestNFT contract
    require e1.msg.sender != WithdrawRequestNFT;
    /// The liquidityPool doesn't pass any ETH when calling requestWithdraw (check!)
    require e1.msg.value == 0; require e2.msg.value == 0;
    /// Sum of native balances cannot exceed 2^256 - 1.
    require nativeBalances[e1.msg.sender] + nativeBalances[WithdrawRequestNFT] <= max_uint256;

    storage initState = lastStorage;

    uint96 amountOfEEth1; 
    uint96 shareOfEEth1;
    uint256 fee1;

    uint96 amountOfEEth2; 
    uint96 shareOfEEth2;
    uint256 fee2;

    requestWithdraw(e1, amountOfEEth1, shareOfEEth1, user1, fee1);

    requestWithdraw(e2, amountOfEEth2, shareOfEEth2, user2, fee2) at initState;
    requestWithdraw@withrevert(e1, amountOfEEth1, shareOfEEth1, user1, fee1);

    assert user1 != user2 => !lastReverted;
}