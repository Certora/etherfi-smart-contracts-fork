// All rules so far:
// https://prover.certora.com/output/80942/4d6713779ccd415c83a0923f4f825f12?anonymousKey=af9ab6b8f7511ff852458d520ddfa3d2ca78a0fb

using EETH as eETH;
using LiquidityPool as LiquidityPool;
using WithdrawRequestNFT as WithdrawRequestNFT;

use builtin rule sanity;

methods {
    function eETH.balanceOf(address _user) external returns (uint256) envfree;
    function eETH.totalShares() external returns (uint256) envfree;
    
    function LiquidityPool.getTotalPooledEther() external returns (uint256) envfree;
    function LiquidityPool.paused() external returns (bool) envfree;

    // src/EtherFiNode.sol
    function _.version() external => NONDET;
    function _.DEPRECATED_phase() external => NONDET;
    function _.DEPRECATED_exitRequestTimestamp() external => NONDET;
    function _.DEPRECATED_exitTimestamp() external => NONDET;
    function _.migrateVersion(uint256 _validatorId, IEtherFiNodesManager.ValidatorInfo _info) external => NONDET;
    function _.updateNumExitRequests(uint16 _up, uint16 _down) external => DISPATCHER(true);
    function _.numAssociatedValidators() external => NONDET;
    function _.unRegisterValidator(uint256 _validatorId, IEtherFiNodesManager.ValidatorInfo _info) external => DISPATCHER(true);
    function _.registerValidator(uint256 _validatorId, bool _enableRestaking) external => DISPATCHER(true);
    function _.eigenPod() external => NONDET;
    function _.isRestakingEnabled() external => NONDET;
    function _.updateNumberOfAssociatedValidators(uint16 _up, uint16 _down) external => DISPATCHER(true);
    function _.validatePhaseTransition(IEtherFiNode.VALIDATOR_PHASE _currentPhase, IEtherFiNode.VALIDATOR_PHASE _newPhase) external => NONDET;
    function _.moveFundsToManager(uint256 _amount) external => DISPATCHER(true);
    function _.getFullWithdrawalPayouts(IEtherFiNodesManager.ValidatorInfo _info, IEtherFiNodesManager.RewardsSplit _SRsplits) external => NONDET;
    function _.getNonExitPenalty(uint32 _tNftExitRequestTimestamp, uint32 _bNftExitRequestTimestamp) external => NONDET;
    // function _.callEigenPod(bytes memory data) external => NONDET;  // we might want to havoc all here
    // function _.forwardCall(address to, bytes memory data) external => NONDET;  // we might want to havoc all here
    function _.withdrawFunds(
        address _treasury, uint256 _treasuryAmount,
        address _operator, uint256 _operatorAmount,
        address _tnftHolder, uint256 _tnftAmount,
        address _bnftHolder, uint256 _bnftAmount
    ) external => DISPATCHER(true);
    function _.getRewardsPayouts(uint32 _exitRequestTimestamp, IEtherFiNodesManager.RewardsSplit _splits) external => NONDET;
    function _.numExitedValidators() external => DISPATCHER(true);
    function _.numExitRequestsByTnft() external => DISPATCHER(true);
    function _.claimQueuedWithdrawals(uint256 maxNumWithdrawals, bool _checkIfHasOutstandingEigenLayerWithdrawals) external => DISPATCHER(true);
    function _.calculateTVL(
        uint256 _beaconBalance,
        IEtherFiNodesManager.ValidatorInfo _info,
        IEtherFiNodesManager.RewardsSplit _SRsplits,
        bool _onlyWithdrawable
    ) external => NONDET;
    function _.queueRestakedWithdrawal() external => DISPATCHER(true);
    function _.updateNumExitedValidators(uint16 _up, uint16 _down) external => DISPATCHER(true);
    function _.processNodeExit() external => DISPATCHER(true);

    // test/eigenlayer-mocks/DelayedWithdrawalRouterMock.sol
    function _.claimDelayedWithdrawals(address recipient, uint256 maxNumberOfWithdrawalsToClaim) external => NONDET;  // we might want to havoc all here
    function _.getClaimableUserDelayedWithdrawals(address user) external => NONDET;
    function _.withdrawalDelayBlocks() external => NONDET;
    function _.getUserDelayedWithdrawals(address user) external => NONDET;

    // src/StakingManager.sol
    // function _.instantiateEtherFiNode(bool _createEigenPod) external => NONDET;  // we might want to havoc all here
    
    // depositContractEth2
    function _.get_deposit_root() external => NONDET;

    // src/eigenlayer-interfaces/IEigenPodManager.sol
    function _.getPod(address podOwner) external => NONDET;
    function _.createPod() external => NONDET;

    // src/eigenlayer-interfaces/IEigenPod.sol
    // function _.withdrawBeforeRestaking() external => NONDET;  // we might want to havoc all here

    // src/interfaces/IEtherFiNodesManager.sol
    function _.eigenPodManager() external => NONDET;
    function _.delayedWithdrawalRouter() external => NONDET;

    // src/NodeOperatorManager.sol
    // function isEligibleToRunValidatorsForSourceOfFund(address _operator, ILiquidityPool.SourceOfFunds _source) external view returns (bool approved) 

    // ERC721ReceiverUpgradeable.sol
    function ERC721Upgradeable._checkOnERC721Received(
        address from,
        address to,
        uint256 tokenId,
        bytes memory data
    ) internal returns (bool) => NONDET;
}

// rule ideas:

// 1. One that requested a withdrawal successfully, can withdraw his funds
//    LiquidityPool.requestWithdraw(address recipient, uint256 amount) -> WithdrawRequestNFT.claimWithdraw(uint256 tokenId)
rule oneCanWithdrawHisFunds() {
    env e1; env e2;
    address recipient; uint256 amount;
    uint256 requestId = LiquidityPool.requestWithdraw(e1, recipient, amount);

    uint256 balanceOfUser_Before = nativeBalances[e2.msg.sender];
    WithdrawRequestNFT.claimWithdraw@withrevert(e2, requestId);
    bool reverted = lastReverted;
    uint256 balanceOfUser_After = nativeBalances[e2.msg.sender];

    assert e2.msg.sender == recipient;  // only the recipient can claim the withdraw
    assert e2.msg.value == 0 => !reverted;  // unless the user send ETH the call should not fail
    assert !reverted => balanceOfUser_After > balanceOfUser_Before;  // one gets some ETH
}

// 2a. Depositing ETH increases the getTotalPooledEther()
// 2b. One cannot get zero shares for successful deposit()
// Passed - https://prover.certora.com/output/80942/d5cc0bbd8c054ab8a68c5107aee62452?anonymousKey=75aa29721ada928aa5894578b430b99710454ac3
rule depositIntegrity() {
    env e;

    uint256 totalPooledEther_Before = LiquidityPool.getTotalPooledEther();
    LiquidityPool.deposit(e);
    uint256 totalPooledEther_After = LiquidityPool.getTotalPooledEther();

    uint256 balanceOfSender = eETH.balanceOf(e.msg.sender);

    assert totalPooledEther_Before < totalPooledEther_After;
    assert balanceOfSender > 0;
}

// eETH.totalShares() and LiquidityPool.getTotalPooledEther() are correlated
rule totalSharesAndTotalPooledEtherCorrelation(method f)
    filtered { f -> f.contract == currentContract && !f.isView} {
    env e; calldataarg args;

    uint256 totalPooledEther_Before = LiquidityPool.getTotalPooledEther();
    uint256 totalShares_Before = eETH.totalShares();

        f(e,args);

    uint256 totalPooledEther_After = LiquidityPool.getTotalPooledEther();
    uint256 totalShares_After = eETH.totalShares();

    assert totalPooledEther_After > totalPooledEther_Before => totalShares_After > totalShares_Before;
    assert totalPooledEther_After < totalPooledEther_Before => totalShares_After < totalShares_Before;
    assert totalPooledEther_After == totalPooledEther_Before => totalShares_After == totalShares_Before;
}


// 6. The more msg.value one deposits, the more shares he gets
rule depositMoreGetMore() {
    env e1; env e2;
    storage initState = lastStorage;

    uint256 balanceBeforeOfSender1 = eETH.balanceOf(e1.msg.sender);
    uint256 balanceBeforeOfSender2 = eETH.balanceOf(e2.msg.sender);

    LiquidityPool.deposit(e1);
    uint256 balanceAfterOfSender1 = eETH.balanceOf(e1.msg.sender);
    mathint balanceIncreaseOfSender1 = balanceAfterOfSender1 - balanceBeforeOfSender1;

    LiquidityPool.deposit(e2) at initState;
    uint256 balanceAfterOfSender2 = eETH.balanceOf(e2.msg.sender);
    mathint balanceIncreaseOfSender2 = balanceAfterOfSender2 - balanceBeforeOfSender2;

    assert  e1.msg.value < e2.msg.value  => balanceIncreaseOfSender1 < balanceIncreaseOfSender2;
}


// 3. What are all the functions that can be run when the contract is paused
// filtered - https://prover.certora.com/output/80942/bcfa0cac53814e3c9077905696d3a8b1?anonymousKey=f98a0edf2a0a1405853e24d8d11b2fe6ac382c2b
rule whoCanRunWhenPaused(method f)
    filtered { f -> f.contract == currentContract && !f.isView} {
    env e;
    calldataarg args;

    bool isPaused = LiquidityPool.paused();
    f@withrevert(e,args);
    bool reverted = lastReverted;

    assert isPaused => reverted;
}


// 4. Who can increase the getTotalPooledEther()
// 5. Who can decrease the getTotalPooledEther()

// 7. One cannot get the same requestId after calling requestWithdraw()


// note: understand what "totalValueOutOfLp" is representing - why it is decreased on receive()? abuse by forced ETH sent?
// typo in src/LiquidityPool.sol line 548, 550 - balanace

// src/EETH.sol line 71 - Why would a user wish to burn its EETH shares?