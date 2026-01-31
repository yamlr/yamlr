#!/usr/bin/env python3
"""
--------------------------------------------------------------------------------
AUTHOR:      Nishar A Sunkesala / FixMyK8s
PURPOSE:      The Shield Engine: Static Analysis & Policy Hardening.
--------------------------------------------------------------------------------
"""
import re
import sys 

class RegexShield:
    @staticmethod
    def sanitize(raw_yaml: str) -> tuple[str, set]:
        """Regex-based emergency cleaner (The First Line of Defense)."""
        issues = set()
        clean = raw_yaml
        
        # 1. Trailing spaces
        if re.search(r' +$', clean, re.MULTILINE):
            issues.add("GEN_TRAILING_SPACE")
            clean = re.sub(r'[ \t]+$', '', clean, flags=re.MULTILINE)
            
        # 2. Tabs to 2 spaces
        if '\t' in clean:
            issues.add("GEN_TABS_FOUND")
            clean = clean.replace('\t', '  ')
            
        # 3. Missing separator dashes?
        # TODO: Add logic here from RegexShield if provided
            
        return clean, issues

class Shield:
    # Severity Constants
    CRITICAL = "CRITICAL" # P0: Service outage
    HIGH = "HIGH"         # P1: Security hole / Partial failure
    MEDIUM = "MEDIUM"     # P2: Resilience risk
    LOW = "LOW"           # P3: Optimization

    DEPRECATIONS = {
        'extensions/v1beta1': {'Deployment': 'apps/v1', 'Ingress': 'networking.k8s.io/v1'},
        'apps/v1beta1': {'Deployment': 'apps/v1', 'StatefulSet': 'apps/v1'},
        'apps/v1beta2': {'Deployment': 'apps/v1', 'DaemonSet': 'apps/v1'},
        'batch/v1beta1': {'CronJob': 'batch/v1'},
        'networking.k8s.io/v1beta1': {'Ingress': 'networking.k8s.io/v1'},
        'autoscaling/v2beta1': {'HorizontalPodAutoscaler': 'autoscaling/v2'},
    }

    def scan(self, doc: dict, all_docs: list) -> list:
        """Single-pass static analysis logic."""
        findings = []
        if not doc: return findings

        kind = doc.get('kind')
        api = doc.get('apiVersion')
        metadata = doc.get('metadata', {})
        name = metadata.get('name')
        spec = doc.get('spec', {})

        # line helper
        def get_line(key=None):
            return 1 # Fallback, actual line calc in Synapse

        # 1. API DEPRECATIONS
        if api in self.DEPRECATIONS:
            replacement = self.DEPRECATIONS[api].get(kind, "updated-api")
            findings.append({
                'code': f"API_DEPRECATED_{api.replace('/','_').upper()}",
                'severity': self.HIGH,
                'line': get_line('apiVersion'),
                'msg': f"API '{api}' is deprecated. Upgrade to '{replacement}'."
            })
        
        # 2. HPA CHECK
        if kind == 'HorizontalPodAutoscaler':
            target = spec.get('scaleTargetRef', {})
            t_kind = target.get('kind')
            t_name = target.get('name')
            
            # Find target
            match = next((d for d in all_docs if d.get('kind') == t_kind and d.get('metadata', {}).get('name') == t_name), None)
            if not match:
                findings.append({'code': 'HPA_ORPHAN', 'severity': self.HIGH, 'msg': f"HPA targets missing '{t_name}'."})
            else:
                # Check metrics request
                t_spec = match.get('spec', {}).get('template', {}).get('spec', {})
                containers = t_spec.get('containers', [])
                if not any(c.get('resources', {}).get('requests', {}) for c in containers):
                    findings.append({'code': 'HPA_MISSING_REQ', 'severity': self.HIGH, 'msg': "HPA enabled but pods missing requests."})

        # 3. RBAC WILDCARD
        if kind == 'Role' or kind == 'ClusterRole':
            rules = doc.get('rules', [])
            for r in rules:
                if '*' in r.get('resources', []) and '*' in r.get('verbs', []):
                    findings.append({'code': "RBAC_WILD_FULL", 'severity': self.CRITICAL, 'msg': "Full Admin Access '*' detected."})

        return findings
