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
    function batchDepositWithBidIds(uint256[], uint256, address, address, bool, uint256) external returns (uint256[] memory);
    function batchCancelDeposit(uint256[], address) external;
    function batchRegisterValidators(uint256[], address, address, IStakingManager.DepositData[]) external;
    function batchApproveRegistration(uint256[], bytes[], bytes[], bytes32[]) external;

    function _.upgradeToAndCall(address,bytes) external => NONDET;

    // Node manager summaries:
    function _.etherfiNodeAddress(uint256) external => NONDET;
    function _.updateEtherFiNode(uint256) external => NONDET;
    function _.allocateEtherFiNode(bool) external => NONDET;
    function _.registerValidator(uint256, bool, address) external => NONDET;
    function _.unregisterValidator(uint256) external => CONSTANT;
    function _.getWithdrawalCredentials(uint256) external => NONDET;
    function _.incrementNumberOfValidators(uint64) external => NONDET;
    function _.generateDepositRoot(bytes, bytes, bytes, uint256) external => NONDET;

    function auctionManager.numberOfActiveBids() external returns (uint256) envfree;
    function auctionManager.isBidActive(uint256) external returns (bool) envfree;
    function auctionManager.membershipManagerContractAddress() external returns (address) envfree;
    function auctionManager.processAuctionFeeTransfer(uint256) external => NONDET;
}

// Functions filtered out since they use `delegatecall`.
definition isFilteredFunc(method f) returns bool = (
    f.selector == sig:upgradeToAndCall(address, bytes).selector
);

definition wei() returns uint256 = 1000000000000000000;

// rule for research purpose.
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
    address tnftHolder; 
    address bnftHolder;
    bool enableRestaking;
    uint256 validatorIds;

    address stakerBefore;
    address stakerAfter;

    // get bid information:
    bool isActiveBefore = auctionManager.isBidActive(bidID);
    stakerBefore, _, _ = bidIdToStakerInfo(bidID);

    batchDepositWithBidIds(e, candidateBidIds, numOfValidators, tnftHolder, bnftHolder, enableRestaking, validatorIds);

    bool isActiveAfter = auctionManager.isBidActive(bidID);
    stakerAfter, _, _ = bidIdToStakerInfo(bidID);

    assert (stakerBefore == 0 && isActiveBefore && numOfValidators > 0) => stakerAfter == bnftHolder && !isActiveAfter;
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
    uint8 phasePre = validatorPhase[validatorId];
    mathint tnftAmountPre = sumAllTNFT;
    mathint bnftAmountPre = sumAllBNFT;

    batchCancelDeposit(e, validatorIds, caller);

    stakerAfter, _, _ = bidIdToStakerInfo(validatorId);
    mathint ethBalanceAfter = nativeBalances[e.msg.sender];
    bool isActiveAfter = auctionManager.isBidActive(validatorId);
    mathint tnftAmountPost = sumAllTNFT;
    mathint bnftAmountPost = sumAllBNFT;

    assert stakerBefore == caller && stakerAfter == 0, "wrong staker settings";
    assert liquidityPoolContract() != e.msg.sender => ethBalanceAfter == ethBalanceBefore + 32, "stake didn't fully refunded";
    assert isActiveAfter, "The bid didn't reenter the auction";
    assert phasePre == 8 => (tnftAmountPost == tnftAmountPre - 1) &&
                            (bnftAmountPost == bnftAmountPre - 1), "nfts wasn't burned when pre validator phase was WAITING_FOR_APPROVAL";
    assert phasePre == 8 => bnft.ownerOf(e, validatorId) == 0 && tnft.ownerOf(e, validatorId) == 0, "wrong nfts were burned";
}

rule integrityOfBatchRegisterValidators(uint256 validatorId) {
    env e;
    require e.msg.sender != currentContract;
    uint256 value = e.msg.value; // == wei() * validatorIds.length
    uint256[] validatorIds = [validatorId];
    address bNftRecipient;
    address tNftRecipient;
    IStakingManager.DepositData[] depositData;

    // LiquidityPool requirements:
    require depositData.length == validatorIds.length;

    uint256 contractBalancePre = nativeBalances[currentContract];
    mathint tnftAmountPre = sumAllTNFT;
    mathint bnftAmountPre = sumAllBNFT;

    batchRegisterValidators(e, validatorIds, bNftRecipient, tNftRecipient, depositData);

    uint8 _validatorPhase = validatorPhase[validatorId];
    uint256 contractBalancePost = nativeBalances[currentContract];
    mathint tnftAmountPost = sumAllTNFT;
    mathint bnftAmountPost = sumAllBNFT;

    // assert validator phase:
    assert _validatorPhase == 2 || _validatorPhase == 8;
    // processAuctionFeeTransfer - not needed, covered by auctionManager spec.
    // NFTS are correctly minted.
    assert contractBalancePre == contractBalancePost, "eth was left in the contract";
    assert tnftAmountPost == tnftAmountPre + 1, "tnft wasn't minted";
    assert bnftAmountPost == bnftAmountPre + 1, "bnft wasn't minted";
    assert tnft.ownerOf(e, validatorId) == tNftRecipient, "tnft was minted for the wrong user";
    assert bnft.ownerOf(e, validatorId) == bNftRecipient, "bnft was minted for the wrong user";
}
