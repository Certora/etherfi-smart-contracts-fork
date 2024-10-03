// import "./ERC721Receiver.spec"; 
// import "./EtherFiNodeInterface.spec"; 
// import "./EtherFiNodesManagerSetup.spec"; 
// import "./EigenLayerMethods.spec"; 
import "./Basic.spec";

// using LiquidityPool as Pool;
using AuctionManager as auctionManager;

methods {
    // dispatcher list for unresolved calls in
    // EtherFiNode.withdrawFunds
    unresolved external in EtherFiNode._ => DISPATCH [
        CallHookHelper.HarnessCallHook()
    ] default NONDET;

    function CallHookHelper.HarnessCallHook() external with (env e) => CVLCallHook(e);

}

// This function is used to catch all cases where there is
// a call outside the contract under verification and save
// the target address whenever the value transferred is nonzero
persistent ghost address money_recipient;
function CVLCallHook(env e)  {
    if (e.msg.value > 0) {
        money_recipient = e.msg.sender;
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

// * whichFunctionSendsETH_EtherFiNode in Basic.spec proves
// that the only functions that move money out of EtherFiNode
// are withdrawFunds and moveFundsToManager.
// * withdrawFunds can only be called by EtherFiNodeManager
// (because of a modifier) and it transfers money to addresses
// passed by parameter
// * EtherFiNodesManager calls EtherFiNode.withdraw in
// distributePayouts which is internal and called by: fullWithdraw,
// partialWithdraw
// * whichFunctionSendsETHFromNode_NodesManager also
// proves that fullWithdraw / partialWithdraw
// are the only functions which cause 

rule money_flow_from_node_full_withdraw {
    uint256 validatorId;
    env e;

    // initialize ghost to currentContract
    require money_recipient == currentContract; 

    // expected party addresses
    address treasury = currentContract.treasuryContract;
    address nodeOperator = auctionManager.getBidOwner(e, validatorId);
    address bnftHolder = currentContract.bnft.ownerOf(e, validatorId);
    address tnftHolder = currentContract.tnft.ownerOf(e, validatorId);

    fullWithdraw(e, validatorId);

    // If money was moved during this call it goes
    // to one of the expected recipients. The
    // case where money_recipient is currentContract
    // models the case where nonzero money is not moved.
    // temporarily made satisfy to check that this is a real result
    // with the routing that I expect
    assert money_recipient == currentContract ||
        money_recipient == treasury ||
        money_recipient == nodeOperator ||
        money_recipient == bnftHolder ||
        money_recipient == tnftHolder; 

    // The following encodes that all of these recipient
    // cases are reachable (and ensures that the above
    // assertion isn't just trivially stuck in the initial state)

    // This unconstrained ghost on which we branch is
    // just here to encode nondeterminstic choice
    mathint nondeterministic_choice;
    if (nondeterministic_choice == 0) {
        satisfy money_recipient == treasury;
    } else if (nondeterministic_choice == 1) {
        satisfy money_recipient == nodeOperator;
    } else if (nondeterministic_choice == 2) {
        satisfy money_recipient == bnftHolder;
    } else {
        satisfy money_recipient == tnftHolder;
    }

}

rule money_flow_from_node_partial_withdraw {
    uint256 validatorId;
    env e;

    // initialize ghost to currentContract
    require money_recipient == currentContract; 

    // expected party addresses
    address treasury = currentContract.treasuryContract;
    address nodeOperator = auctionManager.getBidOwner(e, validatorId);
    address bnftHolder = currentContract.bnft.ownerOf(e, validatorId);
    address tnftHolder = currentContract.tnft.ownerOf(e, validatorId);

    partialWithdraw(e, validatorId);

    // If money was moved during this call it goes
    // to one of the expected recipients. The
    // case where money_recipient is currentContract
    // models the case where nonzero money is not moved.
    assert money_recipient == currentContract ||
        money_recipient == treasury ||
        money_recipient == nodeOperator ||
        money_recipient == bnftHolder ||
        money_recipient == tnftHolder; 

    // The following encodes that all of these recipient
    // cases are reachable (and ensures that the above
    // assertion isn't just trivially stuck in the initial state)


    // This unconstrained ghost on which we branch is
    // just here to encode nondeterminstic choice
    mathint nondeterministic_choice;
    if (nondeterministic_choice == 0) {
        satisfy money_recipient == treasury;
    } else if (nondeterministic_choice == 1) {
        satisfy money_recipient == nodeOperator;
    } else if (nondeterministic_choice == 2) {
        satisfy money_recipient == bnftHolder;
    } else {
        satisfy money_recipient == tnftHolder;
    }
}