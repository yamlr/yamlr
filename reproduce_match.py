
from typing import Dict

def _labels_match(selector: Dict[str, str], labels: Dict[str, str]) -> bool:
    """Checks if a selector matches a set of labels (Simulated)."""
    print(f"DEBUG: Comparing {selector} vs {labels}")
    for key, value in selector.items():
        target = labels.get(key)
        print(f"  Key: {key}, Target: '{target}' ({type(target)}), Value: '{value}' ({type(value)})")
        
        if target is None:
            print("  -> Target is None")
            return False
            
        # Current Logic
        # if str(target).strip() != str(value).strip():
        #     return False
        
        # Original Logic
        if target != value:
             print("  -> Original Mismatch")
             
        # Robust Logic
        if str(target).strip() != str(value).strip():
             print("  -> Robust Mismatch")
             return False
             
    print("  -> Match!")
    return True

# Scenario 1: Identical Strings
s1 = {'app': 'nginx'}
l1 = {'app': 'nginx', 'version': '1.0'}
_labels_match(s1, l1)

# Scenario 2: Int vs String
s2 = {'port': 80}
l2 = {'port': '80'}
_labels_match(s2, l2)

# Scenario 3: Newline
s3 = {'app': 'nginx'}
l3 = {'app': 'nginx\n'}
_labels_match(s3, l3)
