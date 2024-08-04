using AuctionManager as auctionManager;
methods {
    // Getters:
    function maxBatchDepositSize() external returns (uint128) envfree;
    function stakeAmount() external returns (uint128) envfree;
    function liquidityPoolContract() external returns (address) envfree;
    function bidIdToStakerInfo(uint256) external returns (address, bytes1, bytes10) envfree;

    function initialize(address, address) external;
    function initializeOnUpgrade(address, address) external;
    function batchDepositWithBidIds(uint256[], uint256, address, address, address, bool, uint256) external returns (uint256[] memory);
    function batchCancelDeposit(uint256[], address) external;
    function batchRegisterValidators(uint256[], address, address, IStakingManager.DepositData[], address) external;
    function batchApproveRegistration(uint256[], bytes[], bytes[], bytes32[]) external;

    function _.upgradeToAndCall(address,bytes) external => NONDET;
    function _.ownerOf(uint256 tokenId) external => DISPATCHER(true);

    // Auction manager summaries:
    function _.etherfiNodeAddress(uint256) external => NONDET;
    function _.updateEtherFiNode(uint256) external => NONDET;
    function _.allocateEtherFiNode(bool) external => NONDET;
    function _.registerValidator(uint256, bool, address) external => NONDET;

    function auctionManager.numberOfActiveBids() external returns (uint256) envfree;
    function auctionManager.isBidActive(uint256) external returns (bool) envfree;
}
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
    bool isActive = auctionManager.isBidActive(bidID);
    stakerBefore, _, _ = bidIdToStakerInfo(bidID);

    batchDepositWithBidIds(e, candidateBidIds, numOfValidators, validatorSpawner, tnftHolder, bnftHolder, enableRestaking, validatorIds);

    stakerAfter, _, _ = bidIdToStakerInfo(bidID);

    assert (stakerBefore == 0 && isActive && numOfValidators > 0) => stakerAfter == validatorSpawner;
}

rule integrityOfBatchCancelDeposit(uint256 validatorId, address caller) {
    env e;
    uint256[] validatorIds = [validatorId];

    address stakerBefore;
    address stakerAfter;

    stakerBefore, _, _ = bidIdToStakerInfo(validatorId);

    batchCancelDeposit(e, validatorIds, caller);

    stakerAfter, _, _ = bidIdToStakerInfo(validatorId);

    assert stakerBefore == caller && stakerAfter == 0;
}

rule integrityOfBatchRegisterValidators(uint256 validatorId) {
    env e;
    uint256 val = e.msg.value;
    uint256[] validatorIds = [validatorId];
    address bNftRecipient;
    address tNftRecipient;
    IStakingManager.DepositData[] depositData;
    address validatorSpawner;

    batchRegisterValidators(e, validatorIds, bNftRecipient, tNftRecipient, depositData, validatorSpawner);

    satisfy true;
}

rule integrityOfBatchApproveRegistration(uint256 validatorId) {
    env e;
    uint256 val = e.msg.value;
    uint256[] validatorIds = [validatorId];
    bytes[] pubKey;
    bytes[] signature;
    bytes32[] depositDataRootApproval;

    batchApproveRegistration(e, validatorIds, pubKey, signature, depositDataRootApproval);

    satisfy true;
}
