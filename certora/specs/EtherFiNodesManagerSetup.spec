import "./EtherFiNodeSetup.spec";
import "./nftDispach.spec";
import "./EtherFiNodeInterface.spec";

using EtherFiNodesManager as etherFiNodesManager;

methods {
    // Getters:
    function numberOfValidators() external returns (uint64) envfree; // # of validators in LIVE or WAITING_FOR_APPROVAL phases
    function nonExitPenaltyPrincipal() external returns (uint64) envfree;
    function nonExitPenaltyDailyRate() external returns (uint64) envfree;
    function SCALE() external returns (uint64) envfree;
    function treasuryContract() external returns (address) envfree;
    function stakingManagerContract() external returns (address) envfree;
    function auctionManager() external returns (address) envfree;
    function eigenPodManager() external returns (address) envfree;
    function etherfiNodeAddress(uint256) external returns (address) envfree; // validatorId == bidId -> withdrawalSafeAddress
    function unusedWithdrawalSafes(uint256) external returns (address) envfree;

    function _.instantiateEtherFiNode(bool) external => createNewNodeAddress() expect (address);

    // delegationManager summaries:
    function _.delegationManager() external => NONDET;
    function _.beaconChainETHStrategy() external => NONDET;
    function _.queueWithdrawals(IDelegationManager.QueuedWithdrawalParams[]) external => NONDET;
    function _.completeQueuedWithdrawals(IDelegationManager.Withdrawal[],address[][],uint256[],bool[]) external => NONDET; // external call only.

    // Auction manager summaries:
    function _.getBidOwner(uint256) external => NONDET;

    // Deprecated and penalty functions:
    function _.DEPRECATED_delayedWithdrawalRouter() external => NONDET;
    function _.nonExitPenaltyPrincipal() external => NONDET;
    function _.nonExitPenaltyDailyRate() external => NONDET;

    function _.getClaimableUserDelayedWithdrawals(address) external => NONDET;
}

// Functions filtered out since they forwarding external calls.
definition isFilteredFunc(method f) returns bool = (
    f.selector == sig:forwardEigenpodCall(uint256[],bytes[]).selector ||
    f.selector == sig:forwardExternalCall(uint256[],bytes[],address).selector ||
    f.selector == sig:upgradeToAndCall(address, bytes).selector
);

function nodeNotInArray(address EtherFiNode) returns bool {
    return forall uint256 indx . indx < unusedWithdrawalSafesLengthGhost => 
                                       unusedWithdrawalSafesMirror[indx] != EtherFiNode;
}

function nodeNotInAddresses(address EtherFiNode) returns bool {
    return forall uint256 validatorId . etherfiNodeAddressMirror[validatorId] != EtherFiNode;
}

// creates new node address.
function createNewNodeAddress() returns address {
    address newAddress;
    require nodeNotInArray(newAddress);
    require nodeNotInAddresses(newAddress);
    require newAddress != 0;
    return newAddress;
}

ghost mapping(uint256 => address) etherfiNodeAddressMirror {
    init_state axiom forall uint256 validatorId . etherfiNodeAddressMirror[validatorId] == 0;
}

ghost uint256 unusedWithdrawalSafesLengthGhost {
    init_state axiom unusedWithdrawalSafesLengthGhost == 0;
}

ghost mapping(uint256 => address) unusedWithdrawalSafesMirror {
    init_state axiom forall uint256 index . unusedWithdrawalSafesMirror[index] == 0;
}

ghost mapping(address => mathint) associatedValidatorsPerNode {
    init_state axiom forall address node . associatedValidatorsPerNode[node] == 0;
}

hook Sstore etherFiNodesManager.unusedWithdrawalSafes[INDEX uint256 indx] address newSafe (address oldSafe) {
    require oldSafe == unusedWithdrawalSafesMirror[indx];
    unusedWithdrawalSafesMirror[indx] = newSafe;
}

hook Sload address safe etherFiNodesManager.unusedWithdrawalSafes[INDEX uint256 indx] {
    require safe == unusedWithdrawalSafesMirror[indx];
}

hook Sstore etherFiNodesManager.etherfiNodeAddress[KEY uint256 validatorId] address newNode (address oldNode) {
    require oldNode == etherfiNodeAddressMirror[validatorId];
    if (oldNode == 0 && newNode != 0) {
        associatedValidatorsPerNode[newNode] = associatedValidatorsPerNode[newNode] + 1;
    } else if (oldNode != 0 && newNode == 0) {
        associatedValidatorsPerNode[oldNode] = associatedValidatorsPerNode[oldNode] - 1;
    }
    etherfiNodeAddressMirror[validatorId] = newNode;
}

hook Sload address node etherFiNodesManager.etherfiNodeAddress[KEY uint256 validatorId] {
    require node == etherfiNodeAddressMirror[validatorId];
}

// hook unusedWithdrawalSafes length
hook Sstore etherFiNodesManager.unusedWithdrawalSafes.(offset 0) uint256 newlength (uint256 oldlength) {
    require oldlength == unusedWithdrawalSafesLengthGhost;
    unusedWithdrawalSafesLengthGhost = newlength;
    // POP():
    if (oldlength - newlength == 1) {
        unusedWithdrawalSafesMirror[newlength] = 0;
    }
}

hook Sload uint256 length etherFiNodesManager.unusedWithdrawalSafes.(offset 0) {
    require length == unusedWithdrawalSafesLengthGhost;
}

/// @title Verifies that mirroring unusedWithdrawalSafesMirror is done correctly.
invariant ArrayMirrorIntegrity()
    forall uint256 indx.
        (indx < unusedWithdrawalSafesLengthGhost => unusedWithdrawalSafesMirror[indx] != 0) &&
        (indx >= unusedWithdrawalSafesLengthGhost && indx < max_uint256 => unusedWithdrawalSafesMirror[indx] == 0)
        filtered {f -> !isFilteredFunc(f)}
        {
            preserved {
                require unusedWithdrawalSafesLengthGhost < max_uint256 - 3; // -3 for every possible loop iteration.
            }
        }

/// @title Verifies that the amout of linked validators to a node by the manager equals the actual amount of associated validators by the node itseld.
invariant amountOfValidatorPerEtherFiNodeEqualsNumAssociatedValidators()
    associatedValidatorIdsLengthGhost == associatedValidatorsPerNode[etherFiNode]
    filtered {f -> !isFilteredFunc(f)}
    {
        preserved {
            require etherFiNode.version() == 1;
        }
    }

ghost mathint minimalLength;
ghost bool atLeastOnAssociated;

function noValidatorForUnusedNodesRequirements(uint256 validatorId) {
    requireInvariant ArrayMirrorIntegrity();
    // push node to unused safes only if it is the last associated validator:
    requireInvariant amountOfValidatorPerEtherFiNodeEqualsNumAssociatedValidators();
    // require etherFiNode.version() == 1;
    requireInvariant versionIsOneOnlyIfAssociated();
    requireInvariant validatorIdNeverZero();
    requireInvariant noValidatorForUnusedNodes(validatorId);
    require unusedWithdrawalSafesLengthGhost < max_uint256 - 3; // -3 for every possible loop iteration.
}

/// @title Verifies that if there is a node in unused nodes array than there is no validator that is linked to it.
invariant noValidatorForUnusedNodes(uint256 validatorId)
    forall uint256 indx . indx < unusedWithdrawalSafesLengthGhost && validatorId != 0 => 
                                       unusedWithdrawalSafesMirror[indx] != etherfiNodeAddressMirror[validatorId]
    filtered {f -> !isFilteredFunc(f)}
    {
        preserved {
            requireInvariant ArrayMirrorIntegrity();
        }
        preserved registerValidator(uint256 _validatorId, bool _enableRestaking, address _withdrawalSafeAddress) with (env e) {
            // staking manager call allocate etherfi node before this call. which means it is safe to assume _withdrawalSafeAddress is not in unusedSafes.
            require nodeNotInArray(_withdrawalSafeAddress);
            requireInvariant ArrayMirrorIntegrity();
        }
        preserved unregisterValidator(uint256 _validatorId) with (env e) {
            noValidatorForUnusedNodesRequirements(_validatorId);
            require (etherfiNodeAddress(_validatorId) == etherfiNodeAddress(validatorId)) => associatedValidatorIdsLengthGhost >= 2;
        }
        preserved fullWithdraw(uint256 _validatorId) with (env e) {
            noValidatorForUnusedNodesRequirements(_validatorId);
            require (etherfiNodeAddress(_validatorId) == etherfiNodeAddress(validatorId)) => associatedValidatorIdsLengthGhost >= 2;
        } 
        preserved batchFullWithdraw(uint256[] _validatorIds) with (env e) {
            noValidatorForUnusedNodesRequirements(_validatorIds[0]);
            requireInvariant noValidatorForUnusedNodes(_validatorIds[1]);
            requireInvariant noValidatorForUnusedNodes(_validatorIds[2]);
            minimalLength = 0;
            atLeastOnAssociated = false; // Using this for not excluding zero length case.
            if (etherfiNodeAddress(_validatorIds[0]) == etherfiNodeAddress(validatorId)) { minimalLength = minimalLength + 1; atLeastOnAssociated = true;}
            if (etherfiNodeAddress(_validatorIds[1]) == etherfiNodeAddress(validatorId)) { minimalLength = minimalLength + 1; atLeastOnAssociated = true;}
            if (etherfiNodeAddress(_validatorIds[2]) == etherfiNodeAddress(validatorId)) { minimalLength = minimalLength + 1; atLeastOnAssociated = true;}
            if (etherfiNodeAddress(_validatorIds[0]) == etherfiNodeAddress(_validatorIds[1])) { minimalLength = minimalLength + 1; atLeastOnAssociated = true;}
            if (etherfiNodeAddress(_validatorIds[0]) == etherfiNodeAddress(_validatorIds[2])) { minimalLength = minimalLength + 1; atLeastOnAssociated = true;}
            if (etherfiNodeAddress(_validatorIds[1]) == etherfiNodeAddress(_validatorIds[2])) { minimalLength = minimalLength + 1; atLeastOnAssociated = true;}
            if (atLeastOnAssociated) { minimalLength = minimalLength + 1;}
            require associatedValidatorIdsLengthGhost >= minimalLength;
        }
    }

invariant unusedWithdrawalSafesUniqueness(uint256 indx1, uint256 indx2)
    indx1 != indx2 && indx1 < unusedWithdrawalSafesLengthGhost && indx2 < unusedWithdrawalSafesLengthGhost =>
        unusedWithdrawalSafesMirror[indx1] != unusedWithdrawalSafesMirror[indx2]
    filtered {f -> !isFilteredFunc(f)}
    {
        preserved {
            require unusedWithdrawalSafesLengthGhost < max_uint256 - 3; // -3 for every possible loop iteration.
        }
        preserved unregisterValidator(uint256 _validatorId) with (env e) {
            require _validatorId != 0;
            requireInvariant noValidatorForUnusedNodes(_validatorId);
        }
        preserved fullWithdraw(uint256 _validatorId) with (env e) {
            require _validatorId != 0;
            requireInvariant noValidatorForUnusedNodes(_validatorId);
        } 
        preserved batchFullWithdraw(uint256[] _validatorIds) with (env e) {
            require _validatorIds[0] != 0;
            require _validatorIds[1] != 0;
            require _validatorIds[2] != 0;
            requireInvariant noValidatorForUnusedNodes(_validatorIds[0]);
            requireInvariant noValidatorForUnusedNodes(_validatorIds[1]);
            requireInvariant noValidatorForUnusedNodes(_validatorIds[2]);
        }
    }

/// @title Verifies that if there are associated validators to a node then its version is one.
invariant versionIsOneOnlyIfAssociated()
    associatedValidatorsPerNode[etherFiNode] > 0 => etherFiNode.version == 1
    filtered {f -> !isFilteredFunc(f)}
 