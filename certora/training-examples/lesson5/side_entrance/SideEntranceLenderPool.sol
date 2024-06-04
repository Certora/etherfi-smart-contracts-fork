// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;


interface IFlashLoanReceiver {
    function execute() external payable;
}


/**
 * Adapted from:
 * https://github.com/tinchoabbate/damn-vulnerable-defi/blob/v3.0.0/contracts/side-entrance/SideEntranceLenderPool.sol
 */
contract SideEntranceLenderPool {

    mapping (address => uint256) private deposits;
    
    receive() external payable {}

    function deposit() external payable {
        deposits[msg.sender] += msg.value;
    }

    function withdraw() external {
        uint256 amountToWithdraw = deposits[msg.sender];
        deposits[msg.sender] = 0;
        bool success = payable(msg.sender).send(amountToWithdraw);
        require(success, "Wthdraw failed");
    }

    function flashLoan(uint256 amount) external {
        uint256 balanceBefore = address(this).balance;
        require(balanceBefore >= amount, "Not enough ETH in balance to provide loan");

        IFlashLoanReceiver(msg.sender).execute{value: amount}();

        uint256 balanceAfter = address(this).balance;
        require(balanceAfter >= balanceBefore, "Flash loan hasn't been paid back");
    }
}
