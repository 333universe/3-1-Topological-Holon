"""
3+1 Topological Holon Engine & Discovery Adapter.
Implements Persistence Filtration, Betti Summaries, MDL Scale-Shifting,
3+1 Functional Deficit Diagnosis, and Null-Model Z-Surprise Scoring.
"""

import numpy as np
import networkx as nx
from .kernel import BaseDomainAdapter

VALID_EDGE_TYPES = {"AMPLIFIES", "INHIBITS", "DELAYS", "TRANSFORMS", "CONTAINS"}
VALID_PILLARS = {"E", "B", "C", "O"}


class TopologicalHolonEngine:
    """Core engine for Persistence Filtration, MDL Scale-Shifting, and Surprise Scoring."""

    def __init__(self, kernel, persistence_threshold=0.35, z_cutoff=2.5):
        self.kernel = kernel
        self.persistence_threshold = persistence_threshold
        self.z_cutoff = z_cutoff
        self.macro_holons = {}

    def build_graph(self, nodes, edges):
        """Constructs a domain-blind directed graph with typed edges and coupling weights."""
        G = nx.DiGraph()
        for n_id, meta in nodes.items():
            pillar = meta.get("pillar", "E")
            if pillar not in VALID_PILLARS:
                raise ValueError(f"Invalid 3+1 pillar: {pillar}")
            G.add_node(n_id, pillar=pillar, domain_label=meta.get("label", n_id))

        for u, v, etype, weight in edges:
            if etype not in VALID_EDGE_TYPES:
                raise ValueError(f"Invalid edge type: {etype}")
            G.add_edge(u, v, type=etype, weight=float(weight))
        return G

    def filter_persistence(self, G):
        """Prunes low-persistence noise edges below the coupling threshold."""
        G_clean = nx.DiGraph()
        G_clean.add_nodes_from(G.nodes(data=True))
        pruned_count = 0

        for u, v, data in G.edges(data=True):
            if data["weight"] >= self.persistence_threshold:
                G_clean.add_edge(u, v, **data)
            else:
                pruned_count += 1

        return G_clean, pruned_count

    def compute_betti_summary(self, G):
        """Computes H0 (connected components) and H1 (independent cycles)."""
        undirected = G.to_undirected()
        h0 = nx.number_connected_components(undirected)
        cycles = list(nx.simple_cycles(G))
        h1 = len(cycles)
        return {"H0": h0, "H1": h1, "cycles": cycles}

    def evaluate_mdl_compression(self, subgraph_nodes, subgraph_edges):
        """Calculates bit savings for encapsulating an arrangement into a single Holon."""
        n = len(subgraph_nodes)
        e = len(subgraph_edges)
        raw_bits = (n * 8) + (e * 12)
        compressed_bits = 18 + (2 * 4)
        savings = raw_bits - compressed_bits
        return raw_bits, compressed_bits, savings

    def diagnose_3plus1_balance(self, G, node_subset):
        """Checks E, B, C representation inside an arrangement to spot functional deficits."""
        counts = {"E": 0, "B": 0, "C": 0, "O": 0}
        for n in node_subset:
            p = G.nodes[n]["pillar"]
            counts[p] += 1

        missing = [p for p in ("E", "B", "C") if counts[p] == 0]
        return counts, missing

    def compute_surprise_score(self, G_clean, cycle_nodes, num_null_samples=500):
        """Benchmarks mean edge persistence against an unbiased Beta(2,2) background prior."""
        cycle_edges = [
            G_clean[cycle_nodes[i]][cycle_nodes[(i + 1) % len(cycle_nodes)]]["weight"]
            for i in range(len(cycle_nodes))
        ]
        observed_persistence = float(np.mean(cycle_edges))

        rng = np.random.default_rng(42)
        null_means = [
            float(np.mean(rng.beta(2.0, 2.0, size=len(cycle_nodes))))
            for _ in range(num_null_samples)
        ]
        mu = np.mean(null_means)
        sigma = np.std(null_means) + 1e-6
        z_score = (observed_persistence - mu) / sigma
        return round(observed_persistence, 4), round(float(z_score), 2)

    def discover_and_promote(self, G, domain_name="Unknown_Domain"):
        """Full pipeline: Filter Noise -> Detect Cycles/Voids -> Score Surprise -> MDL Promote."""
        G_clean, pruned_edges = self.filter_persistence(G)
        betti = self.compute_betti_summary(G_clean)
        report = {
            "domain": domain_name,
            "pruned_noise_edges": pruned_edges,
            "betti_summary": {"H0": betti["H0"], "H1": betti["H1"]},
            "promoted_holons": [],
            "rejected_coincidences": [],
            "global_void_alerts": [],
        }

        for idx, cycle in enumerate(betti["cycles"]):
            obs_p, z_score = self.compute_surprise_score(G_clean, cycle)
            sub_edges = [(cycle[i], cycle[(i + 1) % len(cycle)]) for i in range(len(cycle))]
            _, _, savings = self.evaluate_mdl_compression(cycle, sub_edges)
            counts, missing_pillars = self.diagnose_3plus1_balance(G_clean, cycle)

            if z_score >= self.z_cutoff and savings > 0:
                holon_id = f"{domain_name}_Holon_{idx + 1}"
                child_kernel = self.kernel.grow_sub_triad(holon_id, profile="STANDARD")
                holon_record = {
                    "holon_id": holon_id,
                    "motif": "BALANCING_OR_REINFORCING_LOOP",
                    "nodes": cycle,
                    "domain_labels": [G_clean.nodes[n]["domain_label"] for n in cycle],
                    "persistence": obs_p,
                    "z_surprise": z_score,
                    "mdl_bit_savings": savings,
                    "pillar_distribution": counts,
                    "missing_pillars": missing_pillars,
                    "assigned_depth": child_kernel.depth,
                }
                self.macro_holons[holon_id] = holon_record
                report["promoted_holons"].append(holon_record)
            else:
                report["rejected_coincidences"].append(
                    {
                        "nodes": cycle,
                        "persistence": obs_p,
                        "z_surprise": z_score,
                        "reason": f"Below Z-cutoff ({self.z_cutoff}) or non-positive MDL savings",
                    }
                )

        if betti["H1"] == 0 and G_clean.number_of_edges() > 0:
            all_nodes = list(G_clean.nodes())
            counts, missing_pillars = self.diagnose_3plus1_balance(G_clean, all_nodes)
            report["global_void_alerts"].append(
                {
                    "alert_type": "TOPOLOGICAL_VOID_OPEN_LOOP",
                    "status": "H1=0 (Broken Feedback Cycle)",
                    "pillar_distribution": counts,
                    "missing_functional_roles": missing_pillars,
                    "neighbor_nodes": [
                        {
                            "id": n,
                            "label": G_clean.nodes[n]["domain_label"],
                            "pillar": G_clean.nodes[n]["pillar"],
                        }
                        for n in all_nodes
                    ],
                }
            )

        return report


class TopologicalDiscoveryAdapter(BaseDomainAdapter):
    """Connects TopologicalHolonEngine telemetry to Universal3Plus1Kernel governance."""

    def __init__(self, engine, latest_report=None):
        self.engine = engine
        self.latest_report = latest_report or {}

    def sense(self, current_weights):
        promoted = len(self.latest_report.get("promoted_holons", []))
        voids = len(self.latest_report.get("global_void_alerts", []))
        variance = round(float(promoted + voids) * 0.1, 4)
        external_shift = voids > 0
        return {"variance": variance, "external_shift": external_shift}

    def act(self, updated_weights, mode):
        return {
            "governance_mode": mode,
            "updated_weights": updated_weights,
            "active_macro_holons": list(self.engine.macro_holons.keys()),
        }
