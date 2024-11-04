// Status: All Rules PASSING: https://prover.certora.com/output/65266/ff3119ec04544fdbb502959ea809567e/?anonymousKey=36c40fc440497ae114c993ed9818d44ad0577708
import "./Basic.spec";

using AuctionManager as auctionManager;

// Tracks if there was ever a transfer to an address
// other than the expected ones.
persistent ghost bool illegal_transfer;

// These are used to pass the relevant addresses to the hook. Calling
// methods on variables does not seem supported within hooks, so
// using these ghosts and calling the relevant functions in the rule
// is a workaround for that
persistent ghost address treasury;
persistent ghost address nodeOperator;
persistent ghost address bnftHolder;
persistent ghost address tnftHolder;

// These are used to express the liveness condition
// that each of these are sent value
persistent ghost bool sent_treasury;
persistent ghost bool sent_nodeOperator;
persistent ghost bool sent_bnftHolder;
persistent ghost bool sent_tnftHolder;

hook CALL(uint g, address addr, uint value, uint argsOffs, uint argLength, uint retOffset, uint retLength) uint rc {
    if (value > 0)  {
        if (!(addr == treasury ||
            addr == nodeOperator ||
            addr == bnftHolder ||
            addr == tnftHolder)) {
            illegal_transfer = true;
        }
        // The OR is used so that we don't unset this.
        // These are true if they are ever sent to
        sent_treasury = sent_treasury || addr == treasury;
        sent_nodeOperator = sent_nodeOperator || addr == nodeOperator;
        sent_bnftHolder = sent_bnftHolder || addr == bnftHolder;
        sent_tnftHolder = sent_tnftHolder || addr == tnftHolder;
    }

}

// the only possible flow of validator funds is eigenpod -> etherfiNode ->
// expectedParties where expected parties in the current contract are currently
// bnftHolder / tnftHolder / nodeOperator / treasury. An upcoming change from @V
// will be adjusting that mechanism slightly so that all funds flow directly to
// the liquidity pool. But the important piece of the property to me is simply
// that funds can't possibly be transferred to an unexpected target. This would
// give the assurance that the worst case scenario of a logic bug is simply that
// some validator funds could be temporarily stuck until we upgrade with a fix,
// but user funds would never be lost.

// We rely on other rules to complete this proof.
// * whichFunctionSendsETH_EtherFiNode in Basic.spec proves
// that the only functions that move money out of EtherFiNode
// are withdrawFunds and moveFundsToManager.
use rule whichFunctionSendsETH_EtherFiNode;

// * withdrawFunds can only be called by EtherFiNodeManager
// (because of a modifier) and it transfers money to addresses
// passed by parameter
// see rule only_nodes_manager below

// * EtherFiNodesManager calls EtherFiNode.withdraw in
// distributePayouts which is internal and called by: fullWithdraw,
// partialWithdraw
// * whichFunctionSendsETHFromNode_NodesManager also
// proves that fullWithdraw / partialWithdraw
// are the only functions which cause money to move out of etherfiNode
use rule whichFunctionSendsETHFromNode_NodesManager;

// We then prove that for full/partial withdraw, money only
// flows to the expected recipients

function callMoneyMovementFunction(env e, method f, uint256 validator) {
    if(f.selector == sig:EtherFiNodesManager.partialWithdraw(uint256).selector){
        partialWithdraw(e, validator);
    }
    if(f.selector == sig:EtherFiNodesManager.fullWithdraw(uint256).selector){
        fullWithdraw(e, validator);
    }
    if(f.selector == sig:EtherFiNodesManager.batchPartialWithdraw(uint256[]).selector){
        uint256[] validators;
        require validators.length == 1;
        require validators[0] == validator;
        batchPartialWithdraw(e, validators);
    }
}

// Money only flows to the expected recipients for full withdraw
rule money_flow_from_node (method f) filtered { f->
    methodsCallEtherNode_NodesManager(f)
}{
    uint256 validatorId;
    env e;

    require treasury == currentContract.treasuryContract;
    require nodeOperator == auctionManager.getBidOwner(e, validatorId);
    require bnftHolder == currentContract.bnft.ownerOf(e, validatorId);
    require tnftHolder == currentContract.tnft.ownerOf(e, validatorId);

    require !sent_treasury;
    require !sent_nodeOperator;
    require !sent_bnftHolder;
    require !sent_tnftHolder;

    require !illegal_transfer;

    callMoneyMovementFunction(e, f, validatorId);

    // The following encodes that all of these recipient
    // cases are reachable (and ensures that the above
    // assertion isn't just trivially stuck in the initial state)

    // This unconstrained ghost on which we branch is
    // just here to encode nondeterminstic choice

    assert !illegal_transfer;


    satisfy treasury != nodeOperator &&
        treasury != bnftHolder &&
        treasury != tnftHolder &&
        nodeOperator != bnftHolder &&
        nodeOperator != tnftHolder &&
        bnftHolder != tnftHolder;

    mathint nondeterministic_choice;

    if (nondeterministic_choice == 0) {
        // to generate call trace
        satisfy sent_treasury;
    } else if (nondeterministic_choice == 1) {
        satisfy sent_nodeOperator;
    } else if (nondeterministic_choice == 2) {
        satisfy sent_bnftHolder;
    } else {
        satisfy sent_tnftHolder;
    }

}

// // These cause hardstops
// // // frontrunning cannot cause withdraw to be blocked
// rule money_flow_from_node_full_withdraw_frontrunning (method f)
// filtered { f->
//     methodsCallEtherNode_NodesManager(f)
// }{
//     uint256 validatorId;
//     env e;
// 
//     storage init = lastStorage;
//     
//     fullWithdraw(e, validatorId);
// 
//     env e2;
//     calldataarg args;
//     f(e2, args);
// 
//     fullWithdraw@withrevert(e, validatorId) at init;
//     assert !lastReverted;
// }
// 
// // frontrunning cannot cause partial withdraw to be blocked
// rule money_flow_from_node_partial_withdraw_frontrunning (method f) 
// filtered { f->
//     methodsCallEtherNode_NodesManager(f)
// }{
//     uint256 validatorId;
//     env e;
// 
//     storage init = lastStorage;
//     
//     partialWithdraw(e, validatorId);
// 
//     env e2;
//     calldataarg args;
//     f(e2, args);
// 
//     partialWithdraw@withrevert(e, validatorId) at init;
//     assert !lastReverted;
// }


// Show that only EtherFiNodesManager can call the
// functions of EtherFiNode that move money out
rule only_nodes_manager (method f) filtered { f -> 
    !f.isView && f.contract == NodeA &&
    methodsSendETH_EtherFiNode(f)
}{
    calldataarg args;
    env e;
    f(e, args);
    assert e.msg.sender == NodeA.etherFiNodesManager;
}