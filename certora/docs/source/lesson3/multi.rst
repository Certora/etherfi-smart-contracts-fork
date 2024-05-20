Multi contract setup
====================

Simple exchange contract
------------------------
Our main example will be this simple
:clink:`Exchange</certora/training-examples/lesson3/exchange/src/Exchange.sol>` contract.
The contract exchanges amounts in one token (:solidity:`_tokenA`) to amounts in another
token (:solidity:`_tokenB`).

.. dropdown:: :clink:`Exchange.sol</certora/training-examples/lesson3/exchange/src/Exchange.sol>`

   .. literalinclude:: ../../../training-examples/lesson3/exchange/src/Exchange.sol
      :language: solidity
      :lines: 6-

The rule
^^^^^^^^
The rule we intend to verify is the following.

.. cvlinclude:: ../../../training-examples/lesson3/exchange/certora/specs/Exchange.spec
   :cvlobject: transferIntegrity
   :caption: :clink:`transferIntegrity</certora/training-examples/lesson3/exchange/certora/specs/Exchange.spec>`


Doing nothing
-------------
We can use a config file like the ones we used before.

.. literalinclude:: ../../../training-examples/lesson3/exchange/certora/confs/DoingNothing.conf
   :language: json
   :caption: :clink:`DoingNothing.conf</certora/training-examples/lesson3/exchange/certora/confs/DoingNothing.conf>`

* The report: `Doing nothing report`_.
* The Prover needs a *concrete implementation* for all functions called to work.
* If an implementation is missing, the Prover

  #. Notes there is an *unresolved call*.
  #. Uses an **automatic** *over-approximation* for the effects of the call.

* If the function is a *view* function, the Prover will use a *non-deeterministic*
  return value (see `NONDET summary`_).
* Otherwise, it will *havoc* all contracts except the calling contract. This means
  other contracts' storage can have any values. The calling contract's storage
  is unchanged, since we **assume** it has re-entrancy protection
  (see `HAVOC summaries`_).


Linking
-------
Using *linking* (see `link`_) we provide the Prover with a concrete implementation
for particular contracts.

.. literalinclude:: ../../../training-examples/lesson3/exchange/certora/confs/Linking.conf
   :language: json
   :caption: :clink:`Linking.conf</certora/training-examples/lesson3/exchange/certora/confs/Linking.conf>`

* This links :solidity:`tokenA = ERC20DummyA` and :solidity:`tokenB = ERC20DummyB`.
* In CVL each :solidity:`contract` has *one unique* instance.
* This means the Prover will not consider other cases, such as when
  :solidity:`tokenA == tokenB`.
* The report is at: `Linking report`_.

.. graphviz::
   :align: center
   :class: only-dark

   digraph {
       graph [
           bgcolor="#1a1a1a" color=gold fontcolor=bisque
           labelloc=t nodesep=0.25 rankdir=BT ranksep=0.5 margin=0
       ]
       node [
           color=gold fontcolor=bisque fillcolor=gray10
           shape=Mrecord fontname="DejaVu Sans Mono" fontsize=8
       ]
       edge [
           color=gold fontcolor=bisque
           arrowhead=normal
           fontname="DejaVu Sans Mono" fontsize=8
       ]

       ERC20 [label="ERC20"]

       Exchange [label="{Exchange|<tokenA> tokenA\l | <tokenB> tokenB\l}"]
       DummyA [label="ERC20DummyA"]
       DummyB [label="ERC20DummyB"]

       DummyA -> ERC20
       DummyB -> ERC20
       Exchange:tokenA -> DummyA [
           label="link" color=orange weight=0 style=dashed arrowhead=open
       ]
       Exchange:tokenB -> DummyB [
           label="link" color=orange weight=0 style=dashed arrowhead=open
       ]
   }

.. graphviz::
   :align: center
   :class: only-light

   digraph {
       graph [
           bgcolor=gray90 color=goldenrod fontcolor=gray9
           labelloc=t nodesep=0.25 rankdir=BT ranksep=0.5 margin=0
       ]
       node [
           color=goldenrod fontcolor=gray9
           shape=Mrecord fontname="DejaVu Sans Mono" fontsize=8
       ]
       edge [
           color=goldenrod fontcolor=gray9
           arrowhead=normal
           fontname="DejaVu Sans Mono" fontsize=8
       ]

       ERC20 [label="ERC20"]

       Exchange [label="{Exchange|<tokenA> tokenA\l | <tokenB> tokenB\l}"]
       DummyA [label="ERC20DummyA"]
       DummyB [label="ERC20DummyB"]

       DummyA -> ERC20
       DummyB -> ERC20
       Exchange:tokenA -> DummyA [
           label="link" color=orange weight=0 style=dashed arrowhead=open
       ]
       Exchange:tokenB -> DummyB [
           label="link" color=orange weight=0 style=dashed arrowhead=open
       ]
   }

Using Dispatcher
----------------
This lets the Prover to choose which implementation to use. The main change is
done in the :cvl:`methods` block in the spec.

.. literalinclude:: ../../../training-examples/lesson3/exchange/certora/confs/Dispatcher.conf
   :language: json
   :caption: :clink:`Linking.conf</certora/training-examples/lesson3/exchange/certora/confs/Dispatcher.conf>`

.. cvlinclude:: ../../../training-examples/lesson3/exchange/certora/specs/ExchangeDispatcher.spec
   :cvlobject: methods
   :caption: :clink:`methods block of ExchangeDispatcher.spec</certora/training-examples/lesson3/exchange/certora/specs/ExchangeDispatcher.spec>`

* Running with the dispatcher finds a counter example, where :cvl:`tokenA == tokenB`.
  See `Dispatcher report`_.
* Using dispatcher is useful when there are several possible known implementations.
* :cvl:`DISPATCHER` is a type of function summary, which we'll see later.
* Note: empty dispatching can result in a vacuous rule.

.. graphviz::
   :align: center
   :class: only-dark

   digraph {
       graph [
           bgcolor="#1a1a1a" color=gold fontcolor=bisque
           labelloc=t nodesep=0.25 rankdir=BT ranksep=0.5 margin=0
       ]
       node [
           color=gold fontcolor=bisque fillcolor=gray10
           shape=Mrecord fontname="DejaVu Sans Mono" fontsize=8
       ]
       edge [
           color=gold fontcolor=bisque
           arrowhead=normal
           fontname="DejaVu Sans Mono" fontsize=8
       ]

       ERC20 [label="ERC20"]

       Exchange [label="{Exchange|<tokenA> tokenA\l | <tokenB> tokenB\l}"]
       DummyA [label="ERC20DummyA"]
       DummyB [label="ERC20DummyB"]

       DummyA -> ERC20
       DummyB -> ERC20

       edge [
           color=red
           fontcolor=bisque
           arrowhead=open
           fontname="DejaVu Sans Mono"
           fontsize=8
           weight=0
           style=dotted
       ]
       Exchange:tokenA -> DummyA
       Exchange:tokenA -> DummyB
       Exchange:tokenB -> DummyA
       Exchange:tokenB -> DummyB
   }

.. graphviz::
   :align: center
   :class: only-light

   digraph {
       graph [
           bgcolor=gray90 color=goldenrod fontcolor=gray9
           labelloc=t nodesep=0.25 rankdir=BT ranksep=0.5 margin=0
       ]
       node [
           color=goldenrod fontcolor=gray9
           shape=Mrecord fontname="DejaVu Sans Mono" fontsize=8
       ]
       edge [
           color=goldenrod fontcolor=gray9
           arrowhead=normal
           fontname="DejaVu Sans Mono" fontsize=8
       ]

       ERC20 [label="ERC20"]

       Exchange [label="{Exchange|<tokenA> tokenA\l | <tokenB> tokenB\l}"]
       DummyA [label="ERC20DummyA"]
       DummyB [label="ERC20DummyB"]

       DummyA -> ERC20
       DummyB -> ERC20

       edge [
           color=red
           fontcolor=bisque
           arrowhead=open
           fontname="DejaVu Sans Mono"
           fontsize=8
           weight=0
           style=dotted
       ]
       Exchange:tokenA -> DummyA
       Exchange:tokenA -> DummyB
       Exchange:tokenB -> DummyA
       Exchange:tokenB -> DummyB
   }

.. tab-set::

   .. tab-item:: Option 1

      .. graphviz::
         :align: center
         :class: only-dark
      
         digraph {
             graph [
                 bgcolor="#1a1a1a" color=gold fontcolor=bisque
                 labelloc=t nodesep=0.25 rankdir=LR ranksep=2 margin=0
             ]
             node [
                 color=gold fontcolor=bisque fillcolor=gray10
                 shape=Mrecord fontname="DejaVu Sans Mono" fontsize=8
             ]
             edge [
                 color=gold
                 fontcolor=bisque
                 arrowhead=open
                 fontname="DejaVu Sans Mono"
                 fontsize=8
                 style=dotted
             ]
      
             subgraph cluster_exchange {
                 graph [color=greenyellow label="Exchange.transferAtoB" labelloc=t margin=8]
                 node [color=greenyellow]
      
                 Atrans [label="tokenA.transferFrom"]
                 Btrans [label="tokenB.transfer"]
             }
             DummyA [label="ERC20DummyA"]
             DummyB [label="ERC20DummyB"]
      
             Atrans -> DummyA [style=invis]
             Btrans -> DummyB [style=invis]

             Atrans -> DummyA [color=red weight=0]
             Btrans -> DummyB [color=red weight=0]
         }

      .. graphviz::
         :align: center
         :class: only-light
      
         digraph {
             graph [
                 bgcolor=gray90 color=goldenrod fontcolor=gray9
                 labelloc=t nodesep=0.25 rankdir=LR ranksep=2 margin=0
             ]
             node [
                 color=goldenrod fontcolor=gray9
                 shape=Mrecord fontname="DejaVu Sans Mono" fontsize=8
             ]
             edge [
                 color=goldenrod
                 fontcolor=gray9
                 arrowhead=open
                 fontname="DejaVu Sans Mono"
                 fontsize=8
                 style=dotted
             ]
      
             subgraph cluster_exchange {
                 graph [color=darkslategray label="Exchange.transferAtoB" labelloc=t margin=8]
                 node [color=darkslategray]
      
                 Atrans [label="tokenA.transferFrom"]
                 Btrans [label="tokenB.transfer"]
             }
             DummyA [label="ERC20DummyA"]
             DummyB [label="ERC20DummyB"]
      
             Atrans -> DummyA [style=invis]
             Btrans -> DummyB [style=invis]

             Atrans -> DummyA [color=red weight=0]
             Btrans -> DummyB [color=red weight=0]
         }

   .. tab-item:: Option 2

      .. graphviz::
         :align: center
         :class: only-dark
      
         digraph {
             graph [
                 bgcolor="#1a1a1a" color=gold fontcolor=bisque
                 labelloc=t nodesep=0.25 rankdir=LR ranksep=2 margin=0
             ]
             node [
                 color=gold fontcolor=bisque fillcolor=gray10
                 shape=Mrecord fontname="DejaVu Sans Mono" fontsize=8
             ]
             edge [
                 color=gold
                 fontcolor=bisque
                 arrowhead=open
                 fontname="DejaVu Sans Mono"
                 fontsize=8
                 style=dotted
             ]
      
             subgraph cluster_exchange {
                 graph [color=greenyellow label="Exchange.transferAtoB" labelloc=t margin=8]
                 node [color=greenyellow]
      
                 Atrans [label="tokenA.transferFrom"]
                 Btrans [label="tokenB.transfer"]
             }
             DummyA [label="ERC20DummyA"]
             DummyB [label="ERC20DummyB"]
      
             Atrans -> DummyA [style=invis]
             Btrans -> DummyB [style=invis]
      
             Atrans -> DummyB [color=cyan weight=0]
             Btrans -> DummyA [color=cyan weight=0]
         }

      .. graphviz::
         :align: center
         :class: only-light
      
         digraph {
             graph [
                 bgcolor=gray90 color=goldenrod fontcolor=gray9
                 labelloc=t nodesep=0.25 rankdir=LR ranksep=2 margin=0
             ]
             node [
                 color=goldenrod fontcolor=gray9
                 shape=Mrecord fontname="DejaVu Sans Mono" fontsize=8
             ]
             edge [
                 color=goldenrod
                 fontcolor=gray9
                 arrowhead=open
                 fontname="DejaVu Sans Mono"
                 fontsize=8
                 style=dotted
             ]
      
             subgraph cluster_exchange {
                 graph [color=darkslategray label="Exchange.transferAtoB" labelloc=t margin=8]
                 node [color=darkslategray]
      
                 Atrans [label="tokenA.transferFrom"]
                 Btrans [label="tokenB.transfer"]
             }
             DummyA [label="ERC20DummyA"]
             DummyB [label="ERC20DummyB"]
      
             Atrans -> DummyA [style=invis]
             Btrans -> DummyB [style=invis]
      
             Atrans -> DummyB [color=blue weight=0]
             Btrans -> DummyA [color=blue weight=0]
         }

   .. tab-item:: Option 3

      .. graphviz::
         :align: center
         :class: only-dark
      
         digraph {
             graph [
                 bgcolor="#1a1a1a" color=gold fontcolor=bisque
                 labelloc=t nodesep=0.25 rankdir=LR ranksep=2 margin=0
             ]
             node [
                 color=gold fontcolor=bisque fillcolor=gray10
                 shape=Mrecord fontname="DejaVu Sans Mono" fontsize=8
             ]
             edge [
                 color=gold
                 fontcolor=bisque
                 arrowhead=open
                 fontname="DejaVu Sans Mono"
                 fontsize=8
                 style=dotted
             ]
      
             subgraph cluster_exchange {
                 graph [color=greenyellow label="Exchange.transferAtoB" labelloc=t margin=8]
                 node [color=greenyellow]
      
                 Atrans [label="tokenA.transferFrom"]
                 Btrans [label="tokenB.transfer"]
             }
             DummyA [label="ERC20DummyA"]
             DummyB [label="ERC20DummyB"]
      
             Atrans -> DummyA [style=invis]
             Btrans -> DummyB [style=invis]
      
             Atrans -> DummyA [color=yellow weight=0]
             Btrans -> DummyA [color=yellow weight=0]
         }

      .. graphviz::
         :align: center
         :class: only-light
      
         digraph {
             graph [
                 bgcolor=gray90 color=goldenrod fontcolor=gray9
                 labelloc=t nodesep=0.25 rankdir=LR ranksep=2 margin=0
             ]
             node [
                 color=goldenrod fontcolor=gray9
                 shape=Mrecord fontname="DejaVu Sans Mono" fontsize=8
             ]
             edge [
                 color=goldenrod
                 fontcolor=gray9
                 arrowhead=open
                 fontname="DejaVu Sans Mono"
                 fontsize=8
                 style=dotted
             ]
      
             subgraph cluster_exchange {
                 graph [color=darkslategray label="Exchange.transferAtoB" labelloc=t margin=8]
                 node [color=darkslategray]
      
                 Atrans [label="tokenA.transferFrom"]
                 Btrans [label="tokenB.transfer"]
             }
             DummyA [label="ERC20DummyA"]
             DummyB [label="ERC20DummyB"]
      
             Atrans -> DummyA [style=invis]
             Btrans -> DummyB [style=invis]
      
             Atrans -> DummyA [color=goldenrod4 weight=0]
             Btrans -> DummyA [color=goldenrod4 weight=0]
         }

   .. tab-item:: Option 4

      .. graphviz::
         :align: center
         :class: only-dark
      
         digraph {
             graph [
                 bgcolor="#1a1a1a" color=gold fontcolor=bisque
                 labelloc=t nodesep=0.25 rankdir=LR ranksep=2 margin=0
             ]
             node [
                 color=gold fontcolor=bisque fillcolor=gray10
                 shape=Mrecord fontname="DejaVu Sans Mono" fontsize=8
             ]
             edge [
                 color=gold
                 fontcolor=bisque
                 arrowhead=open
                 fontname="DejaVu Sans Mono"
                 fontsize=8
                 style=dotted
             ]
      
             subgraph cluster_exchange {
                 graph [color=greenyellow label="Exchange.transferAtoB" labelloc=t margin=8]
                 node [color=greenyellow]
      
                 Atrans [label="tokenA.transferFrom"]
                 Btrans [label="tokenB.transfer"]
             }
             DummyA [label="ERC20DummyA"]
             DummyB [label="ERC20DummyB"]
      
             Atrans -> DummyA [style=invis]
             Btrans -> DummyB [style=invis]
             
             Atrans -> DummyB [color=green weight=0]
             Btrans -> DummyB [color=green weight=0]
         }

      .. graphviz::
         :align: center
         :class: only-light
      
         digraph {
             graph [
                 bgcolor=gray90 color=goldenrod fontcolor=gray9
                 labelloc=t nodesep=0.25 rankdir=LR ranksep=2 margin=0
             ]
             node [
                 color=goldenrod fontcolor=gray9
                 shape=Mrecord fontname="DejaVu Sans Mono" fontsize=8
             ]
             edge [
                 color=goldenrod
                 fontcolor=gray9
                 arrowhead=open
                 fontname="DejaVu Sans Mono"
                 fontsize=8
                 style=dotted
             ]
      
             subgraph cluster_exchange {
                 graph [color=darkslategray label="Exchange.transferAtoB" labelloc=t margin=8]
                 node [color=darkslategray]
      
                 Atrans [label="tokenA.transferFrom"]
                 Btrans [label="tokenB.transfer"]
             }
             DummyA [label="ERC20DummyA"]
             DummyB [label="ERC20DummyB"]
      
             Atrans -> DummyA [style=invis]
             Btrans -> DummyB [style=invis]
             
             Atrans -> DummyB [color=green weight=0]
             Btrans -> DummyB [color=green weight=0]
         }


.. Links
   -----

.. _Doing nothing report:
   https://prover.certora.com/output/98279/38131d5b807e4018a931b33e066f789a?anonymousKey=49cd49e2b48c94a5339d30a0f0575f0c963ce7b6

.. _NONDET summary:
   https://docs.certora.com/en/latest/docs/cvl/methods.html#view-summaries-always-constant-per-callee-constant-and-nondet

.. _HAVOC summaries:
   https://docs.certora.com/en/latest/docs/cvl/methods.html#havoc-summaries-havoc-all-and-havoc-ecf

.. _link: https://docs.certora.com/en/latest/docs/prover/cli/options.html#link

.. _Linking report:
   https://prover.certora.com/output/98279/ba797540ce0d4e2b995a8e66a346ccc9?anonymousKey=aa6982ca71c7845848b5184dac6c3ba7b44b5be6

.. _Dispatcher report:
   https://prover.certora.com/output/98279/85d2d326deb742a7bc4391c084bd0ff7?anonymousKey=6a3c0644935d5abc5a88d118358cd266dc797b81
