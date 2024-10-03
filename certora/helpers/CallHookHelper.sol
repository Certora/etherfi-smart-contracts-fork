// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract CallHookHelper {
    // This funciton is just a way to save msg.sender and msg.value
    // from unresolved calls. This gets routed to a CVL function.
    function HarnessCallHook() external {}
}