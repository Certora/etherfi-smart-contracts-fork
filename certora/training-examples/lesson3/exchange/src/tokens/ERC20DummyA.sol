// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity >=0.8.0;

import {ERC20} from "./ERC20.sol";


contract ERC20DummyA is ERC20 {
  constructor (
    uint8 _decimals
  ) ERC20 ("DummyA", "A", _decimals) {
  }
}
