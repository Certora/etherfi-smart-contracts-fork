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

    // BNFT:
    function burnFromWithdrawal(uint256) external;
    function initialize() external;
    function initializeOnUpgrade(address) external;
    function mint(address, uint256) external;
    function burnFromCancelBNftFlow(uint256) external;
    function upgradeTo(address) external;
}
