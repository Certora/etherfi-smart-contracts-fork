// Ball game example spec

methods {
    function ballPosition() external returns (BallGame.Player) envfree;
}


rule neverDanHasBallPass() {
    require ballPosition() != BallGame.Player.D;
    env e;
    pass(e);
    assert ballPosition() != BallGame.Player.D;
}


invariant neverWillBobNorDanGetBall()
    ballPosition() != BallGame.Player.D && ballPosition() != BallGame.Player.B;
