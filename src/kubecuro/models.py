#!/usr/bin/env python3
"""
AKESO CORE MODELS
-----------------
Defines the fundamental data structures used across the Akeso engine.
These models represent the "Data Contract" between the Lexer, Shadow, and Scanner.

CNCF Standards Compliance:
- Extensible: Uses metadata dictionaries to allow Enterprise (Pro) data injection.
- Optimized: Uses slots and targeted mutability for high-performance manifest healing.

Author: Nishar A Sunkesala / Akeso Team
Date: 2026-01-21
"""

import sys
from dataclasses import dataclass, field
from typing import Optional, Any, List, Union, Dict

@dataclass(slots=True)
class Shard:
    """
    The atomic unit of a Kubernetes manifest.
    A Shard represents a logical line (key-value) and its visual 'intent'.
    
    The 'layout_sequence' holds Gaps and Comments captured by AkesoShadow,
    allowing for a 1:1 faithful reconstruction of the original human layout.
    """
    line_no: int
    indent: int
    key: str
    value: Optional[Any] = None
    is_list_item: bool = False
    is_table_continuation: bool = False
    is_block: bool = False
    is_doc_boundary: bool = False
    comment: Optional[str] = None
    raw_line: str = ""
    
    # layout_sequence stores Gap objects or raw comment strings.
    # We allow mutability here so AkesoShadow can graft layout after Lexing.
    layout_sequence: List[Union[str, Any]] = field(default_factory=list)
    
    # Pro-Extension: Allows Kubecuro to tag shards with intent (e.g., 'SECURITY_ANNOTATION')
    intent_tag: Optional[str] = None


@dataclass
class ManifestIdentity:
    """Represents the discovered 'DNA' of a Kubernetes resource."""
    api_version: Optional[str] = None
    kind: Optional[str] = None
    name: Optional[str] = None
    namespace: Optional[str] = None
    doc_index: int = 0 
    was_repaired: bool = False
    
    # Cross-resource tracking (OSS feature)
    selector: Optional[Dict[str, str]] = None  # For Service/Deployment
    labels: Optional[Dict[str, str]] = None    # For Pod/Deployment
    config_refs: List[str] = field(default_factory=list)  # ConfigMap/Secret names
    volume_refs: List[str] = field(default_factory=list)  # PVC names
    service_refs: List[str] = field(default_factory=list)  # Ingress → Service
    scale_target: Optional[str] = None  # HPA → Deployment/StatefulSet
    service_account: Optional[str] = None  # Pod → ServiceAccount
    
    # Deprecation tracking (OSS feature)
    deprecation_info: Optional[Any] = None  # DeprecationInfo from deprecations.py
    
    def is_deprecated(self) -> bool:
        """Check if this resource uses a deprecated API."""
        return self.deprecation_info is not None

    def is_complete(self) -> bool:
        """Determines if the identity is sufficient for schema-aware healing."""
        return bool(self.kind and self.api_version)

    def __str__(self):
        """Dynamic branding: sys._akeso_provider is set by Kubecuro on initialization."""
        provider = getattr(sys, "_akeso_provider", "Akeso")
        return f"[{provider}] {self.kind or 'Unknown'}/{self.name or 'Unnamed'}"
    
    def to_dict(self) -> dict:
        """
        Serializes the identity object for CLI reporting and API exports.
        """
        return {
            "kind": self.kind,
            "name": self.name,
            "namespace": self.namespace,
            "api_version": self.api_version
        }

@dataclass
class SchemaNode:
    """
    [REFERENCE DOCUMENTATION ONLY]
    
    Defines the expected structure of K8s catalog schemas.
    Currently, catalogs are loaded and used as Dict[str, Any] for flexibility.
    
    This class serves as documentation for the catalog schema format.
    It is NOT instantiated at runtime in the current implementation.
    
    Future Enhancement: Could migrate to Pydantic models for runtime validation.
    """
    node_type: str  # 'object', 'array', 'string', 'integer', 'int_or_string'
    fields: Dict[str, 'SchemaNode'] = field(default_factory=dict)
    item_type: Optional[str] = None  # For arrays: type of items
    ref: Optional[str] = None  # JSON schema $ref if present
    
@dataclass
class HealAction:
    """
    Represents a single healing action taken during the pipeline.
    Used for audit trails and detailed reporting.
    
    Examples:
        - Lexer: Fixed flush-left list at line 23
        - Shield: Added resource limits to container 'web'
        - Validator: Schema validation passed for Deployment/nginx
    
    Author: Nishar A Sunkesala / Akeso Team
    Date: 2026-01-26
    """
    stage: str  # Stage that performed the action (e.g., "Lexer", "Shield")
    action_type: str  # Type of action (e.g., "repair", "harden", "validate")
    target: str  # What was modified (e.g., "line 5", "spec.replicas")
    description: str  # Human-readable description
    severity: str = "INFO"  # INFO, WARNING, ERROR
    
    def to_dict(self) -> dict:
        """Serialize for JSON export."""
        return {
            "stage": self.stage,
            "action_type": self.action_type,
            "target": self.target,
            "description": self.description,
            "severity": self.severity
        }
