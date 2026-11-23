"""3+1 Topological Holon Discovery Engine package."""

from .kernel import Universal3Plus1Kernel, BaseDomainAdapter
from .engine import TopologicalHolonEngine, TopologicalDiscoveryAdapter
from .copilot import SemanticCoPilotBridge
from .loaders import auto_infer_pillars, load_from_csv_text, load_from_time_series

__all__ = [
    "Universal3Plus1Kernel",
    "BaseDomainAdapter",
    "TopologicalHolonEngine",
    "TopologicalDiscoveryAdapter",
    "SemanticCoPilotBridge",
    "auto_infer_pillars",
    "load_from_csv_text",
    "load_from_time_series",
]
