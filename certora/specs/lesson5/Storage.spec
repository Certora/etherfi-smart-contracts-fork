/* Using `lastStorage` example spec */


/// @title Last storage example - transfer via intermediary has no consequences
rule intermediaryTransfer(
    address sender,
    address recipient,
    address intermediary,
    uint256 amount
) {
    // Saving initial storage state
    storage init = lastStorage;

    // Transfer via intermediary
    env e1;
    require e1.msg.sender == sender;
    transfer(e1, intermediary, amount);

    env e2;
    require e2.msg.sender == intermediary;
    transfer(e2, recipient, amount);

    // Save current storage state
    storage viaIntermediary = lastStorage;

    // Transfer directly, using initial storage
    env e3;
    require e3.msg.sender == sender;
    transfer(e3, recipient, amount) at init;

    storage directTransfer = lastStorage;

    assert (
        viaIntermediary == directTransfer,
        "Transfer via intermediary is the same as direct transfer"
    );
}
