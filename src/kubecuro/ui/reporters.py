"""
AKESO REPORTERS
---------------
Structured output generators for CI/CD integration.
"""
import json
import time
from typing import Dict, Any, List

class JSONReporter:
    """Generates a standard JSON report of the execution."""
    
    def generate(self, results: Dict[str, Any], duration: float) -> str:
        processed = results.get("processed_files", [])
        
        # Calculate totals
        total_issues = 0
        for f in processed:
            total_issues += len(f.get("findings", []))
            
        report = {
            "metadata": {
                "tool": "akeso",
                "version": "0.1.0",
                "timestamp": time.time(),
                "duration_seconds": duration
            },
            "summary": {
                "total_files": len(processed),
                "healed_files": results.get("healed_count", 0),
                "total_issues": total_issues
            },
            "results": processed
        }
        return json.dumps(report, indent=2)

class SARIFReporter:
    """Generates GitHub Advanced Security compatible SARIF 2.1.0 output."""
    
    def generate(self, results: Dict[str, Any]) -> str:
        sarif_results = []
        rules = []
        rule_indices = {} # Map rule_id -> index
        
        processed = results.get("processed_files", [])
        
        for file_data in processed:
            file_path = file_data.get("file_path", "unknown")
            findings = file_data.get("findings", [])
            
            for finding in findings:
                rule_id = finding.get("rule_id", "akeso/unknown")
                
                # Register rule if new
                if rule_id not in rule_indices:
                    rule_indices[rule_id] = len(rules)
                    rules.append({
                        "id": rule_id,
                        "name": finding.get("analyzer_name", "Unknown Analyzer"),
                        "shortDescription": {
                            "text": finding.get("message", "No description")
                        },
                        "defaultConfiguration": {
                            "level": "error" if finding.get("severity") == "error" else "warning"
                        }
                    })
                
                # Create SARIF result
                sarif_results.append({
                    "ruleId": rule_id,
                    "ruleIndex": rule_indices[rule_id],
                    "level": "error" if finding.get("severity") == "error" else "warning",
                    "message": {
                        "text": finding.get("message")
                    },
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {
                                    "uri": file_path
                                },
                                "region": {
                                    "startLine": finding.get("line_number", 1) or 1
                                }
                            }
                        }
                    ]
                })

        sarif = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Akeso",
                            "informationUri": "https://github.com/akeso-project/akeso",
                            "rules": rules
                        }
                    },
                    "results": sarif_results
                }
            ]
        }
        
        return json.dumps(sarif, indent=2)
