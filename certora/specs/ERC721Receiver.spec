methods {
    function _.onERC721Received(
        address operator,
        address from,
        uint256 tokenId,
        bytes data
    ) external => CalleeSelector(calledContract) expect bytes4;
}

persistent ghost CalleeSelector(address) returns bytes4;