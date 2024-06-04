methods {
    function sqrt(uint256) external returns (uint256) envfree;
}

rule isSquareRoot(uint256 x) {
    uint256 s = sqrt(x);
    assert s * s <= to_mathint(x);
    assert (s + 1) * (s + 1) > to_mathint(x);
}

rule isSquareRootExample(uint256 x) {
    require x >= 20;
    uint256 s = sqrt(x);
    satisfy s * s <= to_mathint(x);
}
