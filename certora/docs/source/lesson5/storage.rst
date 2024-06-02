.. index::
   single: storage

Storage in CVL
==============

.. index::
   single: storage; direct access

Direct storage access
---------------------

* CVL allows to directly access storage elements from the spec. 
* This should be used prudently, as storage structure is usually an implementation
  detail. It is better that the spec would not rely on implementation details.

Example
^^^^^^^

.. cvlinclude:: ../../../specs/lesson1/Examples.spec
   :cvlobject: revertRule
   :caption: :clink:`From Examples.spec</certora/specs/lesson1/Examples.spec>`


.. index::
   single: lastStorage
   single: storage; lastStorage

Last storage
------------
* CVL allows saving storage states and comparing them.
* It also allows calling functions using a specified storage state.
* This is handy for comparing different operations that should result in the same
  outcome.

Syntax
^^^^^^
* The type is :cvl:`storage`
* CVL has a :cvl:`storage` variable which holds the last storage state called
  :cvl:`lastStorage`
* To run a function at a given storage state use :cvl:`f(e, args) at someStorage;`.

Example
^^^^^^^
* Using :cvl:`lastStorage` we check that in an ERC-20 contract, transferring an amount
  via an intermediary is the same as transferring directly to the final recipient.
  See :clink:`Storage.spec</certora/specs/lesson5/Storage.spec>`.
* We test this spec on :clink:`EETH</src/EETH.sol>`.
* Report: `Storage spec report`_.

.. cvlinclude:: ../../../specs/lesson5/Storage.spec
   :cvlobject: intermediaryTransfer
   :caption: :clink:`Storage.spec</certora/specs/lesson5/Storage.spec>`


.. Links
   -----

.. _Storage spec report:
   https://prover.certora.com/output/98279/eb355f19d68f47069202c37a89684208?anonymousKey=3135f851f84228d7c7bb3c6c8d8de7b781109c1a
