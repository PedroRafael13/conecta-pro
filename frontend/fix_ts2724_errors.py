#!/usr/bin/env python3
"""
Script para corrigir erros TS2724 (tipos com nome errado, com sugestão).
"""

import subprocess
import re
from pathlib import Path

def get_ts2724_errors():
    """Extrai erros TS2724 com sugestões."""
    result = subprocess.run(
        ['npm', 'run', 'type-check'],
        capture_output=True,
        text=True,
        cwd='/opt/conecta-pro/frontend'
    )

    output = result.stdout + result.stderr
    lines = output.split('\n')

    errors = []
    for line in lines:
        if 'error TS2724' in line and 'Did you mean' in line:
            match = re.match(r'^(.+?)\((\d+),(\d+)\): error TS2724:.*named \'(.+?)\'.*Did you mean \'(.+?)\'', line)
            if match:
                file_path, line_num, col_num, wrong_name, correct_name = match.groups()
                errors.append({
                    'file': file_path,
                    'line': int(line_num),
                    'wrong': wrong_name,
                    'correct': correct_name
                })

    return errors

def fix_error(error):
    """Corrige um erro TS2724."""
    file_path = Path('/opt/conecta-pro/frontend') / error['file']

    if not file_path.exists():
        return False

    try:
        content = file_path.read_text()
        lines = content.split('\n')

        line_idx = error['line'] - 1
        if line_idx >= len(lines):
            return False

        line = lines[line_idx]

        # Substituir o nome errado pelo correto
        if error['wrong'] in line and not line.strip().startswith('//'):
            lines[line_idx] = line.replace(error['wrong'], error['correct'], 1)
            file_path.write_text('\n'.join(lines))
            print(f"✓ {file_path.name}:{error['line']} - {error['wrong']} → {error['correct']}")
            return True

        return False

    except Exception as e:
        print(f"Erro ao processar {file_path}: {e}")
        return False

def main():
    print("Buscando erros TS2724...")
    errors = get_ts2724_errors()

    print(f"\nEncontrados {len(errors)} erros TS2724")

    if not errors:
        print("Nenhum erro para corrigir!")
        return

    print("\nCorrigindo tipos...\n")

    fixed = 0
    for error in errors:
        if fix_error(error):
            fixed += 1

    print(f"\n{'='*60}")
    print(f"Corrigidos: {fixed}/{len(errors)} erros")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
