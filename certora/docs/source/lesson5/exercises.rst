Exercises
=========

Ghosts and hooks
----------------

NodeOperatorManager
^^^^^^^^^^^^^^^^^^^
Using ghosts and hooks show for
:clink:`NodeOperatorManager</src/NodeOperatorManager.sol>` that:

#. :solidity:`addressToOperatorData[_user].keysUsed` can be changed only by certain
   functions.
#. Except for :solidity:`initializeOnUpgrade` all other functions can only change the
   :solidity:`keysUsed` only for a single user.

AuctionManager
^^^^^^^^^^^^^^
Show for :clink:`AuctionManager</src/AuctionManager.sol>` that each function only changes
:solidity:`admins` for a single address.


Storage
-------
#. Show for :clink:`EETH</src/EETH.sol>` that transferring from :solidity:`address a`
   to :solidity:`address b` amount :math:`x` followed by amount :math:`y` is the same
   as transferring :math:`x + y`.
#. Write a rule for :clink:`LiquidityPool</src/LiquidityPool.sol>` stating that
   depositing :math:`x` followed by depositing :math:`y` is the same as
   depositing :math:`x + y`.

   * *(Optional)* Try running this rule.

Side entrance
-------------
* This is based on `Damn Vulnerable DeFi Challenge #4 - Side Entrance`_.
* The
  :clink:`SideEntranceLenderPool</certora/training-examples/lesson5/side_entrance/SideEntranceLenderPool.sol>`
  shown below has a vulnerability.
* The
  :clink:`FlashLoanReceiverHarness</certora/training-examples/lesson5/side_entrance/FlashLoanReceiverHarness.sol>`
  is a contract that can receive the loan and "randomly" do various actions.
* **Exercise.** Write a :cvl:`satisfy` rule that exposes the vulnerability.

.. tip::

   Use ``optimistic_fallback`` and ``contract_recursion_limit`` in the config.

.. dropdown:: SideEntranceLenderPool

   .. literalinclude:: ../../../training-examples/lesson5/side_entrance/SideEntranceLenderPool.sol
      :language: solidity
      :lines: 14-
      :caption: :clink:`SideEntranceLenderPool</certora/training-examples/lesson5/side_entrance/SideEntranceLenderPool.sol>`

.. dropdown:: FlashLoanReceiverHarness

   .. literalinclude:: ../../../training-examples/lesson5/side_entrance/FlashLoanReceiverHarness.sol
      :language: solidity
      :lines: 10-
      :caption: :clink:`FlashLoanReceiverHarness</certora/training-examples/lesson5/side_entrance/FlashLoanReceiverHarness.sol>`

.. Links
   -----

.. _Damn Vulnerable DeFi Challenge #4 - Side Entrance:
   https://www.damnvulnerabledefi.xyz/challenges/side-entrance/
