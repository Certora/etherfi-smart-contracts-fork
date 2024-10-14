import "./Basic.spec";

using EETH as eETH;

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
rule donation_frontrunning_cannot_cause_M11 {
    env e;
    int128 accruedRewards;
    storage init = lastStorage;

    // Implicitly assume rebase will not revert from storage "init"
    rebase(e, accruedRewards) at init;

    // Roll back to initial state and donate to EETH
    // Then call rebase again with the same value
    env e_donate;
    uint256 amount;
    eETH.transfer(e_donate, currentContract, amount) at init;

    // rebasing after the donation will also not revert
    rebase@withrevert(e, accruedRewards);
    assert !lastReverted;
}