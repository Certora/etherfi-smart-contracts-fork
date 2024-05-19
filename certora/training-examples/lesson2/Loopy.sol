pragma solidity ^0.8.0;

/// @notice Examples of loop unrolling
contract Loopy {

    function loop(uint n) public pure returns (uint) {
        uint j = 0;
        for (uint i; i < n + 3; i++) {
            j++;
        }
        return j;
    }
    
    /// @notice Unroll of the loop above
    function unrolled(uint n) public pure returns (uint) {
        require(n <= 3);  // 3 unrolls will be enough
        uint j = 0;

        // Start unrolling
        uint i; // i=0
        if (i < n) {
            j++;

            // Next unroll
            i ++; // i=1
            if (i < n) {
                j++;

                // Next unroll
                i++; // i=2
                if (i < n) {
                    j++;

                    i++; // i=3
                }
            }
        }
        // Require that the exit condition holds - in CVL it means _assume_ 
        require(i >= n);
        // Or assert that it holds (in CVL)
        // assert i>=n;
        return j;
    }
}
