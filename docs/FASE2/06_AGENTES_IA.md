# AGENTES IA - CONFIGURACAO E USO
## ERP CONECTA MAIS - FASE 2

**Versao:** 2.0
**Data:** Janeiro 2026
**Objetivo:** Configurar agentes IA para automacao de tarefas

---

## VISAO GERAL

Agentes IA sao processos autonomos que executam tarefas especificas:
- Auditoria de codigo automatica
- Geracao de testes
- Documentacao automatica
- Monitoramento de qualidade
- Revisao de codigo

---

## AGENTE 1: AUDITOR DE CODIGO

### Proposito
Executa auditoria continua de qualidade de codigo.

### Configuracao

```yaml
# /opt/erp-conecta-mais/agents/auditor/config.yaml
name: code-auditor
description: Auditor automatico de codigo
schedule: "*/30 * * * *"  # A cada 30 minutos
enabled: true

triggers:
  - on_file_change:
      patterns:
        - "modules/**/*.py"
        - "core/**/*.py"
  - on_commit:
      branches:
        - main
        - develop

checks:
  - name: pylint
    command: "pylint --rcfile=.pylintrc {file} --output-format=json"
    threshold: 99.0
    blocking: true

  - name: mypy
    command: "mypy {file} --ignore-missing-imports"
    threshold: 0  # 0 errors
    blocking: true

  - name: black
    command: "black --check {file}"
    blocking: false
    auto_fix: true

  - name: isort
    command: "isort --check-only {file}"
    blocking: false
    auto_fix: true

  - name: bandit
    command: "bandit {file} -ll"
    blocking: true

notifications:
  on_failure:
    - slack: "#dev-alerts"
    - email: "dev@conectamais.com.br"

actions:
  on_failure:
    - create_issue: true
    - block_merge: true
  on_success:
    - update_badge: true
```

### Script do Agente

```python
#!/usr/bin/env python3
"""
Agente Auditor de Codigo.

Executa verificacoes de qualidade automaticamente.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


class CodeAuditor:
    """Agente de auditoria de codigo."""

    def __init__(self, config_path: str) -> None:
        """Inicializa o auditor."""
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.results: list[dict[str, Any]] = []

    def run_check(self, check: dict, file_path: str) -> dict[str, Any]:
        """Executa uma verificacao."""
        command = check["command"].format(file=file_path)

        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            cwd="/opt/erp-conecta-mais/backend"
        )

        return {
            "name": check["name"],
            "file": file_path,
            "passed": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr,
            "timestamp": datetime.now().isoformat()
        }

    def audit_file(self, file_path: str) -> list[dict[str, Any]]:
        """Audita um arquivo."""
        results = []

        for check in self.config["checks"]:
            result = self.run_check(check, file_path)
            results.append(result)

            if not result["passed"] and check.get("auto_fix"):
                self.auto_fix(check, file_path)

        return results

    def auto_fix(self, check: dict, file_path: str) -> None:
        """Aplica correcao automatica."""
        if check["name"] == "black":
            subprocess.run(["black", file_path])
        elif check["name"] == "isort":
            subprocess.run(["isort", file_path])

    def audit_all(self) -> dict[str, Any]:
        """Audita todos os arquivos."""
        all_results = []

        for pattern in ["modules/**/*.py", "core/**/*.py"]:
            for file_path in Path("/opt/erp-conecta-mais/backend").glob(pattern):
                results = self.audit_file(str(file_path))
                all_results.extend(results)

        # Calcular score geral
        passed = sum(1 for r in all_results if r["passed"])
        total = len(all_results)

        return {
            "timestamp": datetime.now().isoformat(),
            "total_checks": total,
            "passed": passed,
            "failed": total - passed,
            "score": (passed / total * 100) if total > 0 else 100,
            "results": all_results
        }

    def generate_report(self, results: dict) -> str:
        """Gera relatorio de auditoria."""
        report = f"""
# Relatorio de Auditoria
**Data:** {results['timestamp']}

## Resumo
- Total de verificacoes: {results['total_checks']}
- Passou: {results['passed']}
- Falhou: {results['failed']}
- Score: {results['score']:.1f}%

## Detalhes
"""
        for r in results["results"]:
            status = "PASSOU" if r["passed"] else "FALHOU"
            report += f"- [{status}] {r['name']}: {r['file']}\n"

        return report


if __name__ == "__main__":
    auditor = CodeAuditor("/opt/erp-conecta-mais/agents/auditor/config.yaml")
    results = auditor.audit_all()
    print(json.dumps(results, indent=2))
```

---

## AGENTE 2: GERADOR DE TESTES

### Proposito
Gera testes automaticos para codigo novo.

### Configuracao

```yaml
# /opt/erp-conecta-mais/agents/test-generator/config.yaml
name: test-generator
description: Gera testes automaticos
enabled: true

triggers:
  - on_file_create:
      patterns:
        - "modules/**/models/*.py"
        - "modules/**/services/*.py"
        - "modules/**/controllers/*.py"

templates:
  model_test: |
    """Testes para {model_name}."""
    import pytest
    from {import_path} import {model_name}

    class Test{model_name}:
        """Testes do model {model_name}."""

        def test_create_valid(self) -> None:
            """Testa criacao valida."""
            obj = {model_name}({default_values})
            assert obj is not None

        def test_repr(self) -> None:
            """Testa __repr__."""
            obj = {model_name}({default_values})
            assert "{model_name}" in repr(obj)

  service_test: |
    """Testes para {service_name}."""
    import pytest
    from unittest.mock import MagicMock, patch
    from {import_path} import {service_name}

    class Test{service_name}:
        """Testes do service {service_name}."""

        @pytest.fixture
        def service(self) -> {service_name}:
            """Fixture do service."""
            return {service_name}()

        def test_init(self, service: {service_name}) -> None:
            """Testa inicializacao."""
            assert service is not None

  controller_test: |
    """Testes para {controller_name}."""
    import pytest
    from httpx import AsyncClient
    from fastapi import status

    @pytest.mark.asyncio
    class Test{controller_name}:
        """Testes do controller {controller_name}."""

        async def test_list(self, client: AsyncClient) -> None:
            """Testa listagem."""
            response = await client.get("{endpoint}")
            assert response.status_code == status.HTTP_200_OK

output:
  directory: "tests/"
  naming: "test_{original_name}.py"
```

### Script do Agente

```python
#!/usr/bin/env python3
"""
Agente Gerador de Testes.

Gera testes automaticos para novos arquivos.
"""

import ast
import re
from pathlib import Path
from typing import Any

import yaml


class TestGenerator:
    """Gera testes automaticos."""

    def __init__(self, config_path: str) -> None:
        """Inicializa o gerador."""
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

    def analyze_file(self, file_path: str) -> dict[str, Any]:
        """Analisa arquivo Python."""
        with open(file_path) as f:
            source = f.read()

        tree = ast.parse(source)

        classes = []
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                    "bases": [b.id for b in node.bases if isinstance(b, ast.Name)]
                })
            elif isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "args": [a.arg for a in node.args.args]
                })

        return {
            "path": file_path,
            "classes": classes,
            "functions": functions
        }

    def detect_type(self, file_path: str) -> str:
        """Detecta tipo de arquivo."""
        if "models" in file_path:
            return "model"
        elif "services" in file_path:
            return "service"
        elif "controllers" in file_path:
            return "controller"
        return "unknown"

    def generate_test(self, file_path: str) -> str:
        """Gera arquivo de teste."""
        analysis = self.analyze_file(file_path)
        file_type = self.detect_type(file_path)

        if file_type == "model" and analysis["classes"]:
            return self._generate_model_test(analysis)
        elif file_type == "service" and analysis["classes"]:
            return self._generate_service_test(analysis)
        elif file_type == "controller":
            return self._generate_controller_test(analysis)

        return ""

    def _generate_model_test(self, analysis: dict) -> str:
        """Gera teste de model."""
        template = self.config["templates"]["model_test"]
        class_info = analysis["classes"][0]

        # Extrair import path
        rel_path = Path(analysis["path"]).relative_to("/opt/erp-conecta-mais/backend")
        import_path = str(rel_path).replace("/", ".").replace(".py", "")

        return template.format(
            model_name=class_info["name"],
            import_path=import_path,
            default_values="name='Test'"
        )

    def _generate_service_test(self, analysis: dict) -> str:
        """Gera teste de service."""
        template = self.config["templates"]["service_test"]
        class_info = analysis["classes"][0]

        rel_path = Path(analysis["path"]).relative_to("/opt/erp-conecta-mais/backend")
        import_path = str(rel_path).replace("/", ".").replace(".py", "")

        return template.format(
            service_name=class_info["name"],
            import_path=import_path
        )

    def _generate_controller_test(self, analysis: dict) -> str:
        """Gera teste de controller."""
        template = self.config["templates"]["controller_test"]

        # Extrair nome do controller
        file_name = Path(analysis["path"]).stem
        controller_name = "".join(w.title() for w in file_name.split("_"))

        # Inferir endpoint
        endpoint = f"/api/v1/{file_name.replace('_controller', '')}/"

        return template.format(
            controller_name=controller_name,
            endpoint=endpoint
        )

    def save_test(self, file_path: str, test_content: str) -> str:
        """Salva arquivo de teste."""
        original_name = Path(file_path).stem
        test_name = f"test_{original_name}.py"
        test_path = Path("/opt/erp-conecta-mais/backend/tests") / test_name

        with open(test_path, "w") as f:
            f.write(test_content)

        return str(test_path)


if __name__ == "__main__":
    import sys

    generator = TestGenerator("/opt/erp-conecta-mais/agents/test-generator/config.yaml")

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        test_content = generator.generate_test(file_path)
        if test_content:
            test_path = generator.save_test(file_path, test_content)
            print(f"Teste gerado: {test_path}")
```

---

## AGENTE 3: DOCUMENTADOR

### Proposito
Gera e atualiza documentacao automaticamente.

### Configuracao

```yaml
# /opt/erp-conecta-mais/agents/documenter/config.yaml
name: documenter
description: Gera documentacao automatica
schedule: "0 6 * * *"  # Diariamente as 6h
enabled: true

outputs:
  - type: readme
    path: "modules/{module}/README.md"
    template: module_readme

  - type: api_docs
    path: "docs/api/{module}.md"
    template: api_docs

  - type: changelog
    path: "CHANGELOG.md"
    template: changelog

templates:
  module_readme: |
    # Modulo {module_name}

    ## Descricao
    {description}

    ## Estrutura
    ```
    {structure}
    ```

    ## Models
    {models}

    ## Endpoints
    {endpoints}

    ## Uso
    ```python
    {usage_example}
    ```

  api_docs: |
    # API {module_name}

    ## Endpoints

    {endpoints}

    ## Schemas

    {schemas}
```

### Script do Agente

```python
#!/usr/bin/env python3
"""
Agente Documentador.

Gera documentacao automatica.
"""

import ast
import inspect
from pathlib import Path
from typing import Any

import yaml


class Documenter:
    """Gera documentacao automatica."""

    def __init__(self, config_path: str) -> None:
        """Inicializa o documentador."""
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

    def analyze_module(self, module_path: str) -> dict[str, Any]:
        """Analisa um modulo."""
        path = Path(module_path)

        models = []
        schemas = []
        controllers = []
        services = []

        # Analisar models
        models_path = path / "models"
        if models_path.exists():
            for file in models_path.glob("*.py"):
                if file.name != "__init__.py":
                    models.extend(self._extract_classes(file))

        # Analisar schemas
        schemas_path = path / "schemas"
        if schemas_path.exists():
            for file in schemas_path.glob("*.py"):
                if file.name != "__init__.py":
                    schemas.extend(self._extract_classes(file))

        # Analisar controllers
        controllers_path = path / "controllers"
        if controllers_path.exists():
            for file in controllers_path.glob("*.py"):
                if file.name != "__init__.py":
                    controllers.extend(self._extract_endpoints(file))

        return {
            "name": path.name,
            "path": str(path),
            "models": models,
            "schemas": schemas,
            "controllers": controllers,
            "structure": self._get_structure(path)
        }

    def _extract_classes(self, file_path: Path) -> list[dict]:
        """Extrai classes de um arquivo."""
        classes = []

        with open(file_path) as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node) or ""
                classes.append({
                    "name": node.name,
                    "docstring": docstring,
                    "file": str(file_path)
                })

        return classes

    def _extract_endpoints(self, file_path: Path) -> list[dict]:
        """Extrai endpoints de um controller."""
        endpoints = []

        with open(file_path) as f:
            source = f.read()

        # Buscar decorators @router.get, @router.post, etc
        import re
        pattern = r'@router\.(get|post|put|patch|delete)\s*\(\s*["\']([^"\']+)["\']'

        for match in re.finditer(pattern, source):
            method = match.group(1).upper()
            path = match.group(2)
            endpoints.append({
                "method": method,
                "path": path,
                "file": str(file_path)
            })

        return endpoints

    def _get_structure(self, path: Path) -> str:
        """Gera arvore de diretorio."""
        lines = []

        for item in sorted(path.rglob("*")):
            if "__pycache__" in str(item):
                continue

            rel_path = item.relative_to(path)
            depth = len(rel_path.parts) - 1
            indent = "  " * depth

            if item.is_dir():
                lines.append(f"{indent}{item.name}/")
            else:
                lines.append(f"{indent}{item.name}")

        return "\n".join(lines)

    def generate_readme(self, module_info: dict) -> str:
        """Gera README do modulo."""
        template = self.config["templates"]["module_readme"]

        # Formatar models
        models_text = "\n".join(
            f"- **{m['name']}**: {m['docstring'][:100]}..."
            for m in module_info["models"]
        )

        # Formatar endpoints
        endpoints_text = "\n".join(
            f"- `{e['method']} {e['path']}`"
            for e in module_info["controllers"]
        )

        return template.format(
            module_name=module_info["name"].upper(),
            description=f"Modulo {module_info['name']} do ERP Conecta Mais",
            structure=module_info["structure"],
            models=models_text or "Nenhum model definido",
            endpoints=endpoints_text or "Nenhum endpoint definido",
            usage_example="from modules.{} import ...".format(module_info["name"])
        )

    def update_changelog(self, changes: list[dict]) -> str:
        """Atualiza CHANGELOG."""
        from datetime import datetime

        changelog = f"## [{datetime.now().strftime('%Y-%m-%d')}]\n\n"

        for change in changes:
            changelog += f"- {change['type']}: {change['description']}\n"

        return changelog


if __name__ == "__main__":
    import sys

    documenter = Documenter("/opt/erp-conecta-mais/agents/documenter/config.yaml")

    if len(sys.argv) > 1:
        module_path = sys.argv[1]
        info = documenter.analyze_module(module_path)
        readme = documenter.generate_readme(info)
        print(readme)
```

---

## AGENTE 4: MONITOR DE QUALIDADE

### Proposito
Monitora metricas de qualidade em tempo real.

### Dashboard de Metricas

```python
#!/usr/bin/env python3
"""
Agente Monitor de Qualidade.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path


class QualityMonitor:
    """Monitora qualidade do codigo."""

    def __init__(self) -> None:
        """Inicializa o monitor."""
        self.base_path = Path("/opt/erp-conecta-mais/backend")
        self.metrics_file = self.base_path / "metrics.json"

    def collect_metrics(self) -> dict:
        """Coleta todas as metricas."""
        return {
            "timestamp": datetime.now().isoformat(),
            "pylint_score": self._get_pylint_score(),
            "test_coverage": self._get_test_coverage(),
            "file_count": self._count_files(),
            "line_count": self._count_lines(),
            "complexity": self._get_complexity()
        }

    def _get_pylint_score(self) -> float:
        """Obtem score do Pylint."""
        result = subprocess.run(
            ["pylint", "--rcfile=.pylintrc", "modules/", "core/", "--score=y"],
            capture_output=True,
            text=True,
            cwd=self.base_path
        )

        for line in result.stdout.split("\n"):
            if "rated at" in line:
                score = line.split("rated at")[1].split("/")[0].strip()
                return float(score)

        return 0.0

    def _get_test_coverage(self) -> float:
        """Obtem cobertura de testes."""
        result = subprocess.run(
            ["pytest", "--cov=modules", "--cov-report=json", "-q"],
            capture_output=True,
            text=True,
            cwd=self.base_path
        )

        cov_file = self.base_path / "coverage.json"
        if cov_file.exists():
            with open(cov_file) as f:
                data = json.load(f)
                return data.get("totals", {}).get("percent_covered", 0)

        return 0.0

    def _count_files(self) -> int:
        """Conta arquivos Python."""
        return len(list(self.base_path.glob("**/*.py")))

    def _count_lines(self) -> int:
        """Conta linhas de codigo."""
        total = 0
        for file in self.base_path.glob("**/*.py"):
            if "__pycache__" not in str(file):
                with open(file) as f:
                    total += len(f.readlines())
        return total

    def _get_complexity(self) -> dict:
        """Obtem metricas de complexidade."""
        result = subprocess.run(
            ["radon", "cc", "modules/", "-a", "-j"],
            capture_output=True,
            text=True,
            cwd=self.base_path
        )

        if result.stdout:
            return json.loads(result.stdout)
        return {}

    def save_metrics(self, metrics: dict) -> None:
        """Salva metricas em arquivo."""
        # Carregar historico
        history = []
        if self.metrics_file.exists():
            with open(self.metrics_file) as f:
                history = json.load(f)

        # Adicionar nova entrada
        history.append(metrics)

        # Manter ultimos 30 dias
        history = history[-720:]  # 24 entries/day * 30 days

        with open(self.metrics_file, "w") as f:
            json.dump(history, f, indent=2)

    def generate_report(self, metrics: dict) -> str:
        """Gera relatorio de qualidade."""
        return f"""
# Relatorio de Qualidade
**Data:** {metrics['timestamp']}

## Metricas
| Metrica | Valor | Meta |
|---------|-------|------|
| Pylint Score | {metrics['pylint_score']:.1f}/100 | >= 99 |
| Cobertura | {metrics['test_coverage']:.1f}% | >= 85% |
| Arquivos | {metrics['file_count']} | - |
| Linhas | {metrics['line_count']:,} | - |

## Status
- Pylint: {'OK' if metrics['pylint_score'] >= 99 else 'ATENCAO'}
- Cobertura: {'OK' if metrics['test_coverage'] >= 85 else 'ATENCAO'}
"""


if __name__ == "__main__":
    monitor = QualityMonitor()
    metrics = monitor.collect_metrics()
    monitor.save_metrics(metrics)
    print(monitor.generate_report(metrics))
```

---

## INTEGRACAO COM CLAUDE CODE

### Comandos para Invocar Agentes

```bash
# Auditor
"Execute o agente auditor no modulo CRM"
"Audite o arquivo models/proposal.py"

# Gerador de Testes
"Gere testes para o novo model Proposal"
"Execute o agente de testes para services/"

# Documentador
"Atualize a documentacao do modulo financial"
"Gere README para todos os modulos"

# Monitor
"Mostre as metricas de qualidade atuais"
"Gere relatorio de qualidade"
```

---

## CRON JOBS PARA AGENTES

```bash
# /etc/cron.d/erp-agents

# Auditor - a cada hora
0 * * * * root /opt/erp-conecta-mais/agents/auditor/run.sh >> /var/log/auditor.log 2>&1

# Monitor - a cada 30 minutos
*/30 * * * * root /opt/erp-conecta-mais/agents/monitor/run.sh >> /var/log/monitor.log 2>&1

# Documentador - diariamente as 6h
0 6 * * * root /opt/erp-conecta-mais/agents/documenter/run.sh >> /var/log/documenter.log 2>&1
```

---

*Agentes IA - ERP Conecta Mais Fase 2*
*"Automacao inteligente para qualidade consistente"*
