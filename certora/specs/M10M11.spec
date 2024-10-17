import "./Basic.spec";

using EETH as eETH;
using LiquidityPool as liquidityPool;

// Note: this is meant to catch the finding M10 from
// the certora report.
// This rule shows: "An attacker cannot influence the distributed rewards
// by donating eETH"
// STATUS (1/2) Passing with fix PR
// fix commit from main repo: 246f8ced67b628f320c8958b8b09295c619e82fa
// https://prover.certora.com/output/65266/65d66225cd394cffbd9b3a2e00e1484b/?anonymousKey=30d7b79109d9795d362e7c64537d9b1350acffe1
// STATUS (2/2) Timeout without fix PR:
// See less general version below that is more stable without the fix.
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
// Run https://prover.certora.com/output/65266/8a5abefff1674cce85c0cdcde5950c80/?anonymousKey=42a38819f042cf454cec0ff6110912fb9d23b3e9
// commit from main repo: 246f8ced67b628f320c8958b8b09295c619e82fa
// STATUS (2/2) Counterexample without fix PR (as expected):
// Run https://prover.certora.com/output/65266/4ca76923dc434097b57bf93b2620ae41/?anonymousKey=3d781f6cb09f11c48206c441c77ad1e53099257e
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
// STATUS (1/2): Passing with fix PR:
// fix commit from main repo: 246f8ced67b628f320c8958b8b09295c619e82fa
// Run: https://prover.certora.com/output/65266/2c8b953f42bc4878962025a2c5369b3b/?anonymousKey=60da39e3a293da4459e364dc58a84af57d0045cc
// STATUS (2/2): Counterexample without fix PR:
// Run: https://prover.certora.com/output/65266/673d842c9aae42ffa404e293380dae6b/?anonymousKey=797a7280b4b626fe862954be59e22017856f8769
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