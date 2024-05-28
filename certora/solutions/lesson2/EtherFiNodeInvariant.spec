// Solution to Lesson 2
methods {
    // We can define the getter as `envfree`, but instead we'll use direct storage access
    // function associatedValidatorIndices(uint256) external returns (uint256) envfree;

    // `IEigenPodManager`
    // NOTE: The `EigenPodManagerMock.createPod` function is empty so we use a `NONDET`
    // summary. (`EigenPodManagerMock` is from `test/eigenlayer-mocks/EigenPodManagerMock.sol`).
    // NOTE: Not using specific summary: `function IEigenPodManager.createPod() external =>`
    // since we'll need an implementation for it.
    // TODO: This summary is UNSOUND!
    function _.createPod() external => NONDET;
}

// ---- Definitions ------------------------------------------------------------

/// @title The length of the `associatedValidatorIds` array
definition lenIds() returns uint256 = currentContract.associatedValidatorIds.length;

/// @title The validator id at the given index
definition idFromIndex(uint256 i) returns uint256 = currentContract.associatedValidatorIds[i];

/// @title Direct access to `associatedValidatorIndices` mapping
definition indexFromId(uint256 _id) returns uint256 = (
    currentContract.associatedValidatorIndices[_id]
);

// ---- Invariants -------------------------------------------------------------

/// @title The values of validator indexes are less than the length of the array
invariant mappingLimits(uint256 _id)
    (
        (lenIds() > 0 => indexFromId(_id) < lenIds()) &&
        (lenIds() == 0 => indexFromId(_id) == 0)
    )
    {
        preserved {
            require lenIds() <= 2^10;
        }
        preserved unRegisterValidator(
            uint256 _validatorId,
            IEtherFiNodesManager.ValidatorInfo _info
        ) with (env e) {
            require lenIds() <= 2^10;
            requireInvariant mappingLimits(_validatorId);
            requireInvariant preserveMapping(_validatorId);
            requireInvariant preserveMapping(_id);
        }
    }


/// @title Mapping is left inverse to array
invariant preservingIndexes(uint256 i)
    i < lenIds() => indexFromId(idFromIndex(i)) == i
    {
        preserved {
            requireInvariant mappingLimits(idFromIndex(i));
            requireInvariant preserveMapping(idFromIndex(i));
        }
        preserved unRegisterValidator(
            uint256 _validatorId,
            IEtherFiNodesManager.ValidatorInfo _info
        ) with (env e) {
            requireInvariant mappingLimits(idFromIndex(i));
            requireInvariant preserveMapping(idFromIndex(i));
            // Apply invariants also to `_validatorId`
            requireInvariant preservingIndexes(indexFromId(_validatorId));
            requireInvariant mappingLimits(_validatorId);
            requireInvariant preserveMapping(_validatorId);

            if (lenIds() > 1) {
                uint256 lastIndex = assert_uint256(lenIds() - 1);
                uint256 last = idFromIndex(lastIndex);
                requireInvariant preservingIndexes(lastIndex);
                requireInvariant mappingLimits(last);
                requireInvariant preserveMapping(last);
            }
        }
        preserved migrateVersion(
            uint256 _validatorId,
            IEtherFiNodesManager.ValidatorInfo _info
        ) with (env e1) {
            requireInvariant mappingLimits(idFromIndex(i));
            requireInvariant preserveMapping(idFromIndex(i));
            // Apply invariants also to `_validatorId`
            requireInvariant preservingIndexes(indexFromId(_validatorId));
            requireInvariant mappingLimits(_validatorId);
            requireInvariant preserveMapping(_validatorId);
        }
    }


/// @title Array is left inverse to mapping
invariant preserveMapping(uint256 _id)
    indexFromId(_id) > 0 => idFromIndex(indexFromId(_id)) == _id
    {
        preserved {
            requireInvariant preservingIndexes(indexFromId(_id));
            requireInvariant mappingLimits(_id);
        }
        preserved unRegisterValidator(
            uint256 _validatorId,
            IEtherFiNodesManager.ValidatorInfo _info
        ) with (env e) {
            requireInvariant preservingIndexes(indexFromId(_id));
            requireInvariant mappingLimits(_id);
            // Apply invariants also to `_validatorId`
            requireInvariant preservingIndexes(indexFromId(_validatorId));
            requireInvariant mappingLimits(_validatorId);
            requireInvariant preserveMapping(_validatorId);
        }
    }
