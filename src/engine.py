"""Topological Holon Engine with Z2 Simplicial Homology (Beta_0, Beta_1, Beta_2)
and Iteration 5.0 EMA / Logarithmic Latency Guardrails.
"""

import math
import time
from itertools import combinations
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import networkx as nx

# Fallbacks or stub classes in case kernel is not in the same path
try:
    from .kernel import Universal3Plus1Kernel, BaseDomainAdapter
except (ImportError, ValueError):
    # Stubs to prevent import failures in a standalone notebook cell
    class Universal3Plus1Kernel:
        def __init__(self):
            self.depth = 1
        def grow_sub_triad(self, holon_id, profile):
            return self

    class BaseDomainAdapter:
        pass


class EMATelemetryNormalizer:
    """Self-calibrating EMA normalizer adapted from Iteration 5.0 Spec."""

    def __init__(self, alpha: float = 0.25):
        self.alpha = alpha
        self.ema_means: Dict[str, float] = {}
        self.ema_vars: Dict[str, float] = {}

    def update_and_score(self, metric_name: str, raw_value: float) -> float:
        if metric_name not in self.ema_means:
            self.ema_means[metric_name] = raw_value
            self.ema_vars[metric_name] = max(1e-6, (raw_value * 0.1) ** 2)
            return 0.0
        prev_mean = self.ema_means[metric_name]
        delta = raw_value - prev_mean
        new_mean = prev_mean + self.alpha * delta
        new_var = (1.0 - self.alpha) * (self.ema_vars[metric_name] + self.alpha * (delta ** 2))
        self.ema_means[metric_name] = new_mean
        self.ema_vars[metric_name] = max(1e-6, new_var)
        std_dev = math.sqrt(self.ema_vars[metric_name])
        return delta / std_dev if std_dev > 0 else 0.0


def _gf2_rank(matrix: np.ndarray) -> int:
    """Computes exact matrix rank over the finite field GF(2) (modulo-2 arithmetic)."""
    if matrix.size == 0:
        return 0
    M = matrix.copy() % 2
    rows, cols = M.shape
    rank = 0
    for col in range(cols):
        if rank >= rows:
            break
        pivot = None
        for r in range(rank, rows):
            if M[r, col] == 1:
                pivot = r
                break
        if pivot is None:
            continue
        if pivot != rank:
            M[[rank, pivot]] = M[[pivot, rank]]
        for r in range(rows):
            if r != rank and M[r, col] == 1:
                M[r] ^= M[rank]
        rank += 1
    return rank


class TopologicalHolonEngine:
    """Scans typed relational graphs for H0 clusters, H1 loops, and H2 enclosed cavities."""

    VALID_EDGES = {"AMPLIFIES", "INHIBITS", "DELAYS", "TRANSFORMS", "CONTAINS"}

    def __init__(
        self,
        kernel: Universal3Plus1Kernel,
        persistence_threshold: float = 0.35,
        z_cutoff: float = 2.5,
        base_latency_limit_ms: float = 50.0,
    ):
        self.kernel = kernel
        self.persistence_threshold = persistence_threshold
        self.z_cutoff = z_cutoff
        self.base_latency_limit_ms = base_latency_limit_ms
        self.ema = EMATelemetryNormalizer(alpha=0.25)
        self.macro_holons: Dict[str, Any] = {}

    def get_scaled_latency_limit(self, active_nodes: int) -> float:
        """Iteration 5.0 logarithmic budget scaling for clique-complex enumeration."""
        return self.base_latency_limit_ms * math.log2(max(1, active_nodes) + 1)

    def build_graph(
        self,
        nodes: Dict[str, Dict[str, Any]],
        edges: List[Tuple[str, str, str, float]],
    ) -> nx.DiGraph:
        G = nx.DiGraph()
        for n_id, meta in nodes.items():
            G.add_node(
                n_id,
                pillar=meta.get("pillar", "E"),
                domain_label=meta.get("label", n_id),
            )
        for u, v, etype, weight in edges:
            if etype not in self.VALID_EDGES:
                raise ValueError(f"Invalid edge type '{etype}'. Must be in {self.VALID_EDGES}")
            G.add_edge(u, v, type=etype, weight=float(weight))
        return G

    def filter_persistence(self, G: nx.DiGraph) -> Tuple[nx.DiGraph, int]:
        G_clean = nx.DiGraph()
        G_clean.add_nodes_from(G.nodes(data=True))
        pruned = 0
        for u, v, data in G.edges(data=True):
            self.ema.update_and_score("edge_coupling", data["weight"])
            if data["weight"] >= self.persistence_threshold:
                G_clean.add_edge(u, v, **data)
            else:
                pruned += 1
        return G_clean, pruned

    def compute_betti_numbers(self, G: nx.DiGraph) -> Dict[str, Any]:
        """Builds an undirected Clique Complex (0, 1, 2, 3-simplices) and computes
        exact Betti numbers (Beta_0, Beta_1, Beta_2) over GF(2) within scaled latency budget.
        """
        start_ms = time.perf_counter() * 1000.0
        n_nodes = G.number_of_nodes()
        budget_ms = self.get_scaled_latency_limit(n_nodes)

        U = G.to_undirected()
        vertices = sorted(U.nodes())
        v_idx = {v: i for i, v in enumerate(vertices)}

        edges = sorted(tuple(sorted((u, v))) for u, v in U.edges() if u != v)
        e_idx = {e: i for i, e in enumerate(edges)}

        # Enumerate 2-simplices (triangles) and 3-simplices (tetrahedra)
        cliques = list(nx.enumerate_all_cliques(U))
        triangles = sorted(tuple(sorted(c)) for c in cliques if len(c) == 3)
        t_idx = {t: i for i, t in enumerate(triangles)}

        elapsed = (time.perf_counter() * 1000.0) - start_ms
        capped_3simplices = elapsed > budget_ms
        tetrahedra = [] if capped_3simplices else sorted(tuple(sorted(c)) for c in cliques if len(c) == 4)

        # Boundary matrix d1: edges -> vertices
        d1 = np.zeros((len(vertices), len(edges)), dtype=np.uint8)
        for j, (u, v) in enumerate(edges):
            d1[v_idx[u], j] = 1
            d1[v_idx[v], j] = 1

        # Boundary matrix d2: triangles -> edges
        d2 = np.zeros((len(edges), len(triangles)), dtype=np.uint8)
        for j, (u, v, w) in enumerate(triangles):
            for face in [(u, v), (u, w), (v, w)]:
                d2[e_idx[face], j] = 1

        # Boundary matrix d3: tetrahedra -> triangles
        d3 = np.zeros((len(triangles), len(tetrahedra)), dtype=np.uint8)
        for j, tet in enumerate(tetrahedra):
            for face in combinations(tet, 3):
                d3[t_idx[tuple(sorted(face))], j] = 1

        r1 = _gf2_rank(d1)
        r2 = _gf2_rank(d2)
        r3 = _gf2_rank(d3)

        beta_0 = len(vertices) - r1
        beta_1 = (len(edges) - r1) - r2
        beta_2 = (len(triangles) - r2) - r3

        return {
            "betti": [int(beta_0), int(beta_1), int(beta_2)],
            "simplices": {
                "vertices": len(vertices),
                "edges": len(edges),
                "triangles": len(triangles),
                "tetrahedra": len(tetrahedra),
            },
            "latency_capped": capped_3simplices,
        }

    def compute_surprise_score(
        self, cycle_nodes: List[str], G_clean: nx.DiGraph, num_null_samples: int = 500
    ) -> Tuple[float, float]:
        cycle_edges = [
            G_clean[cycle_nodes[i]][cycle_nodes[(i + 1) % len(cycle_nodes)]]["weight"]
            for i in range(len(cycle_nodes))
        ]
        obs_p = float(np.mean(cycle_edges))
        rng = np.random.default_rng(42)
        null_means = [
            float(np.mean(rng.beta(2.0, 2.0, size=len(cycle_nodes))))
            for _ in range(num_null_samples)
        ]
        mu = float(np.mean(null_means))
        sigma = float(np.std(null_means)) + 1e-6
        z_score = (obs_p - mu) / sigma
        return round(obs_p, 4), round(z_score, 2)

    def evaluate_mdl_compression(self, nodes: List[str], edges: List[Tuple[str, str]]) -> Tuple[int, int, int]:
        raw_bits = (len(nodes) * 8) + (len(edges) * 12)
        compressed_bits = 18 + 8
        return raw_bits, compressed_bits, raw_bits - compressed_bits

    def discover_and_promote(self, G: nx.DiGraph, domain_name: str) -> Dict[str, Any]:
        G_clean, pruned = self.filter_persistence(G)
        homology = self.compute_betti_numbers(G_clean)
        cycles = list(nx.simple_cycles(G_clean))
        promoted = []
        rejected = []

        for idx, cycle in enumerate(cycles):
            obs_p, z_score = self.compute_surprise_score(cycle, G_clean)
            sub_edges = [(cycle[i], cycle[(i + 1) % len(cycle)]) for i in range(len(cycle))]
            _, _, savings = self.evaluate_mdl_compression(cycle, sub_edges)

            counts = {"E": 0, "B": 0, "C": 0, "O": 0}
            for n in cycle:
                counts[G_clean.nodes[n]["pillar"]] += 1
            missing = [p for p in ("E", "B", "C") if counts[p] == 0]

            if z_score >= self.z_cutoff and savings > 0:
                holon_id = f"{domain_name}_Holon_{idx + 1}"
                child_kernel = self.kernel.grow_sub_triad(holon_id, profile="STANDARD")
                record = {
                    "holon_id": holon_id,
                    "nodes": cycle,
                    "labels": [G_clean.nodes[n]["domain_label"] for n in cycle],
                    "persistence": obs_p,
                    "z_surprise": z_score,
                    "mdl_savings_bits": savings,
                    "pillar_balance": counts,
                    "missing_pillars": missing,
                    "assigned_depth": child_kernel.depth,
                }
                self.macro_holons[holon_id] = record
                promoted.append(record)
            else:
                rejected.append({"nodes": cycle, "persistence": obs_p, "z_surprise": z_score})

        void_alert = None
        b0, b1, b2 = homology["betti"]
        if b2 > 0:
            void_alert = {
                "type": "TOPOLOGICAL_2D_CAVITY_H2",
                "signature": f"Betti={homology['betti']} ({b2} hollow 2D shell(s) detected)",
                "missing_pillars": ["O", "B"],
                "exposed_nodes": [
                    {"id": n, **G_clean.nodes[n]} for n in G_clean.nodes()
                ],
            }
        elif len(promoted) == 0 and G_clean.number_of_nodes() >= 3:
            counts = {"E": 0, "B": 0, "C": 0}
            for n in G_clean.nodes():
                p = G_clean.nodes[n]["pillar"]
                if p in counts:
                    counts[p] += 1
            missing = [p for p, c in counts.items() if c == 0]
            void_alert = {
                "type": "TOPOLOGICAL_VOID_OPEN_LOOP",
                "signature": f"H1=0 (Broken Feedback Cycle, Betti={homology['betti']})",
                "missing_pillars": missing,
                "exposed_nodes": [
                    {"id": n, **G_clean.nodes[n]} for n in G_clean.nodes()
                ],
            }
        return {
            "domain": domain_name,
            "pruned_noise_edges": pruned,
            "betti_summary": homology,
            "promoted_holons": promoted,
            "rejected_coincidences": rejected,
            "void_alert": void_alert,
        }


class TopologicalDiscoveryAdapter(BaseDomainAdapter):
    """Connects TopologicalHolonEngine telemetry to Universal3Plus1Kernel."""

    def init(self, engine: TopologicalHolonEngine, latest_report: Optional[Dict[str, Any]] = None):
        self.engine = engine
        self.latest_report = latest_report or {}

    def sense(self, current_weights: Dict[str, float]) -> Dict[str, Any]:
        promoted = self.latest_report.get("promoted_holons", [])
        void_alert = self.latest_report.get("void_alert")
        variance = 0.0 if len(promoted) == 0 else min(1.0, len(promoted) * 0.25)
        return {
            "variance": variance,
            "external_shift": void_alert is not None,
        }

    def act(self, updated_weights: Dict[str, float], mode: str) -> Dict[str, Any]:
        directives = {
            "MODE_A_STABILIZE": "PRUNE_NOISE_AND_CAP_SIMPLEX_DEPTH",
            "MODE_B_GENERATIVE_SPARK": "RELAX_EDGE_CONSTRAINTS_FOR_ANALOGY_SEARCH",
            "QUARANTINE_RESET": "HALT_HYPOTHESIS_GEN_AND_RESTORE_SEED",
            "STEADY_STATE": "SCAN_AND_PROMOTE_HOLONS",
        }
        return {
            "governance_mode": mode,
            "directive": directives.get(mode, "SCAN_AND_PROMOTE_HOLONS"),
            "weights": updated_weights,
        }
