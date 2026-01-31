"""
Script para extrair OpenAPI spec completo do módulo REPORTS.
Versão 2 - Extração via HTTP request para evitar problemas de imports.
"""

import json
import subprocess
import time
import requests
import sys

def start_server():
    """Inicia servidor FastAPI em background."""
    print("🚀 Iniciando servidor FastAPI...")
    proc = subprocess.Popen(
        ["python3", "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8888"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd="/opt/conecta-pro/backend"
    )

    # Aguarda servidor iniciar
    max_attempts = 30
    for i in range(max_attempts):
        try:
            response = requests.get("http://127.0.0.1:8888/health", timeout=2)
            if response.status_code == 200:
                print("✅ Servidor iniciado com sucesso")
                return proc
        except:
            pass
        time.sleep(1)
        if i % 5 == 0:
            print(f"⏳ Aguardando servidor... ({i}/{max_attempts})")

    print("❌ Falha ao iniciar servidor")
    proc.kill()
    return None

def extract_reports_openapi():
    """Extrai OpenAPI spec filtrado para módulo REPORTS."""

    # Inicia servidor
    server_proc = start_server()
    if not server_proc:
        sys.exit(1)

    try:
        print("\n📡 Baixando OpenAPI spec...")
        response = requests.get("http://127.0.0.1:8888/openapi.json", timeout=10)

        if response.status_code != 200:
            print(f"❌ Erro ao baixar OpenAPI: {response.status_code}")
            return

        openapi_schema = response.json()

        # Filtra apenas endpoints de reports
        reports_paths = {}

        # Prefixos que queremos incluir
        prefixes_to_include = [
            "/api/v1/reports",           # Módulo reports principal
            "/api/v1/ai/reports",         # AI Report Generator
            "/api/v1/operacional/reports" # Operational Reports (se existir)
        ]

        for path, path_item in openapi_schema.get("paths", {}).items():
            # Inclui se começar com qualquer um dos prefixos
            if any(path.startswith(prefix) for prefix in prefixes_to_include):
                reports_paths[path] = path_item

        # Extrai schemas usados
        all_schemas = openapi_schema.get("components", {}).get("schemas", {})
        used_schemas = set()

        def extract_schema_refs(obj):
            """Extrai recursivamente todas as referências de schemas."""
            if isinstance(obj, dict):
                if "$ref" in obj:
                    ref = obj["$ref"]
                    if ref.startswith("#/components/schemas/"):
                        schema_name = ref.split("/")[-1]
                        if schema_name not in used_schemas:
                            used_schemas.add(schema_name)
                            # Recursivamente processa o schema referenciado
                            if schema_name in all_schemas:
                                extract_schema_refs(all_schemas[schema_name])
                for value in obj.values():
                    extract_schema_refs(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_schema_refs(item)

        # Extrai schemas dos paths
        extract_schema_refs(reports_paths)

        # Filtra apenas schemas usados
        filtered_schemas = {
            name: schema
            for name, schema in all_schemas.items()
            if name in used_schemas
        }

        # Monta OpenAPI filtrado
        reports_openapi = {
            "openapi": "3.0.0",
            "info": {
                "title": "Conecta PRO - Reports API",
                "version": "2.0.0",
                "description": "API completa do módulo de Relatórios incluindo Reports, Intelligent Reports, AI Reports e Operational Reports"
            },
            "servers": [
                {
                    "url": "http://localhost:8000",
                    "description": "Servidor de desenvolvimento"
                },
                {
                    "url": "https://api.conectapro.com.br",
                    "description": "Servidor de produção"
                }
            ],
            "paths": reports_paths,
            "components": {
                "schemas": filtered_schemas,
                "securitySchemes": openapi_schema.get("components", {}).get("securitySchemes", {})
            }
        }

        # Salva arquivo
        output_file = "openapi-reports.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(reports_openapi, f, ensure_ascii=False, indent=2)

        # Estatísticas
        num_paths = len(reports_paths)
        num_schemas = len(filtered_schemas)

        print(f"\n✅ OpenAPI spec REPORTS extraído com sucesso!")
        print(f"📁 Arquivo: {output_file}")
        print(f"🔗 Endpoints: {num_paths}")
        print(f"📦 Schemas: {num_schemas}")
        print()
        print("Endpoints por categoria:")

        # Conta por prefixo
        for prefix in prefixes_to_include:
            count = sum(1 for path in reports_paths.keys() if path.startswith(prefix))
            if count > 0:
                print(f"  - {prefix}: {count} endpoints")

        # Lista alguns endpoints
        print("\nExemplos de endpoints:")
        for i, path in enumerate(sorted(reports_paths.keys())[:10]):
            print(f"  {i+1}. {path}")

        if num_paths > 10:
            print(f"  ... e mais {num_paths - 10} endpoints")

    finally:
        print("\n🛑 Encerrando servidor...")
        server_proc.terminate()
        server_proc.wait(timeout=5)

if __name__ == "__main__":
    extract_reports_openapi()
