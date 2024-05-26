pragma solidity >=0.8.0;

import {ERC20} from "./tokens/ERC20.sol";


contract Exchange {

  ERC20 public immutable tokenA;
  ERC20 public immutable tokenB;

  constructor (
    address _tokenA,
    address _tokenB
  ) {
    tokenA = ERC20(_tokenA);
    tokenB = ERC20(_tokenB);
  }

  function transferAtoB(uint256 amount) public {
    // Take from A
    tokenA.transferFrom(msg.sender, address(this), amount);
    // Transfer in B
    tokenB.transfer(msg.sender, amount);
  }
  
  function balanceA() public view returns (uint256) {
    return tokenA.balanceOf(address(this));
  }
  
  function balanceB() public view returns (uint256) {
    return tokenB.balanceOf(address(this));
  }
}
