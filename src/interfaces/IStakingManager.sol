// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "./ILiquidityPool.sol";

interface IStakingManager {
    struct DepositData {
        bytes publicKey;
        bytes signature;
        bytes32 depositDataRoot;
        string ipfsHashForEncryptedValidatorKey;
    }

    struct StakerInfo {
        address staker;
        bytes1 dummy;
        bytes10 hash;
    }

    function bidIdToStaker(uint256 id) external view returns (address);

    function getEtherFiNodeBeacon() external view returns (address);

    function initialize(address _auctionAddress, address _depositContractAddress) external;
    function setEtherFiNodesManagerAddress(address _managerAddress) external;
    function setLiquidityPoolAddress(address _liquidityPoolAddress) external;
    
    function batchDepositWithBidIds(uint256[] calldata _candidateBidIds, uint256 _numberOfValidators, address _staker, address _tnftHolder, address _bnftHolder, bool _enableRestaking, uint256 _validatorIdToCoUseWithdrawalSafe) external returns (uint256[] memory);
    function batchRegisterValidators(uint256[] calldata _validatorId, address _bNftRecipient, address _tNftRecipient, DepositData[] calldata _depositData, address _user) external payable;
    function batchApproveRegistration(uint256[] memory _validatorId, bytes[] calldata _pubKey, bytes[] calldata _signature, bytes32[] calldata _depositDataRootApproval) external payable;
    function batchCancelDeposit(uint256[] calldata _validatorIds, address _caller) external;

    function instantiateEtherFiNode(bool _createEigenPod) external returns (address);
}
