using NodeOperatorManager as NodeOperatorManager;
/* Verification of `AuctionManager` */
methods {

    // Getters:
    function whitelistEnabled() external returns (bool) envfree;
    function whitelistBidAmount() external returns (uint128) envfree;
    function minBidAmount() external returns (uint64) envfree;
    function maxBidAmount() external returns (uint64) envfree;
    function numberOfActiveBids() external returns (uint256) envfree;
    function numberOfBids() external returns (uint256) envfree;
    function bids(uint256) external returns (uint256, uint64, address, bool) envfree;
    function getBidOwner(uint256) external returns (address) envfree;
    function isBidActive(uint256) external returns (bool) envfree;


    function NodeOperatorManager.getUserTotalKeys(address) external returns (uint64) envfree;
    function NodeOperatorManager.getNumKeysRemaining(address) external returns (uint64) envfree;


    function _.upgradeToAndCall(address,bytes) external => NONDET;
}

/// Is persistent because it mirrors the PoolManager storage.
persistent ghost mapping(uint256 => uint256) bids_amount {
    init_state axiom forall uint256 bid_id . bids_amount[bid_id] == 0;
}

ghost mathint sum_of_bids {
    init_state axiom sum_of_bids == 0;
}

ghost mathint sum_of_active_bids {
    init_state axiom sum_of_active_bids == 0;
}

ghost mathint sum_of_all_bids_amounts {
    init_state axiom sum_of_all_bids_amounts == 0;
}

ghost mathint sum_of_all_active_bids_amounts {
    init_state axiom sum_of_all_active_bids_amounts == 0;
}

ghost uint256 latest_bid_id;

ghost mapping(uint256 => bool) bids_is_active {
    init_state axiom forall uint256 bid_id . bids_is_active[bid_id] == false;
}

ghost mapping(address => uint256) user_last_bid_id_index {
    init_state axiom forall address user . user_last_bid_id_index[user] == 0;
}

hook Sstore bids[KEY uint256 bid_id].amount uint256 new_amount (uint256 old_amount) {
    bids_amount[bid_id] = new_amount;
    sum_of_bids = sum_of_bids + 1;
    sum_of_all_bids_amounts = sum_of_all_bids_amounts + new_amount;
}

hook Sload uint256 _amount bids[KEY uint256 bid_id].amount {
    require _amount == bids_amount[bid_id];
}

hook Sstore bids[KEY uint256 bid_id].isActive bool new_acitive (bool old_active) {
    if (new_acitive) {
        sum_of_active_bids = sum_of_active_bids + 1;
        sum_of_all_active_bids_amounts = sum_of_all_active_bids_amounts + bids_amount[bid_id];
    } else if (!new_acitive && old_active) {
        sum_of_active_bids = sum_of_active_bids - 1; 
        sum_of_all_active_bids_amounts = sum_of_all_active_bids_amounts - bids_amount[bid_id];
    }
    bids_is_active[bid_id] = new_acitive;
}

hook Sload bool _isActive bids[KEY uint256 bid_id].isActive {
    require _isActive == bids_is_active[bid_id];
}

// Functions filtered out since they use `delegatecall`.
definition isFilteredFunc(method f) returns bool = (
    f.selector == sig:upgradeToAndCall(address, bytes).selector
);

// numberOfActiveBids equals the sum of active bids.
invariant numberOfActiveBidsCorrect() 
    sum_of_active_bids == to_mathint(numberOfActiveBids())
    filtered {f -> !isFilteredFunc(f)}

// numberOfBids equals the sum of all bids.
invariant numberOfBidsEqTheSumOfAllBids() 
    sum_of_bids == to_mathint(numberOfBids())
    filtered {f -> !isFilteredFunc(f)}

// solvency invariant - contract should hold atleast sumOfAllActiveBidAmounts amount of eth.
invariant activeBidsSolvency()
    to_mathint(nativeBalances[currentContract]) >= sum_of_all_active_bids_amounts
    filtered {f -> !isFilteredFunc(f)}

// the sum of all used keys equals num of bids.
// invariant numOfAllUsedKeysEqNumOfBids() {}

// chack for all bids to see if the key index is unique per user.
// rule bidderPubKeyIndexIsUniqePerUser() {}

rule bidImmutability(method f, uint256 bid_id) filtered {f -> !isFilteredFunc(f)} {
    env e;
    calldataarg args;

    require bid_id < numberOfBids();

    uint256 AmountBefore;
    uint64 bidderPubKeyIndexBefore;
    address bidderAddressBefore;
    uint256 AmountAfter;
    uint64 bidderPubKeyIndexAfter;
    address bidderAddressAfter;

    AmountBefore, bidderPubKeyIndexBefore, bidderAddressBefore, _ = bids(bid_id);

    f(e, args);

    AmountAfter, bidderPubKeyIndexAfter, bidderAddressAfter, _ = bids(bid_id);

    assert AmountBefore == AmountAfter, "bid amount was changed";
    assert bidderPubKeyIndexBefore == bidderPubKeyIndexAfter, "bidder key index was changed";
    assert bidderAddressBefore == bidderAddressAfter, "bidder address was changed";
}

/// @title The contact is set as initialized in the constructor -- seems a bug?
invariant alwaysInitialized()
    currentContract._initialized == max_uint8
    filtered {f -> !isFilteredFunc(f)}

rule integrityOfCreateBid(uint256 _bidSize, uint256 _bidAmountPerBid) {
    env e;
    uint256 newBidId;
    mathint msgValue = e.msg.value;
    mathint numberOfBidsBefore = numberOfBids();
    mathint numberOfActiveBidsBefore = numberOfActiveBids();
    mathint bidIndexInBatch = newBidId - numberOfBidsBefore;
    mathint senderFirstKeyIndex = NodeOperatorManager.getUserTotalKeys(e.msg.sender) - NodeOperatorManager.getNumKeysRemaining(e.msg.sender);

    require to_mathint(newBidId) < numberOfBidsBefore + _bidSize;
    require to_mathint(newBidId) >= numberOfBidsBefore;

    // new bid fields:
    uint256 amount;
    uint64 bidderPubKeyIndex;
    address bidderAddress;
    bool isActive;

        createBid(e, _bidSize, _bidAmountPerBid);

    // get one of the new bids:
    amount, bidderPubKeyIndex, bidderAddress, isActive = bids(e, newBidId);

    mathint numberOfBidsAfter = numberOfBids();
    mathint numberOfActiveBidsAfter = numberOfActiveBids(); 
    mathint senderLastKeyIndex = NodeOperatorManager.getUserTotalKeys(e.msg.sender) - NodeOperatorManager.getNumKeysRemaining(e.msg.sender);

    // trivial due to requires:
    assert msgValue == _bidSize * _bidAmountPerBid, "function should have reverted";
    // number of bids update correctly
    assert numberOfBidsAfter == numberOfBidsBefore + _bidSize, "ammount of bids updated incorrectly";
    assert numberOfActiveBidsAfter == numberOfActiveBidsBefore + _bidSize, "ammount of  active bids updated incorrectly";
    assert senderLastKeyIndex == senderFirstKeyIndex + _bidSize, "amount of used keys updated incorrectly";
    // the right bids were added:
    assert amount == _bidAmountPerBid;
    assert bidderPubKeyIndex == assert_uint64(senderFirstKeyIndex + bidIndexInBatch);
    assert bidderAddress == e.msg.sender;
    assert isActive;
}

// rule integrityOfCancelBid(uint256 bidId) {
//     env e;
// }

// rule onlyWhiteListCanBid() {}

/// @title Verifies that all functions can be called
rule sanity(method f) {
    env e;
    calldataarg args;
    f(e, args);
    satisfy true;
}