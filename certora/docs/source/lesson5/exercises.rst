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


