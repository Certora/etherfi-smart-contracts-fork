methods {
    function _.setValidatorPhase(uint256 _validatorId, uint8 _phase) external => ghostSetValidatorPhase(_validatorId, _phase) expect void;
    function _.phase(uint256 _validatorId) external => ghostGetValidatorPhase(_validatorId) expect uint8;
}

// Summaries for staking manager used instead of linking the contract itself.
persistent ghost mapping(uint256 => uint8) validatorPhase {
    init_state axiom forall uint256 validatorId . validatorPhase[validatorId] == 0;
}

function ghostSetValidatorPhase(uint256 validatorId, uint8 phase) {
    validatorPhase[validatorId] = phase;
}

function ghostGetValidatorPhase(uint256 validatorId) returns uint8 {
    return validatorPhase[validatorId];
}
