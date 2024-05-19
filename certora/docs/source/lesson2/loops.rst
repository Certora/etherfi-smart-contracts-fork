.. index::
   single: loop
   single: optimistic_loop
   single: loop_iter
   :name: loop_handling

Loops
=====

Unrolling
---------

* For a complete explanation see `Loop unrolling`_ from the Documentation.
* Loops and recursion are *undecidable* (see `Undecidable problem`_),
  so the Prover must *unroll* loops.
* The number of loop unrolls is determined by the ``loop_iter`` parameter
  (either in config or in CLI).
* At the end of the unrolled loop, we either

  * :cvl:`require` that the stop condition is met, or 
  * :cvl:`assert` that it is met.

* The :cvl:`require` is used if the ``optimistic_loop`` flag is set,
  otherwise the Prover applies the :cvl:`assert`.

Unrolling example
^^^^^^^^^^^^^^^^^
In this example we unroll a loop three times.

.. literalinclude:: ../../../training-examples/lesson2/Loopy.sol
   :language: solidity
   :caption: :clink:`A loop unrolled </certora/training-examples/lesson2/Loopy.sol>`

Pessimistic example
^^^^^^^^^^^^^^^^^^^

* Below is a config running the rule :cvl:`nonZeroTotalKeysIsRegistered` without
  ``optimistic_loop``.
* The rule fails because of this, see `Pessimistic example report`_.

.. cvlinclude:: ../../../specs/lesson2/Invariants.spec
   :cvlobject: nonZeroTotalKeysIsRegistered
   :caption: :clink:`nonZeroTotalKeysIsRegistered</certora/specs/lesson2/Invariants.spec>`

.. literalinclude:: ../../../confs/lesson2/Pessimistic.conf
   :language: json
   :caption: :clink:`Pessimistic.conf</certora/confs/lesson2/Pessimistic.conf>`


Loop iterations
---------------
* The number of ``loop_iter`` determines the number of loop unrolling.
* This can have a critical effect of verification of rules.
* A too low number (with ``optimistic_loop``) can result in a vacuous rule
* A too high number might result in a timeout.

Example
^^^^^^^

* The contract :clink:`Loopy</certora/training-examples/lesson2/Loopy.sol>`.
* The :solidity:`loop` function needs at least 3 iterations to unroll.
* The rule :cvl:`loopExample` below simply asks for any example of a run.
* The Prover fails to find an example (*is vacuous*) with 2 loop iterations:
  `Loopy vacuity report`_.
* The Prover does find an example with 3 loop iterations (using :cvl:`n = 0`):
  `Loopy example three iterations`_.


.. literalinclude:: ../../../training-examples/lesson2/Loopy.sol
   :language: solidity
   :start-at: function loop
   :end-before: Unroll of the loop above
   :caption: :clink:`loop function</certora/training-examples/lesson2/Loopy.sol>`

.. cvlinclude:: ../../../training-examples/lesson2/Loopy.spec
   :cvlobject: loopExample
   :caption: :clink:`loopExample rule</certora/training-examples/lesson2/Loopy.spec>`

.. warning::

   Note how critical the ``loop_iter`` is. Be aware that ``optimistic_loop``
   adds a :cvl:`require` statement that might be unsound.


.. Links
   -----

.. _Loop unrolling: https://docs.certora.com/en/latest/docs/prover/approx/loops.html

.. _Undecidable problem: https://en.wikipedia.org/wiki/Undecidable_problem

.. _Loopy vacuity report:
   https://prover.certora.com/output/98279/3b326dc641bd4f448eb4fe2d7a02a67b?anonymousKey=ee19c9a39c53f3d3f267089d839acce4bb54174f

.. _Loopy example three iterations:
   https://prover.certora.com/output/98279/eece41e0e1e14f8dae4e9ee9974d6cab?anonymousKey=c9bfef41b4392c89c173aafb878df3bf9a732253

.. _Pessimistic example report:
   https://prover.certora.com/output/98279/56187fd455ef46aa858891f925ef8425?anonymousKey=0a855dd0ee7d789132f09c3624ccbba3d8710c59
