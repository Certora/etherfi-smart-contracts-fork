.. _auctionmanager_setup:

Auction manager setup
=====================

Configuration
-------------

Files
^^^^^
Requires only 2 files in the scene.

#. :clink:`AuctionManager.sol</src/AuctionManager.sol>`
#. :clink:`NodeOperatorManager.sol</src/NodeOperatorManager.sol>`

We can optionally add :clink:`MembershipManager.sol</src/MembershipManager.sol>`,
but that would require adding even more contracts. Instead we'll rely on the Prover's
over-approximation.

Linking
^^^^^^^

* Link :cvl:`AuctionManager.nodeOperatorManager` with :cvl:`NodeOperatorManager` contract.
* *Optional* Link :cvl:`NodeOperatorManager.auctionManagerContractAddress`
  with :cvl:`AuctionManager`.

Config
^^^^^^
.. literalinclude:: ../../../confs/lesson3/AuctionManager.conf
   :language: json
   :caption: :clink:`AuctionManager.conf</certora/confs/lesson3/AuctionManager.conf>`


Spec
----

.. index::
   single: sanity

Sanity rule
^^^^^^^^^^^
* A *sanity* rule verifies every method has at least one non-reverting computation path.
  In other words, the method is not *vacuous*.
* Most likely cause of a methods failing sanity is insufficient loop unroll iterations.
* There is a built in rule for that, see `Built in sanity rule`_.

.. cvlinclude:: ../../../specs/lesson3/AuctionManager.spec
   :cvlobject: sanity
   :caption: :clink:`sanity rule</certora/specs/lesson3/AuctionManager.spec>`

Invariant
^^^^^^^^^
* To check a setup it is advisable to have at least one more rule or invariant in addition
  to sanity.
* This invariant shows that the :cvl:`AuctionManager` contract is *always initialized*,
  which might be a problem?
* The method :cvl:`upgradeToAndCall` is filtered out for the usual reason.

.. cvlinclude:: ../../../specs/lesson3/AuctionManager.spec
   :cvlobject: isFilteredFunc alwaysInitialized
   :caption: :clink:`invariant</certora/specs/lesson3/AuctionManager.spec>`


Sanity problem
--------------

Current setup
^^^^^^^^^^^^^
* Report: `setup report`_.
* Sanity fails on :solidity:`NodeOperatorManager.setAuctionContractAddress`, since
  we already linked this address.

.. literalinclude:: ../../../../src/NodeOperatorManager.sol
   :language: solidity
   :start-at: function setAuctionContractAddress
   :end-before: Updates the address of the admin
   :emphasize-lines: 4
   :caption: :clink:`setAuctionContractAddress</src/NodeOperatorManager.sol>`

Minimal setup
^^^^^^^^^^^^^
* Setup is at
  :clink:`AuctionManager_minimal_setup.conf</certora/confs/lesson3/AuctionManager_minimal_setup.conf>`.
* It does not link :cvl:`NodeOperatorManager.auctionManagerContractAddress` to anything.
* Report: `minimal setup report`_.

.. literalinclude:: ../../../confs/lesson3/AuctionManager_minimal_setup.conf
   :language: json
   :caption: :clink:`minimal setup</certora/confs/lesson3/AuctionManager_minimal_setup.conf>`

Remaining sanity (vacuity) problem
""""""""""""""""""""""""""""""""""
* There is still a sanity problem with :cvl:`alwaysInitialized` invariant in the last
  report.
* The problem is with the :cvl:`initialize` function.
* This function reverts if the contract is already initialized -- which is the
  pre-condition of the invariant. Therefore, this function *always* reverts.

.. dropdown:: Initializer modifier

   .. literalinclude:: ../../../../lib/openzeppelin-contracts-upgradeable/contracts/proxy/utils/Initializable.sol
      :language: solidity
      :lines: 83-98
      :emphasize-lines: 4
      :caption: Initializable.sol

.. Links
   -----

.. _Built in sanity rule:
   https://docs.certora.com/en/latest/docs/cvl/builtin.html#basic-setup-checks-sanity

.. _setup report:
   https://prover.certora.com/output/98279/39c9a234531b4d68bf6e9af8669a091c?anonymousKey=81d0d9f2fa8ff5ae6bcde5a47c6800d174cc8fd9

.. _minimal setup report:
   https://prover.certora.com/output/98279/4ecf1872b2e747efbca10890e52f66a0?anonymousKey=9a301cb90d85a08294aa04111f843409e9c2137a
