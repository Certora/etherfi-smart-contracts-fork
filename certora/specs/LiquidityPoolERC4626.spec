using LiquidityPoolERC4626 as Vault;
using EETH as EETH;

use builtin rule sanity;

methods {
    function Vault.totalSupply() external returns (uint256) envfree;
    function Vault.balanceOf(address) external returns (uint256) envfree;
    function Vault.allowance(address,address) external returns (uint256) envfree;
    function Vault.getPrice() external returns (uint256) envfree;
    function Vault.totalAssets() external returns (uint256) envfree;
    function Vault.maxWithdraw(address) external returns (uint256) envfree;
    function Vault.convertToAssets(uint256) external returns (uint256) envfree;
    function Vault.convertToShares(uint256) external returns (uint256) envfree;
    function Vault.previewDeposit(uint256) external returns (uint256) envfree;
    function Vault.previewWithdraw(uint256) external returns (uint256) envfree;
}

function token_totalSupply() returns uint256 {return max_uint256;}
function token_balanceOf(address user) returns uint256 {return nativeBalances[user];}
function token_allowance(address user, address spender) returns uint256 {return 0;}

/// "1" in 18 decimals.
definition WAD() returns uint256 = 10^18;
/// Initial assets set in the constructor (if not set, the default should be zero).
definition INITIAL_ASSETS() returns uint256 = 10^18;
/// Initial shares supply set in the constructor (if not set, the default should be zero).
definition INITIAL_SUPPLY() returns uint256 = 10^18;
/// Initial price set in constructor.
definition INITIAL_PRICE() returns mathint = INITIAL_SUPPLY() == 0 ? WAD() : WAD() * INITIAL_ASSETS() / INITIAL_SUPPLY();
/// Tolerance for maximum round-trip asset change
definition ROUND_TRIP_TOL() returns mathint = 2;
/// Tolerance for maximum relative change of price in 18 decimals (100% = 1e18)
definition RELATIVE_CHANGE_TOL() returns mathint = WAD() / 10000000;
/// IERC20.permit signature.
definition isPermit(method f) returns bool = 
    f.selector == sig:EETH.permit(address,address,uint256,uint256,uint8,bytes32,bytes32).selector;
/// Is called from liquidityPool and restricted to liquidityPool.
definition isEETHMint(method f) returns bool = 
    f.selector == sig:EETH.mintShares(address,uint256).selector;
/// Upgrade methods
definition isUpgrade(method f) returns bool = 
    f.selector == sig:EETH.upgradeToAndCall(address,bytes).selector ||
    f.selector == sig:Vault.upgradeToAndCall(address,bytes).selector;
/// Absolute value 
definition abs(mathint x) returns mathint = x > 0 ? x : -x;
/// Returns whether y is equal to x up to error bound of 'err' (18 decs).
/// e.g. 10% relative error => err = 1e17
definition relativeErrorBound(mathint x, mathint y, mathint err) returns bool = 
    (x != 0 
    ? abs(x - y) * WAD()<= abs(x) * err 
    : abs(y) <= err);
/* =======================================================*/
/// Tracking sum of balances in Vault:

/// True sum of balances.
ghost mathint sumOfBalances {
    init_state axiom sumOfBalances == 0;
}

/// The initial value is being updated as we access the acounts balances one-by-one.
/// Should only be used as an initial value, never post-action!
ghost mathint sumOfBalances_init {
    init_state axiom sumOfBalances_init == 0;
}

ghost mapping(address => bool) didAccessAccount;

function SumTrackingSetup() {
    require sumOfBalances == sumOfBalances_init;
    require forall address account. !didAccessAccount[account];
}

hook Sload uint256 _balance EETH.shares[KEY address account] {
    if(!didAccessAccount[account]) {
        didAccessAccount[account] = true;
        sumOfBalances_init = sumOfBalances_init - _balance;
        require sumOfBalances_init >= 0;
    }
}

hook Sstore EETH.shares[KEY address account] uint256 _balance (uint256 _balance_old) {
    if(!didAccessAccount[account]) {
        didAccessAccount[account] = true;
        sumOfBalances_init = sumOfBalances_init - _balance_old;
        require sumOfBalances_init >= 0;
    }
    sumOfBalances = sumOfBalances + _balance - _balance_old;
}
/*
hook Sload uint256 _totalAssets Vault.totalAssets {
    /// Special assumption: the total assets of the Vault are capped to prevent overflow.
    require _totalAssets * WAD() <= max_uint256;
}*/

/*=======================================================*/

function TokenAssumptions() {
    /// Assumption: token initial supply is larger than shares initial supply.
    require Vault.totalSupply() <= token_totalSupply();
}

/// The total assets (in token value) of a user:
function getUserAssets(address user) returns mathint {
    return token_balanceOf(user) + Vault.maxWithdraw(user);
}

strong invariant AssetsSolvency() totalAssets() - INITIAL_ASSETS() <= to_mathint(token_balanceOf(Vault))
filtered{f -> !isUpgrade(f) && !isEETHMint(f)}
{
    preserved with (env e) {
        requireInvariant PriceIsAtLeastInitial();
        requireInvariant SumOfBalancesIsTotalSupply();
        requireInvariant VaultZeroTokenAllowance(e.msg.sender);
    }
}

strong invariant SumOfBalancesIsTotalSupply() (sumOfBalances == Vault.totalSupply() - INITIAL_SUPPLY() && sumOfBalances >=0)
filtered{f -> !isUpgrade(f) && !isEETHMint(f)}
{
    preserved with (env e) {
        requireInvariant PriceIsAtLeastInitial();
        TokenAssumptions();
        SumTrackingSetup();
    }
}

strong invariant PriceIsAtLeastInitial() to_mathint(Vault.getPrice()) >= INITIAL_PRICE()
filtered{f -> !isUpgrade(f) && !isEETHMint(f)}
/// Is called from liquidityPool and restricted to liquidityPool.
{
    preserved with (env e) {
        requireInvariant SumOfBalancesIsTotalSupply();
        TokenAssumptions();
        SumTrackingSetup();
    }
}

invariant VaultZeroTokenAllowance(address spender) token_allowance(Vault, spender) == 0
filtered{f -> !isPermit(f)} /// We assume the contract doesn't sign any permit off-chain.
{
    preserved with (env e) {
        require e.msg.sender != Vault;
    }
}

rule withdrawSendAssetsToReceiver(address receiver, uint256 assets) 
{
    uint256 balance_before = token_balanceOf(receiver);
        env e;
        withdraw(e, assets, receiver, _);
    uint256 balance_after = token_balanceOf(receiver);

    assert receiver != Vault => balance_after - balance_before == to_mathint(assets);
    assert receiver == Vault => balance_after == balance_before;
}

rule cannotWithdrawMoreThanMax(address owner) 
{
    SumTrackingSetup();
    requireInvariant PriceIsAtLeastInitial();
    requireInvariant SumOfBalancesIsTotalSupply();
    requireInvariant AssetsSolvency();
    uint256 maxValueToWithdraw = maxWithdraw(owner);
    
    env e;
    uint256 assets;
    address receiver;
    withdraw(e, assets, receiver, owner);

    assert assets <= maxValueToWithdraw;
}

rule userAssetsAreStable_deposit() {
    SumTrackingSetup();
    TokenAssumptions();
    requireInvariant PriceIsAtLeastInitial();
    requireInvariant SumOfBalancesIsTotalSupply();
    requireInvariant AssetsSolvency();

    env e; address player = e.msg.sender;
    require player != Vault;

    mathint assets_player_before = getUserAssets(player);
        uint256 assets;
        address receiver;
        deposit(e, assets, receiver);
    mathint assets_player_after = getUserAssets(player);

    assert receiver != player => abs(assets_player_after - assets_player_before + assets) <= 2; /// FAILS
    assert receiver == player => abs(assets_player_after - assets_player_before) <= 2; /// FAILS
}

rule userAssetsAreStable_withdraw() {
    SumTrackingSetup();
    TokenAssumptions();
    requireInvariant PriceIsAtLeastInitial();
    requireInvariant SumOfBalancesIsTotalSupply();
    requireInvariant AssetsSolvency();

    env e; address player = e.msg.sender;
    require player != Vault;

    mathint assets_player_before = getUserAssets(player);
        uint256 assets;
        address receiver;
        withdraw(e, assets, receiver, player);
    mathint assets_player_after = getUserAssets(player);

    assert receiver != player => abs(assets_player_after - assets_player_before + assets) <= 2; /// FAILS
    assert receiver == player => abs(assets_player_after - assets_player_before) <= 2; /// FAILS
}

rule assetsRoundTripConversionIsStable(uint256 amount) {
    TokenAssumptions();
    requireInvariant SumOfBalancesIsTotalSupply();
    requireInvariant PriceIsAtLeastInitial();
    requireInvariant AssetsSolvency();

    uint256 amount_d = Vault.previewDeposit(amount);
    uint256 amount_w = Vault.previewWithdraw(amount);
    assert abs(amount_d-amount_w) <= ROUND_TRIP_TOL();
}

rule PriceStability(uint256 assets, bool depositOrWithdraw) {
    env e;
    SumTrackingSetup();
    TokenAssumptions();
    requireInvariant SumOfBalancesIsTotalSupply();
    requireInvariant PriceIsAtLeastInitial();
    requireInvariant AssetsSolvency();

    uint256 price_pre = getPrice();
    if(depositOrWithdraw) {
        deposit(e, assets, _);
    } else {
        withdraw(e, assets, _, _);
    }
    uint256 price_post = getPrice();

    assert relativeErrorBound(price_post, price_pre, RELATIVE_CHANGE_TOL());
}

rule cannotFrontRunWithdraw(uint256 assets, method f) filtered{f -> f.contract == Vault && !f.isView} {
    env e1; address player = e1.msg.sender;
    env e2; address attacker = e2.msg.sender;
    
    SumTrackingSetup();
    TokenAssumptions();
    requireInvariant PriceIsAtLeastInitial();
    requireInvariant SumOfBalancesIsTotalSupply();
    requireInvariant AssetsSolvency();
    requireInvariant VaultZeroTokenAllowance(attacker);

    /// Two different actors which are not the Vault.
    require player != Vault && attacker != Vault && player != attacker;
    /// Attacker has no allowance from player.
    require Vault.allowance(player, attacker) == 0;
    /// Sum of token balances is capped by total supply.
    require token_balanceOf(attacker) + token_balanceOf(player) + token_balanceOf(Vault) <= to_mathint(token_totalSupply());

    storage initState = lastStorage;
    /// The player withdraws his assets successfully initially.
    withdraw(e1, assets, player, player);

    calldataarg args;
    /// Attacker performs an action.
    f(e2, args) at initState;
   
    /// The player tries to withdraw his assets after the attacker.
    withdraw@withrevert(e1, assets, player, player);

    assert !lastReverted, 
        "No action of a third-party could prevent a player from withdrawing his funds";
}

rule cannotFrontRunRedeem(uint256 assets, method f) filtered{f -> f.contract == Vault && !f.isView} {
    env e1; address player = e1.msg.sender;
    env e2; address attacker = e2.msg.sender;
    
    SumTrackingSetup();
    TokenAssumptions();
    requireInvariant PriceIsAtLeastInitial();
    requireInvariant SumOfBalancesIsTotalSupply();
    requireInvariant AssetsSolvency();
    requireInvariant VaultZeroTokenAllowance(attacker);

    /// Two different actors which are not the Vault.
    require player != Vault && attacker != Vault && player != attacker;
    /// Attacker has no allowance from player.
    require Vault.allowance(player, attacker) == 0;
    /// Sum of token balances is capped by total supply.
    require token_balanceOf(attacker) + token_balanceOf(player) + token_balanceOf(Vault) <= to_mathint(token_totalSupply());
    
    storage initState = lastStorage;
    
    /// The player redeems some shares successfully initially.
    uint256 totalAmountA = maxWithdraw(player);
    withdraw(e1, player, totalAmountA);

    calldataarg args;
    /// Attacker performs an action.
    f(e2, args) at initState;
   
    /// The player tries to redeem his shares after the attacker.
    uint256 totalAmountB = maxWithdraw(player);
    withdraw@withrevert(e1, player, totalAmountB);

    assert !lastReverted, 
        "No action of a third-party could prevent a player from redeeming his shares";
}