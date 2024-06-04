pragma solidity ^0.8.0;

import {ERC20} from "./ERC20.sol";

/**
 * @title Voting contract using square root of balance as voting power
 */
contract VotingSqrt {

    ERC20 public token;

    // `_hasVoted[user]` is true if the user voted.
    mapping(address => bool) internal _hasVoted;

    uint256 public votesInFavor;  // How many in favor
    uint256 public votesAgainst;  // How many opposed
    uint256 public totalVotes;  // Total number voted

    // Vote on the proposal 
    function vote(bool isInFavor) public {
        // `msg.sender` is the address of the caller
        require(!_hasVoted[msg.sender]);
        _hasVoted[msg.sender] = true;

        uint256 power = votingPower(msg.sender);
        totalVotes += power;
        if (isInFavor) {
            votesInFavor += power;
        } else {
            // Bug injected!
            uint256 badPower = power < 10 ? power : 10;
            votesAgainst += badPower;
        }
    }

    /// @dev The voting power of the voter
    function votingPower(address voter) public view returns (uint256) {
        return sqrt(token.balanceOf(voter));
    }

    /// @dev Square root calculation
    function sqrt(uint256 x) public pure returns (uint256) {

        if (x == 0) return 0;
        if (x <= 3) return 1;

        uint256 z = (x + 1) / 2;
        uint256 y = x;
        while (z < y) {
            y = z;
            z = (x / z + z) / 2;
        }
        return y;
    }

    /// @dev Whether the voter has already voted
    function hasVoted(address voter) public view returns (bool) {
        return _hasVoted[voter];
    }
}
