Exercises
=========

Ghosts and hooks
----------------

NodeOperatorManager
^^^^^^^^^^^^^^^^^^^
Using ghosts and hooks show for
:clink:`NodeOperatorManager</src/NodeOperatorManager.sol>` that:

#. :solidity:`addressToOperatorData[_user].keysUsed` can be changed only by certain
   functions.
#. Except for :solidity:`initializeOnUpgrade` all other functions can only change the
   :solidity:`keysUsed` only for a single user.

AuctionManager
^^^^^^^^^^^^^^
Show for :clink:`AuctionManager</src/AuctionManager.sol>` that each function only changes
:solidity:`admins` for a single address.

----

Storage
-------
#. Show for :clink:`EETH</src/EETH.sol>` that transferring from :solidity:`address a`
   to :solidity:`address b` amount :math:`x` followed by amount :math:`y` is the same
   as transferring :math:`x + y`.
#. Write a rule for :clink:`LiquidityPool</src/LiquidityPool.sol>` stating that
   depositing :math:`x` followed by depositing :math:`y` is the same as
   depositing :math:`x + y`.

   * *(Optional)* Try running this rule.

----

Side entrance
-------------
* This is based on `Damn Vulnerable DeFi Challenge #4 - Side Entrance`_.
* The
  :clink:`SideEntranceLenderPool</certora/training-examples/lesson5/side_entrance/SideEntranceLenderPool.sol>`
  shown below has a vulnerability.
* The
  :clink:`FlashLoanReceiverHarness</certora/training-examples/lesson5/side_entrance/FlashLoanReceiverHarness.sol>`
  is a contract that can receive the loan and "randomly" do various actions.
* **Exercise.** Write a :cvl:`satisfy` rule that exposes the vulnerability.

.. tip::

   Use ``optimistic_fallback`` and ``contract_recursion_limit`` in the config.

.. dropdown:: SideEntranceLenderPool

   .. literalinclude:: ../../../training-examples/lesson5/side_entrance/SideEntranceLenderPool.sol
      :language: solidity
      :lines: 14-
      :caption: :clink:`SideEntranceLenderPool</certora/training-examples/lesson5/side_entrance/SideEntranceLenderPool.sol>`

.. dropdown:: FlashLoanReceiverHarness

   .. literalinclude:: ../../../training-examples/lesson5/side_entrance/FlashLoanReceiverHarness.sol
      :language: solidity
      :lines: 10-
      :caption: :clink:`FlashLoanReceiverHarness</certora/training-examples/lesson5/side_entrance/FlashLoanReceiverHarness.sol>`

----

String and hooks
----------------
One possible revert cause is an incorrectly encoded string in storage. This lesson guides
you through identifying this revert cause and checking for it.

The contract
^^^^^^^^^^^^
* The contract :clink:`StrIssue</certora/training-examples/lesson5/string/StrIssue.sol>`
  has an array of structs and functions that manipulate them.

.. dropdown:: StrIssue

   .. literalinclude:: ../../../training-examples/lesson5/string/StrIssue.sol
      :language: solidity
      :lines: 10-
      :caption: :clink:`StrIssue</certora/training-examples/lesson5/string/StrIssue.sol>`

Revert example exercise
^^^^^^^^^^^^^^^^^^^^^^^
Write a spec containing two rule:

#. A rule asserting that :cvl:`push` reverts only when :cvl:`e.msg.value` is non-zero,
#. A rule asserting that :cvl:`getData` reverts only when :cvl:`e.msg.value` is non-zero
   or when the index is out of bounds.

Running the spec you will discover that both rules are violated.

Revert cause
^^^^^^^^^^^^
In general, storage variables are stored in particular slots, where each slot
has 32 bytes, see `Layout of State Variables in Storage`_.
Strings have a particular encoding in storage, meant to avoid wasting storage,
detailed in `Bytes and String Layout in Storage`_. In short:

* If the length of the string, denoted :math:`l`, is 31 bytes or less, 
  the entire string will be
  stored in the relevant slot, and the lowest-order byte will hold
  :math:`2 \cdot l` (twice the length of the string).
* If the length of the string :math:`l` is 32 bytes or more, the value of the slot
  will be :math:`2 \cdot l + 1`.

So values like 3, or 100 cannot be stored in the slot of a string. When reading
a string, Solidity reverts if the value in the slot is invalid. Note that solidity
also reads the existing value *before writing* a new string. So a write could also
potentially result in a revert.

Identifying the cause exercise
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Use a :cvl:`persistent ghost` and a hook to identify when an illegal string is read.
#. Add this cause to the two revert rules, and ensure they are verified.

**Notes.**

* To hook into loads from the slot of the :cvl:`y` field use:

  .. code-block:: cvl
   
     hook Sload bytes32 slotValue structArray[INDEX uint256 index].(offset 32)

* To convert :cvl:`bytes32` to :cvl:`uint256` use:

  .. code-block:: cvl

     uint256 encoded;
     require to_bytes32(encoded) == slotValue;

Verifying all strings are legally encoded exercise
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#. Using a ghost and an :cvl:`Sstore` hook, write an invariant verifying that the
   strings in the field :cvl:`y` of the struct are legally encoded.
#. Run the invariant, it should provide a counter example for the :cvl:`dirty` function.


.. Links
   -----

.. _Damn Vulnerable DeFi Challenge #4 - Side Entrance:
   https://www.damnvulnerabledefi.xyz/challenges/side-entrance/

.. _Layout of State Variables in Storage:
   https://docs.soliditylang.org/en/stable/internals/layout_in_storage.html

.. _Bytes and String Layout in Storage:
   https://docs.soliditylang.org/en/stable/internals/layout_in_storage.html#bytes-and-strin
