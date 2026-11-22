"""
Step 5 Semantic Translation Co-Pilot Bridge.
Translates topological findings and 3+1 functional deficits into human hypotheses.
"""

import json


class SemanticCoPilotBridge:
    """Translates topological voids and cross-domain analogies into structured discovery briefs."""

    PILLAR_DESCRIPTIONS = {
        "E": "Efficiency (Throughput, execution catalyst, or flow routing hub)",
        "B": "Balance (Containment, negative feedback regulator, inhibitor, or verification brake)",
        "C": "Change (Adaptive switch, bifurcation trigger, or state mutator)",
        "O": "Orchestrator (Low-overhead meta-router or deadlock tie-breaker)",
    }

    def build_hypothesis_prompt(self, source_report, target_report):
        """Constructs a domain-grounded discovery prompt from topological comparisons."""
        source_holons = source_report.get("promoted_holons", [])
        target_voids = target_report.get("global_void_alerts", [])

        prompt_lines = [
            "=== 3+1 TOPOLOGICAL HOLON DISCOVERY BRIEF ===",
            f"Reference Domain (Complete Topology): {source_report['domain']}",
            f"Target Domain (Investigated System): {target_report['domain']}",
            "",
            "1. VERIFIED REFERENCE STRUCTURE (H1 Closed Loop):",
        ]

        for h in source_holons:
            prompt_lines.append(
                f"   - Holon ID: {h['holon_id']} | Z-Surprise: {h['z_surprise']} | Nodes: {h['domain_labels']}"
            )

        prompt_lines.append("")
        prompt_lines.append("2. TARGET DOMAIN TOPOLOGICAL VOID & 3+1 DIAGNOSIS:")

        for v in target_voids:
            missing_desc = [
                f"{m} -> {self.PILLAR_DESCRIPTIONS.get(m, m)}"
                for m in v["missing_functional_roles"]
            ]
            prompt_lines.append(f"   - Alert: {v['alert_type']} ({v['status']})")
            prompt_lines.append(f"   - Missing 3+1 Pillar(s): {', '.join(missing_desc)}")
            prompt_lines.append(f"   - Exposed Boundary Nodes: {json.dumps(v['neighbor_nodes'])}")

        prompt_lines.extend(
            [
                "",
                "3. TASK FOR SCIENTIFIC / STRATEGIC CO-PILOT:",
                "   Based on the structural isomorphism between the Reference Domain and Target Domain,",
                "   propose 3 concrete real-world mechanisms, entities, or interventions in the Target Domain",
                "   that fulfill the missing 3+1 functional role(s) and close the topological void.",
            ]
        )

        return "\n".join(prompt_lines)
