#!/usr/bin/env python3
"""
Script para extrair OpenAPI spec do módulo MOBILE - Versão 2.

Abordagem direta: importa apenas o router mobile sem inicializar app completo.

Uso:
    python scripts/extract_openapi_mobile_v2.py
"""

import json
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))


def extract_mobile_openapi():
    """Extrai especificação OpenAPI do módulo MOBILE."""

    print("Extraindo OpenAPI do módulo MOBILE (v2 - direto do router)...")

    # Import apenas do router mobile
    try:
        from fastapi import FastAPI
        from modules.mobile.controllers.mobile_controller import router as mobile_router

        # Criar app temporário apenas com router mobile
        temp_app = FastAPI(
            title="Conecta PRO - Mobile API",
            version="1.0.0",
            description="APIs nativas para dispositivos móveis"
        )

        # Incluir apenas router mobile
        temp_app.include_router(mobile_router, prefix="/api/v1")

        print("✓ Router mobile importado com sucesso")

    except Exception as e:
        print(f"❌ Erro ao importar router mobile: {e}")
        import traceback
        traceback.print_exc()
        raise

    # Gerar OpenAPI spec
    try:
        from fastapi.openapi.utils import get_openapi

        openapi_schema = get_openapi(
            title=temp_app.title,
            version=temp_app.version,
            description=temp_app.description,
            routes=temp_app.routes,
        )

        print(f"✓ OpenAPI gerado com {len(openapi_schema.get('paths', {}))} endpoints")

    except Exception as e:
        print(f"❌ Erro ao gerar OpenAPI: {e}")
        import traceback
        traceback.print_exc()
        raise

    # Salvar arquivo
    output_file = Path(__file__).parent.parent / 'openapi-mobile.json'

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

    print(f"✓ OpenAPI salvo em: {output_file}")
    print(f"✓ Tamanho: {output_file.stat().st_size / 1024:.1f} KB")

    # Listar endpoints
    paths = openapi_schema.get('paths', {})
    if paths:
        print(f"\n📋 {len(paths)} endpoints extraídos:")
        for i, path in enumerate(sorted(paths.keys()), 1):
            methods = list(paths[path].keys())
            methods = [m.upper() for m in methods if m != 'parameters']
            print(f"  {i:2d}. {', '.join(methods):12s} {path}")
    else:
        print("\n⚠️  Nenhum endpoint encontrado!")

    # Listar schemas
    schemas = openapi_schema.get('components', {}).get('schemas', {})
    print(f"\n📦 {len(schemas)} schemas extraídos")

    return openapi_schema


if __name__ == '__main__':
    try:
        spec = extract_mobile_openapi()
        print("\n✅ Extração concluída com sucesso!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro na extração: {e}", file=sys.stderr)
        sys.exit(1)
