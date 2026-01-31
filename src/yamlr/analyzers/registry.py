"""
Yamlr ANALYZER REGISTRY
-----------------------
This module implements the Registry pattern for managing Yamlr Analyzers.
It provides a central point to register, discover, and retrieve all
active semantic checks.

Metadata:
    - Component: Analyzer Registry
    - Author: Yamlr Team
    - Pattern: Singleton / Registry
"""

import logging
from typing import Dict, Type, List, Optional
from yamlr.analyzers.base import BaseAnalyzer

logger = logging.getLogger("yamlr.analyzers.registry")

class AnalyzerRegistry:
    """
    Singleton registry to manage available analyzers.
    Community plugins and core analyzers register themselves here.
    """
    
    _analyzers: Dict[str, Type[BaseAnalyzer]] = {}
    _instances: Dict[str, BaseAnalyzer] = {}

    @classmethod
    def register(cls, analyzer_cls: Type[BaseAnalyzer]):
        """
        Decorator to register a new analyzer class.
        
        Usage:
            @AnalyzerRegistry.register
            class MyCustomAnalyzer(BaseAnalyzer):
                ...
        """
        try:
            # We instantiate it once to get the name property, 
            # or we rely on the class having a static name.
            # Using instantiation aligns with the BaseAnalyzer abstract property pattern.
            name = analyzer_cls.name 
            if isinstance(name, property):
                 # If name is a property, we might need an instance to read it,
                 # or we change the interface to be a class property.
                 # For simplicity, let's assume specific implementation allows access 
                 # or we instantiate a throwaway to check name uniqueness 
                 # BUT safer: let's instantiate lazily.
                 pass
            
            # Use class name as key for internal storage if name is dynamic,
            # but ideally we want the semantic name.
            # Let's assume we can get it or just store by class for now 
            # and verify name upon instantiation.
            cls._analyzers[analyzer_cls.__name__] = analyzer_cls
            logger.debug(f"Registered analyzer: {analyzer_cls.__name__}")
        except Exception as e:
            logger.error(f"Failed to register analyzer {analyzer_cls}: {e}")
        return analyzer_cls

    @classmethod
    def register_defaults(cls):
        """
        Explicitly loads and registers the core standard analyzers.
        This avoids relying on import side-effects in main.py.
        """
        # Import inside method to avoid circular deps or early loading
        try:
            from yamlr.analyzers.cross_resource import CrossResourceAnalyzer
            from yamlr.analyzers.best_practices import (
                ResourceAnalyzer, 
                ImageAnalyzer, 
                SecurityAnalyzer, 
                ProbeAnalyzer
            )
            
            cls.register(CrossResourceAnalyzer)
            cls.register(ResourceAnalyzer)
            cls.register(ImageAnalyzer)
            cls.register(SecurityAnalyzer)
            cls.register(ProbeAnalyzer)
            
            logger.info(f"Registered {len(cls._analyzers)} default analyzers")
        except Exception as e:
            logger.error(f"Failed to register default analyzers: {e}")

    @classmethod
    def get_all_analyzers(cls) -> List[BaseAnalyzer]:
        """
        Returns a list of instantiated analyzer objects ready for execution.
        Instantiates them lazily if not already created.
        Auto-discovers default analyzers if registry is empty.
        """
        # Auto-discover defaults if registry is empty
        if not cls._analyzers:
            cls.register_defaults()
        
        active_analyzers = []
        for class_name, analyzer_cls in cls._analyzers.items():
            if class_name not in cls._instances:
                try:
                    instance = analyzer_cls()
                    cls._instances[class_name] = instance
                except Exception as e:
                    logger.error(f"Could not instantiate analyzer {class_name}: {e}")
                    continue
            
            active_analyzers.append(cls._instances[class_name])
            
        return active_analyzers

    @classmethod
    def clear(cls):
        """Resets the registry (useful for tests)."""
        cls._analyzers = {}
        cls._instances = {}

# Helper decorator for easier imports
register_analyzer = AnalyzerRegistry.register
