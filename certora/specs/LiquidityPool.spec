// All rules so far:
// https://prover.certora.com/output/80942/4ce63acc04c0403fba93bea63085a12d?anonymousKey=acd81edbc58200fa096acd6d0cdf4039fdbe1090

using EETH as eETH;
using LiquidityPool as LiquidityPool;
using WithdrawRequestNFT as WithdrawRequestNFT;

// use builtin rule sanity filtered { f -> f.contract == currentContract};

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

// invariant LiquidityPool.getTotalPooledEther() >= eETH.totalShares()
// Failed - filtered - https://prover.certora.com/output/80942/57d3c1e81b564ab9812bb3736e4356d7?anonymousKey=34a5d17475c8cc44bff1b1532c789ec5f21adaaf
invariant totalPooledEtherMETotalShares()
    LiquidityPool.getTotalPooledEther() >= eETH.totalShares()
    filtered { f -> f.contract == currentContract && !f.isView}



// 1. One that requested a withdrawal successfully, can withdraw his funds
//    step 1: LiquidityPool.requestWithdraw(address recipient, uint256 amount)
//    step 2: WithdrawRequestNFT.finalizeRequests(uint256 requestId)
//    step 3: WithdrawRequestNFT.claimWithdraw(uint256 tokenId)
// Verified - https://prover.certora.com/output/80942/4110c6f01dd146589020689f265dea02?anonymousKey=3889e0a74421c7259d4ce59ff30a97068c3988c8
// Should not revert - Failed - https://prover.certora.com/output/80942/fdcf97f747ca483cb39643ff2a5f49d4?anonymousKey=94fca261acecc70f15e1c3fb5620f795aa37cecd
rule oneCanWithdrawHisFunds() {
    requireInvariant totalPooledEtherMETotalShares;
    env e1; env e2; env e3;
    address recipient; uint256 amount;
    uint256 requestId = LiquidityPool.requestWithdraw(e1, recipient, amount);  // step 1
    WithdrawRequestNFT.finalizeRequests(e2, requestId);  // step 2: admin must first finalize the request

    uint256 balanceOfUser_Before = nativeBalances[e3.msg.sender];
    WithdrawRequestNFT.claimWithdraw@withrevert(e3, requestId);  // step 3
    bool reverted = lastReverted;
    uint256 balanceOfUser_After = nativeBalances[e3.msg.sender];

    assert !reverted => e3.msg.sender == recipient;  // only the recipient can claim the withdraw
    assert !reverted => balanceOfUser_After > balanceOfUser_Before;  // one gets some ETH
    assert e3.msg.value == 0 && e3.msg.sender == recipient && e3.msg.sender != LiquidityPool => !reverted;  // correct call (msg.value == 0) by the correct NFT owner should not revert
}

// 2a. Depositing ETH increases the getTotalPooledEther()
// 2b. One cannot get zero shares for successful deposit()
// with invariant - Pass - https://prover.certora.com/output/80942/6a98b7b79412466494ec1872cba323ac?anonymousKey=312d272f9191b71db197bb646f49bd78786c13d2
// with invariant - Running - https://prover.certora.com/output/80942/666a18a94b1a4f348220f3e99874d397?anonymousKey=4167ca5da1455aa345ec6af148997062c6436b0d
rule depositIntegrity() {
    requireInvariant totalPooledEtherMETotalShares;
    env e;

    uint256 totalPooledEther_Before = LiquidityPool.getTotalPooledEther();
    uint256 balanceOfSender_Before = eETH.balanceOf(e.msg.sender);
    LiquidityPool.deposit(e);
    uint256 totalPooledEther_After = LiquidityPool.getTotalPooledEther();
    uint256 balanceOfSender_After = eETH.balanceOf(e.msg.sender);

    assert totalPooledEther_Before < totalPooledEther_After;
    assert balanceOfSender_Before < balanceOfSender_After;
}

// 3. eETH.totalShares() and LiquidityPool.getTotalPooledEther() are correlated
// Failed - with invariant - https://prover.certora.com/output/80942/e9b14f1594d7464e9bc3149531283cb2?anonymousKey=b20a0ef5c9746fce4f90090604967fa520e1e7b1
rule totalSharesAndTotalPooledEtherCorrelation(method f)
    filtered { f -> f.contract == currentContract && !f.isView} {
    requireInvariant totalPooledEtherMETotalShares;
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


// 4. The more msg.value one deposits, the more shares he gets
// Failed - https://prover.certora.com/output/80942/e9df9a5d210c4cb79f43c226bd9e38db?anonymousKey=42e3ddf926eda3fb007921e6eb6c8870c0ffa524
// Failed - should investigate for a bug - https://prover.certora.com/output/80942/be222d29f1e84ceaa00ca06172330c9d?anonymousKey=3f32c0f24185be43844a5ab7b5a4afd0da32dc8d
// Failed - with invariant - https://prover.certora.com/output/80942/67b1d4811b864d5eb62e0e7acefffebd?anonymousKey=c8d9c451ace6dced95afb29e4df30d5de98bd80c
// Failed - sender != LiquidityPool - https://prover.certora.com/output/80942/6bc6ae1e6c184ac3b42a11ba05666c0d?anonymousKey=a584dbe9a86798a63dab2e38f3eda70bc6489cef
rule depositMoreGetMore() {
    requireInvariant totalPooledEtherMETotalShares;
    env e1; env e2;
    require e1.msg.sender != LiquidityPool;  // external function cannot be called by the same contract
    require e2.msg.sender != LiquidityPool;  // external function cannot be called by the same contract

    storage initState = lastStorage;

    uint256 balanceBeforeOfSender1 = eETH.balanceOf(e1.msg.sender);
    uint256 balanceBeforeOfSender2 = eETH.balanceOf(e2.msg.sender);

    LiquidityPool.deposit(e1);
    uint256 balanceAfterOfSender1 = eETH.balanceOf(e1.msg.sender);
    mathint balanceIncreaseOfSender1 = balanceAfterOfSender1 - balanceBeforeOfSender1;

    LiquidityPool.deposit(e2) at initState;
    uint256 balanceAfterOfSender2 = eETH.balanceOf(e2.msg.sender);
    mathint balanceIncreaseOfSender2 = balanceAfterOfSender2 - balanceBeforeOfSender2;

    assert  e1.msg.value == e2.msg.value  => balanceIncreaseOfSender1 == balanceIncreaseOfSender2;
    assert  e1.msg.value < e2.msg.value  => balanceIncreaseOfSender1 <= balanceIncreaseOfSender2;
}


// 5. What are all the functions that can be paused
// filtered - https://prover.certora.com/output/80942/bcfa0cac53814e3c9077905696d3a8b1?anonymousKey=f98a0edf2a0a1405853e24d8d11b2fe6ac382c2b
// Running - https://prover.certora.com/output/80942/417ce13c8a0f4b4dabd758e3d27fcc12?anonymousKey=28d879fd6fada5a1608b2a0f04afe634e43924d7
rule whoCanBePaused(method f)
    filtered { f -> f.contract == currentContract && !f.isView} {
    env e;
    calldataarg args;

    bool isPaused = LiquidityPool.paused();
    f@withrevert(e,args);
    bool reverted = lastReverted;

    assert isPaused => reverted;
}


// 6. Who can increase the getTotalPooledEther()
// https://prover.certora.com/output/80942/8b5a118c5ec84df780d569962d0dd9f2?anonymousKey=bd8f29f4116b12da37c0406733da7944c961b88c
rule whoCanIncreaseTotalPooledEther(method f)
    filtered { f -> f.contract == currentContract && !f.isView} {
    env e; calldataarg args;

    uint256 totalPooledEther_Before = LiquidityPool.getTotalPooledEther();
    f(e,args);
    uint256 totalPooledEther_After = LiquidityPool.getTotalPooledEther();

    satisfy totalPooledEther_Before < totalPooledEther_After;
}

// 7. Who can decrease the getTotalPooledEther()
// https://prover.certora.com/output/80942/6b71ad9f85fd4baebed3a7c9349144dc?anonymousKey=09efdec159a2da8a870ce37026d7f64b5195e61f
rule whoCanDecreaseTotalPooledEther(method f)
    filtered { f -> f.contract == currentContract && !f.isView} {
    env e; calldataarg args;

    uint256 totalPooledEther_Before = LiquidityPool.getTotalPooledEther();
    f(e,args);
    uint256 totalPooledEther_After = LiquidityPool.getTotalPooledEther();

    satisfy totalPooledEther_Before > totalPooledEther_After;
}

// 8. One cannot get the same requestId after calling requestWithdraw()
// Passed - https://prover.certora.com/output/80942/80dc7fcabd274d8599354214892bb3e9?anonymousKey=225d25416646a64f6f573d1bd6380ed930ceec3d
rule requestIdIsUnique() {
    env e1; env e2; env e3;
    address recipient1; uint256 amount1;
    uint256 requestId1 = LiquidityPool.requestWithdraw(e1, recipient1, amount1);

    address recipient2; uint256 amount2;
    uint256 requestId2 = LiquidityPool.requestWithdraw(e2, recipient2, amount2);

    assert requestId1 < requestId2;    
}


// sanity with filtering
// Passed - https://prover.certora.com/output/80942/393a7796c05c4d9c91b8bd0f3bb4a132?anonymousKey=1b99dde6d8b821cf514480d298c483a1d3800060
rule sanityLocal(method f)
    filtered { f -> f.contract == currentContract && !f.isView} {
    env e; calldataarg args;
    f(e,args);
    satisfy true;
}


// note: understand what "totalValueOutOfLp" is representing - why it is decreased on receive()? abuse by forced ETH sent?
// typo in src/LiquidityPool.sol line 548, 550 - balanace

// src/EETH.sol line 71 - Why would a user wish to burn its EETH shares?