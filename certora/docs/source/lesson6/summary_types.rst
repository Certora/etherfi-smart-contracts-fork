Summary types
=============

Example -- Voting power
-----------------------
* The example in this section is
  :clink:`VotingSqrt.sol</certora/training-examples/lesson6/sqrt/src/VotingSqrt.sol>`
  from folder :clink:`/certora/training-examples/lesson6/sqrt/`.
* This is similar to the simple Voting contract we saw in
  :ref:`simple_voting_contract_example`.
* The difference is the voting power for a voter is the square root of the voter's
  balance in an ERC-20 token
  (:clink:`ERC20.sol</certora/training-examples/lesson6/sqrt/src/ERC20.sol>`).
* I have also injected a bug in the :solidity:`vote` methods, which causes
  votes against to be under-counted.
* The bug comes into effect only when the voting power is greater than 10. This means the
  bug will not be detected with low iteration numbers.

.. dropdown:: Square root code

   .. literalinclude:: ../../../training-examples/lesson6/sqrt/src/VotingSqrt.sol
      :language: solidity
      :lines: 42-54
      :caption: :clink:`The square root function </certora/training-examples/lesson6/sqrt/src/VotingSqrt.sol>`

.. dropdown:: Injected bug

   .. literalinclude:: ../../../training-examples/lesson6/sqrt/src/VotingSqrt.sol
      :language: solidity
      :lines: 20-34
      :emphasize-lines: 11-13
      :caption: :clink:`Vote function with bug </certora/training-examples/lesson6/sqrt/src/VotingSqrt.sol>`


The spec
--------
* The basic spec is
  :clink:`VotingSqrt.spec </certora/training-examples/lesson6/sqrt/certora/specs/VotingSqrt.spec>`.
* The spec contains four simple rules, shown below.

Sum is total votes - invariant
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cvlinclude:: ../../../training-examples/lesson6/sqrt/certora/specs/VotingSqrt.spec
   :cvlobject: sumResultsEqualsTotalVotes

Voting power function properties
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Shows the Voting power function:

#. preserves zero and
#. weakly monotonic increasing.

.. cvlinclude:: ../../../training-examples/lesson6/sqrt/certora/specs/VotingSqrt.spec
   :cvlobject: votingPowerProperties

Vote integrity - rule
^^^^^^^^^^^^^^^^^^^^^
Shows that calling :solidity:`vote`:

#. increases :solidity:`totalVotes` by :solidity:`votingPower(voter)`, and
#. increases :solidity:`votesInFavor` or :solidity:`votesAgainst` similarly.

.. cvlinclude:: ../../../training-examples/lesson6/sqrt/certora/specs/VotingSqrt.spec
   :cvlobject: voteIntegrity

Configuration and report
^^^^^^^^^^^^^^^^^^^^^^^^
* The configuration file
  :clink:`VotingSqrt.conf </certora/training-examples/lesson6/sqrt/certora/confs/VotingSqrt.conf>`
  uses *three loop iterations*.
* The report therefore does not detect any violations,
  `VotingSqrt.spec report (3 iterations)`_.
* We will need to use much higher ``loop_iter`` to detect the injected bug, and
  it may result in a timeout.


Summarizing
-----------
* We can use summaries to try and detect the bug without increasing the ``loop_iter``.
* In the examples below the rules and invariant are all the same as in
  :clink:`VotingSqrt.spec</certora/training-examples/lesson6/sqrt/certora/specs/VotingSqrt.spec>`.
* The change is in the summary of the :solidity:`sqrt` function.

The internal function
^^^^^^^^^^^^^^^^^^^^^
* We are summarizing the internal function of the public method.
* This way both internal and external calls will be summarized.

Always
^^^^^^
* The :cvl:`ALWAYS(value)` summary will always return ``value`` whenever the summarized
  function is called.
* In this case we used the value of ``50``, so the injected bug is detected.
* However, the :cvl:`votingPowerProperties` rule is violated.
* Spec:
  :clink:`VotingSqrtAlways.spec</certora/training-examples/lesson6/sqrt/certora/specs/VotingSqrtAlways.spec>`.
* Report: `Using ALWAYS summary report`_.

.. dropdown:: Always summary

   .. cvlinclude:: ../../../training-examples/lesson6/sqrt/certora/specs/VotingSqrtAlways.spec
      :cvlobject: methods
      :emphasize-lines: 10

Constant
^^^^^^^^
* The :cvl:`CONSTANT` summary will return the same value for every call, but the value
  is non-deterministic.
* This summary detects the injected bug.
* The :cvl:`votingPowerProperties` rule is violated.
* Spec:
  :clink:`VotingSqrtConst.spec </certora/training-examples/lesson6/sqrt/certora/specs/VotingSqrtConst.spec>`.
* Report: `Using CONSTANT summary report`_.

.. dropdown:: Constant summary

   .. cvlinclude:: ../../../training-examples/lesson6/sqrt/certora/specs/VotingSqrtConst.spec
      :cvlobject: methods
      :emphasize-lines: 10

Per callee constant
^^^^^^^^^^^^^^^^^^^
* The :cvl:`PER_CALLEE_CONSTANT` summary will return the same value for every *receiver*
  contracts.


Non-deterministic
^^^^^^^^^^^^^^^^^
* The :cvl:`NONDET` summary returns a non-deterministic value every call.
  This is *sound* to use for :solidity:`view` and :solidity:`pure` functions.
* This summary detects the injected bug.
* But the :cvl:`votingPowerProperties` rule is violated.
* Spec:
  :clink:`VotingSqrtNondet.spec </certora/training-examples/lesson6/sqrt/certora/specs/VotingSqrtNondet.spec>`.
* Report: `Using NONDET summary report`_.

.. dropdown:: Non-deterministic summary

   .. cvlinclude:: ../../../training-examples/lesson6/sqrt/certora/specs/VotingSqrtNondet.spec
      :cvlobject: methods
      :emphasize-lines: 10

Function summary
^^^^^^^^^^^^^^^^
* If we want a more specific behavior, we use a CVL function to summarize the
  given Solidity function.
* In this case we approximate the square root by returning :math:`y` such that
  :math:`y \leq \sqrt{x}`.
* This summary detects the injected bug.
* It also satisfies that :solidity:`votingPower` preserves zero.
* However, the assertion that :solidity:`votingPower` is weakly monotonic increasing is
  violated.
* Spec:
  :clink:`VotingSqrtSummary1.spec </certora/training-examples/lesson6/sqrt/certora/specs/VotingSqrtSummary1.spec>`.
* Report: `Using approximation below report`_.

.. dropdown:: Function summary

   .. cvlinclude:: ../../../training-examples/lesson6/sqrt/certora/specs/VotingSqrtSummary1.spec
      :cvlobject: methods squareRootApprox
      :emphasize-lines: 10, 16-

Better function summary
^^^^^^^^^^^^^^^^^^^^^^^
* As above, here we use a CVL function summary.
* The function used here gives a rounded down square root.
* This summary both detects the injected bug and satisfies the
  :cvl:`votingPowerProperties` rule.
* Spec:
  :clink:`VotingSqrtSummary2.spec </certora/training-examples/lesson6/sqrt/certora/specs/VotingSqrtSummary2.spec>`.
* Report: `Using good approximation report`_.

.. dropdown:: Better function summary

   .. cvlinclude:: ../../../training-examples/lesson6/sqrt/certora/specs/VotingSqrtSummary2.spec
      :cvlobject: methods squareRootApprox


.. Links:
   ------

.. _VotingSqrt.spec report (3 iterations):
   https://prover.certora.com/output/98279/031400ac0c674d1bbb7951bc1397dfa6?anonymousKey=0e734d269ab8d05a223f68c7ed53cc85118db81c

.. _Using ALWAYS summary report:
   https://prover.certora.com/output/98279/264379c091f341ee8ee0067f2112ce34?anonymousKey=37bf979b9c0d287b2913b531bb5aaaa0a1c48fbb

.. _Using CONSTANT summary report:
   https://prover.certora.com/output/98279/b1ec865ad1834b5195cfe3956507517c?anonymousKey=7bbb24ebe9e885b6e03d80d60c2a1e8f3b1ee450

.. _Using NONDET summary report:
   https://prover.certora.com/output/98279/d882494f8e78486e946527b10c7dd83d?anonymousKey=acede672c6769b434f7c9b01d0052f194d70632f

.. _Using approximation below report:
   https://prover.certora.com/output/98279/eaec6df4dc2e45c5abb3b19a76a245ca?anonymousKey=84195411f67981cb5820e79665957987f75b3732

.. _Using good approximation report:
   https://prover.certora.com/output/98279/2f7f6fe8cdcb4a8dac151da3153b876c?anonymousKey=b83cb111b80258132185dfbb26445e1fc3869ed2
