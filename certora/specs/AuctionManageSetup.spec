methods {
    function _.upgradeToAndCall(address,bytes) external => NONDET;
}

persistent ghost mapping(uint256 => uint256) bids_amount {
    init_state axiom forall uint256 bid_id . bids_amount[bid_id] == 0;
}

ghost mathint sum_of_bids {
    init_state axiom sum_of_bids == 0;
}

ghost mathint sum_of_active_bids {
    init_state axiom sum_of_active_bids == 0;
}

ghost mathint sum_of_all_active_bids_amounts {
    init_state axiom sum_of_all_active_bids_amounts == 0;
}

ghost mapping(uint256 => bool) bids_is_active {
    init_state axiom forall uint256 bid_id . bids_is_active[bid_id] == false;
}

hook Sstore bids[KEY uint256 bid_id].amount uint256 new_amount (uint256 old_amount) {
    bids_amount[bid_id] = new_amount;
    sum_of_bids = sum_of_bids + 1;
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
