/* Exercise `forall` quantifier on `EtherFiNode` */
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
        }
    }
