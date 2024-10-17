import "./Basic.spec";

using EETH as eETH;
using LiquidityPool as liquidityPool;

methods {
    // function globalIndexLibrary.calculateVaultEEthShares(
    //     address _membershipManager, 
    //     address _liquidityPool, 
    //     uint256 _ethRewardsPerEEthShareBeforeRebase, 
    //     uint256 _ethRewardsPerEEthShareAfterRebase) external returns (uint128[])=> NONDET;

    // function LiquidityPool.sharesForAmount(uint256 _amount) external returns (uint256)  => CVLSharesForAmount(_amount);
}


// NOTE: may need to model effect of eETH.totalSahres
ghost ghostShares(uint256) returns uint256 {
    axiom forall uint256 x. forall uint256 y. 
        x > y => ghostShares(x) > ghostShares(y);
    axiom forall uint256 x. x == 0 <=> ghostShares(x) == 0;
}
function CVLSharesForAmount(uint256 _amount) returns uint256 {
    return ghostShares(_amount);
}


// Note: this is meant to catch the finding M10 from
// the certora report.
// This rule shows: "An attacker cannot influence the distributed rewards
// by donating eETH"
// STATUS (1/2) Passing with fix PR
// commit from main repo: 246f8ced67b628f320c8958b8b09295c619e82fa
// https://prover.certora.com/output/65266/65d66225cd394cffbd9b3a2e00e1484b/?anonymousKey=30d7b79109d9795d362e7c64537d9b1350acffe1
// STATUS (2/2) ____ without fix PR:
// (TIMEOUT)
rule M10_donation_does_not_affect_rewards {
    env e;
    int128 accruedRewards;
    storage init = lastStorage;

    // tierData leq loop bound
    require currentContract.tierData.length < 3;

    rebase(e, accruedRewards) at init;

    // save the rewards data modified by distributeStaingRewardsV0/V1
    uint96[] rewards_idx_before; // tierData[i].rewardsGlobalIndex
    uint128[] tier_shares_before; //  tierDeposits[i].shares
    uint128[] pooled_shares; // tierVaults[i].totalPooledEEthShares
    uint256 td_length = currentContract.tierDeposits.length;
    require rewards_idx_before.length == td_length;
    require tier_shares_before.length == td_length;
    require pooled_shares.length == td_length;
    require forall uint256 i. i < td_length =>
        rewards_idx_before[i] == 
            currentContract.tierData[i].rewardsGlobalIndex &&
        tier_shares_before[i] ==
            currentContract.tierDeposits[i].shares &&
        pooled_shares[i] ==
            currentContract.tierVaults[i].totalPooledEEthShares;
        
    
    // Roll back to initial state and donate to EETH
    // Then call rebase with the same value again
    env e_donate;
    uint256 amount;
    eETH.transfer(e_donate, currentContract, amount) at init;
    rebase(e, accruedRewards);

    // Assert the tier data is the same if donation happened before the rebase
    assert forall uint256 i. i < td_length =>
        rewards_idx_before[i] == 
            currentContract.tierData[i].rewardsGlobalIndex &&
        tier_shares_before[i] ==
            currentContract.tierDeposits[i].shares &&
        pooled_shares[i] ==
            currentContract.tierVaults[i].totalPooledEEthShares;

}

// Note: this is meant to catch the finding M10 from
// the certora report.
// This rule shows: "An attacker cannot influence the distributed rewards
// by donating eETH"
// STATUS (1/2) Passing with fix PR
// https://prover.certora.com/output/65266/8a5abefff1674cce85c0cdcde5950c80/?anonymousKey=42a38819f042cf454cec0ff6110912fb9d23b3e9
// commit from main repo: 246f8ced67b628f320c8958b8b09295c619e82fa
// STATUS (2/2) Counterexample without fix PR (as expected):
// https://prover.certora.com/output/65266/4ca76923dc434097b57bf93b2620ae41/?anonymousKey=3d781f6cb09f11c48206c441c77ad1e53099257e
rule eeth_donation_cant_affect_staking_rewards_M10_singe_case {
    env e;
    int128 accruedRewards;
    storage init = lastStorage;

    // Assume tierData.length is 1 for now
    require currentContract.tierData.length == 1;

    rebase(e, accruedRewards) at init;
    // Get rewardsIndex for tier 0 
    uint96 rewardsGlobalIndex0NoDonation =
        currentContract.tierData[0].rewardsGlobalIndex;
    uint128 tier_shares_no_donation =
        currentContract.tierDeposits[0].shares;
    uint128 pool_shares_no_donation =
        currentContract.tierVaults[0].totalPooledEEthShares;

    // Roll back to initial state and donate to EETH
    // Then call rebase with the same value again
    env e_donate;
    uint256 amount;
    eETH.transfer(e_donate, currentContract, amount) at init;
    rebase(e, accruedRewards);
    // Get rewardsIndex for tier 0 for execution with donation
    uint96 rewardsGlobalIndex0WithDonation =
        currentContract.tierData[0].rewardsGlobalIndex;

    assert rewardsGlobalIndex0NoDonation ==
        rewardsGlobalIndex0WithDonation;
    assert currentContract.tierDeposits[0].shares ==
        tier_shares_no_donation;
    assert currentContract.tierVaults[0].totalPooledEEthShares ==
        pool_shares_no_donation;

}

// Note: this is meant to catch the finding M11 from
// the certora report.
// This rule shows: "An attacker cannot frontrun the call
// to rebase with a donation to cause it to revert".
// Note that rebase is reached by EtherFiAdmin.executeTasks
// (which was mentioned as the frontrunning target)
// and that rebase also reaches calculateRescaledTierRewards
// which is the site of the divide by 0 in the finding.
// 
// STATUS: Timeout
// https://prover.certora.com/output/65266/d7721945d0844b9d989821c715abb1ff/?anonymousKey=e27fe93bcc011ada8b4c97fbd456bc13cbbecf05
// Run link with more understandable bounds:
// https://prover.certora.com/output/65266/1c903adf6a30422eb9007d4834ed7649/?anonymousKey=03ddbe3750fe1c51eaed36039af424cbba0e53ec
rule donation_frontrunning_cannot_cause_M11 {
    env e;
    int128 accruedRewards;
    storage init = lastStorage;

    env e_donate;
    uint256 amount;

    require amount < 5192296858534827628530496329220095;
    // min and max uint112
    require accruedRewards >  -5192296858534827628530496329220095 &&
        accruedRewards < 5192296858534827628530496329220095;
    
    require eETH.shares[currentContract] < max_uint112;

    // Implicitly assume rebase will not revert from storage "init"
    rebase(e, accruedRewards) at init;

    // Roll back to initial state and donate to EETH
    // Then call rebase again with the same value
    eETH.transfer(e_donate, currentContract, amount) at init;

    require eETH.shares[currentContract] < max_uint112;
    require eETH.totalShares < max_uint112;

    // rebasing after the donation will also not revert
    rebase@withrevert(e, accruedRewards);
    assert !lastReverted;
}