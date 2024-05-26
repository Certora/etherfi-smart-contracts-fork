using EETH as eETH;
using LiquidityPool as LiquidityPool;

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
    // function _.migrateVersion(uint256, IEtherFiNodesManager.ValidatorInfo memory) external => DISPATCHER(true);
    function _.migrateVersion(uint256 _validatorId, IEtherFiNodesManager.ValidatorInfo _info) external => NONDET;
    function _.updateNumExitRequests(uint16 _up, uint16 _down) external => DISPATCHER(true);
    function _.numAssociatedValidators() external => NONDET;
    function _.unRegisterValidator(uint256 _validatorId, IEtherFiNodesManager.ValidatorInfo _info) external => DISPATCHER(true);
    function _.registerValidator(uint256 _validatorId, bool _enableRestaking) external => DISPATCHER(true);
    function _.eigenPod() external => NONDET;
    function _.isRestakingEnabled() external => NONDET;
    function _.updateNumberOfAssociatedValidators(uint16 _up, uint16 _down) external => DISPATCHER(true);
    function _.validatePhaseTransition(IEtherFiNode.VALIDATOR_PHASE _currentPhase, IEtherFiNode.VALIDATOR_PHASE _newPhase) external => NONDET;

    // src/StakingManager.sol
    function _.instantiateEtherFiNode(bool _createEigenPod) external => NONDET;  // we might want to havoc all here
    
    // depositContractEth2
    function _.get_deposit_root() external => NONDET;

    // src/eigenlayer-interfaces/IEigenPodManager.sol
    function _.getPod(address podOwner) external => NONDET;
    function _.createPod() external => NONDET;

    // src/interfaces/IEtherFiNodesManager.sol
    function _.eigenPodManager() external => NONDET;

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
// Running - https://prover.certora.com/output/80942/2f2249c7db39465a9b4766dc8c6ea5a0?anonymousKey=377fee6010e423a3471f23395b9182705a7a84d3
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
// failed - https://prover.certora.com/output/80942/b562bf4a407245dc8bc0702872d4b983?anonymousKey=129c043bf399da67995d48126e605de946e9c933
// failed - https://prover.certora.com/output/80942/a254fb8858b247b380e93211f26f428d?anonymousKey=548464a7a47afe6ece046e63353a8480df84e5dc
// 
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
// bad? - https://prover.certora.com/output/80942/bc4f398231404337a9f0250986b2e7d7?anonymousKey=92ba99bddf1c1b74c0365620cf91ce9ea6fc370a
// fixed? - https://prover.certora.com/output/80942/31b3b07eb5f44ddda1c76195ac348fb0?anonymousKey=2b44c6bdb34375e10998d5f802cdbd3b07f3b898
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