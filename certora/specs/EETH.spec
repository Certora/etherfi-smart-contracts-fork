methods {
    function totalShares() external returns (uint256) envfree;
    function shares(address) external returns (uint256) envfree;
}


// It is better to use `mathint` since doesn't overflow or underflow
persistent ghost mathint sumOfShares {
    // `init_state` determines the state after the constructor
    init_state axiom sumOfShares == 0;
}

ghost mapping(address => uint256) sharesGhost {
    init_state axiom forall address user . sharesGhost[user] == 0;
}


hook Sstore shares[KEY address _user] uint256 newVal (uint256 oldVal) {
    // Update the sum in every change
    sumOfShares = sumOfShares + newVal - oldVal;
    sharesGhost[_user] = newVal;
}


/// @title `totalShares` is the sum of all shares
invariant totalSharesIsSumOfShares()
    to_mathint(totalShares()) == sumOfShares
    filtered {
            f -> f.selector != sig:upgradeToAndCall(address,bytes).selector
    }


/// @title The sum of shares of two users is not greater than total shares
invariant sumOfTwo(address user1, address user2)
    shares(user1) + shares(user2) <= sumOfShares
    filtered {
            f -> f.selector != sig:upgradeToAndCall(address,bytes).selector
    }
    {
        preserved {
            requireInvariant totalSharesIsSumOfShares();
        }
    }