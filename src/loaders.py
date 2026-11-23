"""Real-World Data Ingestion Adapters for the 3+1 Topological Holon Engine.

Converts raw CSV edge lists, JSON concept triples, and multivariate numerical
time-series tables into typed (E, B, C, O) Holon graphs ready for (Beta_0, Beta_1, Beta_2)
homology scanning and cross-domain analogy discovery.
"""

import csv
import io
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import networkx as nx


def auto_infer_pillars(
    nodes: Dict[str, Dict[str, Any]],
    edges: List[Tuple[str, str, str, float]],
) -> Dict[str, Dict[str, Any]]:
    """Infers 3+1 functional roles (E, B, C, O) for unlabeled nodes from local topology.

    - High inhibitory / feedback participation -> B (Balance)
    - High transformation / branching degree  -> C (Change)
    - High directional throughput flow        -> E (Efficiency)
    - Low-load high-betweenness coordinator   -> O (Orchestrator)
    """
    in_deg = {n: 0 for n in nodes}
    out_deg = {n: 0 for n in nodes}
    inhib_count = {n: 0 for n in nodes}
    transform_count = {n: 0 for n in nodes}

    for u, v, etype, _ in edges:
        if u in out_deg:
            out_deg[u] += 1
        if v in in_deg:
            in_deg[v] += 1
        if etype in ("INHIBITS", "DELAYS"):
            if u in inhib_count:
                inhib_count[u] += 1
            if v in inhib_count:
                inhib_count[v] += 1
        elif etype in ("TRANSFORMS", "CONTAINS"):
            if u in transform_count:
                transform_count[u] += 1

    inferred = {}
    for n_id, meta in nodes.items():
        updated_meta = dict(meta)
        if "pillar" not in updated_meta or not updated_meta["pillar"]:
            total_deg = in_deg[n_id] + out_deg[n_id]
            if inhib_count[n_id] >= 1 and in_deg[n_id] >= 1 and out_deg[n_id] >= 1:
                updated_meta["pillar"] = "B"
            elif transform_count[n_id] >= 1 or (out_deg[n_id] > in_deg[n_id] and total_deg >= 2):
                updated_meta["pillar"] = "C"
            elif total_deg == 0:
                updated_meta["pillar"] = "O"
            else:
                updated_meta["pillar"] = "E"
        inferred[n_id] = updated_meta
    return inferred


def load_from_csv_text(
    csv_content: str,
    default_edge_type: str = "AMPLIFIES",
    auto_pillars: bool = True,
) -> Tuple[Dict[str, Dict[str, Any]], List[Tuple[str, str, str, float]]]:
    """Parses CSV relational data with columns: source, target, [edge_type], [weight], [source_pillar], [target_pillar]."""
    reader = csv.DictReader(io.StringIO(csv_content.strip()))
    nodes: Dict[str, Dict[str, Any]] = {}
    edges: List[Tuple[str, str, str, float]] = []

    raw_weights = []
    parsed_rows = []
    for row in reader:
        u = row["source"].strip()
        v = row["target"].strip()
        etype = (row.get("edge_type") or default_edge_type).strip().upper()
        w = float(row.get("weight") or 0.85)
        raw_weights.append(abs(w))
        parsed_rows.append((u, v, etype, w, row))

    max_w = max(raw_weights) if raw_weights else 1.0
    scale = max_w if max_w > 1.0 else 1.0

    for u, v, etype, w, row in parsed_rows:
        if u not in nodes:
            nodes[u] = {"label": row.get("source_label", u).strip()}
            if row.get("source_pillar"):
                nodes[u]["pillar"] = row["source_pillar"].strip().upper()
        if v not in nodes:
            nodes[v] = {"label": row.get("target_label", v).strip()}
            if row.get("target_pillar"):
                nodes[v]["pillar"] = row["target_pillar"].strip().upper()

        norm_w = round(min(1.0, abs(w) / scale), 4)
        edges.append((u, v, etype, norm_w))

    if auto_pillars:
        nodes = auto_infer_pillars(nodes, edges)
    return nodes, edges


def load_from_time_series(
    series_dict: Dict[str, List[float]],
    corr_threshold: float = 0.45,
    auto_pillars: bool = True,
) -> Tuple[Dict[str, Dict[str, Any]], List[Tuple[str, str, str, float]]]:
    """Converts multivariate numerical time-series into a signed topological graph.

    Positive correlation (+r) -> AMPLIFIES edge
    Negative correlation (-r) -> INHIBITS edge
    """
    names = list(series_dict.keys())
    matrix = np.array([series_dict[k] for k in names], dtype=float)
    corr = np.corrcoef(matrix)

    nodes = {name: {"label": name} for name in names}
    edges: List[Tuple[str, str, str, float]] = []

    n = len(names)
    for i in range(n):
        for j in range(i + 1, n):
            r = float(corr[i, j])
            if np.isnan(r) or abs(r) < corr_threshold:
                continue
            # Orient causality by variance / lead-lag proxy (higher variance drives lower variance)
            var_i = float(np.var(matrix[i]))
            var_j = float(np.var(matrix[j]))
            src, dst = (names[i], names[j]) if var_i >= var_j else (names[j], names[i])
            etype = "AMPLIFIES" if r > 0 else "INHIBITS"
            edges.append((src, dst, etype, round(abs(r), 4)))

    if auto_pillars:
        nodes = auto_infer_pillars(nodes, edges)
    return nodes, edges
