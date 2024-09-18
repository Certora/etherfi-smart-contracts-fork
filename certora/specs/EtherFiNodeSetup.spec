methods {
    // Getters:
    function eigenPod() external returns (address) envfree;
    function isRestakingEnabled() external returns (bool) envfree;
    function version() external returns (uint16) envfree;
    function _numAssociatedValidators() internal returns (uint16);
    function associatedValidatorIndices(uint256) external returns (uint256) envfree;
    function numExitedValidators() external returns (uint16) envfree;
    function numExitRequestsByTnft() external returns (uint16) envfree;
    function associatedValidatorIds(uint256) external returns (uint256) envfree;
    // Track the amount of pending/completed withdrawals;
    function pendingWithdrawalFromRestakingInGwei() external returns (uint64) envfree;
    function completedWithdrawalFromRestakingInGwei() external returns (uint64) envfree;
    function updateNumberOfAssociatedValidators(uint16, uint16) external;

    function numAssociatedValidators() external returns (uint256) envfree;
    function registerValidator(uint256, bool) external;
    function validatePhaseTransition(IEtherFiNode.VALIDATOR_PHASE, IEtherFiNode.VALIDATOR_PHASE) external returns (bool) envfree;

    // IEigenPodManager summaries:
    function _.eigenPodManager() external => NONDET;
    function _.getPod(address) external => NONDET;
    function _.createPod() external => NONDET;

    // munge:
    function getAssociatedValidatorIdsLength() external returns (uint256) envfree;

}

definition NOT_INITIALIZED() returns IEtherFiNode.VALIDATOR_PHASE = IEtherFiNode.VALIDATOR_PHASE.NOT_INITIALIZED;
definition STAKE_DEPOSITED() returns IEtherFiNode.VALIDATOR_PHASE = IEtherFiNode.VALIDATOR_PHASE.STAKE_DEPOSITED;
definition LIVE() returns IEtherFiNode.VALIDATOR_PHASE = IEtherFiNode.VALIDATOR_PHASE.LIVE;
definition EXITED() returns IEtherFiNode.VALIDATOR_PHASE = IEtherFiNode.VALIDATOR_PHASE.EXITED;
definition FULLY_WITHDRAWN() returns IEtherFiNode.VALIDATOR_PHASE = IEtherFiNode.VALIDATOR_PHASE.FULLY_WITHDRAWN;
definition BEING_SLASHED() returns IEtherFiNode.VALIDATOR_PHASE = IEtherFiNode.VALIDATOR_PHASE.BEING_SLASHED;
definition WAITING_FOR_APPROVAL() returns IEtherFiNode.VALIDATOR_PHASE = IEtherFiNode.VALIDATOR_PHASE.WAITING_FOR_APPROVAL;

// CALL FORWARDING filtered:
definition callForwarding(method f) returns bool =
    f.selector == sig:callEigenPod(bytes).selector ||
    f.selector == sig:forwardCall(address, bytes).selector;

persistent ghost uint256 associatedValidatorIdsLengthGhost {
    init_state axiom associatedValidatorIdsLengthGhost == 0;
}

persistent ghost mapping(uint256 => uint256) associatedValidatorIndicesGhost {
    init_state axiom forall uint256 validator . associatedValidatorIndicesGhost[validator] == 0;
}

persistent ghost mathint sumAllAssociatedValidatorIndicesGhost {
    init_state axiom sumAllAssociatedValidatorIndicesGhost == 0;
    axiom sumAllAssociatedValidatorIndicesGhost >= 0;
}

persistent ghost mapping(uint256 => uint256) associatedValidatorIdsGhost {
    init_state axiom forall uint256 index . associatedValidatorIdsGhost[index] == 0;
}

persistent ghost mathint sumAllAssociatedValidatorIds {
    init_state axiom sumAllAssociatedValidatorIds == 0;
    axiom sumAllAssociatedValidatorIds >= 0;
}
persistent ghost uint32 latestBlockGhost {
    init_state axiom latestBlockGhost == 0;
}

persistent ghost mapping(uint256 => uint32) restakingObservedExitBlocksGhost {
    init_state axiom forall uint256 validatorId . restakingObservedExitBlocksGhost[validatorId] == 0;
}

hook Sstore restakingObservedExitBlocks[KEY uint256 validatorId] uint32 newblock (uint32 oldBlock) {
    if (newblock > latestBlockGhost) {
        latestBlockGhost = newblock;
    }
    restakingObservedExitBlocksGhost[validatorId] = newblock;
}

hook Sload uint32 blockNumber restakingObservedExitBlocks[KEY uint256 validatorId] {
    require blockNumber == restakingObservedExitBlocksGhost[validatorId];
}

hook Sstore associatedValidatorIds.(offset 0) uint256 newlength (uint256 oldlength) {
    require oldlength == associatedValidatorIdsLengthGhost;
    associatedValidatorIdsLengthGhost = newlength;
}

hook Sload uint256 length associatedValidatorIds.(offset 0) {
    require length == associatedValidatorIdsLengthGhost;
}

hook Sstore associatedValidatorIndices[KEY uint256 validator] uint256 newIndecies (uint256 oldIndecies) {
    associatedValidatorIndicesGhost[validator] = newIndecies;
    sumAllAssociatedValidatorIndicesGhost = sumAllAssociatedValidatorIndicesGhost + newIndecies - oldIndecies;
}

hook Sload uint256 indecies associatedValidatorIndices[KEY uint256 validator] {
    require indecies == associatedValidatorIndicesGhost[validator];
}

hook Sstore associatedValidatorIds[INDEX uint256 index] uint256 newValidator (uint256 oldValidator) {
    if (newValidator == 0 && oldValidator != 0) {
        sumAllAssociatedValidatorIds = sumAllAssociatedValidatorIds - 1;
    } else if (newValidator != 0 && oldValidator == 0) {
        sumAllAssociatedValidatorIds = sumAllAssociatedValidatorIds + 1;
    }
    associatedValidatorIdsGhost[index] = newValidator;
}

hook Sload uint256 validator associatedValidatorIds[INDEX uint256 index] {
    require validator == associatedValidatorIdsGhost[index];
}

invariant mirrorLength()
    associatedValidatorIdsLengthGhost == getAssociatedValidatorIdsLength();

invariant validatorIndeciesLessThanLength(uint256 validatorId, uint256 index)
    forall uint256 validator . associatedValidatorIndicesGhost[validator] <= associatedValidatorIdsLengthGhost;

invariant validatorPastLengthAreNullified()
    forall uint256 index . index > associatedValidatorIdsLengthGhost => associatedValidatorIdsGhost[index] == 0 
    {
        preserved registerValidator(uint256 validatorId, bool redtskingEnabled) with (env e) {
            require validatorId != 0;
        }
    }

// invariant mirrorIntegrity(uint256 index)
//     index < associatedValidatorIdsLengthGhost => 
//         associatedValidatorIndicesGhost[associatedValidatorIdsGhost[index]] == index &&
//         associatedValidatorIdsGhost[associatedValidatorIndicesGhost[validator]] == validator;

invariant validatorIndeciesValidaorIdMirror()
    forall uint256 validatorId . associatedValidatorIndicesGhost[validatorId] != 0 => 
            associatedValidatorIdsGhost[associatedValidatorIndicesGhost[validatorId]] == validatorId;

invariant validatorIdNeverZero() 
    forall uint256 index . index < associatedValidatorIdsLengthGhost => associatedValidatorIdsGhost[index] != 0
    {
        preserved registerValidator(uint256 validatorId, bool redtskingEnabled) with (env e) {
            // validatorId starts from 1.
            require validatorId != 0;
        }
    }

// invariant validatorIndeciesValidaorIdMirror()
//     forall uint256 validatorId . associatedValidatorIndices(validatorId) != 0 =>
//             associatedValidatorIds(associatedValidatorIndices(validatorId)) == validatorId;

// it is not proven and might be allowed by the system but it helps to prove properties on the EtherFiNode.
// invariant validatorIdsAreUnique(uint256 validatorId) if there are two different indexes then their validatorId is different (if indexes less than length)
//     (validatorId != 0 && associatedValidatorIndicesGhost[validatorId] == 0) => (forall uint256 index . associatedValidatorIdsGhost[index] != validatorId);

invariant blockNumberValidity(uint32 blockNumber)
    blockNumber >= latestBlockGhost
    { 
        preserved with (env e) {
            require e.block.number == blockNumber;
        }
    }

invariant validatorIdsAreUnique()
    forall uint256 index1 . forall uint256 index2 . 
        (index1 != index2 && index1 < associatedValidatorIdsLengthGhost && index2 < associatedValidatorIdsLengthGhost) => 
            associatedValidatorIdsGhost[index1] != associatedValidatorIdsGhost[index2]
    {
        preserved with (env e) {
            requireInvariant validatorIdNeverZero();
            requireInvariant validatorPastLengthAreNullified();
        }
    }


    // אם אינדקס קטן אז שונה מאפס ואם גדול אז שווה לאפס
