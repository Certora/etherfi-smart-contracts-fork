// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/draft-IERC20Permit.sol";

import "@openzeppelin-upgradeable/contracts/token/ERC20/IERC20Upgradeable.sol";
import "@openzeppelin-upgradeable/contracts/token/ERC721/IERC721ReceiverUpgradeable.sol";
import "@openzeppelin-upgradeable/contracts/proxy/utils/Initializable.sol";
import "@openzeppelin-upgradeable/contracts/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin-upgradeable/contracts/access/OwnableUpgradeable.sol";

import "./interfaces/IRegulationsManager.sol";
import "./interfaces/IStakingManager.sol";
import "./interfaces/IEtherFiNodesManager.sol";
import "./interfaces/IeETH.sol";
import "./interfaces/IStakingManager.sol";
import "./interfaces/IMembershipManager.sol";
import "./interfaces/ITNFT.sol";
import "./interfaces/IWithdrawRequestNFT.sol";
import "./interfaces/ILiquidityPool.sol";
import "./interfaces/IEtherFiAdmin.sol";
import "./interfaces/IAuctionManager.sol";
import "./interfaces/ILiquifier.sol";
import "./interfaces/IPausable.sol";


contract LiquidityPool is Initializable, OwnableUpgradeable, UUPSUpgradeable, ILiquidityPool, IPausable {
    //--------------------------------------------------------------------------------------
    //---------------------------------  STATE-VARIABLES  ----------------------------------
    //--------------------------------------------------------------------------------------

    IStakingManager public stakingManager;
    IEtherFiNodesManager public nodesManager;
    IRegulationsManager public DEPRECATED_regulationsManager;
    IMembershipManager public membershipManager;
    ITNFT public tNft;
    IeETH public eETH; 

    bool public DEPRECATED_eEthliquidStakingOpened;

    uint128 public totalValueOutOfLp;
    uint128 public totalValueInLp;

    address public DEPRECATED_admin;

    uint32 public numPendingDeposits; // number of validator deposits, which needs 'registerValidator'

    address public DEPRECATED_bNftTreasury;
    IWithdrawRequestNFT public withdrawRequestNFT;

    BnftHolder[] public bnftHolders;
    uint128 public DEPRECATED_maxValidatorsPerOwner;
    uint128 public DEPRECATED_schedulingPeriodInSeconds;

    HoldersUpdate public DEPRECATED_holdersUpdate;

    mapping(address => bool) public DEPRECATED_admins;
    mapping(SourceOfFunds => FundStatistics) public DEPRECATED_fundStatistics;
    mapping(uint256 => bytes32) public depositDataRootForApprovalDeposits;
    address public etherFiAdminContract;
    bool public DEPRECATED_whitelistEnabled;
    mapping(address => bool) public DEPRECATED_whitelisted;
    mapping(address => BnftHoldersIndex) public bnftHoldersIndexes;

    bool public restakeBnftDeposits;
    uint128 public ethAmountLockedForWithdrawal;
    bool public paused;
    IAuctionManager public auctionManager;
    ILiquifier public liquifier;

    bool private isLpBnftHolder;

    RoleRegistry public roleRegistry;

    //--------------------------------------------------------------------------------------
    //-------------------------------------  ROLES  ---------------------------------------
    //--------------------------------------------------------------------------------------

    bytes32 public constant LIQUIDITY_POOL_ADMIN_ROLE = keccak256("LIQUIDITY_POOL_ADMIN_ROLE");

    //--------------------------------------------------------------------------------------
    //-------------------------------------  EVENTS  ---------------------------------------
    //--------------------------------------------------------------------------------------

    event Paused(address account);
    event Unpaused(address account);

    event Deposit(address indexed sender, uint256 amount, SourceOfFunds source, address referral);
    event Withdraw(address indexed sender, address recipient, uint256 amount, SourceOfFunds source);
    event UpdatedWhitelist(address userAddress, bool value);
    event BnftHolderDeregistered(address user, uint256 index);
    event BnftHolderRegistered(address user, uint256 index);
    event UpdatedSchedulingPeriod(uint128 newPeriodInSeconds);
    event ValidatorRegistered(uint256 indexed validatorId, bytes signature, bytes pubKey, bytes32 depositRoot);
    event ValidatorApproved(uint256 indexed validatorId);
    event ValidatorRegistrationCanceled(uint256 indexed validatorId);
    event Rebase(uint256 totalEthLocked, uint256 totalEEthShares);
    event WhitelistStatusUpdated(bool value);

    error IncorrectCaller();
    error InvalidAmount();
    error InvalidParams();
    error DataNotSet();
    error InsufficientLiquidity();
    error SendFail();
    error IncorrectRole();

    //--------------------------------------------------------------------------------------
    //----------------------------  STATE-CHANGING FUNCTIONS  ------------------------------
    //--------------------------------------------------------------------------------------

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    receive() external payable {
        if (msg.value > type(uint128).max) revert InvalidAmount();
        totalValueOutOfLp -= uint128(msg.value);
        totalValueInLp += uint128(msg.value);
    }

    function initialize(address _eEthAddress, address _stakingManagerAddress, address _nodesManagerAddress, address _membershipManagerAddress, address _tNftAddress, address _etherFiAdminContract, address _withdrawRequestNFT) external initializer {
        if (_eEthAddress == address(0) || _stakingManagerAddress == address(0) || _nodesManagerAddress == address(0) || _membershipManagerAddress == address(0) || _tNftAddress == address(0)) revert DataNotSet();
        
        __Ownable_init();
        __UUPSUpgradeable_init();
        eETH = IeETH(_eEthAddress);
        stakingManager = IStakingManager(_stakingManagerAddress);
        nodesManager = IEtherFiNodesManager(_nodesManagerAddress);
        membershipManager = IMembershipManager(_membershipManagerAddress);
        tNft = ITNFT(_tNftAddress);
        paused = true;
        restakeBnftDeposits = false;
        ethAmountLockedForWithdrawal = 0;
        etherFiAdminContract = _etherFiAdminContract;
        withdrawRequestNFT = IWithdrawRequestNFT(_withdrawRequestNFT);
        DEPRECATED_admins[_etherFiAdminContract] = true;
        isLpBnftHolder = false;
    }

    function initializeOnUpgrade(address _auctionManager, address _liquifier) external onlyOwner { 
        require(_auctionManager != address(0) && _liquifier != address(0), "Invalid params");

        auctionManager = IAuctionManager(_auctionManager);
        liquifier = ILiquifier(_liquifier);
    }

    function initializeV2dot5(address _roleRegistry) external onlyOwner {
        require(address(roleRegistry) == address(0x00), "already initialized");
        
        // TODO: compile list of values in DEPRECATED_admins to clear out
        roleRegistry = RoleRegistry(_roleRegistry);
    }

    // Used by eETH staking flow
    function deposit() external payable returns (uint256) {
        return deposit(address(0));
    }

    // Used by eETH staking flow
    function deposit(address _referral) public payable whenNotPaused returns (uint256) {
        emit Deposit(msg.sender, msg.value, SourceOfFunds.EETH, _referral);

        return _deposit(msg.sender, msg.value, 0);
    }

    // Used by eETH staking flow through Liquifier contract; deVamp
    function depositToRecipient(address _recipient, uint256 _amount, address _referral) public whenNotPaused returns (uint256) {
        require(msg.sender == address(liquifier), "Incorrect Caller");

        emit Deposit(_recipient, _amount, SourceOfFunds.EETH, _referral);

        return _deposit(_recipient, 0, _amount);
    }

    // Used by ether.fan staking flow
    function deposit(address _user, address _referral) external payable whenNotPaused returns (uint256) {
        require(msg.sender == address(membershipManager), "Incorrect Caller");

        emit Deposit(msg.sender, msg.value, SourceOfFunds.ETHER_FAN, _referral);

        return _deposit(msg.sender, msg.value, 0);
    }

    /// @notice withdraw from pool
    /// @dev Burns user share from msg.senders account & Sends equivalent amount of ETH back to the recipient
    /// @param _recipient the recipient who will receives the ETH
    /// @param _amount the amount to withdraw from contract
    /// it returns the amount of shares burned
    function withdraw(address _recipient, uint256 _amount) external whenNotPaused returns (uint256) {
        uint256 share = sharesForWithdrawalAmount(_amount);
        require(msg.sender == address(withdrawRequestNFT) || msg.sender == address(membershipManager), "Incorrect Caller");
        if (totalValueInLp < _amount || (msg.sender == address(withdrawRequestNFT) && ethAmountLockedForWithdrawal < _amount) || eETH.balanceOf(msg.sender) < _amount) revert InsufficientLiquidity();
        if (_amount > type(uint128).max || _amount == 0 || share == 0) revert InvalidAmount();

        totalValueInLp -= uint128(_amount);
        if (msg.sender == address(withdrawRequestNFT)) {
            ethAmountLockedForWithdrawal -= uint128(_amount);
        }

        eETH.burnShares(msg.sender, share);

        _sendFund(_recipient, _amount);

        return share;
    }

    /// @notice request withdraw from pool and receive a WithdrawRequestNFT
    /// @dev Transfers the amount of eETH from msg.senders account to the WithdrawRequestNFT contract & mints an NFT to the msg.sender
    /// @param recipient address that will be issued the NFT
    /// @param amount requested amount to withdraw from contract
    /// @return uint256 requestId of the WithdrawRequestNFT
    function requestWithdraw(address recipient, uint256 amount) public whenNotPaused returns (uint256) {
        uint256 share = sharesForAmount(amount);
        if (amount > type(uint96).max || amount == 0 || share == 0) revert InvalidAmount();

        // transfer shares to WithdrawRequestNFT contract from this contract
        eETH.transferFrom(msg.sender, address(withdrawRequestNFT), amount);

        uint256 requestId = withdrawRequestNFT.requestWithdraw(uint96(amount), uint96(share), recipient, 0);
       
        emit Withdraw(msg.sender, recipient, amount, SourceOfFunds.EETH);

        return requestId;
    }

    /// @notice request withdraw from pool with signed permit data and receive a WithdrawRequestNFT
    /// @dev accepts PermitInput signed data to approve transfer of eETH (EIP-2612) so withdraw request can happen in 1 tx
    /// @param _owner address that will be issued the NFT
    /// @param _amount requested amount to withdraw from contract
    /// @param _permit signed permit data to approve transfer of eETH
    /// @return uint256 requestId of the WithdrawRequestNFT
    function requestWithdrawWithPermit(address _owner, uint256 _amount, PermitInput calldata _permit)
        external
        whenNotPaused
        returns (uint256)
    {
        eETH.permit(msg.sender, address(this), _permit.value, _permit.deadline, _permit.v, _permit.r, _permit.s);
        return requestWithdraw(_owner, _amount);
    }

    /// @notice request withdraw of some or all of the eETH backing a MembershipNFT and receive a WithdrawRequestNFT
    /// @dev Transfers the amount of eETH from MembershipManager to the WithdrawRequestNFT contract & mints an NFT to the recipient
    /// @param recipient address that will be issued the NFT
    /// @param amount requested amount to withdraw from contract
    /// @param fee the burn fee to be paid by the recipient when the withdrawal is claimed (WithdrawRequestNFT.claimWithdraw)
    /// @return uint256 requestId of the WithdrawRequestNFT
    function requestMembershipNFTWithdraw(address recipient, uint256 amount, uint256 fee) public whenNotPaused returns (uint256) {
        if (msg.sender != address(membershipManager)) revert IncorrectCaller();
        uint256 share = sharesForAmount(amount);
        if (amount > type(uint96).max || amount == 0 || share == 0) revert InvalidAmount();

        // transfer shares to WithdrawRequestNFT contract
        eETH.transferFrom(msg.sender, address(withdrawRequestNFT), amount);

        uint256 requestId = withdrawRequestNFT.requestWithdraw(uint96(amount), uint96(share), recipient, fee);

        emit Withdraw(msg.sender, recipient, amount, SourceOfFunds.ETHER_FAN);

        return requestId;
    }

    // [Liquidty Pool Staking flow]
    // Step 1: [Deposit] initiate spinning up the validators & allocate withdrawal safe contracts
    // Step 2: create the keys using the desktop app
    // Step 3: [Register] register the validator keys sending 1 ETH to the eth deposit contract
    // Step 4: wait for the oracle to approve and send the rest 31 ETH to the eth deposit contract

    /// Step 1. [Deposit]
    /// @param _candidateBidIds validator IDs that have been matched with the BNFT holder on the FE
    /// @param _numberOfValidators how many validators the user wants to spin up. This can be less than the candidateBidIds length. 
    ///         we may have more Ids sent in than needed to spin up incase some ids fail.
    function batchDeposit(uint256[] calldata _candidateBidIds, uint256 _numberOfValidators) public payable whenNotPaused returns (uint256[] memory) {
        return batchDeposit(_candidateBidIds, _numberOfValidators, 0);
    }

    /// @param _candidateBidIds validator IDs that have been matched with the BNFT holder on the FE
    /// @param _numberOfValidators how many validators the user wants to spin up. This can be less than the candidateBidIds length. 
    ///         we may have more Ids sent in than needed to spin up incase some ids fail.
    /// @param _validatorIdToShareSafeWith The validator ID of the validator that the user wants to shafe the withdrawal safe with
    /// @return Array of bids that were successfully processed.
    function batchDeposit(uint256[] calldata _candidateBidIds, uint256 _numberOfValidators, uint256 _validatorIdToShareSafeWith) public payable whenNotPaused returns (uint256[] memory) {
        return _batchDeposit(_candidateBidIds, _numberOfValidators, _validatorIdToShareSafeWith);
    }

    /// @notice register validators they have deposited. This triggers a 1 ETH transaction to the beacon chain.
    /// @param _validatorIds The ids of the validators to register
    /// @param _registerValidatorDepositData As in the solo staking flow, the BNFT player must send in a deposit data object (see ILiquidityPool for struct data)
    ///         to register the validators. However, the signature and deposit data root must be for a 1 ETH deposit
    /// @param _depositDataRootApproval The deposit data roots for each validator for the 31 ETH transaction which will happen in the approval
    ///         step. See the Staking Manager for details.
    /// @param _signaturesForApprovalDeposit Much like the deposit data root. This is the signature for each validator for the 31 ETH 
    ///         transaction which will happen in the approval step.
    function batchRegister(
        uint256[] calldata _validatorIds,
        IStakingManager.DepositData[] calldata _registerValidatorDepositData,
        bytes32[] calldata _depositDataRootApproval,
        bytes[] calldata _signaturesForApprovalDeposit
    ) external whenNotPaused {
        address _bnftRecipient = isLpBnftHolder ? address(this) : msg.sender;
        return _batchRegister(_validatorIds, _registerValidatorDepositData, _depositDataRootApproval, _signaturesForApprovalDeposit, _bnftRecipient);
    }

    function _batchDeposit(uint256[] calldata _candidateBidIds, uint256 _numberOfValidators, uint256 _validatorIdToShareSafeWith) internal returns (uint256[] memory) {
        address tnftHolder = address(this);
        address bnftHolder = isLpBnftHolder ? address(this) : msg.sender;
        uint256 _stakerDepositAmountPerValidator = isLpBnftHolder ? 0 : 2 ether;

        require(_isStaker(), "Incorrect Caller");        
        require(msg.value == _numberOfValidators * _stakerDepositAmountPerValidator, "Not Enough Deposit");
        require(totalValueInLp + msg.value >= 32 ether * _numberOfValidators, "Not enough balance");

        uint256[] memory newValidators = stakingManager.batchDepositWithBidIds(_candidateBidIds, _numberOfValidators, msg.sender, tnftHolder, bnftHolder, SourceOfFunds.EETH, restakeBnftDeposits, _validatorIdToShareSafeWith);
        numPendingDeposits += uint32(newValidators.length);
        
        // In the case when some bids are already taken, we refund 2 ETH for each
        if (_numberOfValidators > newValidators.length) {
            uint256 returnAmount = _stakerDepositAmountPerValidator * (_numberOfValidators - newValidators.length);
            _sendFund(msg.sender, returnAmount);
        }

        return newValidators;
    }

    function _batchRegister(
        uint256[] calldata _validatorIds,
        IStakingManager.DepositData[] calldata _registerValidatorDepositData,
        bytes32[] calldata _depositDataRootApproval,
        bytes[] calldata _signaturesForApprovalDeposit,
        address _bnftRecipient
    ) internal {
        require(_validatorIds.length == _registerValidatorDepositData.length && _validatorIds.length == _depositDataRootApproval.length && _validatorIds.length == _signaturesForApprovalDeposit.length, "lengths differ");
        
        numPendingDeposits -= uint32(_validatorIds.length);

        // If the LP is the B-nft holder, the 1 ether (for each validator) is taken from the LP
        // otherwise, the 1 ether is taken from the B-nft holder's separate deposit. Thus, we don't need to update the accounting
        uint256 outboundEthAmountFromLp = isLpBnftHolder ? 1 ether * _validatorIds.length : 0;
        _accountForEthSentOut(outboundEthAmountFromLp);

        stakingManager.batchRegisterValidators{value: 1 ether * _validatorIds.length}(_validatorIds, _bnftRecipient, address(this), _registerValidatorDepositData, msg.sender);
        
        for(uint256 i; i < _validatorIds.length; i++) {
            depositDataRootForApprovalDeposits[_validatorIds[i]] = _depositDataRootApproval[i];
            emit ValidatorRegistered(_validatorIds[i], _signaturesForApprovalDeposit[i], _registerValidatorDepositData[i].publicKey, _depositDataRootApproval[i]);
        }
    }

    /// @notice Approves validators and triggers the 31 ETH transaction to the beacon chain (rest of the stake).
    /// @dev This gets called by the Oracle and only when it has confirmed the withdraw credentials of the 1 ETH deposit in the registration
    ///         phase match the withdraw credentials stored on the beacon chain. This prevents a front-running attack.
    /// @param _validatorIds The IDs of the validators to be approved
    /// @param _pubKey The pubKey for each validator being spun up.
    /// @param _signature The signatures for each validator for the 31 ETH transaction that were emitted in the register phase
    function batchApproveRegistration(
        uint256[] memory _validatorIds, 
        bytes[] calldata _pubKey,
        bytes[] calldata _signature
    ) external whenNotPaused {
        if (!roleRegistry.hasRole(LIQUIDITY_POOL_ADMIN_ROLE, msg.sender)) revert IncorrectRole();
        require(_validatorIds.length == _pubKey.length && _validatorIds.length == _signature.length, "lengths differ");

        bytes32[] memory depositDataRootApproval = new bytes32[](_validatorIds.length);
        for(uint256 i; i < _validatorIds.length; i++) {
            depositDataRootApproval[i] = depositDataRootForApprovalDeposits[_validatorIds[i]];
            delete depositDataRootForApprovalDeposits[_validatorIds[i]];        

            emit ValidatorApproved(_validatorIds[i]);
        }

        // As the LP is the T-NFT holder, the 30 ETH is taken from the LP for each validator
        // 
        // If the LP is the B-NT holder, the 1 ether for each validator is taken from the LP as well
        // otherwise, the 1 ether is taken from the B-nft holder's separate deposit
        uint256 outboundEthAmountFromLp = isLpBnftHolder ? 31 ether * _validatorIds.length : 30 ether * _validatorIds.length;
        _accountForEthSentOut(outboundEthAmountFromLp);

        stakingManager.batchApproveRegistration{value: 31 ether * _validatorIds.length}(_validatorIds, _pubKey, _signature, depositDataRootApproval);
    }

    /// @notice Cancels a BNFT players deposits (whether validator is registered or deposited. Just not live on beacon chain)
    /// @dev This is called only in the BNFT player flow
    /// @param _validatorIds The IDs to be cancelled
    function batchCancelDeposit(uint256[] calldata _validatorIds) external whenNotPaused {
        _batchCancelDeposit(_validatorIds, msg.sender);
    }

    function _batchCancelDeposit(uint256[] calldata _validatorIds, address _bnftStaker) internal {
        uint256 returnAmount = 0;

        for (uint256 i = 0; i < _validatorIds.length; i++) {
            if(nodesManager.phase(_validatorIds[i]) == IEtherFiNode.VALIDATOR_PHASE.WAITING_FOR_APPROVAL) {
                if (!isLpBnftHolder) returnAmount += 1 ether;
                emit ValidatorRegistrationCanceled(_validatorIds[i]);
            } else {
                if (!isLpBnftHolder) returnAmount += 2 ether;
                numPendingDeposits -= 1;
            }
        }

        stakingManager.batchCancelDepositAsBnftHolder(_validatorIds, _bnftStaker);

        _sendFund(_bnftStaker, returnAmount);
    }

    /// @notice The admin can register an address to become a BNFT holder
    /// @param _user The address of the BNFT player to register
    function registerAsBnftHolder(address _user) public {
        if (!roleRegistry.hasRole(LIQUIDITY_POOL_ADMIN_ROLE, msg.sender)) revert IncorrectRole();
        require(!bnftHoldersIndexes[_user].registered, "Already registered");  

        BnftHolder memory bnftHolder = BnftHolder({
            holder: _user,
            timestamp: 0
        });

        uint256 index = bnftHolders.length;

        bnftHolders.push(bnftHolder);
        bnftHoldersIndexes[_user] = BnftHoldersIndex({
            registered: true,
            index: uint32(index)
        });

        emit BnftHolderRegistered(_user, index);
    }

    /// @notice Removes a BNFT player from the bnftHolders array
    /// @param _bNftHolder Address of the BNFT player to remove
    function deRegisterBnftHolder(address _bNftHolder) external {
        require(bnftHoldersIndexes[_bNftHolder].registered, "Not registered");
        uint256 index = bnftHoldersIndexes[_bNftHolder].index;
        require(roleRegistry.hasRole(LIQUIDITY_POOL_ADMIN_ROLE, msg.sender) || msg.sender == bnftHolders[index].holder, "Incorrect Caller");
        
        uint256 endIndex = bnftHolders.length - 1;
        address endUser = bnftHolders[endIndex].holder;

        //Swap the end BNFT player with the BNFT player being removed
        bnftHolders[index] = bnftHolders[endIndex];
        bnftHoldersIndexes[endUser].index = uint32(index);
        
        //Pop the last user as we have swapped them around
        bnftHolders.pop();
        delete bnftHoldersIndexes[_bNftHolder];

        emit BnftHolderDeregistered(_bNftHolder, index);
    }

    /// @notice Send the exit requests as the T-NFT holder of the LiquidityPool validators
    function sendExitRequests(uint256[] calldata _validatorIds) external {
        if (!roleRegistry.hasRole(LIQUIDITY_POOL_ADMIN_ROLE, msg.sender)) revert IncorrectRole();
        
        nodesManager.batchSendExitRequest(_validatorIds);
    }

    /// @notice Rebase by ether.fi
    function rebase(int128 _accruedRewards) public {
        if (msg.sender != address(membershipManager)) revert IncorrectCaller();
        totalValueOutOfLp = uint128(int128(totalValueOutOfLp) + _accruedRewards);

        emit Rebase(getTotalPooledEther(), eETH.totalShares());
    }

    /// @notice Whether or not nodes created via bNFT deposits should be restaked
    function setRestakeBnftDeposits(bool _restake) external {
        if (!roleRegistry.hasRole(LIQUIDITY_POOL_ADMIN_ROLE, msg.sender)) revert IncorrectRole();

        restakeBnftDeposits = _restake;
    }

    // Pauses the contract
    function pauseContract() external {
        if (!roleRegistry.hasRole(roleRegistry.PROTOCOL_PAUSER(), msg.sender)) revert IncorrectRole();
        if (paused) revert("Pausable: already paused");
        
        paused = true;
        emit Paused(msg.sender);
    }

    // Unpauses the contract
    function unPauseContract() external {
        if (!roleRegistry.hasRole(roleRegistry.PROTOCOL_UNPAUSER(), msg.sender)) revert IncorrectRole();
        if (!paused) revert("Pausable: not paused");

        paused = false;
        emit Unpaused(msg.sender);
    }

    // DEPRECATED, just existing not to touch EtherFiAdmin contract
    function setStakingTargetWeights(uint32 _eEthWeight, uint32 _etherFanWeight) external {
    }

    function updateBnftMode(bool _isLpBnftHolder) external {
        if (!roleRegistry.hasRole(LIQUIDITY_POOL_ADMIN_ROLE, msg.sender)) revert IncorrectRole();

        // Never toggle it in the process of deposit-regiration
        isLpBnftHolder = _isLpBnftHolder;
    }

    function addEthAmountLockedForWithdrawal(uint128 _amount) external {
        if (!(msg.sender == address(etherFiAdminContract) || msg.sender == address(withdrawRequestNFT))) revert IncorrectCaller();

        ethAmountLockedForWithdrawal += _amount;
    }

    // This function can't change the TVL
    // but used only to correct the errors in tracking {totalValueOutOfLp} and {totalValueInLp}
    function updateTvlSplits(int128 _diffTotalValueOutOfLp, int128 _diffTotalValueInLp) external onlyOwner {
        uint256 tvl = getTotalPooledEther();

        totalValueOutOfLp = uint128(int128(totalValueOutOfLp) + _diffTotalValueOutOfLp);
        totalValueInLp = uint128(int128(totalValueInLp) + _diffTotalValueInLp);

        if(tvl != getTotalPooledEther()) revert();
    }

    function reduceEthAmountLockedForWithdrawal(uint128 _amount) external {
        if (msg.sender != address(withdrawRequestNFT)) revert IncorrectCaller();

        ethAmountLockedForWithdrawal -= _amount;
    }

    //--------------------------------------------------------------------------------------
    //------------------------------  INTERNAL FUNCTIONS  ----------------------------------
    //--------------------------------------------------------------------------------------

    function _deposit(address _recipient, uint256 _amountInLp, uint256 _amountOutOfLp) internal returns (uint256) {
        totalValueInLp += uint128(_amountInLp);
        totalValueOutOfLp += uint128(_amountOutOfLp);
        uint256 amount = _amountInLp + _amountOutOfLp;
        uint256 share = _sharesForDepositAmount(amount);
        if (amount > type(uint128).max || amount == 0 || share == 0) revert InvalidAmount();

        eETH.mintShares(_recipient, share);

        return share;
    }

    function _sharesForDepositAmount(uint256 _depositAmount) internal view returns (uint256) {
        uint256 totalPooledEther = getTotalPooledEther() - _depositAmount;
        if (totalPooledEther == 0) {
            return _depositAmount;
        }
        return (_depositAmount * eETH.totalShares()) / totalPooledEther;
    }

    function _sendFund(address _recipient, uint256 _amount) internal {
        uint256 balanace = address(this).balance;
        (bool sent, ) = _recipient.call{value: _amount}("");
        require(sent && address(this).balance == balanace - _amount, "SendFail");
    }

    function _accountForEthSentOut(uint256 _amount) internal {
        totalValueOutOfLp += uint128(_amount);
        totalValueInLp -= uint128(_amount);
    }

    function _authorizeUpgrade(address newImplementation) internal override onlyOwner {}

    //--------------------------------------------------------------------------------------
    //------------------------------------  GETTERS  ---------------------------------------
    //--------------------------------------------------------------------------------------

    function getTotalEtherClaimOf(address _user) external view returns (uint256) {
        uint256 staked;
        uint256 totalShares = eETH.totalShares();
        if (totalShares > 0) {
            staked = (getTotalPooledEther() * eETH.shares(_user)) / totalShares;
        }
        return staked;
    }

    function getTotalPooledEther() public view returns (uint256) {
        return totalValueOutOfLp + totalValueInLp;
    }

    function sharesForAmount(uint256 _amount) public view returns (uint256) {
        uint256 totalPooledEther = getTotalPooledEther();
        if (totalPooledEther == 0) {
            return 0;
        }
        return (_amount * eETH.totalShares()) / totalPooledEther;
    }

    /// @dev withdrawal rounding errors favor the protocol by rounding up
    function sharesForWithdrawalAmount(uint256 _amount) public view returns (uint256) {
        uint256 totalPooledEther = getTotalPooledEther();
        if (totalPooledEther == 0) {
            return 0;
        }

        // ceiling division so rounding errors favor the protocol
        uint256 numerator = _amount * eETH.totalShares();
        return (numerator + totalPooledEther - 1) / totalPooledEther;
    }

    function amountForShare(uint256 _share) public view returns (uint256) {
        uint256 totalShares = eETH.totalShares();
        if (totalShares == 0) {
            return 0;
        }
        return (_share * getTotalPooledEther()) / totalShares;
    }

    function getImplementation() external view returns (address) {return _getImplementation();}

    function _isStaker() internal view returns (bool) {
        uint32 index = bnftHoldersIndexes[msg.sender].index;
        return bnftHoldersIndexes[msg.sender].registered && bnftHolders[index].holder == msg.sender;
    }

    function _requireNotPaused() internal view virtual {
        require(!paused, "Pausable: paused");
    }

    //--------------------------------------------------------------------------------------
    //-----------------------------------  MODIFIERS  --------------------------------------
    //--------------------------------------------------------------------------------------

    modifier whenNotPaused() {
        _requireNotPaused();
        _;
    }
}
