// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;


import {IFlashLoanReceiver, SideEntranceLenderPool} from "./SideEntranceLenderPool.sol";


// A contract that may do anything in the SideEntranceLenderPool
// We use the Provver's over-approximation of storage for enabling any possible action.
contract FlashLoanReceiverHarness is IFlashLoanReceiver {

    // The pool
    SideEntranceLenderPool public pool;

    // Which function to call
    enum Func {
        Deposit,
        Withdraw,
        FlashLoan,
        Transfer
    }
    mapping(uint8 => Func) public toCalls;

    // The amounts to use in the function calls
    mapping(uint8 => uint256) public amounts;

    // The iteration number
    uint8 public i;

    receive() external payable {}

    function execute() external payable {
        require(msg.sender == address(pool));

        i += 1;  // Increase iteration

        if (toCalls[i] == Func.Deposit) {
            pool.deposit{value: amounts[i]}();
        } else if (toCalls[i] == Func.Withdraw) {
            pool.withdraw();
        } else if (toCalls[i] == Func.FlashLoan) {
            pool.flashLoan(amounts[i]);
        } else {
            // Repay some money
            i += 1;
            bool success = payable(address(pool)).send(amounts[i]);
            require(success);
        }
    }
}
