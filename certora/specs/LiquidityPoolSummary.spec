import "LiquidityPoolMock.spec";

methods {
    /// LiquidityPool mock
    function _.reduceEthAmountLockedForWithdrawal(uint128 amount) external => reduceEthAmount(amount) expect void;
    function _.addEthAmountLockedForWithdrawal(uint128 amount) external => addEthAmount(amount) expect void;
    function _.withdraw(address recipient, uint256 amount) external with (env e) => withdrawCVL(e.msg.sender, recipient,amount) expect uint256;
    function _.amountForShare(uint256 shares) external => amountForShareCVL(shares) expect uint256;
    function _.sharesForAmount(uint256 amount) external => sharesForAmountCVL(amount) expect uint256;
    function _.getTotalPooledEther() external => getTotalPooledEtherCVL() expect uint256;
    function _.getTotalEtherClaimOf(address user) external => getTotalEtherClaimOfCVL(user) expect uint256;
}