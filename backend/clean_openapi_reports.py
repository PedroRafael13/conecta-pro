"""
Script para limpar OpenAPI spec do FastAPI removendo schemas problemáticos.
Fix para Orval que não aceita anyOf com type: "null".
"""

import json
import copy

def clean_schema(obj):
    """Remove anyOf problemáticos e converte para formato compatível."""
    if isinstance(obj, dict):
        # Se tem anyOf com null, converte para opcional simples
        if 'anyOf' in obj:
            any_of = obj['anyOf']
            # Procura por tipo não-null
            non_null_types = [item for item in any_of if item.get('type') != 'null']

            if len(non_null_types) == 1:
                # Substitui anyOf pelo tipo direto
                del obj['anyOf']
                obj.update(non_null_types[0])
            elif len(non_null_types) > 1:
                # Se tem múltiplos tipos não-null, mantém anyOf apenas deles
                obj['anyOf'] = non_null_types

        # Recursivamente limpa todos os valores
        for key, value in list(obj.items()):
            if isinstance(value, (dict, list)):
                clean_schema(value)

    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                clean_schema(item)

    return obj

def clean_openapi_reports():
    """Limpa OpenAPI spec do módulo REPORTS."""
    print("📖 Lendo OpenAPI spec...")
    with open("openapi-reports.json", "r", encoding="utf-8") as f:
        openapi = json.load(f)

    print("🧹 Limpando schemas problemáticos...")

    # Limpa paths
    if 'paths' in openapi:
        clean_schema(openapi['paths'])

    # Limpa components
    if 'components' in openapi:
        clean_schema(openapi['components'])

    # Salva arquivo limpo
    output_file = "openapi-reports-clean.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(openapi, f, ensure_ascii=False, indent=2)

    print(f"\n✅ OpenAPI spec limpo salvo em: {output_file}")

    # Estatísticas
    num_paths = len(openapi.get('paths', {}))
    num_schemas = len(openapi.get('components', {}).get('schemas', {}))

    print(f"📊 Endpoints: {num_paths}")
    print(f"📦 Schemas: {num_schemas}")

if __name__ == "__main__":
    clean_openapi_reports()
