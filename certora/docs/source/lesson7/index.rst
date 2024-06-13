Spec checking
=============

Slides
------
* `Spec checking slides`_ link.


Main example
------------
* The main example will be the three invariants for
  :clink:`EtherFiNode</src/EtherFiNode.sol>` from
  :clink:`EtherFiNode_forall.spec</certora/specs/lesson7/EtherFiNode_forall.spec>`.
* `EtherFiNode invariants report`_ link, using
  :clink:`EtherFiNode_forall.conf</certora/confs/lesson7/EtherFiNode_forall.conf>`

* working with `sanity checking flag`_ :

  * `with rule_sanity basic`_
  * `with rule_sanity advanced`_
  notice that advanced has false positives 

* understanding vacuity on ``initialize()`` function with the ``coverage_info`` flag: `unsat core`_ 

* mutation-testing with the command ``certoraMutate certora/confs/lesson7/EtherFiNode_forall.conf`` on both manual mutations and automatic ones. Result is via mail and in the dashboard under mutations runs. likn of `_mutations run`_ 


.. dropdown:: EtherFiNode_forall.spec

   .. literalinclude:: ../../../specs/lesson7/EtherFiNode_forall.spec
      :language: cvl
      :caption: :clink:`EtherFiNode_forall.spec</certora/specs/lesson7/EtherFiNode_forall.spec>`


.. Links
   -----

.. _Spec checking slides:
   https://docs.google.com/presentation/d/1E6orv97uF18qEI3nxNOyfBb5nxlQqAdmL5TBBor1HZs/edit?usp=sharing

.. _EtherFiNode invariants report:
   https://prover.certora.com/output/98279/e31e6d10ce29425393b65045f3de2e50?anonymousKey=76fe7f24b05b1cdf2e797b2d84afcb3df6fd45cc

.. _sanity checking flag: 
   https://docs.certora.com/en/latest/docs/prover/checking/sanity.html 

.. _with rule_sanity basic:
   https://prover.certora.com/output/40726/d99f5ee4a6824e55b97e082fb5255c62/?anonymousKey=e6c8188f28167a55208b99ec96be9bb55e05f20c

.. _with rule_sanity advanced:
   https://prover.certora.com/output/40726/d221923eb8e24b109b0c2625c0e68db4/?anonymousKey=657330ded2b336e7671b9ac84a5dd461e7c7537c

.. _unsat_core:
   https://prover.certora.com/output/40726/ec31bfcaf322407b9c6cc24eec49ab15/UnsatCoreVisualisation.html?anonymousKey=6a711afa6db2a2a0358486834cde40956e6e752e

.. _mutations run:
   https://mutation-testing.certora.com/?id=d9db0adf-5f95-4c76-9365-ff1e55693f45&anonymousKey=30ff9215-76fb-4a9d-8e24-9b6296ee27b0   
