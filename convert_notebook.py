import json
import re

notebook_path = "__Preprocessing_all (2).ipynb"
output_path = "preprocessing_script.py"

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

with open(output_path, 'w', encoding='utf-8') as f:
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = cell['source']
            for line in source:
                # Comment out magics
                if line.strip().startswith('%') or line.strip().startswith('!'):
                    f.write('# ' + line)
                else:
                    f.write(line)
            f.write('\n\n')

print(f"Converted {notebook_path} to {output_path}")
