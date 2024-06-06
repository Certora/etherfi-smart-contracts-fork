Catch unresolved calls
======================

* The "catch unresolved-calls entry", aka :cvl:`DISPATCH` list, gives the Prover
  various alternatives to check for when encountering an unresolved call.
* This unresolved call needs to be unresolved also with respect to all other entries.
* See `Catch unresolved-calls entry`_ in the documentation.


Multicall example
-----------------

* The :clink:`Multicall</certora/training-examples/lesson6/multicall/Multicall.sol>`
  contract is allows general batch calls via the :solidity:`multicall` function.
* The :solidity:`sumBalances` function uses :solidity:`multicall` to calculate
  the sum of balances of several addresses.
* We show how to use :cvl:`DISPATCH` list to verify this contract.

.. dropdown:: Multicall contract

   .. _multicall_code:

   .. literalinclude:: ../../../training-examples/lesson6/multicall/Multicall.sol
      :language: solidity
      :lines: 5-
      :lineno-start: 5
      :emphasize-lines: 7
      :caption: :clink:`Multicall</certora/training-examples/lesson6/multicall/Multicall.sol>`

Spec
^^^^
* The spec
  :clink:`Multicall.spec</certora/training-examples/lesson6/multicall/Multicall.spec>`
  has two simple rules:

  #. An example showing a call trace for :solidity:`sumOfThree`.
  #. A rule verifying :solidity:`sumOfThree`.

* To resolve the :solidity:`address(this).delegatecall` from line 11 of
  :ref:`multicall_code`, we add the :cvl:`DISPATCH` list below.
  This includes only the :cvl:`getBalance` among its options.

.. cvlinclude:: ../../../training-examples/lesson6/multicall/Multicall.spec
   :language: cvl
   :lines: 2-10
   :emphasize-lines: 6-8
   :caption: Dispatch list with one function

Alternatively, we can include all the functions of the contract in the
:cvl:`DISPATCH` list as shown below. But this will be slower.

.. cvlinclude:: ../../../training-examples/lesson6/multicall/Multicall_slow.spec
   :language: cvl
   :lines: 2-10
   :emphasize-lines: 6-8
   :caption: :clink:`Dispatch list with entire contract</certora/training-examples/lesson6/multicall/Multicall_slow.spec>`

Reports
^^^^^^^
* `Dispatch list example report`_ -- for
  :clink:`Multicall.spec</certora/training-examples/lesson6/multicall/Multicall.spec>`.
* `Dispatch list with entire contract report`_ -- for
  :clink:`Multicall_slow.spec</certora/training-examples/lesson6/multicall/Multicall_slow.spec>`
  (using the entire contract in the :cvl:`DISPATCH` list).

.. Links
   -----

.. _Catch unresolved-calls entry:
   https://docs.certora.com/en/latest/docs/cvl/methods.html#catch-unresolved-calls-entry

.. _Dispatch list example report:
   https://prover.certora.com/output/98279/f22e78bc57ee4641a4316097b6c2f5a1?anonymousKey=320b318e16f5cee2d3d9b23157bea2c9466a3485

.. _Dispatch list with entire contract report:
   https://prover.certora.com/output/98279/60ca5b8f93194a3781d71933fa04f62b?anonymousKey=1a5d5b25e2c7d2325e78fc546df8722d6ca416b5

