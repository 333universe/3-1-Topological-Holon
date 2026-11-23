[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/333universe/3-1-Topological-Holon/blob/main/notebooks/quickstart.ipynb)
[![3+1 Topological Holon CI](https://github.com/333universe/3-1-Topological-Holon/actions/workflows/ci.yml/badge.svg)](https://github.com/333universe/3-1-Topological-Holon/actions/workflows/ci.yml)


 # 3+1 Topological Holon Discovery Engine

A domain-agnostic **Topological Discovery Engine** built on **Object–Arrangement Duality**, **GF(2) Simplicial Homology (Beta_0, Beta_1, Beta_2)**, and the **3+1 Holographic Systems Architecture**.

Instead of retrieving pre-labeled documents via rigid keywords or vector distances, this engine treats every entity as a scale-fluid **Holon**—simultaneously a unified **Object** (`1.0000`) from the outside and a relational **Arrangement** (`0.3333 E + 0.3333 B + 0.3333 C + 0.0001 O`) on the inside—to discover cross-domain structural analogies and diagnose missing functional pillars inside topological voids.

---

## Core Architecture

1. **Invariant 3+1 Holographic Base Kernel (`src/kernel.py`):**
   * Enforces the conservation law `E (0.3333) + B (0.3333) + C (0.3333) + O (0.0001) = 1.0000`.
   * Governs search execution via **Mode A** (anti-burnout stabilization), **Mode B** (Delta-Epsilon symmetry-breaking sparks), and recursive fractal scale-shifting (`grow_sub_triad()`).
2. **GF(2) Simplicial Homology & Surprise Engine (`src/engine.py`):**
   * Evaluates 5 universal edge primitives (`AMPLIFIES`, `INHIBITS`, `DELAYS`, `TRANSFORMS`, `CONTAINS`).
   * Computes exact **Betti numbers (Beta_0, Beta_1, Beta_2)** over modulo-2 boundary matrices to detect broken feedback loops (`H_1 = 0`) and hollow 2D shells (`H_2 > 0`).
   * Filters coincidental noise via **Null-Model Z-Surprise scoring** and promotes high-persistence arrangements into higher-order Holons via **Minimum Description Length (MDL)** compression.
3. **Real-World Data Loaders (`src/loaders.py`):**
   * Ingests raw CSV relational edge lists (`load_from_csv_text`) and multivariate numerical time-series (`load_from_time_series` with lagged cross-correlation) with automatic `E / B / C / O` pillar inference (`auto_infer_pillars`).
4. **Semantic Co-Pilot Bridge (`src/copilot.py`):**
   * Translates detected topological voids and cross-domain isomorphisms into structured scientific or strategic hypothesis prompts.

---

## Repository Structure

```text
3-1-Topological-Holon/
├── .github/workflows/ci.yml           # Automated GitHub Actions verification
├── examples/
│   └── demo_fractal_discovery.py      # 3-part benchmark (Voids, Depth 0-2 Fractal, H2 Cavities)
├── notebooks/
│   └── quickstart.ipynb               # One-click Google Colab quickstart
├── src/
│   ├── __init__.py
│   ├── kernel.py                      # Universal3Plus1Kernel & BaseDomainAdapter
│   ├── engine.py                      # TopologicalHolonEngine & GF(2) Betti Solver
│   ├── loaders.py                     # CSV & Lagged Time-Series Ingestion Adapters
│   └── copilot.py                     # SemanticCoPilotBridge
├── LICENSE
├── README.md
└── requirements.txt
```

---

## Quickstart

```
git clone https://github.com
cd 3-1-Topological-Holon
pip install -e ".[dev]"
python examples/demo_fractal_discovery.py
```


