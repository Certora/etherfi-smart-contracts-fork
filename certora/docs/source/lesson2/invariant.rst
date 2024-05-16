.. index::
   single: invariant

Invariants
==========

Introduction
------------

* Use invariants for properties about the state (storage).
* See `Invariants`_ documentation, in particular `Invariants and induction`_ section.


Ball game example
-----------------

Rules
^^^^^

* Four players: A, B, C, D.
* Players A and C pass to each other.
* Players B and D pass to each other.
* The game begins with player A holding the ball.

Code modeling the game
^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../training-examples/lesson2/ballgame/BallGame.sol
   :language: solidity


Invariants
^^^^^^^^^^

Bad invariant
"""""""""""""

.. cvlinclude:: ../../../training-examples/lesson2/ballgame/BallGame.spec
   :cvlobject: neverWillDGetTheBall

Fixed invariant
"""""""""""""""

.. cvlinclude:: ../../../training-examples/lesson2/ballgame/BallGame.spec
   :cvlobject: neverWillDGetTheBall_fixed

* `Ball game report`_

----

NodeOperatorManager invariant
-----------------------------

The invariant
^^^^^^^^^^^^^
This invariant says that if an operator has non-zero total keys, then it is registered.

.. cvlinclude:: ../../../specs/lesson2/Invariants.spec
   :cvlobject: nonZeroTotalKeysIsRegistered
   :caption: :clink:`nonZeroTotalKeysIsRegistered</certora/specs/lesson2/Invariants.spec>`

* Report: `NodeOperatorManager filtered invariant report`_.

.. _filter_out_upgrade:

On filtering
^^^^^^^^^^^^
Why did we filter
"""""""""""""""""
The Prover finds a violation for the rule when calling the function
:cvl:`upgradeToAndCall`. Here is how the violation came to be.

#. The Prover is unable to find a target for :solidity:`target.delegatecall(data)`
   in line 202 of |ERC1967UpgradeUpgradeable.sol|.
#. Therefore the Prover uses an over-approximation -- _havoc_. This means all storage
   variables can be changed, see `Havoc documentation`_.
#. Report: `NodeOperatorManager unfiltered invariant report`_.

.. dropdown:: ERC1967UpgradeUpgradeable.sol -- relevant function

  .. literalinclude:: ../../../../lib/openzeppelin-contracts-upgradeable/contracts/proxy/ERC1967/ERC1967UpgradeUpgradeable.sol
     :language: solidity
     :lines: 198-204
     :emphasize-lines: 5

How to fix this
"""""""""""""""
* We can provide an implementation, i.e. a concrete target for the :solidity:`delegatecall`.
* We can use `Summaries`_ -- this is the preferred option, which we will learn about later.
* We chose filter out :cvl:`upgradeToAndCall`, since this is the simplest way.

.. tip::

   Do not filter out methods every time an invariant fails on them. Filtering should be
   used sparingly and only for a good reason.

.. index::
   single: sig
   single: selector
   single: method

Detour -- identifying a function
""""""""""""""""""""""""""""""""
To filter out :cvl:`upgradeToAndCall` we used the following syntax to identify a function:

.. cvlinclude:: ../../../specs/lesson2/Invariants.spec
   :cvlobject: nonZeroTotalKeysIsRegistered
   :lines: 4-

Additional data about :cvl:`method f` we have in CVL:

* :cvl:`bool f.isView` -- if :cvl:`f` is a :solidity:`view` function.
* :cvl:`bool f.isPure` -- if it is a :solidity:`pure` function.
* :cvl:`address f.contract` -- the contract of :cvl:`f`.


.. Links
   -----

.. _Invariants: https://docs.certora.com/en/latest/docs/cvl/invariants.html

.. _Invariants and induction:
   https://docs.certora.com/en/latest/docs/cvl/invariants.html#invariants-and-induction

.. _Ball game report:
   https://prover.certora.com/output/98279/9eccea2b12fc40a3bc0e3195b13e1fad?anonymousKey=e78179db104e95ea08e65556cf63675ecff1100e

.. _NodeOperatorManager unfiltered invariant report:
   https://prover.certora.com/output/98279/cc5b76a360224c6e832d4af09544d2bf?anonymousKey=9282d09459b252f2455cd5e2572080b7343b361e

.. _NodeOperatorManager filtered invariant report:
   https://prover.certora.com/output/98279/cc5b76a360224c6e832d4af09544d2bf?anonymousKey=9282d09459b252f2455cd5e2572080b7343b361e

.. _Invariant filters: https://docs.certora.com/en/latest/docs/cvl/invariants.html#filters

.. _Havoc documentation: https://docs.certora.com/en/latest/docs/user-guide/glossary.html#term-havoc

.. _Summaries: https://docs.certora.com/en/latest/docs/cvl/methods.html#summaries


.. Substitutions
   -------------

.. |ERC1967UpgradeUpgradeable.sol| replace::
   :clink:`ERC1967UpgradeUpgradeable.sol</lib/openzeppelin-contracts-upgradeable/contracts/proxy/ERC1967/ERC1967UpgradeUpgradeable.sol>`
