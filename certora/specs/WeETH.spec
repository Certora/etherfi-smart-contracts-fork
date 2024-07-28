methods {
    function totalShares() external returns (uint256) envfree;
    function shares(address) external returns (uint256) envfree;
    function allowance(address, address) external returns (uint256) envfree;

    function _.sharesForAmount(uint256 amount) external => identity(amount) expect uint256;
}

function identity(uint256 x) returns uint256 {
    return x;
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

hook Sload uint256 _shares shares[KEY address _user] {
    require _shares == sharesGhost[_user];
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

/**
Verify that there is no fee on transfer.
**/
rule noFeeOnTransfer(address bob, uint256 amount) {
    env e;
    require bob != e.msg.sender;
    uint256 balanceSenderBefore = shares(e.msg.sender);
    uint256 balanceBefore = shares(bob);

    transfer(e, bob, amount);

    uint256 balanceAfter = shares(bob);
    uint256 balanceSenderAfter = shares(e.msg.sender);
    assert balanceAfter == assert_uint256(balanceBefore + amount);
    assert balanceSenderAfter == assert_uint256(balanceSenderBefore - amount);
}

/**
Token transfer works correctly. Balances are updated if not reverted. 
If reverted then the transfer amount was too high, or the recipient either 0, the same as the sender or the currentContract.
**/
rule transferCorrect(address to, uint256 amount) {
    env e;
    require e.msg.value == 0 && e.msg.sender != 0;
    uint256 fromBalanceBefore = shares(e.msg.sender);
    uint256 toBalanceBefore = shares(to);
    require fromBalanceBefore + toBalanceBefore <= max_uint256;

    transfer@withrevert(e, to, amount);
    bool reverted = lastReverted;
    if (!reverted) {
        if (e.msg.sender == to) {
            assert shares(e.msg.sender) == fromBalanceBefore;
        } else {
            assert shares(e.msg.sender) == assert_uint256(fromBalanceBefore - amount);
            assert shares(to) == assert_uint256(toBalanceBefore + amount);
        }
    } else {
        assert amount > fromBalanceBefore || to == 0 || e.msg.sender == to || to == currentContract;
    }
}

/**
Test that transferFrom works correctly. Balances are updated if not reverted.
**/
rule transferFromCorrect(address from, address to, uint256 amount) {
    env e;
    require e.msg.value == 0;
    uint256 fromBalanceBefore = shares(from);
    uint256 toBalanceBefore = shares(to);
    uint256 allowanceBefore = allowance(from, e.msg.sender);
    require fromBalanceBefore + toBalanceBefore <= max_uint256;

    transferFrom(e, from, to, amount);

    assert from != to =>
        shares(from) == assert_uint256(fromBalanceBefore - amount) &&
        shares(to) == assert_uint256(toBalanceBefore + amount);
}

/**
transferFrom should revert if and only if the amount is too high or the recipient is 0 or the contract itself.
**/
rule transferFromReverts(address from, address to, uint256 amount) {
    env e;
    uint256 allowanceBefore = allowance(from, e.msg.sender);
    uint256 fromBalanceBefore = shares(from);
    require from != 0 && e.msg.sender != 0;
    require e.msg.value == 0;
    require fromBalanceBefore + shares(to) <= max_uint256;

    transferFrom@withrevert(e, from, to, amount);

    assert lastReverted <=> (allowanceBefore < amount || amount > fromBalanceBefore || to == 0 || to == currentContract);
}

/**
Transfer from msg.sender to recipient doesn't change the balance of other addresses.
**/
rule TransferDoesntChangeOtherBalance(address to, uint256 amount, address other) {
    env e;
    require other != e.msg.sender;
    require other != to && other != currentContract;
    uint256 balanceBefore = shares(other);
    transfer(e, to, amount); 
    assert balanceBefore == shares(other);
}

/**
Transfer from sender to recipient using transferFrom doesn't change the balance of other addresses.
**/
rule TransferFromDoesntChangeOtherBalance(address from, address to, uint256 amount, address other) {
    env e;
    require other != from;
    require other != to;
    uint256 balanceBefore = shares(other);
    transferFrom(e, from, to, amount); 
    assert balanceBefore == shares(other);
}

// rule mintMonotonicity() {}

// rule mintAccumulativity() {}

// rule burnMonotonicity() {}

// rule burnAccumulativity() {}
