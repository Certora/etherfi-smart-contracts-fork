/* Invariants for `EtherFiNode`
 * These show that the `associatedValidatorIds` array and `associatedValidatorIndices`
 * mapping are roughly inverse to each other.
 */
methods {
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
/// @notice Necessary since quantifiers do not support Solidity calls
definition indexFromId(uint256 _id) returns uint256 = (
    currentContract.associatedValidatorIndices[_id]
);

// ---- Invariants -------------------------------------------------------------

/// @title The values of validator indexes are less than the length of the array
invariant mappingLimits()
    forall uint256 _id. (indexFromId(_id) < lenIds() || indexFromId(_id) == 0)
    {
        preserved {
            require lenIds() <= 2^10;
            requireInvariant preserveMapping();
        }
    }


/// @title Mapping is left inverse to array
/// @notice Fails on the two filtered out methods below!
invariant preservingIndexes()
    forall uint256 i. i < lenIds() => indexFromId(idFromIndex(i)) == i
    filtered {
        // These two methods add Ids without checking they do not already exist in
        // the array.
        f -> f.selector != sig:registerValidator(uint256,bool).selector &&
        f.selector != sig:migrateVersion(uint256, IEtherFiNodesManager.ValidatorInfo).selector
    }
    {
        preserved {
            requireInvariant mappingLimits();
            requireInvariant preserveMapping();
        }
    }


/// @title Array is left inverse to mapping
invariant preserveMapping()
    forall uint256 _id. indexFromId(_id) > 0 => idFromIndex(indexFromId(_id)) == _id
    {
        preserved {
            requireInvariant mappingLimits();
            requireInvariant preservingIndexes();
        }
    }
