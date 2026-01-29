
import os
import re

def refactor_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Imports: from kubecuro -> from kubecuro
    new_content = re.sub(r'from kubecuro\b', 'from kubecuro', content)
    
    # 2. Imports: import kubecuro -> import kubecuro
    new_content = re.sub(r'import kubecuro\b', 'import kubecuro', new_content)
    
    # 3. Loggers: "akeso." -> "kubecuro."
    new_content = new_content.replace('logging.getLogger("kubecuro', 'logging.getLogger("kubecuro')
    new_content = new_content.replace("logging.getLogger('kubecuro", "logging.getLogger('kubecuro")
    
    # 4. Strings in setup/config (pyproject.toml handled separately, but some .py might have it)
    # Be careful not to replace general strings unless sure.
    # We will stick to imports and loggers for code safety.
    
    if content != new_content:
        print(f"Refactoring {filepath}...")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

def main():
    targets = ['src', 'tests', 'hack']
    for target in targets:
        for root, dirs, files in os.walk(target):
            for file in files:
                if file.endswith('.py'):
                    refactor_file(os.path.join(root, file))
    
    # Also handle root files like debug_spec.py
    for file in os.listdir('.'):
        if file.endswith('.py') and file != 'hack': # skip dirs
             refactor_file(file)

if __name__ == "__main__":
    main()
