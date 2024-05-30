Reentrancy vulnerability check
==============================

The check
---------

Basic idea
^^^^^^^^^^

   The contract's storage between function calls satisfies the invariants of the spec
   when assuming external calls do not re-enter the contract.
   
* Let's call the contract's expected storage state between calls a *"good"* state.
* The storage state during a function call might change to a *"bad"* state, i.e. a
  state which might not satisfy the invariants.
* An external call to a non-view function while the storage is in a *"bad"* state
  exposes the contract to exploits.
* Solution (partial): ensure such external calls are done only when the storage
  is in a good state. So for every function either:

  * external calls are done before any storage access, or
  * external calls are done only after all storage access.

Spec
^^^^
* The spec uses `Persistent ghosts`_, which are not affected by reverts of havocs.
* Using hooks, the spec sets these ghost flags if storage was accessed before or
  after an external call.
* The spec contains a single parametric rule, asserting there are no functions with
  storage access both before and after an external call.

.. literalinclude:: ../../../specs/lesson5/reentrancy.spec
   :language: cvl
   :lines: 12-
   :caption: :clink:`Reentrancy spec</certora/specs/lesson5/reentrancy.spec>`


Unguarded pool example
----------------------

Pool code
^^^^^^^^^
* The :clink:`UnguardedPool</certora/training-examples/lesson5/pool/UnguardedPool.sol>` 
  inherits from a basic :clink:`ERC20</certora/training-examples/lesson5/pool/ERC20.sol>`
  contract.
* The pool mints shares in return for depositing the underlying assets,
  and transfers an amount in the underlying asset when the user withdraws shares.
* The :solidity:`nonReentrant` modifier has been disabled in this contract.
* The pool has an additional vulnerability due to the way it calculates the conversion
  between amount and shares.

.. dropdown:: UnguardedPool code

   .. literalinclude:: ../../../training-examples/lesson5/pool/UnguardedPool.sol
      :language: solidity
      :lines: 11-
      :emphasize-lines: 4-6

Config
^^^^^^
* The config used (see below) does not use any linking, as these are not needed for this
  check.
* It requires additional ``prover_args``, see below.

.. literalinclude:: ../../../training-examples/lesson5/pool/reentrancy_unguarded.conf
   :language: json
   :emphasize-lines: 15
   :caption: :clink:`Reentrancy config for UnguardedPool</certora/training-examples/lesson5/pool/reentrancy_unguarded.conf>`

Report
^^^^^^
* `Reentrancy report for UnguardedPool`_.
* Only the :solidity:`deposit` function failed the report.
* The reason for the fail is that the pool mints shares *after* calling
  :solidity:`asset.transferFrom`.
* A malicious asset can exploit this vulnerability (this scenario is unlikely).
 
.. literalinclude:: ../../../training-examples/lesson5/pool/UnguardedPool.sol
   :language: solidity
   :lines: 25-42
   :emphasize-lines: 16-17
   :caption: :clink:`deposit</certora/training-examples/lesson5/pool/UnguardedPool.sol>`

Exploiting the pool
^^^^^^^^^^^^^^^^^^^
* We write a malicious asset, that front runs deposits to the pool, this is done
  in the :solidity:`tranferFrom` function. This is the
  :clink:`ExploitingAsset</certora/training-examples/lesson5/pool/ExploitingAsset.sol>`.
* We write a spec that instructs the Prover to find an example of a successful exploit, in
  :clink:`ReentrancyExploit.spec</certora/training-examples/lesson5/pool/ReentrancyExploit.spec>`.
* The config requires an additional parameter: ``contract_recursion_limit``, see
  :clink:`ReentrancyExploit.conf</certora/training-examples/lesson5/pool/ReentrancyExploit.conf>`.
* The report shows an example of successfully exploiting the pool,
  see `Exploiting the pool report`_.

.. literalinclude:: ../../../training-examples/lesson5/pool/ExploitingAsset.sol
   :language: solidity
   :lines: 17-
   :caption: :clink:`ExploitingAsset</certora/training-examples/lesson5/pool/ExploitingAsset.sol>`

.. cvlinclude:: ../../../training-examples/lesson5/pool/ReentrancyExploit.spec
   :cvlobject: reentrancyExploitExample
   :caption: :clink:`ReentrancyExploit.spec</certora/training-examples/lesson5/pool/ReentrancyExploit.spec>`

.. literalinclude:: ../../../training-examples/lesson5/pool/ReentrancyExploit.conf
   :language: json
   :emphasize-lines: 8-9, 13
   :caption: :clink:`ReentrancyExploit.conf</certora/training-examples/lesson5/pool/ReentrancyExploit.conf>`


Testing on current contracts
----------------------------
* `Reentrancy report for EETH`_
* `Reentrancy report for NodeOperatorManager`_
* `Reentrancy report for AuctionManager`_ -- shows a violation in two functions, one is
  declared :solidity:`nonReentrant`, but the other one isn't!


.. Links
   -----

.. _Persistent ghosts:
   https://docs.certora.com/en/latest/docs/cvl/ghosts.html#ghosts-vs-persistent-ghosts

.. _Reentrancy report for UnguardedPool:
   https://prover.certora.com/output/98279/48d3d06fa0f149d183c3493b92058934?anonymousKey=1643a79f491a4254d7a8d60a0713639c5ea91409

.. _Exploiting the pool report:
   https://prover.certora.com/output/98279/324f0a836d864c7fab5a5c4558ec6c49?anonymousKey=dd7e6dab1e0a84ec0e7143b36790a11bc10d880f

.. _Reentrancy report for EETH:
   https://prover.certora.com/output/98279/c113832ece98408a92b847d58e4bf749?anonymousKey=f7a0612c0ae77f5c117632c6a2d2c1a92172ed0a

.. _Reentrancy report for NodeOperatorManager:
   https://prover.certora.com/output/98279/858500931e34478a948d65a903fd3ed9?anonymousKey=bf30f08bf9e33cf77c0bd2cb908e94bd0a4527ef

.. _Reentrancy report for AuctionManager:
   https://prover.certora.com/output/98279/308bdf50471e4fdbb846d0b80aa08b01?anonymousKey=8244daa3fad3a828138a1170cac99b5ce2f30484
