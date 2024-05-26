.. graphviz::
   :align: center
   :class: only-dark

   digraph {
       graph [
           bgcolor="#1a1a1a" color=gold fontcolor=bisque
           labelloc=t nodesep=0.5 rankdir=TB ranksep=1.0 margin=0
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

       LiquidityPool [
           color=cyan
           label="{LiquidityPool|
           <stakingManager> stakingManager\l |
           <nodesManager> nodesManager\l |
           <membershipManager> membershipManager\l |
           <tNft> tNft\l |
           <eETH> eETH\l |
           <withdrawRequestNFT> withdrawRequestNFT\l |
           <auctionManager> auctionManager\l |
           <liquifier> liquifier\l}"
       ]

       EETH [label="{EETH|<liquidityPool> liquidityPool\l}"]
       StakingManager [
           label="{StakingManager|
           <auctionManager> auctionManager\l |
           <nodesManager> nodesManager\l |
           <BNFTInterfaceInstance> BNFTInterfaceInstance\l |
           <TNFTInterfaceInstance> TNFTInterfaceInstance}"
       ]
       EtherFiNodesManager [
           label="{EtherFiNodesManager| <tnft> tnft\l | <bnft> bnft\l |
           <stakingManagerContract> stakingManagerContract\l}"
       ]
       MembershipManager
       TNFT
       BNFT
       EETH
       WithdrawRequestNFT
       AuctionManager
       Liquifier

       LiquidityPool:stakingManager -> StakingManager
       LiquidityPool:nodesManager -> EtherFiNodesManager
       LiquidityPool:membershipManager -> MembershipManager
       LiquidityPool:tNft -> TNFT
       LiquidityPool:eETH -> EETH
       LiquidityPool:withdrawRequestNFT -> WithdrawRequestNFT
       LiquidityPool:auctionManager -> AuctionManager
       LiquidityPool:liquifier -> Liquifier
       EETH:liquidityPool -> LiquidityPool
       StakingManager:auctionManager -> AuctionManager
       StakingManager:nodesManager -> EtherFiNodesManager
       StakingManager:BNFTInterfaceInstance -> BNFT
       StakingManager:TNFTInterfaceInstance -> TNFT
       EtherFiNodesManager:tnft -> TNFT
       EtherFiNodesManager:bnft -> BNFT
       EtherFiNodesManager:stakingManagerContract -> StakingManager
   }

.. graphviz::
   :align: center
   :class: only-light

   digraph {
       graph [
           bgcolor=gray90 color=goldenrod fontcolor=gray9
           labelloc=t nodesep=0.5 rankdir=TB ranksep=1.0 margin=0
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

       LiquidityPool [
           color=blue
           label="{LiquidityPool|
           <stakingManager> stakingManager\l |
           <nodesManager> nodesManager\l |
           <membershipManager> membershipManager\l |
           <tNft> tNft\l |
           <eETH> eETH\l |
           <withdrawRequestNFT> withdrawRequestNFT\l |
           <auctionManager> auctionManager\l |
           <liquifier> liquifier\l}"
       ]

       EETH [label="{EETH|<liquidityPool> liquidityPool\l}"]
       StakingManager [
           label="{StakingManager|
           <auctionManager> auctionManager\l |
           <nodesManager> nodesManager\l |
           <BNFTInterfaceInstance> BNFTInterfaceInstance\l |
           <TNFTInterfaceInstance> TNFTInterfaceInstance}"
       ]
       EtherFiNodesManager [
           label="{EtherFiNodesManager| <tnft> tnft\l | <bnft> bnft\l |
           <stakingManagerContract> stakingManagerContract\l}"
       ]
       MembershipManager
       TNFT
       BNFT
       EETH
       WithdrawRequestNFT
       AuctionManager
       Liquifier

       LiquidityPool:stakingManager -> StakingManager
       LiquidityPool:nodesManager -> EtherFiNodesManager
       LiquidityPool:membershipManager -> MembershipManager
       LiquidityPool:tNft -> TNFT
       LiquidityPool:eETH -> EETH
       LiquidityPool:withdrawRequestNFT -> WithdrawRequestNFT
       LiquidityPool:auctionManager -> AuctionManager
       LiquidityPool:liquifier -> Liquifier
       EETH:liquidityPool -> LiquidityPool
       StakingManager:auctionManager -> AuctionManager
       StakingManager:nodesManager -> EtherFiNodesManager
       StakingManager:BNFTInterfaceInstance -> BNFT
       StakingManager:TNFTInterfaceInstance -> TNFT
       EtherFiNodesManager:tnft -> TNFT
       EtherFiNodesManager:bnft -> BNFT
       EtherFiNodesManager:stakingManagerContract -> StakingManager
   }
