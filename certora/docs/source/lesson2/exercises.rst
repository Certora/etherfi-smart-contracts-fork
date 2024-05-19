Exercises
=========


NodeOperatorManager exercises
-----------------------------
#. Write an invariant for :clink:`NodeOperatorManager contract</src/NodeOperatorManager.sol>`
   proving that used keys is not greater than total keys
   (filter out the :cvl:`upgradeToAndCall` method).
#. The invariant you wrote fails on :cvl:`initializeOnUpgrade`. Understand the
   counter-example and fix the code appropriately.
#. Write a parametric rule showing that :cvl:`keysUsed` can only increase by 1 for
   each function call other than :cvl:`initializeOnUpgrade`.
#. Write a parametric rule (or rules) showing that only :cvl:`pauseContract` can
   pause a contract, and only :cvl:`unPauseContract` can end the pause.


EtherFiNode exercise
--------------------
This exercise is for :clink:`/src/EtherFiNode.sol`.

#. In the file :clink:`/certora/specs/lesson2/EtherFiNodeInvariant.spec`, write
   an invariant stating that:
   :solidity:`associatedValidatorIndices[associatedValidatorIds[i]] == i` when
   :solidity:`i < associatedValidatorIds.length`.
#. Use :clink:`/certora/confs/lesson2/EtherFiNodeInvariant.conf` config to check
   this invariant.
#. You will get a violation for :solidity:`registerValidator(uint256, bool)`.
   Fix the code and rerun.


Voting contract exercises
-------------------------
Additional exercises regarding the
:clink:`Voting contract</certora/training-examples/lesson1/solidity_intro/Voting.spec>`.

#. Write a parametric rule saying ``votesInFavor``, ``votesAgainst`` and ``totalVotes``
   are all non-decreasing.
#. Write an invariant saying the sum of votes in favor and against equals the total votes.
