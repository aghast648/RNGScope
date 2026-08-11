# RNGScope

**RNGScope** is an experimental research project for studying how well different analysis methods can detect structure, bias, entropy loss, and predictability in **synthetically generated random and pseudo-random sequences**.

The project combines **information theory, statistical randomness testing, machine learning, and small-scale quantum-computing experiments** in a common evaluation framework. Its main purpose is not to assume that AI or quantum methods are superior, but to test where they provide measurable value compared with conventional techniques.

> **Project status:** early research and implementation stage. The repository structure and research plan are being established before the main experimental pipeline is implemented.

---

## Research Question

The central question is:

> **Can an automated analysis system determine whether a synthetic sequence generator contains detectable statistical weakness or deterministic structure, and can that information be used to predict future outputs better than chance?**

A second objective is to compare three families of approaches:

1. **Classical statistical and information-theoretic analysis**
2. **Machine-learning-based sequence analysis**
3. **Small-scale quantum or quantum-inspired experiments**

The comparison is intended to determine what each approach can detect, how reliably it detects it, and whether the additional complexity of ML or quantum methods produces a meaningful advantage.

---

## Project Objectives

RNGScope is designed around the following objectives:

- Build multiple controllable synthetic sequence generators with known properties.
- Introduce controlled defects such as bias, correlation, periodicity, low entropy, and deterministic structure.
- Measure randomness using statistical and information-theoretic techniques.
- Train ML models to classify generators or detect weak structure in sequences.
- Test whether sequence models can predict future symbols better than an appropriate chance baseline.
- Compare ML results against conventional mathematical and statistical methods.
- Explore whether small quantum-computing experiments contribute anything useful to the analysis.
- Maintain reproducible experiments with clearly recorded parameters, datasets, metrics, and results.

---

## Experimental Philosophy

A central principle of this project is that the **ground truth is known**.

Instead of collecting unknown real-world tokens or authentication data, RNGScope generates controlled datasets where the underlying mechanism is explicitly defined. This makes it possible to answer questions such as:

- Did an analysis method actually detect a weakness?
- What type of weakness was present?
- How strong did the weakness need to become before detection was reliable?
- Could the model predict unseen outputs, or did it only memorize training data?
- Does a more complex method outperform a simpler baseline?

This controlled design is important because a statistical anomaly alone does not necessarily imply useful predictability.

---

## Planned Generator Families

The first versions of RNGScope will focus on synthetic generators that provide increasing levels of difficulty.

Examples include:

- IID Bernoulli bit sources
- Biased Bernoulli sources
- Periodic and partially periodic generators
- Markov-chain sources
- Simple linear or deterministic recurrence generators
- Standard software PRNG outputs used as strong negative controls
- Simulated quantum-derived bit sources

Additional generators may be added as the project develops.

---

## Analysis Pipeline

### 1. Statistical and Information-Theoretic Baseline

The classical analysis layer will establish the reference performance for the project.

Planned measurements include:

- symbol frequency and bias
- Shannon entropy
- min-entropy estimates
- conditional entropy
- autocorrelation
- transition probabilities
- run-length statistics
- serial and block statistics
- compression-based indicators
- selected established randomness tests

These methods provide interpretable baselines against which ML-based approaches can be evaluated.

### 2. Machine-Learning Analysis

The ML stage will investigate whether learned models can detect structure that is difficult to capture with individual statistical tests.

Possible experiments include:

- generator classification
- anomaly detection
- engineered statistical-feature classifiers
- sequence prediction
- recurrent or temporal models
- lightweight neural sequence models

Performance will be evaluated on **held-out sequences generated independently from the training data**.

A successful prediction experiment must outperform a clearly defined chance or probabilistic baseline on unseen data.

### 3. Quantum / Quantum-Inspired Experiments

Quantum computing is treated as an experimental comparison rather than an assumed advantage.

Initial work may use:

- Qiskit simulators
- simple quantum circuits for random-bit generation
- small quantum feature representations
- toy quantum classifiers or kernels where computationally practical

Classical baselines will always be retained so that any claimed benefit can be measured objectively.

---

## Evaluation

Experiments should be evaluated using metrics appropriate to the task.

For detection and classification:

- accuracy
- precision / recall
- F1 score
- ROC-AUC where appropriate
- false-positive and false-negative rates

For sequence prediction:

- prediction accuracy
- log loss / cross-entropy
- improvement over chance
- calibration where relevant

For randomness analysis:

- entropy estimates
- correlation measurements
- statistical-test outcomes
- sensitivity to controlled defect strength

The project will place particular emphasis on **generalization**, **reproducibility**, and comparison against simple baselines.

---

## Repository Structure

```text
RNGScope/
│
├── README.md
├── requirements.txt
├── pyproject.toml
│
├── docs/
│   └── research_plan.md
│
├── notes/
│   └── day-01-information-theory-harvard.pdf
│
├── src/
│   ├── .gitkeep
│   ├── generators/
│   │   └── .gitkeep
│   ├── analysis/
│   │   └── .gitkeep
│   ├── models/
│   │   └── .gitkeep
│   └── utils/
│       └── .gitkeep
│
└── experiments/
    ├── .gitkeep
    ├── notebooks/
    │   └── .gitkeep
    └── results/
        └── .gitkeep
```

### Directory Roles

- **`src/generators/`** — synthetic data sources and controlled weak generators
- **`src/analysis/`** — statistical, entropy, correlation, and randomness-analysis tools
- **`src/models/`** — machine-learning and experimental prediction models
- **`src/utils/`** — shared utilities, configuration, reproducibility helpers, and data handling
- **`experiments/notebooks/`** — exploratory analysis and experiment notebooks
- **`experiments/results/`** — generated plots, tables, metrics, and experiment outputs
- **`docs/`** — research design, methodology, and technical documentation
- **`notes/`** — personal study and research notes

---

## Development Roadmap

### Phase 1 — Foundations

- [ ] Implement basic synthetic generators
- [ ] Implement reproducible dataset generation
- [ ] Build entropy and frequency analysis tools
- [ ] Add correlation and transition analysis
- [ ] Establish visualization utilities
- [ ] Define baseline experiments

### Phase 2 — Statistical Benchmarking

- [ ] Evaluate generators using classical tests
- [ ] Measure sensitivity to controlled bias and correlation
- [ ] Establish baseline detection thresholds
- [ ] Record reproducible benchmark results

### Phase 3 — Machine Learning

- [ ] Build feature-based classifiers
- [ ] Test anomaly-detection approaches
- [ ] Develop sequence-prediction experiments
- [ ] Compare predictions against chance baselines
- [ ] Compare ML results with statistical methods

### Phase 4 — Quantum Comparison

- [ ] Implement simple Qiskit-based experiments
- [ ] Evaluate simulated quantum-derived sequences
- [ ] Test selected quantum or quantum-inspired analysis methods
- [ ] Compare results with equivalent classical approaches

### Phase 5 — Research Synthesis

- [ ] Consolidate experimental results
- [ ] Perform ablation and robustness studies
- [ ] Document limitations and negative results
- [ ] Produce a technical report or preprint-style manuscript

---

## Scope and Safety Boundary

RNGScope is a **synthetic randomness-analysis project**.

Executable experiments in this repository are intended to operate only on:

- locally generated numerical sequences
- synthetic bit streams
- deliberately constructed toy generators
- controlled experimental datasets

The project is **not intended for attacking or predicting real authentication systems** and does not provide workflows for obtaining, intercepting, reproducing, or bypassing real credentials, OTPs, session tokens, cookies, API keys, or other authentication material.

Security-related motivation is studied indirectly through the mathematical properties of randomness in a controlled research environment.

---

## Reproducibility Principles

As the implementation develops, experiments should record at minimum:

- generator type
- generator parameters
- random seed where applicable
- sequence length
- dataset split
- analysis method or model configuration
- evaluation metric
- software/library versions

Generated results should be reproducible from committed experiment configurations whenever practical.

---

## Long-Term Direction

RNGScope is intended to evolve from a learning project into a compact research platform for comparing methods of randomness analysis.

Potential extensions include:

- more sophisticated entropy estimators
- automated experiment orchestration
- explainable ML analysis of detected structure
- comparison of PRNG and quantum-derived datasets
- FPGA-based sequence generation or acceleration
- larger quantum experiments when suitable hardware or cloud resources are available
- publication-quality benchmark datasets and results

The priority is to establish strong classical baselines and experimentally justified conclusions before increasing model or system complexity.
