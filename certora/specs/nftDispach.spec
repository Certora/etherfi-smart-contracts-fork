using TNFT as tnft;
using BNFT as bnft;

methods {
    // IERC721Upgradeable:
    function _.balanceOf(address) external => DISPATCHER(true);
    function _.ownerOf(uint256) external => DISPATCHER(true);
    function _.safeTransferFrom(address, address, uint256, bytes) external => DISPATCHER(true);
    function _.safeTransferFrom(address, address, uint256) external => DISPATCHER(true);
    function _.transferFrom(address, address, uint256) external => DISPATCHER(true);
    function _.approve(address, uint256) external => DISPATCHER(true);
    function _.setApprovalForAll(address, bool) external => DISPATCHER(true);
    function _.getApproved(uint256) external => DISPATCHER(true);
    function _.isApprovedForAll(address, address) external => DISPATCHER(true);

    // BNFT:
    function _.burnFromWithdrawal(uint256) external => DISPATCHER(true);
    function _.initialize() external => DISPATCHER(true);
    function _.initializeOnUpgrade(address) external => DISPATCHER(true);
    function _.mint(address, uint256) external => DISPATCHER(true);
    function _.burnFromCancelBNftFlow(uint256) external => DISPATCHER(true);
    function _.upgradeTo(address) external => DISPATCHER(true);
}

persistent ghost mapping(uint256 => address) tnftOwners {
    init_state axiom forall uint256 id . tnftOwners[id] == 0;
}

persistent ghost mapping(address => uint256) tntBalances {
    init_state axiom forall address owner . tntBalances[owner] == 0;
}

persistent ghost mathint sumAllTNFT {
    init_state axiom sumAllTNFT == 0;
}

persistent ghost mathint sumAllTNFTBalances {
    init_state axiom sumAllTNFTBalances == 0;
}

persistent ghost mapping(uint256 => address) bnftOwners {
    init_state axiom forall uint256 id . bnftOwners[id] == 0;
}

persistent ghost mapping(address => uint256) bntBalances {
    init_state axiom forall address owner . bntBalances[owner] == 0;
}

persistent ghost mathint sumAllBNFT {
    init_state axiom sumAllBNFT == 0;
}

persistent ghost mathint sumAllBNFTBalances {
    init_state axiom sumAllBNFTBalances == 0;
}

hook Sstore tnft._owners[KEY uint256 id] address newOwner (address oldOwner) {
    if(oldOwner == 0 && newOwner != 0) {
        sumAllTNFT = sumAllTNFT + 1;
    } else if(newOwner == 0 && oldOwner != 0) {
         sumAllTNFT = sumAllTNFT - 1;
    }
    tnftOwners[id] = newOwner;
}

hook Sload address owner tnft._owners[KEY uint256 id] {
    require owner == tnftOwners[id];
}

hook Sstore bnft._owners[KEY uint256 id] address newOwner (address oldOwner) {
    if(oldOwner == 0 && newOwner != 0) {
        sumAllBNFT = sumAllBNFT + 1;
    } else if(newOwner == 0 && oldOwner != 0) {
         sumAllBNFT = sumAllBNFT - 1;
    }
    bnftOwners[id] = newOwner;
}

hook Sload address owner bnft._owners[KEY uint256 id] {
    require owner == bnftOwners[id];
}

hook Sstore tnft._balances[KEY address owner] uint256 newCount (uint256 oldCount) {
    sumAllTNFTBalances = sumAllTNFTBalances - oldCount + newCount;
    tntBalances[owner] = newCount;
}

hook Sload uint256 count tnft._balances[KEY address owner] {
    require count == tntBalances[owner];
}

hook Sstore bnft._balances[KEY address owner] uint256 newCount (uint256 oldCount) {
    sumAllBNFTBalances = sumAllBNFTBalances - oldCount + newCount;
    bntBalances[owner] = newCount;
}

hook Sload uint256 count bnft._balances[KEY address owner] {
    require count == bntBalances[owner];
}

// amount of tnfts with owner equals the sum of every tnft owner balance.
invariant sumAllTNFTEqSumAllTNFTBalances()
    sumAllTNFTBalances == sumAllTNFT;

// amount of bnfts with owner equals the sum of every bnft owner balance.
invariant sumAllBNFTEqSumAllBNFTBalances()
    sumAllBNFTBalances == sumAllBNFT;
