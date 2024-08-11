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

persistent ghost mathint sumAllTNFT {
    init_state axiom sumAllTNFT == 0;
}

persistent ghost mapping(uint256 => address) bnftOwners {
    init_state axiom forall uint256 id . bnftOwners[id] == 0;
}

persistent ghost mathint sumAllBNFT {
    init_state axiom sumAllBNFT == 0;
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

