import "./ERC721Receiver.spec";
import "./EtherFiNodeInterface.spec";
import "./EtherFiNodesManagerSetup.spec";
import "./EigenLayerMethods.spec";

using LiquidityPool as Pool;

/// Linking all instances of treasury contract address to a ghost unique address.

persistent ghost address treasuryAddress;

hook Sload address _treasury EtherFiNodesManager.treasuryContract {
    require treasuryAddress == _treasury;
}

hook Sload address _treasury LiquidityPool.treasury {
    require treasuryAddress == _treasury;
}

use builtin rule sanity filtered{f -> f.contract == NodesManager && ignoreMethods_NodesManager(f)}

rule payableNonZeroMsgValue(method f) filtered{f -> f.isPayable} {
    env e;
    calldataarg args;
    f(e,args);

    satisfy e.msg.value > 0;
}

definition methodsSendETH_EtherFiNode(method f) returns bool = 
    f.selector == sig:EtherFiNodeA.moveFundsToManager(uint256).selector ||
    f.selector == sig:EtherFiNodeA.withdrawFunds(address,uint256,address,uint256,address,uint256,address,uint256).selector;

rule whichFunctionSendsETH_EtherFiNode(method f) 
filtered{f -> !f.isView && f.contract == NodeA} 
{
    env e;
    require e.msg.sender != NodeA;   /// Node doesn't call itself;
    calldataarg args;
    mathint balance_before = nativeBalances[NodeA];
    f(e, args);
    mathint balance_after = nativeBalances[NodeA];

    assert balance_after < balance_before => methodsSendETH_EtherFiNode(f);
    satisfy methodsSendETH_EtherFiNode(f) => balance_after < balance_before;
}

definition methodsCallEtherNode_NodesManager(method f) returns bool =
    f.selector == sig:EtherFiNodesManager.partialWithdraw(uint256).selector ||
    f.selector == sig:EtherFiNodesManager.fullWithdraw(uint256).selector;

rule whichFunctionSendsETHFromNode_NodesManager(method f) 
filtered{f -> !f.isView && ignoreMethods_NodesManager(f) && f.contract == NodesManager} 
{
    env e;
    require e.msg.sender != NodesManager;   /// Nodes manager doesn't call itself;
    calldataarg args;
    mathint balance_before = nativeBalances[NodeA];
    f(e, args);
    mathint balance_after = nativeBalances[NodeA];

    assert balance_after < balance_before => methodsCallEtherNode_NodesManager(f);
    satisfy methodsCallEtherNode_NodesManager(f) => balance_after < balance_before;
}

definition methodsSendETH_Pool(method f) returns bool = 
    f.selector == sig:LiquidityPool.batchRegister(uint256[],IStakingManager.DepositData[],bytes32[],bytes[]).selector ||
    f.selector == sig:LiquidityPool.withdraw(address,uint256).selector ||
    f.selector == sig:LiquidityPool.batchApproveRegistration(uint256[],bytes[],bytes[]).selector ||
    f.selector == sig:LiquidityPool.batchCancelDeposit(uint256[]).selector;

rule whichFunctionSendsETH_Pool(method f) 
filtered{f -> !f.isView && f.contract == Pool} 
{
    env e;
    require e.msg.sender != Pool;   /// Pool doesn't call itself;
    calldataarg args;
    mathint balance_before = nativeBalances[Pool];
    f(e, args);
    mathint balance_after = nativeBalances[Pool];

    assert balance_after < balance_before => methodsSendETH_Pool(f);
    satisfy methodsSendETH_Pool(f) => balance_after < balance_before;
}