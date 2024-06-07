Exercises
=========

General LiquidityPool exercises
-------------------------------
#. Write a rule asserting that if there are zero shares but
   :solidity:`getTotalPooledEther() > 0` then this state persists.

   * Was your rule verified?
   * Does this indicate a problem?

#. Prove an invariant showing the pool is solvent.

   .. dropdown:: Hint

      Prove that :cvl:`getTotalPooledEther() >= amountForShare(eETH.totalShares())`.


#. Write a parametric rule stating all the functions that can cause
   :solidity:`getTotalPooledEther(user)` to decrease.
#. Write an invariant asserting the ETH balance of the pool is at least the
   :solidity:`getTotalPooledEther`. Does it hold?
