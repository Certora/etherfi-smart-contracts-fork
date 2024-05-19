/* Ball game example spec */
methods {
    function ballPosition() external returns (BallGame.Player) envfree;
}


invariant neverWillDGetTheBall()
    ballPosition() != BallGame.Player.D;


invariant neverWillDGetTheBall_fixed()
    ballPosition() != BallGame.Player.B && ballPosition() != BallGame.Player.D;
