/* Re-entrance vulnerability spec
 * This spec, is adapted from:
 * `https://github.com/Certora/Examples/blob/master/CVLByExample/Reentrancy/certora/spec/NoGuardSafety.spec`
 * It is intended for contracts without re-entrance guard that need to be checked for
 * such vulnerabilities.
 *
 * The basic idea is that all storage access (load or store) should be done either
 * before any external call or after an external call. If there are functions with
 * access both before and after external call, they may be vulnerable.
 */

// ---- Ghosts -----------------------------------------------------------------

/// @title Ghost indicating if an external call occurred
persistent ghost bool called_extcall;

/// @title Ghost indicating storage was accessed before external call
persistent ghost bool storage_access_before_call;

/// @title Ghost indicating storage was accessed after external call
persistent ghost bool storage_access_after_call;

// ---- Hooks ------------------------------------------------------------------

// We are hooking here on "CALL" opcodes
hook CALL(
    uint g, address addr, uint value, uint argsOffset, uint argsLength,
    uint retOffset, uint retLength
) uint rc {
    called_extcall = true;  // Update the ghost
}

// For every store set storage_access_before_call or storage_access_after_call
// according to the call state
hook ALL_SSTORE(uint loc, uint v) {
    if (!called_extcall) {
       storage_access_before_call = true;
    } else {
        storage_access_after_call = true; 
    }
} 

// For every load set storage_access_before_call or storage_access_after_call
// according to the call state
hook ALL_SLOAD(uint loc) uint v {
    if (!called_extcall) {
       storage_access_before_call = true;
    } else {
        storage_access_after_call = true; 
    }
} 

// ---- Rules ------------------------------------------------------------------

/// @title All storage access should be done either before or after a call
rule reentrancySafety(method f) {
    // Set all ghost flags to false 
    require (
        !called_extcall &&
        !storage_access_before_call &&
        !storage_access_after_call
    );

    calldataarg args;
    env e;
    f(e,args);
    assert (
        !(storage_access_before_call && storage_access_after_call),
        "Reentrancy weakness exists"
    );
}
