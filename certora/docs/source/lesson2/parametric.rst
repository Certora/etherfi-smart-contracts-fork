.. index::
   single: parametric
   single: rule; parametric

Parametric rules
================

* For properties of *state transitions*, e.g. "The number of people voted cannot decrease"
* See `Parametric rules (from Documentation)`_ and
  `Parametric rules (from Tutorials)`_


Example
-------

The property
^^^^^^^^^^^^
The value of a user's :solidity:`totalKeys` can be changed in one of two ways:

#. By the user calling :solidity:`registerNodeOperator`.
#. By the owner calling :solidity:`initializeOnUpgrade`.

The rule
^^^^^^^^

.. cvlinclude:: ../../../specs/lesson2/Invariants.spec
   :cvlobject: totalKeysAllowedChanges
   :caption: :clink:`Invariants.spec</certora/specs/lesson2/Invariants.spec>`

.. note::

   We filter out :cvl:`upgradeToAndCall` for the same reason we did in
   :ref:`filter_out_upgrade`.


.. Links
   -----

.. _Parametric rules (from Tutorials):
   https://docs.certora.com/projects/tutorials/en/latest/lesson2_started/parametric.html

.. _Parametric rules (from Documentation):
   https://docs.certora.com/en/latest/docs/cvl/rules.html#parametric-rules
