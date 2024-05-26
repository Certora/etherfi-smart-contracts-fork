Exercises
=========

Liquidity Pool setup
--------------------
Complete the :solidity:`LiquidityPool` setup by finding solutions for:

#. :ref:`unresolved_etherfinode_calls`.
#. :ref:`unresolved_call_to_erc721`.
#. :ref:`unresolved_call_to_idepositcontract`.

Add the solution in :ref:`unresolved_to_eigenpodmanager` to complete the setup.


More invariants and parametric rules
------------------------------------
These exercises are for the :clink:`AuctionManager</src/AuctionManager.sol>` contract
and the minimal setup from :ref:`auctionmanager_setup`.

.. note::

   * In some of these exercises you will have a sanity (vacuity) issue with
     the :solidity:`initialize` method.
   * For these exercises you can filter out the :cvl:`upgradeToAndCall` method.
   * Hint: you will need require an invariant in these exercises.

#. Write an invariant showing bids with :solidity:`bidId` higher or equal to
   :solidity:`numberOfBids` have :solidity:`address(0)` as bid owner (i.e. have not
   been created).
#. Write a parametric rule showing the number of bids cannot decrease.
#.  Write a parametric rule showing that once the bid owner is set, it cannot be changed.
