import "./Basic.spec";

using EETH as eETH;
using LiquidityPool as liquidityPool;

// Note: this is meant to catch the finding M10 from
// the certora report.
// This rule shows: "An attacker cannot influence the distributed rewards
// by donating eETH"
// STATUS (1/2): passes with the fix PR
// commit from main repo: 246f8ced67b628f320c8958b8b09295c619e82fa
// https://prover.certora.com/output/65266/22e44bbfc4304ecaa8a9d8e792c56b30/?anonymousKey=c6113a5a763bd8e4a5bd52fd55a7896e2146c0be
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