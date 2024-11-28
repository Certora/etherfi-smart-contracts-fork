using EtherFiNode as etherFiNode;

methods {
    // Getters:
    function etherFiNode.version() external returns (uint16) envfree;
    function etherFiNode._numAssociatedValidators() internal returns (uint16);
    function etherFiNode.associatedValidatorIndices(uint256) external returns (uint256) envfree;
    function etherFiNode.numExitedValidators() external returns (uint16) envfree;
    function etherFiNode.numExitRequestsByTnft() external returns (uint16) envfree;
    function etherFiNode.associatedValidatorIds(uint256) external returns (uint256) envfree;
    // Track the amount of pending/completed withdrawals;
    function etherFiNode.pendingWithdrawalFromRestakingInGwei() external returns (uint64) envfree;
    function etherFiNode.completedWithdrawalFromRestakingInGwei() external returns (uint64) envfree;
    function etherFiNode.updateNumberOfAssociatedValidators(uint16, uint16) external;

    function etherFiNode.numAssociatedValidators() external returns (uint256) envfree;
    function etherFiNode.registerValidator(uint256, bool) external;
    function etherFiNode.validatePhaseTransition(IEtherFiNode.VALIDATOR_PHASE, IEtherFiNode.VALIDATOR_PHASE) external returns (bool) envfree;

    // IEigenPodManager summaries:
    function _.eigenPodManager() external => NONDET;
    function _.getPod(address) external => NONDET;
    function _.createPod() external => NONDET;

    // IEigenPod summaries:
    function _.withdrawableRestakedExecutionLayerGwei() external => NONDET;
}

definition NOT_INITIALIZED() returns IEtherFiNode.VALIDATOR_PHASE = IEtherFiNode.VALIDATOR_PHASE.NOT_INITIALIZED;
definition STAKE_DEPOSITED() returns IEtherFiNode.VALIDATOR_PHASE = IEtherFiNode.VALIDATOR_PHASE.STAKE_DEPOSITED;
definition LIVE() returns IEtherFiNode.VALIDATOR_PHASE = IEtherFiNode.VALIDATOR_PHASE.LIVE;
definition EXITED() returns IEtherFiNode.VALIDATOR_PHASE = IEtherFiNode.VALIDATOR_PHASE.EXITED;
definition FULLY_WITHDRAWN() returns IEtherFiNode.VALIDATOR_PHASE = IEtherFiNode.VALIDATOR_PHASE.FULLY_WITHDRAWN;
definition BEING_SLASHED() returns IEtherFiNode.VALIDATOR_PHASE = IEtherFiNode.VALIDATOR_PHASE.BEING_SLASHED;
definition WAITING_FOR_APPROVAL() returns IEtherFiNode.VALIDATOR_PHASE = IEtherFiNode.VALIDATOR_PHASE.WAITING_FOR_APPROVAL;

persistent ghost uint256 associatedValidatorIdsLengthGhost {
    init_state axiom associatedValidatorIdsLengthGhost == 0;
    axiom associatedValidatorIdsLengthGhost < max_uint128;
}

ghost uint256 biggestValidatorIndex {
    init_state axiom biggestValidatorIndex == 0;
}

persistent ghost mapping(uint256 => uint256) associatedValidatorIndicesGhost {
    init_state axiom forall uint256 validator . associatedValidatorIndicesGhost[validator] == 0;
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

hook Sstore etherFiNode.restakingObservedExitBlocks[KEY uint256 validatorId] uint32 newblock (uint32 oldBlock) {
    if (newblock > latestBlockGhost) {
        latestBlockGhost = newblock;
    }
    restakingObservedExitBlocksGhost[validatorId] = newblock;
}

hook Sload uint32 blockNumber etherFiNode.restakingObservedExitBlocks[KEY uint256 validatorId] {
    require blockNumber == restakingObservedExitBlocksGhost[validatorId];
}

hook Sstore etherFiNode.associatedValidatorIds.(offset 0) uint256 newlength (uint256 oldlength) {
    require oldlength == associatedValidatorIdsLengthGhost;
    associatedValidatorIdsLengthGhost = newlength;
}

hook Sload uint256 length etherFiNode.associatedValidatorIds.(offset 0) {
    require length == associatedValidatorIdsLengthGhost;
}

hook Sstore etherFiNode.associatedValidatorIndices[KEY uint256 validator] uint256 newIndecies (uint256 oldIndecies) {
    require oldIndecies == associatedValidatorIndicesGhost[validator];
    if (newIndecies > biggestValidatorIndex) { biggestValidatorIndex = newIndecies; }
    associatedValidatorIndicesGhost[validator] = newIndecies;
}

hook Sload uint256 indecies etherFiNode.associatedValidatorIndices[KEY uint256 validator] {
    require indecies == associatedValidatorIndicesGhost[validator];
}

hook Sstore etherFiNode.associatedValidatorIds[INDEX uint256 index] uint256 newValidator (uint256 oldValidator) {
    require oldValidator == associatedValidatorIdsGhost[index];
    if (newValidator == 0 && oldValidator != 0) { // removing a validator
        sumAllAssociatedValidatorIds = sumAllAssociatedValidatorIds - 1;
    } else if (newValidator != 0 && oldValidator == 0) { // adding new validator
        sumAllAssociatedValidatorIds = sumAllAssociatedValidatorIds + 1;
    }
    associatedValidatorIdsGhost[index] = newValidator;
}

hook Sload uint256 validator etherFiNode.associatedValidatorIds[INDEX uint256 index] {
    require validator == associatedValidatorIdsGhost[index];
}

function validatorNotInArray(uint256 validatorId) returns bool {
    return forall uint256 indx . indx < associatedValidatorIdsLengthGhost => 
                                       associatedValidatorIdsGhost[indx] != validatorId;
}

/// @title Verifies that any associated validator ID can never be zero.
invariant validatorIdNeverZero() 
    forall uint256 index . index < associatedValidatorIdsLengthGhost => associatedValidatorIdsGhost[index] != 0
    {
        preserved etherFiNode.registerValidator(uint256 validatorId, bool redtskingEnabled) with (env e) {
            // validatorId starts from 1.
            require validatorId != 0;
        }
    }

// for use in future rules - requires that the current block number is valid.
invariant blockNumberValidity(uint32 blockNumber)
    blockNumber >= latestBlockGhost
    { 
        preserved with (env e) {
            require e.block.number == blockNumber;
        }
    }

/// @title Verifies that the associated validator IDs are unique.
invariant validatorIdsAreUnique()
    forall uint256 index1 . forall uint256 index2 . 
        (index1 != index2 && index1 < associatedValidatorIdsLengthGhost && index2 < associatedValidatorIdsLengthGhost) => 
            associatedValidatorIdsGhost[index1] != associatedValidatorIdsGhost[index2]
    {
        preserved with (env e) {
            requireInvariant validatorIdNeverZero();
            // proven in versionIsOneOnlyIfAssociated() invariant.
            require associatedValidatorIdsLengthGhost > 0 => etherFiNode.version == 1;
        }
        preserved etherFiNode.registerValidator(uint256 validatorId, bool redtskingEnabled) with (env e) {
            // validatorId starts from 1.
            require validatorId != 0;
            // EtherFiNodeManager requires that the validator is not already installed in this node -
            // the invariant amountOfValidatorPerEtherFiNodeEqualsNumAssociatedValidators() combined with this followinh code ensures that it is safe: 
            // (etherfiNodeAddress[_validatorId] != address(0)) revert AlreadyInstalled(); 
            require validatorNotInArray(validatorId);
        } 
    }
    