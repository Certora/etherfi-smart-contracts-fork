/* Invariants and parametric rules examples */
methods {
    function getUserTotalKeys(address) external returns (uint64) envfree;
    function registered(address) external returns (bool) envfree;
    function owner() external returns (address) envfree;
}

// ---- Definitions ------------------------------------------------------------

/// @title A convinient definition - a definition is a macro
definition keysUsed(address _user) returns uint64 = (
    currentContract.addressToOperatorData[_user].keysUsed
);

// ---- Invariants -------------------------------------------------------------

/// @title A user with non-zero total keys must be registered
invariant nonZeroTotalKeysIsRegistered(address _user)
    getUserTotalKeys(_user) > 0 => registered(_user)
    filtered {
            f -> f.selector != sig:upgradeToAndCall(address,bytes).selector
    }


/// @title Unregistered operator has no used keys - without preserved block
invariant unregisterdKeysUnused_NoPreserved(address _user)
    !registered(_user) => keysUsed(_user) == 0
    filtered {
            f -> f.selector != sig:upgradeToAndCall(address,bytes).selector
    }


/// @title Unregistered operator has no used keys - using generic preserved block
invariant unregisterdKeysUnused(address _user)
    !registered(_user) => keysUsed(_user) == 0
    filtered {
            f -> f.selector != sig:upgradeToAndCall(address,bytes).selector
    }
    {
        preserved {
            requireInvariant nonZeroTotalKeysIsRegistered(_user);
        }
    }


/// @title Unregistered operator has no used keys - using method specific preserved block
invariant unregisterdKeysUnused_MethodSpecific(address _user)
    !registered(_user) => keysUsed(_user) == 0
    filtered {
            f -> f.selector != sig:upgradeToAndCall(address,bytes).selector
    }
    {
        preserved fetchNextKeyIndex(address user2) with (env e) {
            requireInvariant nonZeroTotalKeysIsRegistered(user2);
        }
    }

// ---- Parametric rules -------------------------------------------------------

/// @title Total keys can be changed only in very specific ways
rule totalKeysAllowedChanges(address _user, method f) filtered {
    f -> f.selector != sig:upgradeToAndCall(address,bytes).selector
} {
    uint64 totalPre = getUserTotalKeys(_user);

    env e;
    calldataarg args;
    f(e, args);

    uint64 totalPost = getUserTotalKeys(_user);
    assert (
        totalPre != totalPost => (
            f.selector == sig:registerNodeOperator(bytes, uint64).selector &&
            e.msg.sender == _user
        ) || (
            f.selector == sig:initializeOnUpgrade(
                address[], bytes[], uint64[], uint64[]
            ).selector &&
            e.msg.sender == owner()
        ),
        "total keys allowed changes"
    );
}


/// @title Number of used keys cannot decrease
rule usedKeysNonDecreasing(address _user, method f) filtered {
    f -> f.selector != sig:upgradeToAndCall(address,bytes).selector
} {
    // Without this requirement we'll get a violation from `registerNodeOperator`
    requireInvariant unregisterdKeysUnused(_user);

    uint64 preNumUsed = keysUsed(_user);

    env e;
    calldataarg args;
    f(e, args);

    uint64 postNumUsed = keysUsed(_user);
    assert (
        f.selector != sig:initializeOnUpgrade(address[], bytes[], uint64[], uint64[]).selector
        => postNumUsed >= preNumUsed,
        "num keys used is non-decreasing"
    );
}


/// @title Invariant nonZeroTotalKeysIsRegistered as a rule
/// @notice Does not check the constructor!
rule nonZeroTotalKeysIsRegistered_Parametric(address _user, method f) filtered {
    f -> f.selector != sig:upgradeToAndCall(address,bytes).selector
} {
    require getUserTotalKeys(_user) > 0 => registered(_user);  // Pre-condition
    
    env e;
    calldataarg args;
    f(e, args);

    assert getUserTotalKeys(_user) > 0 => registered(_user);  // Post-condition
}


/// @title A parametric rule that is verified but will never occur
/// @notice We require a state that is not reachable.
rule wrongParametric(address _user, method f) filtered {
    f -> f.selector != sig:upgradeToAndCall(address,bytes).selector
} {
    uint64 totalPre = getUserTotalKeys(_user);
    require totalPre > 0 && !registered(_user) => keysUsed(_user) > totalPre;
    
    env e;
    calldataarg args;
    f(e, args);

    uint64 totalPost = getUserTotalKeys(_user);
    assert totalPost > 0 && !registered(_user) => keysUsed(_user) > totalPost;
}
