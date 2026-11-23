
import math
import numpy as np
import pytest

from src.kernel import Universal3Plus1Kernel, BaseDomainAdapter
from src.engine import (
    EMATelemetryNormalizer,
    TopologicalHolonEngine,
    TopologicalDiscoveryAdapter,
    _gf2_rank,
)
from src.loaders import (
    auto_infer_pillars,
    load_from_csv_text,
    load_from_time_series,
)
from src.copilot import SemanticCoPilotBridge


class DummyStagnantShiftAdapter(BaseDomainAdapter):
    """Triggers Mode B generative spark when variance is zero and external_shift is True."""

    def sense(self, current_weights):
        return {"variance": 0.0, "external_shift": True}


class DummySteadyAdapter(BaseDomainAdapter):
    """Keeps system in steady state with no external shift."""

    def sense(self, current_weights):
        return {"variance": 0.5, "external_shift": False}


# ==============================================================================
# 1. KERNEL INVARIANTS & CYBERNETIC GOVERNANCE TESTS
# ==============================================================================


def test_kernel_conservation_law():
    kernel = Universal3Plus1Kernel(profile="STANDARD")
    total = sum(kernel.weights.values())
    assert math.isclose(total, 1.0000, rel_tol=1e-9)
    assert kernel.weights["O"] == 0.0001


def test_kernel_invalid_profile_raises():
    with pytest.raises(ValueError, match="Unknown tolerance profile"):
        Universal3Plus1Kernel(profile="NON_EXISTENT")


def test_kernel_core_quarantine_reset():
    kernel = Universal3Plus1Kernel(profile="STANDARD")
    # Corrupt the 0.0001 Holographic Orchestrator core
    kernel.weights["O"] = 0.0050
    result = kernel.step(DummySteadyAdapter())
    assert result["mode"] == "QUARANTINE_RESET"
    assert kernel.weights == kernel.immutable_seed


def test_kernel_mode_a_stabilize_on_bound_breach():
    kernel = Universal3Plus1Kernel(profile="TIGHT")
    # Force Efficiency above TIGHT ceiling (0.3600)
    kernel.weights["E"] = 0.4500
    kernel.weights["B"] = 0.2166
    result = kernel.step(DummySteadyAdapter())
    assert result["mode"] == "MODE_A_STABILIZE"
    assert kernel.weights == {"E": 0.3333, "B": 0.3333, "C": 0.3333, "O": 0.0001}


def test_kernel_mode_b_spark_and_elasticity_return():
    kernel = Universal3Plus1Kernel(profile="STANDARD")
    # Step 1: Stagnant variance + external shift triggers Mode B
    res1 = kernel.step(DummyStagnantShiftAdapter())
    assert res1["mode"] == "MODE_B_GENERATIVE_SPARK"
    assert kernel.weights["C"] == 0.4000
    assert kernel.weights["E"] == 0.2666
    assert kernel.elasticity_timer == 1

    # Step 2: Steady adapter decrements elasticity timer and restores parity
    res2 = kernel.step(DummySteadyAdapter())
    assert res2["mode"] == "STEADY_STATE"
    assert kernel.elasticity_timer == 0
    assert kernel.weights == {"E": 0.3333, "B": 0.3333, "C": 0.3333, "O": 0.0001}


def test_kernel_fractal_sub_triad_recursion():
    root = Universal3Plus1Kernel(profile="STANDARD", depth=0)
    child = root.grow_sub_triad("B", profile="TIGHT")
    grandchild = child.grow_sub_triad("C", profile="WIDE")

    assert child.depth == 1
    assert grandchild.depth == 2
    tree = root.get_fractal_tree()
    assert tree["depth"] == 0
    assert "B" in tree["children"]
    assert "C" in tree["children"]["B"]["children"]


# ==============================================================================
# 2. GF(2) HOMOLOGY, BETTI NUMBERS, & ENGINE DISCOVERY TESTS
# ==============================================================================


def test_gf2_rank_modulo_two_cancellation():
    # Three edges forming a triangle over GF(2) have linearly dependent rows (rank 2)
    triangle_d1 = np.array(
        [,
 ,
 ,
        ],
        dtype=np.uint8,
    )
    assert _gf2_rank(triangle_d1) == 2


def test_ema_telemetry_normalizer():
    ema = EMATelemetryNormalizer(alpha=0.5)
    z0 = ema.update_and_score("edge_coupling", 0.5)
    assert z0 == 0.0
    z1 = ema.update_and_score("edge_coupling", 0.9)
    assert z1 > 0.0


def test_engine_invalid_edge_raises():
    engine = TopologicalHolonEngine(Universal3Plus1Kernel())
    nodes = {"A": {"pillar": "E"}, "B": {"pillar": "B"}}
    with pytest.raises(ValueError, match="Invalid edge type"):
        engine.build_graph(nodes, [("A", "B", "UNKNOWN_EDGE", 0.9)])


def test_betti_closed_loop_h1_vs_open_chain():
    engine = TopologicalHolonEngine(Universal3Plus1Kernel(), persistence_threshold=0.35)
    nodes = {
        "N1": {"pillar": "E", "label": "Catalyst"},
        "N2": {"pillar": "C", "label": "Mutator"},
        "N3": {"pillar": "B", "label": "Inhibitor"},
        "N4": {"pillar": "E", "label": "Sensor"},
    }
    # 4-cycle has no 3-cliques (triangles), so Beta_0 = 1, Beta_1 = 1, Beta_2 = 0
    closed_edges = [
        ("N1", "N2", "AMPLIFIES", 0.92),
        ("N2", "N3", "TRANSFORMS", 0.90),
        ("N3", "N4", "INHIBITS", 0.91),
        ("N4", "N1", "DELAYS", 0.93),
    ]
    G_closed = engine.build_graph(nodes, closed_edges)
    report_closed = engine.discover_and_promote(G_closed, "ClosedDomain")

    assert report_closed["betti_summary"]["betti"] == [1, 1, 0]
    assert len(report_closed["promoted_holons"]) == 1
    assert report_closed["void_alert"] is None
    assert report_closed["promoted_holons"][0]["assigned_depth"] == 1

    # Remove inhibitory return edge -> broken feedback loop (Beta_1 = 0 -> void alert)
    open_edges = closed_edges[:3]
    G_open = engine.build_graph(nodes, open_edges)
    report_open = engine.discover_and_promote(G_open, "BrokenDomain")

    assert report_open["betti_summary"]["betti"] == [1, 0, 0]
    assert len(report_open["promoted_holons"]) == 0
    assert report_open["void_alert"] is not None
    assert report_open["void_alert"]["type"] == "TOPOLOGICAL_VOID_OPEN_LOOP"


def test_betti_h2_octahedral_cavity_detection():
    engine = TopologicalHolonEngine(Universal3Plus1Kernel(), persistence_threshold=0.35)
    # Octahedron: 6 vertices, 12 edges, 8 triangles, 0 tetrahedra -> Betti = [1, 0, 1]
    verts = ["v0", "v1", "v2", "v3", "v4", "v5"]
    nodes = {v: {"pillar": "E", "label": v} for v in verts}
    opposite = {("v0", "v5"), ("v5", "v0"), ("v1", "v3"), ("v3", "v1"), ("v2", "v4"), ("v4", "v2")}

    edges = []
    for i in range(len(verts)):
        for j in range(i + 1, len(verts)):
            u, v = verts[i], verts[j]
            if (u, v) not in opposite:
                edges.append((u, v, "AMPLIFIES", 0.95))

    G_oct = engine.build_graph(nodes, edges)
    report = engine.discover_and_promote(G_oct, "HollowShellDomain")

    assert report["betti_summary"]["betti"] == [1, 0, 1]
    assert report["void_alert"] is not None
    assert report["void_alert"]["type"] == "TOPOLOGICAL_2D_CAVITY_H2"


def test_discovery_adapter_integration():
    kernel = Universal3Plus1Kernel()
    engine = TopologicalHolonEngine(kernel)
    fake_void_report = {
        "promoted_holons": [],
        "void_alert": {"type": "TOPOLOGICAL_VOID_OPEN_LOOP"},
    }
    adapter = TopologicalDiscoveryAdapter(engine, latest_report=fake_void_report)
    action = kernel.step(adapter)

    assert action["governance_mode"] == "MODE_B_GENERATIVE_SPARK"
    assert action["directive"] == "RELAX_EDGE_CONSTRAINTS_FOR_ANALOGY_SEARCH"


# ==============================================================================
# 3. DATA LOADERS & SEMANTIC CO-PILOT BRIDGE TESTS
# ==============================================================================


def test_csv_loader_and_pillar_inference():
    csv_data = (
        "source,target,edge_type,weight\n"
        "A,B,AMPLIFIES,10.0\n"
        "B,C,TRANSFORMS,8.0\n"
        "C,A,INHIBITS,9.0\n"
    )
    nodes, edges = load_from_csv_text(csv_data, auto_pillars=True)
    assert len(nodes) == 3
    assert len(edges) == 3
    # Weights should be normalized against max weight (10.0)
    assert edges[0][3] == 1.0
    assert edges[1][3] == 0.8
    # Node C participates in INHIBITS and has both in_deg >= 1 and out_deg >= 1 -> pillar B
    assert nodes["C"]["pillar"] == "B"


def test_time_series_loader_detects_lagged_inhibition():
    # X drives Y at lag 1, and Y suppresses X at lag 1
    series = {
        "Driver": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],
        "Brake": [8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0],
    }
    nodes, edges = load_from_time_series(series, corr_threshold=0.5, max_lag=1)
    assert "Driver" in nodes and "Brake" in nodes
    assert any(etype == "INHIBITS" for _, _, etype, _ in edges)


def test_copilot_bridge_prompt_generation():
    bridge = SemanticCoPilotBridge()
    source_report = {
        "domain": "Cellular Glycolysis",
        "promoted_holons": [
            {
                "holon_id": "Cellular Glycolysis_Holon_1",
                "z_surprise": 4.12,
                "labels": ["ATP", "PFK", "Citrate"],
            }
        ],
    }
    target_report = {
        "domain": "Supply Chain Logistics",
        "void_alert": {
            "type": "TOPOLOGICAL_VOID_OPEN_LOOP",
            "signature": "H1=0 (Broken Feedback Cycle, Betti=[1, 0, 0])",
            "missing_pillars": ["B"],
            "exposed_nodes": [{"id": "PortA", "pillar": "E"}],
        },
    }
    prompt = bridge.build_hypothesis_prompt(source_report, target_report)
    assert "Cellular Glycolysis_Holon_1" in prompt
    assert "Supply Chain Logistics" in prompt
    assert "TOPOLOGICAL_VOID_OPEN_LOOP" in prompt
    assert "Balance (Containment" in prompt
