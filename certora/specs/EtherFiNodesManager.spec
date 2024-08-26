methods {
    function _.setValidatorPhase(uint256 _validatorId, uint8 _phase) external => ghostSetValidatorPhase(_validatorId, _phase) expect void;
    function _.phase(uint256 _validatorId) external => ghostGetValidatorPhase(_validatorId) expect uint8;
}

persistent ghost mapping(uint256 => uint8) validatorPhase {
    init_state axiom forall uint256 validatorId . validatorPhase[validatorId] == 0;
}

function ghostSetValidatorPhase(uint256 validatorId, uint8 phase) {
    validatorPhase[validatorId] = phase;
}

function ghostGetValidatorPhase(uint256 validatorId) returns uint8 {
    return validatorPhase[validatorId];
}

// enum VALIDATOR_PHASE {
//         NOT_INITIALIZED,0
//         STAKE_DEPOSITED,1
//         LIVE,2
//         EXITED,3
//         FULLY_WITHDRAWN,4
//         DEPRECATED_CANCELLED,5
//         BEING_SLASHED,6
//         DEPRECATED_EVICTED,7
//         WAITING_FOR_APPROVAL,8
//         DEPRECATED_READY_FOR_DEPOSIT,9
//     }

// definition NOT_INITIALIZED() returns uint8 = IEtherFiNode.VALIDATOR_PHASE.NOT_INITIALIZED;
// definition STAKE_DEPOSITED() returns uint8 = IEtherFiNode.VALIDATOR_PHASE.STAKE_DEPOSITED;
// definition NOT_INITIALIZED() returns uint8 = IEtherFiNode.VALIDATOR_PHASE.NOT_INITIALIZED;
// definition NOT_INITIALIZED() returns uint8 = IEtherFiNode.VALIDATOR_PHASE.NOT_INITIALIZED;
// definition NOT_INITIALIZED() returns uint8 = IEtherFiNode.VALIDATOR_PHASE.NOT_INITIALIZED;

// // Verify state diafram from documentation.
// // State Transition Diagram for StateMachine contract:
// //
// //      NOT_INITIALIZED <-
// //              |        |
// //              ↓        |
// //      STAKE_DEPOSITED --
// //           /    \      |
// //          ↓      ↓     |
// //         LIVE <- WAITING_FOR_APPROVAL
// //         |  \ 
// //         |   ↓  
// //         |  BEING_SLASHED
// //         |   /
// //         ↓  ↓
// //         EXITED
// //         |
// //         ↓
// //     FULLY_WITHDRAWN
// rule validatorStateTransitions(method f, uint256 validatorId) {
//     env e;
//     calldataarg args;
//     bool res;

//     uint8 phaseBefore = validatorPhase[validatorId];
//         res = f(e, args); // call phase instead.
//     uint8 phaseAfter = validatorPhase[validatorId];

//     assert phaseAfter == 0 => phaseBefore == 0 || phaseBefore == 1 || phaseBefore == 8, "NOT_INITIALIZED transtion violated";
//     assert phaseAfter == 1 => phaseBefore == 0, "STAKE_DEPOSITED transtion violated";
//     assert phaseAfter == 2 => phaseBefore == 1 || phaseBefore == 8, "LIVE transtion violated";
//     assert phaseAfter == 3 => phaseBefore == 2 || phaseBefore == 6, "EXITED transtion violated";
//     assert phaseAfter == 4 => phaseBefore == 3, "FULLY_WITHDRAWN transtion violated";
//     assert phaseAfter == 6 => phaseBefore == 2, "BEING_SLASHED transtion violated";
//     assert phaseAfter == 8 => phaseBefore == 1, "WAITING_FOR_APPROVAL transtion violated";
// }


// methods effecting only one Node
// dosnt fail when must succeed
// who changes the eth balance of the contract
// amount of tnft / bnft must eq the amount of validator in phase live or waiting for approval.
// no different node should share the same validator id.
