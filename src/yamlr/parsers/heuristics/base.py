from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any

class BaseHeuristic(ABC):
    """
    Abstract strategy for a specific healing heuristic.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this heuristic."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this heuristic fixes."""
        pass

    @abstractmethod
    def apply(self, line: str, context: Dict[str, Any]) -> str:
        """
        Applies the heuristic to a single line of code.
        
        Args:
            line: The raw line content (stripped or semi-processed)
            context: Shared state (e.g., stats counter, block state)
            
        Returns:
            The potentially modified line.
        """
        pass
