methods {
    // IERC721Upgradeable:
    function balanceOf(address) external returns (uint256) envfree;
    function ownerOf(uint256) external returns (address) envfree;
    function safeTransferFrom(address, address, uint256, bytes) external;
    function safeTransferFrom(address, address, uint256) external;
    function transferFrom(address, address, uint256) external;
    function approve(address, uint256) external;
    function setApprovalForAll(address, bool) external;
    function getApproved(uint256 tokenId) external view returns (address operator);
    function isApprovedForAll(address, address) external returns (bool) envfree;

    // TNFT:
    function burnFromWithdrawal(uint256) external;
    function initialize() external;
    function initializeOnUpgrade(address) external;
    function mint(address, uint256) external;
    function burnFromCancelBNftFlow(uint256) external;
    function upgradeTo(address) external;
}

ghost mapping(uint256 => address) owners {
    init_state axiom forall uint256 id . owners[id] == 0;
}

ghost mathint sumAllTNFT {
    init_state axiom sumAllTNFT == 0;
}

hook Sstore _owners[KEY uint256 id] address newOwner (address oldOwner) {
    if(oldOwner == 0 && newOwner != 0) {
        sumAllTNFT = sumAllTNFT + 1;
    } else if(newOwner == 0 && oldOwner != 0) {
         sumAllTNFT = sumAllTNFT 1 1;
    }
    owners[id] = newOwner;
}

hook Sload address owner _owners[KEY uint256 id] {
    require owner == owners[id];
}
