"""3+1 Topological Holon Discovery Engine package."""

from .kernel import Universal3Plus1Kernel, BaseDomainAdapter
from .engine import TopologicalHolonEngine, TopologicalDiscoveryAdapter
from .copilot import SemanticCoPilotBridge

__all__ = [
    "Universal3Plus1Kernel",
    "BaseDomainAdapter",
    "TopologicalHolonEngine",
    "TopologicalDiscoveryAdapter",
    "SemanticCoPilotBridge",
]

