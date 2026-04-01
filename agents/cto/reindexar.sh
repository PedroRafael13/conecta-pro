#!/bin/bash
# Reindexar conhecimento CTO após cada deploy
cd /opt/conecta-pro

ULTIMO_COMMIT=$(git log --oneline -1 --format="%H")
INDEXADO_FILE="agents/cto/knowledge/.ultimo_commit"

if [ -f "$INDEXADO_FILE" ]; then
    ULTIMO_INDEXADO=$(cat "$INDEXADO_FILE")
    if [ "$ULTIMO_COMMIT" = "$ULTIMO_INDEXADO" ]; then
        echo "$(date): Sem mudanças — reindexação desnecessária"
        exit 0
    fi
fi

echo "$(date): Novo commit $ULTIMO_COMMIT — reindexando..."

python3 - << 'PYEOF'
import os, ast, json, re, subprocess
from pathlib import Path
from datetime import datetime

BACKEND_DIR = Path("/opt/conecta-pro/backend")
OUTPUT = Path("/opt/conecta-pro/agents/cto/knowledge/codigo")

indice = {"gerado_em": datetime.now().isoformat(), "total_arquivos": 0,
          "total_linhas": 0, "total_funcoes": 0, "total_classes": 0,
          "modulos": {}, "endpoints": [], "services": [], "models": [],
          "tasks": [], "integracoes": []}

todos_endpoints = []
todas_integracoes = set()

for fpath in sorted(BACKEND_DIR.rglob("*.py")):
    if any(p in str(fpath) for p in ["__pycache__", "alembic/versions"]):
        continue
    try:
        content = fpath.read_text(encoding="utf-8", errors="ignore")
    except:
        continue

    modulo = str(fpath.relative_to(BACKEND_DIR))
    info = {"arquivo": modulo, "linhas": len(content.split("\n")),
            "funcoes": [], "classes": [], "endpoints": []}

    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                info["classes"].append({"nome": node.name, "linha": node.lineno})
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                info["funcoes"].append({"nome": node.name, "linha": node.lineno,
                                        "is_async": isinstance(node, ast.AsyncFunctionDef)})
    except:
        pass

    eps = re.findall(r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']', content)
    for method, path in eps:
        ep = {"method": method.upper(), "path": path, "arquivo": modulo}
        info["endpoints"].append(ep)
        todos_endpoints.append(ep)

    for integ in ["cora","inter","solides","nfse","esocial","reinf","telegram","sefaz","redis","celery","govbr"]:
        if integ in content.lower():
            todas_integracoes.add(integ)

    indice["total_arquivos"] += 1
    indice["total_linhas"] += info["linhas"]
    indice["total_funcoes"] += len(info["funcoes"])
    indice["total_classes"] += len(info["classes"])
    indice["modulos"][modulo] = info

indice["endpoints"] = todos_endpoints
indice["integracoes"] = list(todas_integracoes)

resumo = {
    "gerado_em": indice["gerado_em"],
    "total_arquivos": indice["total_arquivos"],
    "total_linhas": indice["total_linhas"],
    "total_funcoes": indice["total_funcoes"],
    "total_classes": indice["total_classes"],
    "total_endpoints": len(todos_endpoints),
}

(OUTPUT / "backend_completo.json").write_text(json.dumps(indice, indent=2, ensure_ascii=False, default=str))
(OUTPUT / "backend_resumo.json").write_text(json.dumps(resumo, indent=2, ensure_ascii=False, default=str))
print(f"Reindexado: {indice['total_arquivos']} arquivos, {len(todos_endpoints)} endpoints")
PYEOF

echo "$ULTIMO_COMMIT" > "$INDEXADO_FILE"
echo "$(date): Reindexação concluída"
