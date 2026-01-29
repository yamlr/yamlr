"""
AKESO ANALYZER INTERFACE
------------------------
This module defines the abstract base class and data structures for the
Analyzer Plugin System. All semantic checks (built-in or custom) must
adhere to this interface to be executable by the Healing Pipeline.

Metadata:
    - Component: Analyzer Interface
    - Author: Akeso Team
    - License: Apache 2.0
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

# We iterate over ManifestIdentity objects in the pipeline
# We need to import this carefully to avoid circular imports if possible,
# or define a Protocol if strictly necessary. For now, we assume it's available.
# To keep this file clean and standalone, we might use stricter typing or
# Just 'Any' for complex objects if we want to decouple, but let's try to be precise.
# Assuming ManifestIdentity is in akeso.core.pipeline (based on previous context) logic,
# or akeso.core.engine. Wait, ManifestIdentity is likely defined in pipeline or a types module.
# Based on summary, it's used in pipeline.
# Let's use Any for the input type signature to avoid circular dependency hell
# until we place it in a shared types module.

@dataclass
class AnalysisResult:
    """
    Standardized result object returned by an analyzer.
    Captures a specific issue found during analysis.
    """
    analyzer_name: str
    severity: str  # "INFO", "WARNING", "ERROR"
    message: str
    resource_name: str
    resource_kind: str
    file_path: str
    rule_id: Optional[str] = None  # New: For config ignores
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    
    # Metadata for potential auto-fixes (Pro feature)
    fix_available: bool = False
    fix_id: Optional[str] = None

class BaseAnalyzer(ABC):
    """
    Abstract Base Class for all Akeso Analyzers.
    
    Any custom logic to check for semantic errors (like Ghost Services,
    missing labels, etc.) must inherit from this class and implement
    the `analyze` method.
    """

    @property
    def analyzer_type(self) -> str:
        """
        Determines when the analyzer runs.
        - 'metadata': Runs at Stage 3.5 on ManifestIdentity (fast, cross-resource).
        - 'content': Runs at Stage 6.5 on Reconstructed Dicts (deep inspection).
        Default: 'metadata'
        """
        return "metadata"

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique identifier for the analyzer.
        Example: "ghost-service-detector"
        """
        pass

    @abstractmethod
    def analyze(self, identities: List[Any]) -> List[AnalysisResult]:
        """
        Refactored core logic to analyze a collection of resources.
        
        Args:
            identities: A list of ManifestIdentity objects representing
                       all discovered resources in the workspace.
                       
        Returns:
            A list of AnalysisResult objects detailing any findings.
        """
        pass
