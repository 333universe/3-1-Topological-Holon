"""
Invariant 3+1 Holographic Base Kernel (v5.0 Spec Compliant).
Governs tripartite macro-execution (Efficiency, Balance, Change) via an orthogonal
0.0001 Holographic Orchestrator with recursive fractal scaling.
"""


class Universal3Plus1Kernel:
    """Invariant 3+1 Holographic Base Kernel with Recursive Fractal Spawning."""

    def __init__(self, profile="STANDARD", depth=0):
        self.immutable_seed = {"E": 0.3333, "B": 0.3333, "C": 0.3333, "O": 0.0001}
        self.weights = self.immutable_seed.copy()
        self.depth = depth
        self.sub_kernels = {}
        profiles = {
            "TIGHT": {"floor": 0.3000, "ceiling": 0.3600, "window": 0},
            "STANDARD": {"floor": 0.2000, "ceiling": 0.4000, "window": 1},
            "WIDE": {"floor": 0.1000, "ceiling": 0.5500, "window": 3},
        }
        if profile not in profiles:
            raise ValueError(f"Unknown tolerance profile: {profile}")
        self.bounds = profiles[profile]
        self.hard_stop_floor = 0.0500
        self.elasticity_timer = 0

    def verify_core_integrity(self):
        """Holographic Quarantine & Reset (+/- 1% Checksum on 0.0001 Core)."""
        if abs(self.weights["O"] - 0.0001) > 0.000001:
            self.weights = self.immutable_seed.copy()
            return "QUARANTINE_RESET_EXECUTED"
        return "CORE_NOMINAL"

    def step(self, domain_adapter):
        """Execute one closed-loop cybernetic governance cycle."""
        if self.verify_core_integrity() != "CORE_NOMINAL":
            return domain_adapter.act(self.weights, mode="QUARANTINE_RESET")

        telemetry = domain_adapter.sense(self.weights)

        # MODE A: Stabilizing Anchor (Anti-Chaos Governance)
        if any(
            self.weights[k] > self.bounds["ceiling"] or self.weights[k] < self.bounds["floor"]
            for k in ("E", "B", "C")
        ):
            self._rebalance_to_parity()
            return domain_adapter.act(self.weights, mode="MODE_A_STABILIZE")

        # MODE B: Generative Anomaly (Anti-Stagnation Symmetry Breaking)
        if telemetry.get("variance", 0) == 0 and telemetry.get("external_shift", False):
            shift = min(0.0667, self.bounds["ceiling"] - self.weights["C"])
            self.weights["C"] = round(self.weights["C"] + shift, 4)
            self.weights["E"] = round(max(self.hard_stop_floor, self.weights["E"] - shift), 4)
            self.elasticity_timer = self.bounds["window"]
            return domain_adapter.act(self.weights, mode="MODE_B_GENERATIVE_SPARK")

        # Automatic Return-to-Center Timer
        if self.elasticity_timer > 0:
            self.elasticity_timer -= 1
            if self.elasticity_timer == 0:
                self._rebalance_to_parity()

        return domain_adapter.act(self.weights, mode="STEADY_STATE")

    def grow_sub_triad(self, pillar_key, profile="STANDARD"):
        """Fractal Expansion: Normalize any pillar/holon to 1.0000 and spawn a child triad."""
        self.sub_kernels[pillar_key] = Universal3Plus1Kernel(profile=profile, depth=self.depth + 1)
        return self.sub_kernels[pillar_key]

    def get_fractal_tree(self):
        """Recursively returns the active Depth 0 -> Depth N kernel hierarchy."""
        return {
            "depth": self.depth,
            "weights": self.weights,
            "children": {k: v.get_fractal_tree() for k, v in self.sub_kernels.items()},
        }

    def _rebalance_to_parity(self):
        for k in ("E", "B", "C"):
            self.weights[k] = 0.3333


class BaseDomainAdapter:
    """Template Interface for Plugging Any Domain into Universal3Plus1Kernel."""

    def sense(self, current_weights):
        return {"variance": 0.0, "external_shift": False}

    def act(self, updated_weights, mode):
        return {"mode": mode, "weights": updated_weights}
