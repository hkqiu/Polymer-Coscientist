# Polymer Coscientist

**A self-evolving, experiment-grounded generative scientific agent for adaptive inverse design of functional polymers.**

This repository accompanies the paper:

> **A materials discovery agent for adaptive inverse design of functional polymers**
> Renming Wan, Haoke Qiu, Yurun Lyu, Jiahui Chen, Yusong Cao, Jiangai Long, Aolin Sun, Zhuoqun Han, Kuncheng Lv, Sheng Ma, Zhao-Yan Sun, Wantong Song
> State Key Laboratory of Polymer Science and Technology, Changchun Institute of Applied Chemistry, CAS

Code and data supporting the results in the manuscript will be released here.

## Overview

Scientific agents are beginning to reshape materials discovery, but in experimental chemical and materials systems they typically operate as correlation-driven optimizers and rarely generate explicit, reusable scientific knowledge. **Polymer Coscientist** is a self-evolving agentic framework that generates, evaluates, and learns from polymeric mRNA carriers through closed-loop experimental cycles.

The agent couples three decoupled components:

- **PolyTAO generator** — a fine-tuned generative model that proposes experimentally executable polymer candidates within a modular side-chain chemical space (epoxide / acrylate / dioxaphospholane oxide modules on a poly(L-lysine) backbone).
- **Performance-aware gating core** — a LightGBM-based probabilistic classifier that ranks generated candidates by their likelihood of high transfection performance.
- **Agent memory & reasoning layer** — a knowledge-accumulating reasoning module that reflects on experimental outcomes, extracts and revises design rules, and guides candidate prioritization across feedback cycles.

Across 50 rounds of self-evolution on 1,126 experimentally characterized polymer carriers, the agent accumulated 110 reusable design rules, including non-obvious structure–property relationships. In prospective discovery, the agent explored a validation space of ~50,000 candidate polymers and identified carriers with intramuscular mRNA transfection comparable to clinical-grade lipid nanoparticles (LNPs), achieving an ~20-fold enrichment in high-performance hit rate over empirical screening.

## Key results

- **Model-readable polymer action space**: 1,126 PLL-based polymer carriers synthesized and evaluated via automated liquid-handling within 3 days, providing ratio-resolved structure–transfection training data.
- **Decoupled learning architecture**: independent training of the PolyTAO generator, LightGBM gating model (AUC 0.96 for the high-transfection tier), and the agent's evolving knowledge memory.
- **Self-evolving knowledge**: 110 chronological design rules (64 high-confidence, 18 explicit revisions), with agent discrimination accuracy improving from 0.60 to 0.93 over 50 feedback rounds.
- **System-level enrichment**: integrating generation + gating + agent memory increased executable high-performance hits ~5.9-fold over generation alone (74.3 vs. 12.7 average hits per top-100 trial).
- **Prospective validation**: 10 of 15 agent-generated candidates exceeded the LipoMAX benchmark in vitro (66.7% hit rate vs. ~3.3% for empirical screening); in vivo intramuscular transfection matched SM102-LNP, with an unexpected spleen-biased biodistribution profile after intravenous administration.

## Repository status

This repository is being organized to accompany the manuscript. Code, trained model weights, and processed datasets will be added progressively as the paper moves through review and release. Planned contents include:

- Polymer generator (PolyTAO) fine-tuning and inference code
- Gating model (LightGBM) training and evaluation scripts
- Agent reasoning / knowledge-memory pipeline
- Processed experimental datasets (structure–transfection records)
- Analysis and figure-generation notebooks

## Citation

A citation entry will be added upon publication. If you use this work in the meantime, please cite the manuscript by title and author list above.

## Contact

For questions about this work, please contact the corresponding authors listed in the manuscript, or open an issue in this repository.

## License

This repository is released under the [Apache License 2.0](LICENSE) unless otherwise noted for specific datasets or third-party components.
