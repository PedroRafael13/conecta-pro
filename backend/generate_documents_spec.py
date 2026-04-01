"""Script para gerar spec OpenAPI do módulo documents."""

import json

from fastapi import FastAPI

from modules.documents.controllers import router


def generate_spec():
    """Gera spec OpenAPI do módulo documents."""
    # Criar app temporária
    app = FastAPI(
        title="Document Intelligence API",
        version="1.0.0",
        description="API de processamento inteligente de documentos com OCR e IA",
    )
    app.include_router(router, prefix="/api/v1")

    # Gerar spec OpenAPI
    spec = app.openapi()

    # Salvar
    output_path = "/opt/conecta-pro/frontend/openapi-documents.json"
    with open(output_path, "w") as f:
        json.dump(spec, f, indent=2)

    print(f"✓ Spec OpenAPI gerada: {output_path}")
    print(f"✓ Total de endpoints: {len(spec['paths'])}")
    print(f"✓ Total de schemas: {len(spec.get('components', {}).get('schemas', {}))}")
    print("\nEndpoints:")
    for path in sorted(spec["paths"].keys()):
        methods = list(spec["paths"][path].keys())
        print(f"  {path}: {', '.join(m.upper() for m in methods)}")


if __name__ == "__main__":
    generate_spec()
