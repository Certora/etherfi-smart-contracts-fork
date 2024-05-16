Preserved blocks and more
=========================


.. index::
   single: requireInvariant

requireInvariant
----------------

* E.g. :cvl:`requireInvariant(account);`
* Requires the invariant (with the given parameters) holds.
* This is *sound* in rules, as long as we verify the invariant itself.
* It is also *sound* to use inside :cvl:`preserved` blocks, even of the invariant itself,
  see `Invariants and induction`_.

In a nutshell, the reason :cvl:`requireInvariant` is sound inside a :cvl:`preserved`
block of the invariant itself, is that we assume the invariant in the *pre-state*.
In other words, we make it part of the induction assumption.

Example -- a parametric rule
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   **Property.** The number of used keys cannot decrease.

.. cvlinclude:: ../../../specs/lesson2/Invariants.spec
   :cvlobject: keysUsed unregisterdKeysUnused usedKeysNonDecreasing 
   :caption: :clink:`usedKeysNonDecreasing</certora/specs/lesson2/Invariants.spec>`

* Regarding the :cvl:`definition` see :ref:`definition_discussion` below.
* Note issue with :solidity:`initializeOnUpgrade` -- it can decrease the number of used
  keys.
* Report: `usedKeysNonDecreasing report without requireInvariant`_.
* Report: `usedKeysNonDecreasing report using requireInvariant`_.

.. index::
   single: definition
   :name: definition_discussion

Definition
""""""""""
A :cvl:`definition` in CVL is a macro, see `Definitions documentation`_.

----

.. index::
   single: preserved

Preserved blocks
----------------

* A way to handle particular functions differently within invariants, or to relate to
  the :cvl:`env`.
* Adds the preserved block as a pre-condition.
* See `Preserved blocks (from Documentation)`_ and also
  `Preserved blocks (from Tutorials)`_.

Example
^^^^^^^

   **Property.** The number of used keys for unregistered user is zero.

Without a preserved block
"""""""""""""""""""""""""
* Without using a :cvl:`preserved` block we get a counter example when calling
  :cvl:`fetchNextKeyIndex`.
* Report: `preserved blocks examples report`_.
* The counter example assumes :cvl:`_user` is not registered, but with
  *non-zero total keys* when :cvl:`fetchNextKeyIndex` is called.

.. cvlinclude:: ../../../specs/lesson2/Invariants.spec
   :cvlobject: unregisterdKeysUnused_NoPreserved
   :caption: :clink:`unregisterdKeysUnused_NoPreserved</certora/specs/lesson2/Invariants.spec>`

A generic preserved block
"""""""""""""""""""""""""
* One solution is to add a generic :cvl:`preserved` block, as below.
* Report: `preserved blocks examples report`_.

.. cvlinclude:: ../../../specs/lesson2/Invariants.spec
   :cvlobject: unregisterdKeysUnused
   :caption: :clink:`unregisterdKeysUnused</certora/specs/lesson2/Invariants.spec>`

Method specific preserved block
"""""""""""""""""""""""""""""""
* We can also use a preserved block for a specific method, see below.
* Report: `preserved blocks examples report`_.

.. cvlinclude:: ../../../specs/lesson2/Invariants.spec
   :cvlobject: unregisterdKeysUnused_MethodSpecific
   :caption: :clink:`unregisterdKeysUnused_MethodSpecific</certora/specs/lesson2/Invariants.spec>`


.. Links
   -----

.. _Preserved blocks (from Documentation):
   https://docs.certora.com/en/latest/docs/cvl/invariants.html#preserved-blocks

.. _Preserved blocks (from Tutorials):
   https://docs.certora.com/projects/tutorials/en/latest/lesson4_invariants/invariants/preserved.html

.. _Invariants and induction:
   https://docs.certora.com/en/latest/docs/cvl/invariants.html#invariants-and-induction

.. _Definitions documentation:
   https://docs.certora.com/en/latest/docs/cvl/defs.html

.. _usedKeysNonDecreasing report without requireInvariant:
   https://prover.certora.com/output/98279/055e41a949bd4418a0e79fc309767485?anonymousKey=9483ddf7100f5aef68a308b0f43068126e4b3342

.. _usedKeysNonDecreasing report using requireInvariant:
   https://prover.certora.com/output/98279/95a9d881a78f441e89b5f6a84199502a?anonymousKey=5db7bae8283ac4c77c37bbbb80f58c937ba58139

.. _preserved blocks examples report:
   https://prover.certora.com/output/98279/9866a5ef93c242de8c603b79ba7f7800?anonymousKey=f0e5a5e87d8f3c1f1da4e53ed082292522ace825
