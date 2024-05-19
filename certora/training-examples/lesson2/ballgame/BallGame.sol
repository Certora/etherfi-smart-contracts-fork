pragma solidity ^0.8.20;


contract BallGame {

  enum Player {
    A, B, C, D
  }
  Player public ballPosition;

  constructor() {
    ballPosition = Player.A;  // Starting state
  }

  function pass() external {
    if (ballPosition == Player.A) {
      ballPosition = Player.C;
    } else if (ballPosition == Player.C) {
      ballPosition = Player.A;
    } else if (ballPosition == Player.B) {
      ballPosition = Player.D;
    } else {
      ballPosition = Player.B;
    }
  }
}
