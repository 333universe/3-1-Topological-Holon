
"""End-to-end demonstration of the 3+1 Topological Holon Discovery Engine.

Runs two verified benchmarks in a single command:
1. Cross-Domain Isomorphism & Functional Void Detection (Biology vs. Supply Chain)
2. Multi-Level Fractal Scale-Shifting (Depth 0 -> Depth 1 -> Depth 2)
"""

import json
import os
import sys

# Ensure repository root is on sys.path so `from src import ...` works anywhere
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src import (
    Universal3Plus1Kernel,
    TopologicalHolonEngine,
    TopologicalDiscoveryAdapter,
    SemanticCoPilotBridge,
)


def run_cross_domain_void_demo():
    print("=" * 72)
    print("PART 1: CROSS-DOMAIN ISOMORPHISM & 3+1 VOID DETECTION")
    print("=" * 72)

    kernel = Universal3Plus1Kernel(profile="WIDE")
    engine = TopologicalHolonEngine(kernel=kernel, persistence_threshold=0.35, z_cutoff=2.5)

    # Domain A: Complete Cellular Metabolic Balancing Loop + Adversarial Noise
    bio_nodes = {
        "B1": {"label": "Glucose_Intake", "pillar": "E"},
        "B2": {"label": "Pyruvate_Flux", "pillar": "C"},
        "B3": {"label": "ATP_Synthesis", "pillar": "E"},
        "B4": {"label": "PFK_Allosteric_Brake", "pillar": "B"},
        "X1": {"label": "Spurious_Metabolite_1", "pillar": "E"},
        "X2": {"label": "Spurious_Metabolite_2", "pillar": "C"},
        "X3": {"label": "Spurious_Metabolite_3", "pillar": "B"},
    }
    bio_edges = [
        ("B1", "B2", "TRANSFORMS", 0.92),
        ("B2", "B3", "AMPLIFIES", 0.89),
        ("B3", "B4", "AMPLIFIES", 0.91),
        ("B4", "B1", "INHIBITS", 0.88),
        ("X1", "X2", "AMPLIFIES", 0.38),
        ("X2", "X3", "DELAYS", 0.37),
        ("X3", "X1", "INHIBITS", 0.39),
        ("B1", "X1", "DELAYS", 0.15),
        ("X2", "B3", "AMPLIFIES", 0.12),
    ]

    G_bio = engine.build_graph(bio_nodes, bio_edges)
    bio_report = engine.discover_and_promote(G_bio, domain_name="Cellular_Metabolism")

    # Domain B: Supply Chain missing its Balance (B) feedback regulator
    supply_nodes = {
        "S1": {"label": "Raw_Material_Orders", "pillar": "E"},
        "S2": {"label": "Factory_Assembly", "pillar": "C"},
        "S3": {"label": "Warehouse_Inventory", "pillar": "E"},
    }
    supply_edges = [
        ("S1", "S2", "TRANSFORMS", 0.90),
        ("S2", "S3", "AMPLIFIES", 0.87),
        ("S1", "S3", "DELAYS", 0.18),
    ]

    G_supply = engine.build_graph(supply_nodes, supply_edges)
    supply_report = engine.discover_and_promote(G_supply, domain_name="Global_Supply_Chain")

    adapter = TopologicalDiscoveryAdapter(engine, latest_report=supply_report)
    gov_status = kernel.step(adapter)

    copilot = SemanticCoPilotBridge()
    brief = copilot.build_hypothesis_prompt(bio_report, supply_report)

    print(f"Promoted Reference Holons: {len(bio_report['promoted_holons'])}")
    print(f"Rejected Noise Cycles:     {len(bio_report['rejected_coincidences'])}")
    print(f"Kernel Governance Mode:    {gov_status['governance_mode']}\n")
    print(brief)


def run_fractal_depth2_demo():
    print("\n" + "=" * 72)
    print("PART 2: MULTI-LEVEL FRACTAL SCALE-SHIFTING (DEPTH 0 -> 1 -> 2)")
    print("=" * 72)

    root_kernel = Universal3Plus1Kernel(profile="WIDE", depth=0)
    meso_kernel = root_kernel.grow_sub_triad("Cellular_Energy_System_Depth1", profile="STANDARD")
    sub_engine = TopologicalHolonEngine(kernel=meso_kernel, persistence_threshold=0.35, z_cutoff=2.5)

    micro_nodes = {
        "G1": {"label": "Glucose_Transport", "pillar": "E"},
        "G2": {"label": "Hexokinase_Step", "pillar": "C"},
        "G3": {"label": "Pyruvate_Output", "pillar": "E"},
        "B1": {"label": "ATP_Sensor", "pillar": "B"},
        "B2": {"label": "PFK_Inhibitor", "pillar": "B"},
        "B3": {"label": "AMP_Activator", "pillar": "C"},
        "D1": {"label": "Random_Noise_1", "pillar": "E"},
        "D2": {"label": "Random_Noise_2", "pillar": "B"},
        "D3": {"label": "Random_Noise_3", "pillar": "C"},
    }
    micro_edges = [
        ("G1", "G2", "TRANSFORMS", 0.91),
        ("G2", "G3", "AMPLIFIES", 0.89),
        ("G3", "G1", "AMPLIFIES", 0.90),
        ("B1", "B2", "INHIBITS", 0.88),
        ("B2", "B3", "DELAYS", 0.87),
        ("B3", "B1", "AMPLIFIES", 0.89),
        ("D1", "D2", "AMPLIFIES", 0.38),
        ("D2", "D3", "INHIBITS", 0.37),
        ("D3", "D1", "DELAYS", 0.39),
    ]

    G_micro = sub_engine.build_graph(micro_nodes, micro_edges)
    depth2_report = sub_engine.discover_and_promote(G_micro, domain_name="Micro_Pathway")

    h1_id = depth2_report["promoted_holons"][0]["holon_id"]
    h2_id = depth2_report["promoted_holons"][1]["holon_id"]


    # Collapse the two Depth-2 Holons into Objects at Depth 1
    meso_engine = TopologicalHolonEngine(kernel=root_kernel, persistence_threshold=0.35, z_cutoff=2.5)
    meso_nodes = {
        h1_id: {"label": "Collapsed_Object_1", "pillar": "E"},
        h2_id: {"label": "Collapsed_Object_2", "pillar": "B"},
        "R1": {"label": "Hormonal_Insulin_Switch", "pillar": "C"},
    }
    meso_edges = [
        (h1_id, h2_id, "AMPLIFIES", 0.93),
        (h2_id, "R1", "TRANSFORMS", 0.91),
        ("R1", h1_id, "INHIBITS", 0.92),
    ]

    G_meso = meso_engine.build_graph(meso_nodes, meso_edges)
    depth1_report = meso_engine.discover_and_promote(G_meso, domain_name="Meso_Organelle")

    promoted_meso = depth1_report["promoted_holons"]
    print(f"Depth 2 Holons Promoted: {len(depth2_report['promoted_holons'])}")
    print(f"Depth 1 Meso-Holon:      {promoted_meso['holon_id']} (Missing Pillars: {promoted_meso['missing_pillars']})")
    print("\nActive 3+1 Fractal Kernel Tree:")
    print(json.dumps(root_kernel.get_fractal_tree(), indent=2))


if __name__ == "__main__":
    run_cross_domain_void_demo()
    run_fractal_depth2_demo()
