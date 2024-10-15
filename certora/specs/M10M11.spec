import "./Basic.spec";

using EETH as eETH;
using LiquidityPool as liquidityPool;

// Note: this is meant to catch the finding M10 from
// the certora report.
// This rule shows: "An attacker cannot influence the distributed rewards
// by donating eETH"
// STATUS (1/2): passes with the fix PR
// commit from main repo: 246f8ced67b628f320c8958b8b09295c619e82fa
// https://prover.certora.com/output/65266/81afa94e9f7b4c1b967d8308f427e1ba/?anonymousKey=4c6d2851cdf960fccc33a1bf8ce49f25434aea21
// STATUS (2/2): fails without the fix PR (as expected):
// https://prover.certora.com/output/65266/17bbb3dcd6c4478ab74ee7de3d1af1b6?anonymousKey=65c7d98202b96cbb848701546dbd98fdabe4a3a5
rule eeth_donation_cant_affect_staking_rewards_M10 {
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

// Note: this is meant to catch the finding M10 from
// the certora report.
// This rule shows: "An attacker cannot influence the distributed rewards
// by donating eETH"
// STATUS (1/2) Passing with fix PR
// commit from main repo: 246f8ced67b628f320c8958b8b09295c619e82fa
// https://prover.certora.com/output/65266/65d66225cd394cffbd9b3a2e00e1484b/?anonymousKey=30d7b79109d9795d362e7c64537d9b1350acffe1
// STATUS (2/2) Failing without fix PR (as expected):
// https://prover.certora.com/output/65266/4f0b272aae8f4d50b12ea67154f20da9/?anonymousKey=31f95550a4d6604f48a105b46af4cb924fdbf25f
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
        
    
    // Get rewardsIndex for tier 0 
    // uint96 rewardsGlobalIndex0NoDonation =
    //     currentContract.tierData[0].rewardsGlobalIndex;

    // Roll back to initial state and donate to EETH
    // Then call rebase with the same value again
    env e_donate;
    uint256 amount;
    eETH.transfer(e_donate, currentContract, amount) at init;
    rebase(e, accruedRewards);
    // Get rewardsIndex for tier 0 for execution with donation
    // uint96 rewardsGlobalIndex0WithDonation =
    //     currentContract.tierData[0].rewardsGlobalIndex;

    // Assert the tier data is the same if donation happened before the rebase
    assert forall uint256 i. i < td_length =>
        rewards_idx_before[i] == 
            currentContract.tierData[i].rewardsGlobalIndex &&
        tier_shares_before[i] ==
            currentContract.tierDeposits[i].shares &&
        pooled_shares[i] ==
            currentContract.tierVaults[i].totalPooledEEthShares;


    // assert forall uint256 i. i < currentContract.tierData.length =>
    //     rewards_idx_before[i] == currentContract.tierData[i].rewardsGlobalIndex;

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

    // avoid overflow when minting shares
    // require require_uint256(amount + eETH.shares[currentContract]) <
    //     max_uint256;

    // Donation could cause an overflow on the following line of EETH.sol
    //     function mintShares(address _user, uint256 _share) external onlyPoolContract {
    //     shares[_user] += _share;
    // which is reached on call to liquidityPool.deposit
    // OVERFLOW CEX Link:
    // https://prover.certora.com/output/65266/35a73a9218834d1487920f643e0d1cb3/?anonymousKey=b4ffada6cef7d18842c83dbae54bb1af3a500339
    // require require_uint256(eETH.shares[currentContract] + fanBoostThresholdEthAmount(e) ) < max_uint256;

    // Implicitly assume rebase will not revert from storage "init"
    rebase(e, accruedRewards) at init;

    // Roll back to initial state and donate to EETH
    // Then call rebase again with the same value
    eETH.transfer(e_donate, currentContract, amount) at init;

    // Need to ensure that minting shares during LiquidityPool.donate
    // in rebase does not cause an overflow
    // uint256 boostThreshold = fanBoostThresholdEthAmount(e);
    // uint256 totalPooledEther = require_uint256(liquidityPool.getTotalPooledEther(e) - boostThreshold);
    // require totalPooledEther > 0;
    // uint256 mintedShares = require_uint256((boostThreshold * eETH.totalShares(e)) / totalPooledEther);
    // require require_uint256(eETH.shares[currentContract] + mintedShares) < max_uint256;
    // require require_uint256(eETH.shares[currentContract] + boostThreshold) < max_uint256;

    require eETH.shares[currentContract] < max_uint112;
    require eETH.totalShares < max_uint112;

    // rebasing after the donation will also not revert
    rebase@withrevert(e, accruedRewards);
    assert !lastReverted;
}