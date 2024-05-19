Invariant vs. Parametric
========================

Writing an invariant as a rule
------------------------------

The invariant
^^^^^^^^^^^^^

   If a user's total keys is non-zero, then the user is registered.

.. cvlinclude:: ../../../specs/lesson2/Invariants.spec
   :cvlobject: nonZeroTotalKeysIsRegistered
   :caption: :clink:`nonZeroTotalKeysIsRegistered</certora/specs/lesson2/Invariants.spec>`


Correct translation to a rule
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. important::

   This only translates the **induction step** to a rule.

.. cvlinclude:: ../../../specs/lesson2/Invariants.spec
   :cvlobject: nonZeroTotalKeysIsRegistered_Parametric
   :caption: :clink:`nonZeroTotalKeysIsRegistered_Parametric</certora/specs/lesson2/Invariants.spec>`

Report: `report of nonZeroTotalKeysIsRegistered as a rule`_.


Parametric rules can be wrong
-----------------------------

* Parametric rules do not have the induction base
* So they can prove a property that is unreachable

Example
^^^^^^^
Here is a parametric rule saying that keys used is always greater than total keys,
provided total keys is non-zero and the user is *not registered*. This is a condition
that cannot be reached by the system.

.. cvlinclude:: ../../../specs/lesson2/Invariants.spec
   :cvlobject: wrongParametric
   :caption: :clink:`wrongParametric</certora/specs/lesson2/Invariants.spec>`

Report: `report of wrong parametric rule`_.


.. Links
   -----

.. _report of nonZeroTotalKeysIsRegistered as a rule:
   https://prover.certora.com/output/98279/db8e8210af8a436a91916f9e336cfbef?anonymousKey=7fb470aeb391e25691a25f4ee941fbe0849c0b94

.. _report of wrong parametric rule:
   https://prover.certora.com/output/98279/90b70ecf8b044ef796b1bf2d64e49e25?anonymousKey=83b9fea6037f4111896a292828af5dc46a0fc455
