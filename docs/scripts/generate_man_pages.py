import datetime
import os
import re
import sys
from pathlib import Path

def md_to_troff(markdown_text, command_name):
    # Basic header
    date_str = datetime.datetime.now().strftime("%B %Y")
    troff = f'.TH "{command_name.upper()}" "1" "{date_str}" "Yamlr Manual" "User Commands"\n'

    lines = markdown_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]

        # Headers
        if line.startswith('# '): # H1 (Command Name & Short Desc)
            pass # Handled by .TH
        elif line.startswith('## '): # H2 (Sections)
            section = line[3:].strip().upper()
            troff += f'.SH "{section}"\n'
        elif line.startswith('### '): # H3 (Subsections)
            subsection = line[4:].strip()
            troff += f'.SS "{subsection}"\n'

        # Lists
        elif line.strip().startswith('* ') or line.strip().startswith('- '):
            item = line.strip()[2:]
            # Bold flags like `-f` or `--flag`
            item = re.sub(r'`(-[^`]+)`', r'\\fB\1\\fR', item)
            # Code spans
            item = re.sub(r'`([^`]+)`', r'\\fB\1\\fR', item)
            troff += f'.IP "\\(bu" 2\n{item}\n'

        # Code Blocks
        elif line.strip().startswith('```'):
            troff += '.nf\n.RS\n' # No-fill mode, indented
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                troff += lines[i] + '\n'
                i += 1
            troff += '.RE\n.fi\n' # End indent, fill mode

        # Normal Text
        elif line.strip():
            text = line
            # Bold
            text = re.sub(r'\*\*([^*]+)\*\*', r'\\fB\1\\fR', text)
            # Italic
            text = re.sub(r'\*([^*]+)\*', r'\\fI\1\\fR', text)
            # Code spans
            text = re.sub(r'`([^`]+)`', r'\\fB\1\\fR', text)
            troff += f'{text}\n.PP\n'

        i += 1

    return troff

def generate_man_pages(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith(".md"):
            filepath = os.path.join(input_dir, filename)

            # CRITICAL FIX: Ensure correct naming convention (yamlr_heal.md -> yamlr-heal.1)
            # Replace underscores with hyphens to match kubectl style (kubectl-apply.1)
            command_name = filename.replace('_', '-').replace('.md', '')

            with open(filepath, 'r', encoding='utf-8') as f:
                md_content = f.read()

            troff_content = md_to_troff(md_content, command_name)

            output_filename = f"{command_name}.1"
            output_path = os.path.join(output_dir, output_filename)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(troff_content)

            print(f"Generated {output_path}")

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent.parent
    generate_man_pages(str(base_dir / "docs" / "cli"), str(base_dir / "docs" / "man" / "man1"))
