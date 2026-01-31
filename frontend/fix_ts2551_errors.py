#!/usr/bin/env python3
"""
Script para corrigir erros TS2551 automaticamente usando as sugestões do TypeScript.
"""

import subprocess
import re
from pathlib import Path

def get_ts2551_errors():
    """Executa type-check e extrai erros TS2551 com sugestões."""
    result = subprocess.run(
        ['npm', 'run', 'type-check'],
        capture_output=True,
        text=True,
        cwd='/opt/conecta-pro/frontend'
    )

    output = result.stdout + result.stderr
    lines = output.split('\n')

    errors = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if 'error TS2551' in line and 'Did you mean' in line:
            # Extrair informações do erro
            match = re.match(r'^(.+?)\((\d+),(\d+)\): error TS2551: Property \'(.+?)\' does not exist.*Did you mean \'(.+?)\'', line)
            if match:
                file_path, line_num, col_num, wrong_name, correct_name = match.groups()
                errors.append({
                    'file': file_path,
                    'line': int(line_num),
                    'col': int(col_num),
                    'wrong': wrong_name,
                    'correct': correct_name
                })
        i += 1

    return errors

def fix_error(error):
    """Corrige um erro específico no arquivo."""
    file_path = Path('/opt/conecta-pro/frontend') / error['file']

    if not file_path.exists():
        print(f"Arquivo não encontrado: {file_path}")
        return False

    try:
        content = file_path.read_text()
        lines = content.split('\n')

        # Linha é 1-indexed, converter para 0-indexed
        line_idx = error['line'] - 1

        if line_idx >= len(lines):
            print(f"Linha {error['line']} não existe em {file_path}")
            return False

        line = lines[line_idx]

        # Substituir apenas a primeira ocorrência do nome errado na linha
        if error['wrong'] in line:
            lines[line_idx] = line.replace(error['wrong'], error['correct'], 1)
            file_path.write_text('\n'.join(lines))
            print(f"✓ {file_path.name}:{error['line']} - {error['wrong']} → {error['correct']}")
            return True
        else:
            print(f"✗ {file_path.name}:{error['line']} - Texto '{error['wrong']}' não encontrado")
            return False

    except Exception as e:
        print(f"Erro ao processar {file_path}: {e}")
        return False

def main():
    print("Buscando erros TS2551...")
    errors = get_ts2551_errors()

    print(f"\nEncontrados {len(errors)} erros TS2551 com sugestões")

    if not errors:
        print("Nenhum erro para corrigir!")
        return

    print("\nCorrigindo erros...\n")

    fixed = 0
    for error in errors:
        if fix_error(error):
            fixed += 1

    print(f"\n{'='*60}")
    print(f"Corrigidos: {fixed}/{len(errors)} erros")
    print(f"{'='*60}")

    # Executar type-check novamente para mostrar progresso
    print("\nExecutando type-check novamente...")
    result = subprocess.run(
        ['npm', 'run', 'type-check', '2>&1', '|', 'grep', '"error TS"', '|', 'wc', '-l'],
        shell=True,
        capture_output=True,
        text=True,
        cwd='/opt/conecta-pro/frontend'
    )
    print(f"Erros restantes: {result.stdout.strip()}")

if __name__ == '__main__':
    main()
