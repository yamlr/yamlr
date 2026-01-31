#!/usr/bin/env python3
"""
Extractor for Port definitions (Service & Workload).

Extracts:
- Service: spec.ports[] (port, targetPort, name)
- Workload: spec.containers[].ports[] (containerPort, name)
"""

from typing import List
from yamlr.models import Shard, ManifestIdentity

class PortsExtractor:
    """Extracts Port information from Services and Workloads."""
    
    @staticmethod
    def extract_if_applicable(
        shard: Shard,
        key: str,
        val: str,
        path_keys: List[str],
        identity: ManifestIdentity
    ) -> bool:
        
        # 1. SERVICE PORTS
        if identity.kind == "Service":
            if "ports" in path_keys:
                # Standardize key names
                if key not in ("port", "targetPort", "name", "nodePort", "protocol"):
                    return False
                
                # If this is a new list item, it starts a new port entry
                if shard.is_list_item:
                    identity.service_ports.append({})
                
                # Ensure we have a dict to write to (handling edge case of malformed YAML)
                if not identity.service_ports:
                    identity.service_ports.append({})
                
                identity.service_ports[-1][key] = val
                return True

        # 2. WORKLOAD PORTS
        # Deployments, Pods, StatefulSets, DaemonSets, Jobs, CronJobs
        elif identity.kind in ("Deployment", "StatefulSet", "DaemonSet", "Pod", "Job", "CronJob", "ReplicaSet"):
            if "containers" in path_keys and "ports" in path_keys:
                # We simply collect ALL container ports into a flat list for now
                # This is sufficient for "Does this port exist?" checks
                
                if key == "containerPort":
                    if val and val not in identity.container_ports:
                        identity.container_ports.append(val)
                    return True
                
                if key == "name":
                    # Named ports are also valid targets
                    if val and val not in identity.container_ports:
                        identity.container_ports.append(val)
                    return True
                    
        return False
