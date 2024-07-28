methods {
    function wrap(uint256) external returns (uint256);
    function wrapWithPermit(uint256, ILiquidityPool.PermitInput) external returns (uint256);
    function unwrap(uint256) external returns (uint256);
    function rescueTreasuryWeeth() external;
    function getWeETHByeETH(uint256) external returns (uint256) envfree;
    function getEETHByWeETH(uint256) external returns (uint256) envfree;
    function getRate() external returns (uint256) envfree;

    function _.sharesForAmount(uint256 amount) external => identity(amount) expect uint256;
    function _.amountForShare(uint256 amount) external => identity(amount) expect uint256;
}

function identity(uint256 x) returns uint256 {
    return x;
}

