import "./Basic.spec";

using EETH as eETH;

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