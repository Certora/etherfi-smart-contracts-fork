// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import {IERC20Upgradeable} from "@openzeppelin-upgradeable/contracts/token/ERC20/IERC20Upgradeable.sol";
import {LiquidityPool} from "src/LiquidityPool.sol";

contract LiquidityPoolERC4626 is LiquidityPool {

    constructor() payable LiquidityPool() {
        require (msg.value >= 1 ether, "MUST BOOTSTRAP WITH SUFFICIENT ETH");
        _deposit(msg.sender, msg.value, 0);
    }

    function deposit(uint256 amount, address receiver) external payable returns (uint256) {
        require (msg.value == amount);
        return _deposit(receiver, amount, 0);
    }

    function withdraw(uint256 amount, address receiver, address owner) external returns (uint256) {
        require (owner == msg.sender);
        return this.withdraw(receiver, amount);
    }

    function balanceOf(address user) public view returns (uint256) {
        return eETH.balanceOf(user);
    }

    function allowance(address owner, address spender) public view returns (uint256) {
        (bool success, bytes memory returndata) = address(eETH).staticcall(abi.encodeWithSelector(IERC20Upgradeable.allowance.selector, owner, spender));
        require (success, "Failed");
        return abi.decode(returndata, (uint256));
    }

    function totalSupply() public view returns (uint256) {
        return eETH.totalShares();
    }

    function totalAssets() public view returns (uint256) {
        return getTotalPooledEther();
    }

    function getPrice() public view returns (uint256) {
        return amountForShare(10**18);
    }

    function convertToShares(uint256 assets) public view returns (uint256) {
        return sharesForAmount(assets);
    }

    function convertToAssets(uint256 shares) public view returns (uint256) {
        return amountForShare(shares);
    }

    function maxWithdraw(address user) public view returns (uint256) {
        return this.getTotalEtherClaimOf(user);
    }

    function previewDeposit(uint256 assets) external view returns (uint256) {
        return _sharesForDepositAmount(assets);
    }

    function previewWithdraw(uint256 assets) external view returns (uint256) {
        return sharesForWithdrawalAmount(assets);
    }
}