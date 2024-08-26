import "./EtherFiNodeSetup.spec";

use invariant mirrorLength;
use invariant validatorPastLengthAreNullified;
use invariant validatorIndeciesLessThanLength;
use invariant validatorIndeciesValidaorIdMirror;
use invariant blockNumberValidity;
use invariant validatorIdsAreUnique;
use invariant validatorIdNeverZero;
use builtin rule sanity;

rule integrityRegisterValidator(uint256 validatorId, bool enableRestaking) {
    env e;
    requireInvariant validatorIndeciesValidaorIdMirror();
    require version() == 1;
    require validatorId != 0;

    mathint numOfValidatorsPre = sumAllAssociatedValidatorIds;
    require numOfValidatorsPre < max_uint256;

    bool validatorExistsPre = (associatedValidatorIndicesGhost[validatorId] != 0);

    registerValidator(e, validatorId, enableRestaking);

    bool validatorExistsPost = (associatedValidatorIndicesGhost[validatorId] != 0);

    mathint numOfValidatorsPost = sumAllAssociatedValidatorIds;

    assert !validatorExistsPre && validatorExistsPost => numOfValidatorsPost == numOfValidatorsPre + 1;
    assert !validatorExistsPre => associatedValidatorIdsGhost[assert_uint256(numOfValidatorsPre)] == validatorId;
    assert !validatorExistsPre => associatedValidatorIndicesGhost[validatorId] == numOfValidatorsPre;
}

rule integrityOfUnregisterValidator(uint256 validatorId, IEtherFiNodesManager.ValidatorInfo info) {
    env e;
    bool succeed;

    mathint numOfValidatorsPre = sumAllAssociatedValidatorIds;

    bool validatorExistsPre = (associatedValidatorIndicesGhost[validatorId] != 0);
    
    succeed = unRegisterValidator(e, validatorId, info);

    bool validatorExistsPost = (associatedValidatorIndicesGhost[validatorId] != 0);
    assert false;
}

rule pendingComplitedWithdrawalsCorrelation(method f) {
    env e;
    calldataarg args;

    uint64 pendingPre =  pendingWithdrawalFromRestakingInGwei();
    uint64 completedPre =  completedWithdrawalFromRestakingInGwei();

    f(e, args);

    uint64 pendingPost =  pendingWithdrawalFromRestakingInGwei();
    uint64 completedPost =  completedWithdrawalFromRestakingInGwei();

    assert pendingPost < pendingPre => completedPost > completedPre;
}

rule whoLeaveEth(method f, address membershipAddress) {
    env e;
    // require membershipAddress != e.msg.sender;
    // require auctionManager.membershipManagerContractAddress() == membershipAddress;
    calldataarg args;
    uint256 contractBalancePre = nativeBalances[currentContract];
        f(e,args);
    uint256 contractBalancePost = nativeBalances[currentContract];
    assert contractBalancePre == contractBalancePost;
}

// Verify state diafram from documentation.
// State Transition Diagram for StateMachine contract:
//
//      NOT_INITIALIZED <-
//              |        |
//              ↓        |
//      STAKE_DEPOSITED --
//           /    \      |
//          ↓      ↓     |
//         LIVE <- WAITING_FOR_APPROVAL
//         |  \ 
//         |   ↓  
//         |  BEING_SLASHED
//         |   /
//         ↓  ↓
//         EXITED
//         |
//         ↓
//     FULLY_WITHDRAWN
rule validatorStateTransitions(IEtherFiNode.VALIDATOR_PHASE oldPhase, IEtherFiNode.VALIDATOR_PHASE newPhase) {
    bool res;

    IEtherFiNode.VALIDATOR_PHASE phaseBefore = oldPhase;
        res = validatePhaseTransition(oldPhase, newPhase); // call phase instead.
    IEtherFiNode.VALIDATOR_PHASE phaseAfter = newPhase;

    assert phaseAfter == NOT_INITIALIZED() => phaseBefore == NOT_INITIALIZED() || phaseBefore == STAKE_DEPOSITED() || phaseBefore == WAITING_FOR_APPROVAL(), "NOT_INITIALIZED transtion violated";
    assert phaseAfter == STAKE_DEPOSITED() => phaseBefore == NOT_INITIALIZED(), "STAKE_DEPOSITED transtion violated";
    assert phaseAfter == LIVE() => phaseBefore == STAKE_DEPOSITED() || phaseBefore == WAITING_FOR_APPROVAL(), "LIVE transtion violated";
    assert phaseAfter == EXITED() => phaseBefore == LIVE() || phaseBefore == BEING_SLASHED(), "EXITED transtion violated";
    assert phaseAfter == FULLY_WITHDRAWN() => phaseBefore == EXITED(), "FULLY_WITHDRAWN transtion violated";
    assert phaseAfter == BEING_SLASHED() => phaseBefore == LIVE(), "BEING_SLASHED transtion violated";
    assert phaseAfter == WAITING_FOR_APPROVAL() => phaseBefore == STAKE_DEPOSITED(), "WAITING_FOR_APPROVAL transtion violated";
}

// version is always 1 (after initialization).
invariant versionIsOne()
    version() == 1;

invariant sumAllExitedLessThanAllAssociated()
    assert_uint256(numExitedValidators() + numExitRequestsByTnft()) <= numAssociatedValidators();

//TODO: if NOT_INITIALIZED how can be associated????
rule registerValidatorThenUnregisteringNeverReverts(uint256 validatorId, bool enableRestaking) {
    env e;
    IEtherFiNodesManager.ValidatorInfo info;
    require version() == 1; // required by the node manager.
    require associatedValidatorIdsLengthGhost < max_uint256; // causes overflows.
    requireInvariant associatedValidatorIdsLengthEqNumOfValidators();

    registerValidator(e, validatorId, enableRestaking);
    // set validator phase to IEtherFiNode.VALIDATOR_PHASE.STAKE_DEPOSITED - required by the node manager.
    require info.validatorIndex == 0; // requires by the node manager.

    require (info.phase == NOT_INITIALIZED() || info.phase == FULLY_WITHDRAWN()); // requires by the node manager.
    if (info.phase == FULLY_WITHDRAWN()) {
        require numExitedValidators() > 0; // FULLY_WITHDRAWN can be only if exited before.
    }
    require info.exitRequestTimestamp == 0; // seens to be a deprecated filed in the struct.

    bool succeed = unRegisterValidator@withrevert(e, validatorId, info);

    bool didRevert = lastReverted;

    assert !didRevert;
}

invariant associatedValidatorIdsLengthEqNumOfValidators() 
    associatedValidatorIdsLengthGhost == numAssociatedValidators()
    { 
        preserved {
            requireInvariant versionIsOne();
        } preserved unRegisterValidator(uint256 validatorId, IEtherFiNodesManager.ValidatorInfo info) with (env e) {
            if (info.phase == FULLY_WITHDRAWN() && numAssociatedValidators() > 0) {
                // TODO: is it even possible with the tool?
                updateNumberOfAssociatedValidators(e, 0, 1); // done by node manager at fullWithdraw. (calls processFullWithdraw).
                // associatedValidatorIdsLengthGhost = assert_uint256(associatedValidatorIdsLengthGhost - 1); // was never in this array if NOT_INITIALIZED.
            } else if (info.phase == NOT_INITIALIZED() && associatedValidatorIdsLengthGhost > 0) {
                updateNumberOfAssociatedValidators(e, 0, 1); // done by node manager at fullWithdraw. (calls processFullWithdraw).
            }
        } 
        preserved processFullWithdraw(uint256 validatorId) with (env e) {
            if (associatedValidatorIdsLengthGhost > 0) {
                associatedValidatorIdsLengthGhost = assert_uint256(associatedValidatorIdsLengthGhost - 1); // done by node manager at fullWithdraw. (calls unregister before)
            }
        }
    }

// numexited + num exited < numallassosiated

// pending Gwei correlation with assosiatedValidators
// invariant pendingGweiAssociatedValidatorsCorrelation()

// restakingObservedExitBlocks are less than current.block - only for corrcness (may cause false violations)

// for node manager:
// no same validatorId is present/assosiated in defferent etherFiNodes
// sumAllAssociatedValidatorIds equals _numAssociatedValidators - because it is update in the manager while sumAllAssociatedValidatorIds is tracked through the node itself
// sumAllAssociatedValidatorIds equals sum of validators in a suitable PHASE.
// _numAssociatedValidators equals sum of validators in a suitable PHASE.

