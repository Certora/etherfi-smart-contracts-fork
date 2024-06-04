Method entries and call resolution order
========================================

* See `Methods entry patterns`_.

The examples below use the 
:clink:`Exchange</certora/training-examples/lesson3/exchange/src/Exchange.sol>` contract,
which we encountered in :ref:`multi_contract_exchange`.

.. dropdown:: :clink:`Exchange.sol</certora/training-examples/lesson3/exchange/src/Exchange.sol>`

   .. literalinclude:: ../../../training-examples/lesson3/exchange/src/Exchange.sol
      :language: solidity
      :lines: 6-

.. index::
   single: call-resolution

Call resolution order
---------------------

#. Calls from CVL are never summarized.
#. Exact function entries, where both contract and function signature are provided,
   e.g. :cvl:`function ERC20.balanceOf(address) external returns (uint256) => NONDET;`.
#. Wildcard contract, e.g. :cvl:`function _.fun(address a) ...;`.
#. Wildcard function, e.g. :cvl:`function ERC20._ external => NONDET;`.
#. `Catch unresolved-calls entry`_ using :cvl:`DISPATCH` list.


Direct calls from CVL
---------------------

.. literalinclude:: ../../../training-examples/lesson3/exchange/certora/specs/direct_cvl.spec
   :language: cvl
   :lines: 3-
   :emphasize-lines: 8, 17, 20
   :lineno-start: 3
   :caption: :clink:`direct_cvl.spec</certora/training-examples/lesson3/exchange/certora/specs/direct_cvl.spec>`

* The call to :cvl:`_ERC20DummyA.balanceOf` in line 19 uses the actual code of
  :cvl:`ERC20DummyA`, since it is called directly from CVL.
* The function :cvl:`Exchange.balanceA` called in line 22, contains a call to
  :cvl:`tokenA.balanceOf`. This call is summarized as :cvl:`NONDET` according to
  line 10.
* Hence the rule can be satisfied, see `direct calls from CVL report`_.


Exact function entries
----------------------

.. literalinclude:: ../../../training-examples/lesson3/exchange/certora/specs/exact_summary.spec
   :language: cvl
   :lines: 3-
   :emphasize-lines: 9, 12, 21
   :lineno-start: 3
   :caption: :clink:`exact_summary.spec</certora/training-examples/lesson3/exchange/certora/specs/exact_summary.spec>`

* In line 23:

  * The call to :cvl:`balanceA()` will return zero, as summarized in line 11. Since
    exact entry take precedence.
  * The call to :cvl:`balanceB()` will use a dispatcher, as summarized in line 14 using
    a wildcard contract.

* To satisfy the condition in line 23, the Prover must assume that :cvl:`tokenB` is
  `ERC20DummyB`.
* Report: `exact summary precedence report`_.


.. Links
   -----

.. _Methods entry patterns:
   https://docs.certora.com/en/latest/docs/cvl/methods.html#methods-entry-patterns

.. _Catch unresolved-calls entry:
   https://docs.certora.com/en/latest/docs/cvl/methods.html#catch-unresolved-calls-entry

.. _direct calls from CVL report:
   https://prover.certora.com/output/98279/6c013693c05a435f802872067f8fd538?anonymousKey=2292b257e871f589461b29de93e79a1f214ba3a4

.. _exact summary precedence report:
   https://prover.certora.com/output/98279/69e84fe0072c44938c9551d739db4c6e?anonymousKey=6954f67602ee2eaf25c12cfc3db572e0655d18bd
