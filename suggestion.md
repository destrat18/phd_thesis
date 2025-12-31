
# Title suggestions for Chapters 2–7

This file proposes short, informative alternatives for **chapter** and **section/subsection** titles in Chapters 2–7.

Scope and constraints I followed
- I scanned every `chapters/**/*.tex` file and based suggestions on the actual section text (definitions, models, algorithms, and experimental narratives).
- I did **not** propose changes for the per-chapter `\section{Introduction}` headings (you explicitly allow that repeated title).
- I avoided generic repeats like “Our Algorithm” / “Experimental Results” across chapters; each **recommended** title below is intended to be unique across the thesis.
- I kept titles short (typically 2–6 words) and biased toward *what the section establishes* (model, theorem toolkit, cost model, etc.), not the internal name of the tool/algorithm.

---

## Chapter 2 (Preliminaries)

### Chapter title
Current: **Preliminaries**
- Recommended: **Foundations**
- Alternatives: **Technical Background**; **Models and Notation**

### Section: Blockchain and Smart Contracts
What it covers: blockchain objects, consensus/mining, incentives, fees, smart contracts, and key design choices.
- Recommended: **Blockchain Model and Incentives**
- Alternatives: **Consensus, Fees, and Contracts**; **Blockchains and Smart Contracts**

### Section: Bitcoin Architecture
What it covers: PoW, longest-chain consensus, UTXO, fees, forks, and double-spending/confirmations.
- Recommended: **Bitcoin: PoW, UTXO, Finality**
- Alternatives: **Bitcoin Protocol Mechanics**; **Bitcoin Consensus and Fees**

### Section: Cardano Architecture
What it covers: EUTXO, PoS/Ouroboros slots/epochs, stake pools, reward sources, and block validity constraints (dependencies/conflicts/size).
- Recommended: **Cardano: EUTXO and Block Validity**
- Alternatives: **Cardano Transaction Constraints**; **Cardano Execution and Rewards**

### Section: Ethereum Architecture
What it covers: account/world-state model, EVM execution, gas, fee decomposition, out-of-gas behavior, and why costs can be polynomial.
- Recommended: **Ethereum Execution and Gas Accounting**
- Alternatives: **EVM State and Gas**; **Gas, Fees, and Reverts**

### Section: Graph Sparsity Parameters
What it covers: **(currently empty in `chapters/prelim/prelim-parameters.tex`)**.
Rigor note: Because there is no content yet, I can only propose titles *conditional on intended content*. If this section is meant to support later chapters (treewidth/treedepth/pathwidth), a title should reflect that.
- Recommended (if it defines width/depth measures used later): **Graph Width Measures**
- Alternatives: **Sparsity Parameters for Graphs**; **Decomposition Parameters**

### Section: Algebraic-Geometry Theorems
What it covers: positivity/entailment certificates (Farkas, Handelman, Putinar), SOS templates, and reductions to quadratic constraints.
- Recommended: **Positivity Certificates for Constraints**
- Alternatives: **Entailments to Quadratic Constraints**; **Algebraic Tools for Synthesis**

#### Subsection: Farkas Lemma
What it covers: linear entailments and feasibility certificates; reduction recipe (algorithm/pseudocode).
- Recommended: **Linear Certificates (Farkas)**
- Alternatives: **Farkas Certificates**; **Linear Entailment Reduction**

#### Subsection: Handelman's Theorem
What it covers: compact polytope assumptions, monoids of constraints, representing positive polynomials via monoid combinations.
- Recommended: **Monoid Certificates (Handelman)**
- Alternatives: **Handelman Representation**; **Compact-Polytope Positivity**

#### Subsection: Putinar's Positivstellensatz
What it covers: SOS multipliers, semialgebraic sets, SOS templates via PSD matrices / Cholesky.
- Recommended: **SOS Certificates (Putinar)**
- Alternatives: **Putinar Positivity**; **Semialgebraic SOS Proofs**

#### Subsection: Summary of the Mathematical Tools
What it covers: a decision summary comparing applicability (linear/nonlinear antecedents/consequents) and practical escalation strategy.
- Recommended: **Toolchain Summary and Applicability**
- Alternatives: **When Each Theorem Applies**; **Certificate Selection Summary**

---

## Chapter 3 (Optimal Block Production)

### Chapter title
Current: **Optimal Block Production Problem**
- Recommended: **Revenue-Optimal Block Assembly**
- Alternatives: **Fee-Maximizing Block Production**; **Optimal Block Construction**

### Section: Modeling Block Construction on Cardano
What it covers: formal optimization problem under size limit, dependencies/conflicts via DCGs, and why treedepth is the right sparsity notion for 1-second slots.
- Recommended: **Cardano Block Selection Model**
- Alternatives: **Cardano DCG Optimization Model**; **Block Constraints and Objective**

#### Subsection: Treedepth
What it covers: treedepth decompositions, computability at small depth, and ancestor-set notation used by the DP.
- Recommended: **Treedepth Decompositions**
- Alternatives: **Treedepth as Sparsity**; **Ancestor-Based Decomposition**

### Section: Treedepth-Based Optimal Block Construction for Cardano
What it covers: exact DP on canonical subgraphs keyed by ancestor subsets and remaining capacity; runtime in $O(n\,k\,2^d\,d^2)$.
- Recommended: **Exact DP via Treedepth (Cardano)**
- Alternatives: **Treedepth DP for Optimal Blocks**; **Ancestor-Set Dynamic Programming**
- More suggestions: **Optimal Block Packing with Treedepth**; **DP on Ancestor Subsets**; **Treedepth-Constrained Block Assembly**; **Cardano Block Optimization via Treedepth**; **Dynamic Programming for Cardano Blocks**; **Treedepth-Driven Block Construction**

### Section: Runtime and Revenue Improvements on Real-World Cardano Data
What it covers: Pixiu implementation, treedepth distribution, runtime (<1s), and quantified revenue improvements on 50 days of blocks.
- Recommended: **Cardano Evaluation on Real Blocks**
- Alternatives: **Empirical Gains on Cardano**; **Runtime and Revenue Study (Cardano)**
- More suggestions: **Block-Level Revenue Analysis (Cardano)**; **Performance and Profitability on Cardano**; **Cardano Block Optimization Results**; **Real-World Cardano Block Study**; **Cardano Block Assembly: Runtime and Revenue**; **Cardano: Empirical Runtime and Revenue Gains**; **Cardano Block Evaluation: Speed and Revenue**

### Section: A Randomized Framework for Ethereum Block Construction
What it covers: why state-dependent gas makes ordering hard; formal objective (tips under gas limit); motivates neighborhood-based sparsity and randomized sampling.
- Recommended: **State-Dependent Fee Optimization (Ethereum)**
- Alternatives: **Ethereum Block Ordering Model**; **Block Construction with Dynamic Fees**

#### Subsection: Problem Definition
What it covers: formal model for blocks as ordered sequences with nonce constraints; definitions of $\delta_{\tx}$, gas, tips, and the constrained maximization.
- Recommended: **Fee-Maximizing Block Formalization**
- Alternatives: **Formal Mining Objective**; **Block Revenue Objective**

#### Subsection: Ethereum Architecture
What it covers: fee mechanics (base fee + tip), gas accounting/refunds/oog, and why transaction interactions can be context-dependent.
- Recommended: **Fee Mechanics and State Dependence**
- Alternatives: **Gas, Tips, and World State**; **Ethereum Fee Model Essentials**

### Section: Our Mining Framework for Ethereum
What it covers: sampling permutations, decision-tree neighborhood discovery, rule extraction, ILP encoding, solver step; emphasizes locality of interactions.
- Recommended: **Sampling-to-ILP Block Optimization**
- Alternatives: **Learning Local Gas Rules**; **Neighborhood-Based Block Ordering**

### Section: Revenue Gains and Runtime on Real-World Ethereum Blocks
What it covers: 50k-block mempool dataset, 12s budget, baselines (real miners + reference greedy), large annualized revenue improvements.
- Recommended: **Large-Scale Ethereum Revenue Study**
- Alternatives: **Real-Block Evaluation (Ethereum)**; **Runtime and Revenue Results (Ethereum)**

---

## Chapter 4 (Derivatives and Bitcoin Security)

### Chapter title
Current: **Options and Futures Imperil Bitcoin's Security**
- Recommended: **Derivatives-Driven Reorg Incentives**
- Alternatives: **Derivatives and Bitcoin Security**; **Shorting Incentives for Reorgs**

### Section: Overview of the Attack
What it covers: majority (reorg) attacks, why <50% can still succeed given persistence, why costs are lower than expected, and how derivatives create incentives.
- Recommended: **Reorg Attacks: Feasibility and Motives**
- Alternatives: **Reorg Threat Model**; **From Hashpower to Incentives**

### Section: Block-reverting as a Minority Miner
What it covers: Markov-chain modeling of 6-block reorg attempts; two variants (publish at 0 vs 1); exact success probabilities via value iteration.
- Recommended: **Markov Analysis of Minority Reorgs**
- Alternatives: **Minority Reorg Success Probabilities**; **Stochastic Model of Reversions**

### Section: Cost of the Attack
What it covers: cost model to acquire hash share $q$, ASIC price tiers, converting desired share to required added hashpower, historical sensitivity.
- Recommended: **Cost Model for Hashpower Share**
- Alternatives: **ASIC-Based Attack Costing**; **Hashpower Acquisition Costs**

### Section: Bitcoin Derivatives
What it covers: futures/options primer, short exposure, empirical scale of derivatives volume vs attack costs, discussion of detectability via open interest.
- Recommended: **Derivatives as Attack Payoff**
- Alternatives: **Short Exposure via Futures/Options**; **Market Incentives for Attacks**

---

## Chapter 5 (Parametric Gas Bounds)

### Chapter title
Current: **Gas Upper-bounds for Smart Contracts**
- Recommended: **Parametric Gas Upper Bounds**
- Alternatives: **Gas-Bound Synthesis for Contracts**; **Sound Gas Upper Bounds**

### Section: Gas Upper Bound as Synthesis Problem
What it covers: motivation (library safety, out-of-gas vulnerabilities), formal problem ($B_f$ parametric bounds), undecidability/abstractions, why polynomial bounds matter.
- Recommended: **Problem: Parametric Gas-Bound Synthesis**
- Alternatives: **Formulating Gas-Bound Synthesis**; **Why Polynomial Gas Bounds**

### Section: Our Algorithm
What it covers: pipeline from EVM bytecode → CFG/RBR → PTS, remaining-gas polynomials on cutsets, entailment generation, and reduction via theorems to quadratic constraints.
- Recommended: **Bytecode-to-PTS Bound Synthesis**
- Alternatives: **Remaining-Gas Polynomial Method**; **Constraint-Based Gas Synthesis**

#### Subsection: Intermediate Representations and Polynomial Transition Systems
What it covers: CFG/RBR extraction (EthIR/GASTAP), PTS formalism, valuations/runs/cutsets/basic paths, sound abstractions for non-polynomial ops.
- Recommended: **From Bytecode to PTS**
- Alternatives: **PTS Modeling Pipeline**; **Intermediate Forms and PTS**

#### Subsection: Synthesizing Parametric Gas Bounds
What it covers: remaining-gas polynomial templates at cutpoints, entailment constraints for basic paths, translation to quadratic constraints via certificate theorems.
- Recommended: **Remaining-Gas Template Synthesis**
- Alternatives: **Entailment-Driven Bound Synthesis**; **Template Constraints for Gas**

#### Subsection: Soundness, Completeness and Complexity
What it covers: formal guarantees (soundness + semi-completeness), assumptions (bounded vars, polynomiality), and complexity discussion.
- Recommended: **Correctness and Complexity Guarantees**
- Alternatives: **Soundness and Completeness**; **Guarantees and Limits**

### Section: Experimental Results
What it covers: implementation pipeline and solvers, benchmark suite (24k contracts), comparisons vs `solc` and GASTAP, coverage and tightness results.
- Recommended: **Evaluation on 24k Ethereum Contracts**
- Alternatives: **Benchmarking Gas Bounds**; **Empirical Comparison of Bounds**

---

## Chapter 6 (DEX Routing)

### Chapter title
Current: **Optimal Routing for Decentralized Exchanges**
- Recommended: **Scalable Routing in DEX Graphs**
- Alternatives: **DEX Routing at Scale**; **Robust DEX Route Finding**

### Section: Exchange Rates as a Routing Problem
What it covers: DeFi/AMMs, token/pool graph model, shortest-path via $-\log$ rates, negative cycles as arbitrage, and why existing methods fail at scale.
- Recommended: **DEX Routing as Shortest Paths**
- Alternatives: **Graph Model of Exchange Rates**; **Routing with Arbitrage Cycles**

### Section: Our Algorithm
What it covers: treewidth-based preprocessing (tree decomposition → chordal completion + PEO), enforcing DPC, answering SSSP queries efficiently; handles negative cycles conservatively.
- Recommended: **Treewidth-Preprocessed Routing Queries**
- Alternatives: **Chordal-DPC Routing Framework**; **Structure-Aware SSSP Routing**

#### Subsection: Formulating DEX prices as a graph problem
What it covers: AMM/CFMM pricing, spot vs trade price (focus on spot), directed weighted graph abstraction, and shortest-path transformation.
- Recommended: **AMM Spot Prices as Graph Weights**
- Alternatives: **DEX Graph Construction**; **Log-Weight Routing Model**

#### Subsection: The Algorithm Overview
What it covers: offline preprocessing vs online queries; completion+PEO; DPC; correctness/complexity theorem.
- Recommended: **Preprocess-and-Query Pipeline**
- Alternatives: **Offline/Online Routing Framework**; **From Tree Decomposition to Queries**

#### Subsection: Handling Dynamic Edge Additions
What it covers: incremental updates when new pools/edges appear; preserving efficiency under graph dynamics.
- Recommended: **Incremental Pool Updates**
- Alternatives: **Dynamic Graph Updates**; **Edge-Addition Handling**

### Section: Experimental Results
What it covers: Uniswap snapshot dataset, token-set scaling to 100k, measured treewidth growth, update dynamics, success rates under negative cycles, runtime comparisons.
- Recommended: **Uniswap Scalability and Robustness Study**
- Alternatives: **Empirical Routing Performance (Uniswap)**; **Scaling to 100k Tokens**

---

## Chapter 7 (Compiler Gas Superoptimization)

### Chapter title
Current: **Gas Optimization for Smart Contract Compilers**
- Recommended: **Compiler-Level Gas Superoptimization**
- Alternatives: **Optimizing Bytecode Gas Costs**; **Superoptimization for Smart Contracts**

### Section: Gas Optimization Problem
What it covers: why gas optimization matters, `solc --optimize`, superoptimization framing, Syrup 2.0 Max-SMT approach, and illustrative example.
- Recommended: **Gas Optimization via Superoptimization**
- Alternatives: **Superoptimization for EVM Blocks**; **Motivation and Prior Work**

### Section: Our Algorithm
What it covers: empirical motivation (SMT scalability vs block size), compositionality intuition, DP over all split points using Syrup as a black box.
- Recommended: **Compositional DP over Basic Blocks**
- Alternatives: **Dynamic Programming for Block Rewrites**; **Divide-and-Optimize Strategy**

### Section: Experimental Results
What it covers: benchmarks from Syrup paper, aggregate gas savings (baseline vs Syrup vs DP), histograms, and real-world block traces.
- Recommended: **Results on Syrup Benchmark Suite**
- Alternatives: **Empirical Gas Savings Study**; **Evaluation on Real Contracts**

