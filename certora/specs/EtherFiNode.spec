import "./EtherFiNodeSetup.spec";

use invariant validatorIdsAreUnique;
use invariant validatorIdNeverZero;

/// @title whenever the pending withdrawal amount is decreased (completed) the number of completed withdrawals increases.
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

/// @title Verify validator state transition diagram from documentation.
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

/// @title registering a validator and then unregistering it should never revert.
rule registerValidatorThenUnregisteringNeverReverts(uint256 validatorId, bool enableRestaking) {
    env e;
    IEtherFiNodesManager.ValidatorInfo info;
    require version() == 1; // required by the node manager.
    require associatedValidatorIdsLengthGhost < max_uint256; // causes overflows.
    requireInvariant associatedValidatorIdsLengthEqNumOfValidators();

    registerValidator(e, validatorId, enableRestaking);
    // set validator phase to IEtherFiNode.VALIDATOR_PHASE.STAKE_DEPOSITED - required by the node manager.
    require info.validatorIndex == 0;

    require (info.phase == NOT_INITIALIZED() || info.phase == FULLY_WITHDRAWN()); // requires by the node manager.
    if (info.phase == FULLY_WITHDRAWN()) {
        require numExitedValidators() > 0; // FULLY_WITHDRAWN can be only if exited before.
    }
    require info.exitRequestTimestamp == 0; // seems to be a deprecated filed in the struct.

    bool succeed = unRegisterValidator@withrevert(e, validatorId, info);

    bool didRevert = lastReverted;

    assert !didRevert;
}

// This invariant is artificially true for the sake of registerValidatorThenUnregisteringNeverReverts.
// it is not accurate because associatedValidatorIdsLengthGhost counts validators in STAKE_DEPOSITED, WAITING_FOR_APPROVAL phases as well.
invariant associatedValidatorIdsLengthEqNumOfValidators() 
    associatedValidatorIdsLengthGhost == numAssociatedValidators()
    filtered { f -> f.selector != sig:updateNumberOfAssociatedValidators(uint16,uint16).selector }
    { 
        preserved {
            require version() == 1;
        } preserved unRegisterValidator(uint256 validatorId, IEtherFiNodesManager.ValidatorInfo info) with (env e) {
            if (info.phase == FULLY_WITHDRAWN() && numAssociatedValidators() > 0) {
                updateNumberOfAssociatedValidators(e, 0, 1); // done by node manager at fullWithdraw. (calls processFullWithdraw).
            } else if (info.phase == NOT_INITIALIZED() && associatedValidatorIdsLengthGhost > 0) {
                // phase is NOT_INITIALIZED so shouldn't be in numAssociatedValidators.
                updateNumberOfAssociatedValidators(e, 0, 1); // done by node manager at fullWithdraw. (calls processFullWithdraw).
            }
        } 
        preserved processFullWithdraw(uint256 validatorId) with (env e) {
            if (associatedValidatorIdsLengthGhost > 0) {
                associatedValidatorIdsLengthGhost = assert_uint256(associatedValidatorIdsLengthGhost - 1); // done by node manager at fullWithdraw. (calls unregister before)
            }
        }
        preserved registerValidator(uint256 validatorId, bool restakingEnabled) with (env e) {
            // phase is STAKE_DEPOSITED so shouldn't be in numAssociatedValidators.
            updateNumberOfAssociatedValidators(e, 1, 0); // should fail for register validator. this is a patch.
        }
    }
