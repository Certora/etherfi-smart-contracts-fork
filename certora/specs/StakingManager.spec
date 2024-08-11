import "./nftDispach.spec";
import "./EtherFiNodesManager.spec";

using AuctionManager as auctionManager;

methods {
    // Getters:
    function maxBatchDepositSize() external returns (uint128) envfree;
    function stakeAmount() external returns (uint128) envfree;
    function liquidityPoolContract() external returns (address) envfree;
    function bidIdToStakerInfo(uint256) external returns (address, bytes1, bytes10) envfree;
    function depositContractEth2() external returns (address) envfree;

    function initialize(address, address) external;
    function initializeOnUpgrade(address, address) external;
    function batchDepositWithBidIds(uint256[], uint256, address, address, address, bool, uint256) external returns (uint256[] memory);
    function batchCancelDeposit(uint256[], address) external;
    function batchRegisterValidators(uint256[], address, address, IStakingManager.DepositData[], address) external;
    function batchApproveRegistration(uint256[], bytes[], bytes[], bytes32[]) external;

    function _.upgradeToAndCall(address,bytes) external => NONDET;

    // Node manager summaries:
    function _.etherfiNodeAddress(uint256) external => NONDET;
    function _.updateEtherFiNode(uint256) external => NONDET;
    function _.allocateEtherFiNode(bool) external => NONDET;
    function _.registerValidator(uint256, bool, address) external => NONDET;
    function _.unregisterValidator(uint256) external => CONSTANT;
    function _.getWithdrawalCredentials(uint256) external => NONDET;
    function _.incrementNumberOfValidators(uint256) external => NONDET;

    function _.generateDepositRoot(bytes, bytes, bytes, uint256) external => NONDET;

    // roleRegistry summaries:
    // function _.hasRole(address) external => NONDET;
    // function hasRole(bytes32, address) external => NONDET;

    function auctionManager.numberOfActiveBids() external returns (uint256) envfree;
    function auctionManager.isBidActive(uint256) external returns (bool) envfree;
    function auctionManager.membershipManagerContractAddress() external returns (address) envfree;
}

// Functions filtered out since they use `delegatecall`.
definition isFilteredFunc(method f) returns bool = (
    f.selector == sig:upgradeToAndCall(address, bytes).selector
);

definition wei() returns uint256 = 1000000000000000000;

// struct DepositData {
//         bytes publicKey;
//         bytes signature;
//         bytes32 depositDataRoot;
//         string ipfsHashForEncryptedValidatorKey;
//     }

// struct StakerInfo {
//         address staker;
//         bytes1 dummy;
//         bytes10 hash;
//     }
rule whoLeaveEth(method f, address membershipAddress) 
    filtered { f -> !isFilteredFunc(f) } {
    env e;
    require membershipAddress != e.msg.sender;
    require auctionManager.membershipManagerContractAddress() == membershipAddress;
    calldataarg args;
    uint256 contractBalancePre = nativeBalances[currentContract];
        f(e,args);
    uint256 contractBalancePost = nativeBalances[currentContract];
    assert contractBalancePre == contractBalancePost;
}


rule integrityOfBatchDepositWithBidIds(uint256 bidID) {
    env e;
    uint256[] candidateBidIds = [bidID];
    uint256 numOfValidators;
    address validatorSpawner;
    address tnftHolder; 
    address bnftHolder;
    bool enableRestaking;
    uint256 validatorIds;

    address stakerBefore;
    address stakerAfter;

    // get bid information:
    bool isActiveBefore = auctionManager.isBidActive(bidID);
    stakerBefore, _, _ = bidIdToStakerInfo(bidID);

    batchDepositWithBidIds(e, candidateBidIds, numOfValidators, validatorSpawner, tnftHolder, bnftHolder, enableRestaking, validatorIds);

    bool isActiveAfter = auctionManager.isBidActive(bidID);
    stakerAfter, _, _ = bidIdToStakerInfo(bidID);

    assert (stakerBefore == 0 && isActiveBefore && numOfValidators > 0) => stakerAfter == validatorSpawner && !isActiveAfter;
}

rule integrityOfBatchCancelDeposit(uint256 validatorId, address caller) {
    env e;
    require e.msg.sender != currentContract;
    require e.msg.sender != auctionManager;
    uint256[] validatorIds = [validatorId];

    address stakerBefore;
    address stakerAfter;
    mathint ethBalanceBefore = nativeBalances[e.msg.sender];

    stakerBefore, _, _ = bidIdToStakerInfo(validatorId);

    batchCancelDeposit(e, validatorIds, caller);

    stakerAfter, _, _ = bidIdToStakerInfo(validatorId);
    mathint ethBalanceAfter = nativeBalances[e.msg.sender];
    bool isActiveAfter = auctionManager.isBidActive(validatorId);

    assert stakerBefore == caller && stakerAfter == 0, "wrong staker settings";
    assert ethBalanceAfter == ethBalanceBefore + 32, "stake didn't fully refunded";
    assert isActiveAfter, "The bid didn't reenter the auction";
}

// tokens are burned:
// TNFTInterfaceInstance.burnFromCancelBNftFlow(nftTokenId);
// BNFTInterfaceInstance.burnFromCancelBNftFlow(nftTokenId);
// no token owner
// owner nftBalance decresed by 1 for each token burned

rule batchCancelDepositFR(method f, uint256 validatorId, address caller) 
    filtered { f -> !isFilteredFunc(f)  
                && f.selector != sig:pauseContract().selector
                || f.selector != sig:instantiateEtherFiNode(bool).selector
                || f.selector != sig:initialize(address,address).selector } {
    env e;
    env eFr;
    calldataarg args;
    require eFr.msg.sender != e.msg.sender;
    require e.msg.sender != currentContract;
    require e.msg.sender != auctionManager;
    require eFr.msg.sender != currentContract;
    require eFr.msg.sender != auctionManager;
    require e.msg.sender != 0;
    require eFr.msg.sender != 0;
    uint256[] validatorIds = [validatorId];

    storage initState = lastStorage; 

    batchCancelDeposit(e, validatorIds, caller);

    f(eFr, args) at initState;

    batchCancelDeposit@withrevert(e, validatorIds, caller);

    bool didRvert = lastReverted;

    assert !didRvert;    
}

rule batchDepositFR(method f, uint256 bidID) 
    filtered { f -> !isFilteredFunc(f)  
                && f.selector != sig:pauseContract().selector
                || f.selector != sig:instantiateEtherFiNode(bool).selector
                || f.selector != sig:initialize(address,address).selector } {
    env e;
    env eFr;
    calldataarg args;
    require eFr.msg.sender != e.msg.sender;
    require e.msg.sender != currentContract;
    require e.msg.sender != auctionManager;
    require eFr.msg.sender != currentContract;
    require eFr.msg.sender != auctionManager;
    require e.msg.sender != 0;
    require eFr.msg.sender != 0;
    uint256[] candidateBidIds = [bidID];
    uint256 numOfValidators;
    address validatorSpawner;
    address tnftHolder; 
    address bnftHolder;
    bool enableRestaking;
    uint256 validatorIds;

    storage initState = lastStorage; 

    batchDepositWithBidIds(e, candidateBidIds, numOfValidators, validatorSpawner, tnftHolder, bnftHolder, enableRestaking, validatorIds);

    f(eFr, args) at initState;

    batchDepositWithBidIds@withrevert(e, candidateBidIds, numOfValidators, validatorSpawner, tnftHolder, bnftHolder, enableRestaking, validatorIds);

    bool didRvert = lastReverted;

    assert !didRvert;    
}

rule batchRegisterValidatorsFR(method f, uint256 bidID) 
    filtered { f -> !isFilteredFunc(f)  
                && f.selector != sig:pauseContract().selector
                || f.selector != sig:instantiateEtherFiNode(bool).selector
                || f.selector != sig:initialize(address,address).selector } {
    env e;
    env eFr;
    calldataarg specificArgs;
    calldataarg args;
    require eFr.msg.sender != e.msg.sender;
    require e.msg.sender != currentContract;
    require e.msg.sender != auctionManager;
    require eFr.msg.sender != currentContract;
    require eFr.msg.sender != auctionManager;
    require e.msg.sender != 0;
    require eFr.msg.sender != 0;

    storage initState = lastStorage; 

    batchRegisterValidators(e, specificArgs);

    f(eFr, args) at initState;

    batchRegisterValidators@withrevert(e, specificArgs);

    bool didRvert = lastReverted;

    assert !didRvert;    
}

rule batchApproveRegistrationFR(method f, uint256 bidID) 
    filtered { f -> !isFilteredFunc(f)  
                && f.selector != sig:pauseContract().selector
                || f.selector != sig:instantiateEtherFiNode(bool).selector
                || f.selector != sig:initialize(address,address).selector } {
    env e;
    env eFr;
    calldataarg args;
    calldataarg specificArgs;
    require eFr.msg.sender != e.msg.sender;
    require e.msg.sender != currentContract;
    require e.msg.sender != auctionManager;
    require eFr.msg.sender != currentContract;
    require eFr.msg.sender != auctionManager;
    require e.msg.sender != 0;
    require eFr.msg.sender != 0;

    storage initState = lastStorage; 

    batchApproveRegistration(e, specificArgs);

    f(eFr, args) at initState;

    batchApproveRegistration@withrevert(e, specificArgs);

    bool didRvert = lastReverted;

    assert !didRvert;    
}

rule integrityOfBatchRegisterValidators(uint256 validatorId) {
    env e;
    uint256 value = e.msg.value; // == wei() * validatorIds.length
    uint256[] validatorIds = [validatorId];
    address bNftRecipient;
    address tNftRecipient;
    IStakingManager.DepositData[] depositData;
    address validatorSpawner;

    // LiquidityPool requirements:
    require depositData.length == validatorIds.length;

    uint256 contractBalancePre = nativeBalances[currentContract];

    batchRegisterValidators(e, validatorIds, bNftRecipient, tNftRecipient, depositData, validatorSpawner);

    uint8 _validatorPhase = validatorPhase[validatorId];
    uint256 contractBalancePost = nativeBalances[currentContract];

    // assert validator phase:
    assert _validatorPhase == 2 || _validatorPhase == 8;
    // processAuctionFeeTransfer
    // NFTS are correctly minted.
}

rule integrityOfBatchApproveRegistration(uint256 validatorId) {
    env e;
    uint256 val = e.msg.value;
    uint256[] validatorIds = [validatorId];
    bytes[] pubKey;
    bytes[] signature;
    bytes32[] depositDataRootApproval;

    // LiquidityPool requirements:
    require validatorIds.length == pubKey.length;
    require validatorIds.length == signature.length;

    batchApproveRegistration(e, validatorIds, pubKey, signature, depositDataRootApproval);

    uint8 _validatorPhase = validatorPhase[validatorId];

    // assert validator phase:
    satisfy true;
}


