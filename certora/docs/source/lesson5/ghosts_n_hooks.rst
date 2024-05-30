Ghosts and hooks
================

Links:

* `Ghosts and hooks (from Tutorials)`_
* `Ghosts (from Documentation)`_
* `Hooks (from Documentation)`_

.. index::
   single: hook

Storage hooks
-------------

A *storage hook* is a CVL function that will be executed whenever a particular storage
is loaded or stored (modified).

Example
^^^^^^^
We have an example of the Voting contract with a bug in
:clink:`VotingBug4.sol </certora/training-examples/lesson1/buggy_voting/VotingBug4.sol>`.
The bug enables voters in favor to vote many times.

.. dropdown:: VotingBug4.sol

   .. literalinclude:: ../../../training-examples/lesson1/buggy_voting/VotingBug4.sol
      :language: solidity
      :lines: 4-

Here is a basic spec that catches this bug.

.. literalinclude:: ../../../training-examples/lesson1/solidity_intro/SimpleHook.spec
   :language: cvl
   :lines: 4-
   :caption: :clink:`SimpleHook.spec</certora/training-examples/lesson1/solidity_intro/SimpleHook.spec>`

The report: `Simple hook report`_.


.. index::
   single: ghost

Ghost variables
---------------

* *Ghost* variables are "global" variables defined in CVL and accessible from
  CVL rules, invariants, hooks and functions.
* Ordinary ghost variables behave like storage variables. In particular they also revert
  when the transaction reverts.
* In contrast, *persistent* ghosts do not revert when the transaction reverts. They are
  also not havoc'd.

Example
^^^^^^^
Here is a very basic example, using the
:clink:`VotingFixed.sol</certora/training-examples/lesson1/solidity_intro/VotingFixed.sol>`
contract.

.. literalinclude:: ../../../training-examples/lesson1/solidity_intro/SimpleGhost.spec
   :language: cvl
   :lines: 4-
   :caption: :clink:`SimpleHook.spec</certora/training-examples/lesson1/solidity_intro/SimpleGhost.spec>`


.. Links
   -----

.. _Ghosts and hooks (from Tutorials):
   https://docs.certora.com/projects/tutorials/en/latest/lesson4_invariants/ghosts/basics.html

.. _Ghosts (from Documentation): https://docs.certora.com/en/latest/docs/cvl/ghosts.html
.. _Hooks (from Documentation): https://docs.certora.com/en/latest/docs/cvl/hooks.html

.. _Simple hook report:
   https://prover.certora.com/output/98279/6cc239b73af441a0912ee17f1ce44cd2?anonymousKey=3c5b9b9870c97454e77e60404627075dac16a987
