Liquidity pool setup
====================

Initial setup
-------------

Basic sanity
^^^^^^^^^^^^

Sanity rule and config
""""""""""""""""""""""
* For the initial test we'll use only a simple sanity rule.
* Checks sanity of all methods and call resolution.
* Allows us to verify number of iterations.

.. cvlinclude:: ../../../specs/liquidity/initial.spec
   :cvlobject: sanity
   :caption: :clink:`Sanity rule</certora/specs/liquidity/initial.spec>`

The basic initial config is minimal:

.. literalinclude:: ../../../confs/liquidity/initial.conf
   :language: json
   :caption: :clink:`Initial confiig</certora/confs/liquidity/initial.conf>`

Report
""""""
* Report: `initial report`_.
* All methods pass sanity, so loop iterations is fine.
* The report shows many call resolution issues.

Below is an example of missing link to :solidity:`EETH`. Since there is no link to
a relevant contract, the return value can be *anything*.
See :cvl:`NONDET` summary description in `View summaries`_.

.. image:: initial_report_resolution_eeth_nondet.png
   :alt: Call resolution for EETH

Here is another example. In this case the Prover uses :cvl:`HAVOC_ECF` summary which
assumes all contracts *other than* :solidity:`LiquidityPool` might have their storage
*arbitrarily changed*, see `Havoc summaries`_. Such a summary is sound if the contract
has *re-entrace guard*, but not in this case.

.. image:: initial_report_resolution_eeth_havoc_ecf.png
   :alt: Call resolution for EETH - HAVOC_ECF

----

Testing a proper rule
^^^^^^^^^^^^^^^^^^^^^
* Add the rule :cvl:`onlyOwnerCanChangeAdmin`, below.
* Run with a similar config.
* Report: `initial rule report`_.

.. cvlinclude:: ../../../specs/liquidity/initial_rule.spec
   :cvlobject: onlyOwnerCanChangeAdmin
   :caption: :clink:`onlyOwnerCanChangeAdmin</certora/specs/liquidity/initial_rule.spec>`

Violations
""""""""""
#. :solidity:`updateWhitelistedAddresses` -- requires use of ``optimistic_loop``,
   note that in the previous run the example used a single loop.
   Similarly for all the batch calls.
#. :solidity:`upgradeToAndCall` -- we've seen this before, cause by the
   :solidity:`delegatecall` instruction, we'll filter it out.

Retesting
"""""""""
* Filtered out :solidity:`upgradeToAndCall`.
* Added ``optimistic_loop``.
* See
  :clink:`initial_rule_improved.spec</certora/specs/liquidity/initial_rule_improved.spec>`
  and
  :clink:`initial_rule_improved.conf</certora/confs/liquidity/initial_rule_improved.conf>`.
* Report: `improved initial rule report`_.


----

Linking
-------

Parametric contracts
^^^^^^^^^^^^^^^^^^^^
* We're adding more contracts to the scene.
* By default, parametric rules and invariants will run on *all* functions from
  all these contracts.
* This can cause long running times.
* To limit the contracts used in parametric rules and invariants, use the
  ``parametric_contracts`` option, see `Parametric contracts`_. This can be *unsound*.
* For training we will only use the :solidity:`LiquidityPool` as a parametric contract.

.. code-block:: json

   "parametric_contracts": ["LiquidityPool"],

.. warning:: Limiting the parametric contracts can be *unsound*.

Initial linked contracts
^^^^^^^^^^^^^^^^^^^^^^^^

.. include:: graphs/initial_links.rst

Configuration
^^^^^^^^^^^^^

.. literalinclude:: ../../../confs/liquidity/links_initial.conf
   :language: json
   :caption: :clink:`Config file</certora/confs/liquidity/links_initial.conf>`

* Report: `linked pool initial config report`_.


Optimistic fallback
^^^^^^^^^^^^^^^^^^^
* In the report the Prover suggests using ``optimistic_fallback``, see image below.
* This will prevent unresolved calls to fallback from arbitrarily changing storage
  of contracts (*havocing*).
* See `Optimistic fallback`_.

.. image:: ./links_initial_optimistic_fallback.png
   :alt: Optimistic fallback recommended

.. warning::

   Using optimistic fallback implies you assume fallback functions will not change
   storage.

Optimistic hashing
^^^^^^^^^^^^^^^^^^
* Similar to loops unrolling, the Prover "unrolls" hashed arrays, if the array is
  too long it reports a violation.
* To avoid this case use ``optimistic_hashing`` which will cause the Prover to
  *assume* that the hashed arrays length is at most ``hashing_length_bound``.
* See `Optimistic hashing`_ and `Modeling of Hashing in the Certora Prover`_.

.. image:: ./links_initial_optimistic_hashing.png
   :alt: Optimistic hashing recommended

.. warning::

   Like all assumptions, using ``optimistic_hashing`` may be unsound.


Calls to EtherFiNode
--------------------

Example
^^^^^^^
.. literalinclude:: ../../../../src/EtherFiNodesManager.sol
   :language: solidity
   :lines: 566-578
   :emphasize-lines: 10
   :caption: :clink:`EtherFiNodesManager line 575</src/EtherFiNodesManager.sol>`

Simple solution
^^^^^^^^^^^^^^^
* Add :clink:`EtherFiNode</src/EtherFiNode.sol>` to the scene.
* Use dispatcher on all non-view :solidity:`EtherFiNode` functions.

Better solution
^^^^^^^^^^^^^^^
* Create several contracts inheriting from :clink:`EtherFiNode</src/EtherFiNode.sol>`
  and add them to the scene.
* Use dispatcher on *all* :solidity:`EtherFiNode` functions.


Call to IERC721ReceiverUpgradeable
----------------------------------

Example
^^^^^^^
.. literalinclude:: ../../../../src/LiquidityPool.sol
   :language: solidity
   :lines: 237-250
   :emphasize-lines: 9
   :caption: :clink:`LiquidityPool.requestMembershipNFTWithdraw</src/LiquidityPool.sol>`

.. literalinclude:: ../../../../src/WithdrawRequestNFT.sol
   :language: solidity
   :lines: 57-66
   :emphasize-lines: 6
   :caption: :clink:`WithdrawRequestNFT.requestWithdraw</src/WithdrawRequestNFT.sol>`

.. literalinclude:: ../../../../lib/openzeppelin-contracts-upgradeable/contracts/token/ERC721/ERC721Upgradeable.sol
   :language: solidity
   :lines: 267-277
   :emphasize-lines: 8
   :caption: :clink:`ERC721Upgradeable</lib/openzeppelin-contracts-upgradeable/contracts/token/ERC721/ERC721Upgradeable.sol>`

.. literalinclude:: ../../../../lib/openzeppelin-contracts-upgradeable/contracts/token/ERC721/ERC721Upgradeable.sol
   :language: solidity
   :lines: 434-456
   :emphasize-lines: 8
   :caption: :clink:`ERC721Upgradeable</lib/openzeppelin-contracts-upgradeable/contracts/token/ERC721/ERC721Upgradeable.sol>`

Solution
^^^^^^^^
* Add a mock to the scene, e.g.
  :clink:`ERC721ReceiverMockUpgradeable</lib/openzeppelin-contracts-upgradeable/contracts/mocks/ERC721ReceiverMockUpgradeable.sol>`.
* Use :cvl:`DISPATCHER(true)` for the call to :solidity:`onERC721Received`.


Calls to IDepositContract
-------------------------
.. todo:: The link ``StakingManager:depositContractEth2=ETHDepositMock``.

Example
^^^^^^^
.. literalinclude:: ../../../../src/LiquidityPool.sol
   :language: solidity
   :lines: 359-378
   :emphasize-lines: 19
   :caption: :clink:`LiquidityPool.batchApproveRegistration</src/LiquidityPool.sol>`

.. literalinclude:: ../../../../src/StakingManager.sol
   :language: solidity
   :lines: 194-211
   :emphasize-lines: 16
   :caption: :clink:`StakingManager.batchApproveRegistration</src/StakingManager.sol>`

.. literalinclude:: ../../../../src/StakingManager.sol
   :language: solidity
   :lines: 49-51
   :emphasize-lines: 2
   :caption: :clink:`StakingManager.depositContractEth2</src/StakingManager.sol>`

.. literalinclude:: ../../../../src/interfaces/IDepositContract.sol
   :language: solidity
   :lines: 9-39
   :emphasize-lines: 1
   :caption: :clink:`IDepositContract</src/interfaces/IDepositContract.sol>`

Solution
^^^^^^^^
* Use a mock :clink:`ETHDepositMock</test/eigenlayer-mocks/ETHDepositMock.sol>`.
* Note this file requires Solidity 0.8.12 compiler -- use ``solc_map``.

.. literalinclude:: ../../../../test/eigenlayer-mocks/ETHDepositMock.sol
   :language: solidity
   :lines: 7-
   :caption: :clink:`ETHDepositMock</test/eigenlayer-mocks/ETHDepositMock.sol>`


Calls to IEigenPodManager
-------------------------

Example
^^^^^^^
.. literalinclude:: ../../../../src/LiquidityPool.sol
   :language: solidity
   :lines: 268-272, 314-332
   :caption: :clink:`LiquidityPool.batchDepositAsBnftHolder</src/LiquidityPool.sol>`

.. literalinclude:: ../../../../src/StakingManager.sol
   :language: solidity
   :lines: 134-142
   :emphasize-lines: 8
   :caption: :clink:`StakingManager.batchDepositWithBidIds</src/StakingManager.sol>`

.. literalinclude:: ../../../../src/StakingManager.sol
   :language: solidity
   :lines: 339-367
   :emphasize-lines: 27
   :caption: :clink:`StakingManager._processDeposits</src/StakingManager.sol>`

.. literalinclude:: ../../../../src/StakingManager.sol
   :language: solidity
   :lines: 429-448
   :emphasize-lines: 8
   :caption: :clink:`StakingManager._processDeposit</src/StakingManager.sol>`

.. literalinclude:: ../../../../src/EtherFiNodesManager.sol
   :language: solidity
   :lines: 349-363
   :emphasize-lines: 9
   :caption: :clink:`EtherFiNodesManager.allocateEtherFiNode</src/EtherFiNodesManager.sol>`

.. literalinclude:: ../../../../src/StakingManager.sol
   :language: solidity
   :lines: 248-258
   :emphasize-lines: 8
   :caption: :clink:`StakingManager.instantiateEtherFiNode</src/StakingManager.sol>`

.. literalinclude:: ../../../../src/EtherFiNode.sol
   :language: solidity
   :lines: 552-558
   :emphasize-lines: 4
   :caption: :clink:`EtherFiNode.createEigenPod</src/EtherFiNode.sol>`


* Report: `Call to IEigenPodManager report`_.



.. Links
   -----

.. _Modeling of Hashing in the Certora Prover:
   https://docs.certora.com/en/latest/docs/prover/approx/hashing.html

.. _Optimistic hashing:
   https://docs.certora.com/en/latest/docs/prover/cli/options.html#optimistic-hashing

.. _Optimistic fallback:
   https://docs.certora.com/en/latest/docs/prover/cli/options.html#optimistic-fallback

.. _View summaries:
   https://docs.certora.com/en/latest/docs/cvl/methods.html#view-summaries-always-constant-per-callee-constant-and-nondet

.. _Havoc summaries:
   https://docs.certora.com/en/latest/docs/cvl/methods.html#havoc-summaries-havoc-all-and-havoc-ecf

.. _Parametric contracts:
   https://docs.certora.com/en/latest/docs/prover/cli/options.html#parametric-contracts-contract-name

.. _Call to IEigenPodManager report:
   https://prover.certora.com/output/98279/603d7f041e46446a9afa3755db399741/?anonymousKey=b5ba63525b67eed409cc4ada2ca2529fd039c2b8

.. _Final report:
   https://prover.certora.com/output/98279/4ffb8fd67b2c49aba32108dbb925991d?anonymousKey=10848f89d1c1c950e58d7217d787690d48c62638


.. _initial report:
   https://prover.certora.com/output/98279/113b6f56febd4d4a8aa10a399deea45d?anonymousKey=434e8d7793559531458daa309ad06970586b7f96

.. _initial rule report:
   https://prover.certora.com/output/98279/4a8dad63da7143429772b8b07230ce8f?anonymousKey=59a8f064aa6a11672ff953ceb4b6dcc7922278d2

.. _improved initial rule report:
   https://prover.certora.com/output/98279/327e365d45024a9aaaeeb9d825ce360f?anonymousKey=db854e209e815e8abecaeb66d4e4a5e6b974f30f


.. _linked pool initial config report:
   https://prover.certora.com/output/98279/e819a92093fc4b5bb33aa27697deb2bf?anonymousKey=d5cc018d13f6f7cb78c9120815879122a4a96aca
