// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0;

import {IERC20, ERC20} from './ERC20.sol';


/** @dev This pool contract has two vulnarbilities.
 *  1. The `nonReentrant` modifier has been disabled.
 *  2. If it depolyed with underlaying asset it could get stolen by the first depositor.
 */
contract UnguardedPool is ERC20 {

    /// @notice This re-entrancy guard has been disabled.
    modifier nonReentrant() {
        _;
    }
  
    IERC20 public asset;   
  
    function sharesToAmount(uint256 shares) public view virtual returns (uint256) {
        uint256 poolBalance = asset.balanceOf(address(this));  
        return shares * poolBalance / totalSupply();  
    }
  
    function amountToShares(uint256 amount) public view virtual returns (uint256) {
        uint256 poolBalance = asset.balanceOf(address(this));   
        return amount * totalSupply() / poolBalance;   
    }
  
    function deposit(uint256 amount) public nonReentrant() returns(uint256 shares) {
        uint256 poolBalance = asset.balanceOf(address(this));

        if (totalSupply()==0 || poolBalance == 0){
            shares = amount;
        } else{
            shares = amountToShares(amount);
            require (shares != 0);
        }

        asset.transferFrom(msg.sender, address(this), amount);
        _mint(msg.sender, shares);
    }
  
    function withdraw(uint256 shares) public nonReentrant() returns (uint256 amountOut)  {
        uint256 poolBalance = asset.balanceOf(address(this));
        require (poolBalance != 0);
  
        amountOut = sharesToAmount(shares);
        require (amountOut != 0);
  
        _burn(msg.sender,shares);
        asset.transferFrom(address(this), msg.sender, amountOut);
    }
}
