.. index::
   single: sum

Sum pattern
===========
This pattern is commonly used to prove in ERC-20 that the :solidity:`totalSupply` is the
sum of all balances. We'll use the :clink:`EETH</src/EETH.sol>` contract for this example.


Spec
----
* Below is the ghost, hook and invariant.
* Report: `sum pattern report`_.

.. literalinclude:: ../../../specs/lesson5/sum_pattern.spec
   :language: cvl
   :lines: 6-25
   :caption: :clink:`sum_pattern.spec</certora/specs/lesson5/sum_pattern.spec>`


Notes
-----

Using consequences
^^^^^^^^^^^^^^^^^^
* Once this sum invariant is proved, we can require its consequences as needed.
* For example, consider the :cvl:`sumOfTwo` invariant below.
* The :cvl:`sumOfTwo` invariant is violated (see `sum of two report`_) since the
  :cvl:`totalSharesIsSumOfShares` invariant is insufficient for the Prover to deduce this.
* Instead, use :cvl:`require shares(user1) + shares(user2) <= sumOfShares` if needed.

.. cvlinclude:: ../../../specs/lesson5/sum_pattern.spec
   :cvlobject: sumOfTwo
   :caption: :clink:`sumOfTwo</certora/specs/lesson5/sum_pattern.spec>`

.. caution::

   Recall that :cvl:`require` statements can be *unsound*. Use them sparingly and ensure
   they are indeed consequences of the invariant you proved.


.. Links
   -----

.. _sum pattern report:
   https://prover.certora.com/output/98279/f1dcdda0b33c4cb49d3157ef7340206e?anonymousKey=238a1ffed3a788874ef8f2f701c776747063a9f8

.. _sum of two report:
   https://prover.certora.com/output/98279/ed453a165b8442508f3654befc358cdd?anonymousKey=1c2ffd0b85cd724ce7875f456cfd1b4a7af80c86
