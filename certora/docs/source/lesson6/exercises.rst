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
   :solidity:`getTotalEtherClaimOf(user)` to decrease.
#. Write an invariant asserting the ETH balance of the pool is at least the
   :solidity:`getTotalPooledEther`. Does it hold?
#. Write a parametric rule asserting that :solidity:`getTotalEtherClaimOf(user)`
   and :solidity:`eETH.shares(user)` are *weakly correlated*. Meaning when one increases
   the other does not decrease, and when one decreases the other does not increase.

----

Storage exercises
-----------------
#. Write a rule asserting that if two users deposit the same ETH into the pool, and
   the pool is in the same state for both, they get the same amount of shares.
#. Show that if user :math:`a` deposits more ETH than user :math:`b`, then :math:`a`
   should get the same or more shares than :math:`b`.

----

EtherFiNode Forall exercises
----------------------------

These exercises are for the :clink:`/src/EtherFiNode.sol` contract. 

We start with an example on how to use the :cvl:`forall` quantifier in CVL.
The invariant :cvl:`mappingLimits` shown below asserts that values in
:solidity:`associatedValidatorIndices` are less than the length of the
:solidity:`associatedValidatorIds` array.

.. cvlinclude:: ../../../specs/lesson6/EtherFiNodeInvariant_forall.spec
   :cvlobject: lenIds idFromIndex indexFromId mappingLimits
   :caption: :clink:`EtherFiNodeInvariant_forall.spec</certora/specs/lesson6/EtherFiNodeInvariant_forall.spec>`

#. Add to the spec two invariants (using :cvl:`forall`) asserting that:

   * :cvl:`indexFromId(idFromIndex(i)) == i` for index :cvl:`i` less than
     the length of :solidity:`associatedValidatorIds` array.
   * :cvl:`idFromIndex(indexFromId(_id)) == _id` for :cvl:`_id` such that
     :solidity:`associatedValidatorIndices[_id] > 0`.

#. Run the spec using the
   :clink:`EtherFiNodeInvariant_forall.conf</certora/confs/lesson6/EtherFiNodeInvariant_forall.conf>`
   config file.
#. Add :cvl:`preserved` blocks to the spec to make the rules verified.
