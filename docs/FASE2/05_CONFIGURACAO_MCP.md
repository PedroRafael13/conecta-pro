# CONFIGURACAO MCP - SERVIDORES E FERRAMENTAS
## ERP CONECTA MAIS - FASE 2

**Versao:** 2.0
**Data:** Janeiro 2026
**Objetivo:** Configurar servidores MCP para Claude Code

---

## O QUE E MCP (Model Context Protocol)

MCP permite que Claude Code acesse ferramentas externas:
- Bancos de dados
- APIs REST
- Sistemas de arquivos
- Servicos de terceiros
- Ferramentas de desenvolvimento

---

## SERVIDORES MCP RECOMENDADOS

### 1. MCP PostgreSQL
**Funcao:** Acesso direto ao banco de dados
**Instalacao:**
```bash
npm install -g @anthropic/mcp-server-postgres
```

**Configuracao (~/.claude/settings.json):**
```json
{
  "mcpServers": {
    "postgres": {
      "command": "mcp-server-postgres",
      "args": ["--connection-string", "postgresql://user:pass@localhost:5432/erp_db"],
      "env": {
        "PGPASSWORD": "sua_senha"
      }
    }
  }
}
```

**Capacidades:**
- Executar queries SQL
- Ver schema do banco
- Listar tabelas
- Descrever colunas
- Executar migrations

**Uso no Claude Code:**
```
"Liste as tabelas do schema public"
"Descreva a tabela leads"
"Execute: SELECT COUNT(*) FROM leads WHERE status = 'NEW'"
```

---

### 2. MCP Filesystem
**Funcao:** Acesso ao sistema de arquivos
**Instalacao:**
```bash
npm install -g @anthropic/mcp-server-filesystem
```

**Configuracao:**
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "mcp-server-filesystem",
      "args": ["--root", "/opt/erp-conecta-mais"]
    }
  }
}
```

**Capacidades:**
- Ler arquivos
- Escrever arquivos
- Listar diretorios
- Buscar arquivos
- Mover/renomear

---

### 3. MCP Git
**Funcao:** Operacoes Git
**Instalacao:**
```bash
npm install -g @anthropic/mcp-server-git
```

**Configuracao:**
```json
{
  "mcpServers": {
    "git": {
      "command": "mcp-server-git",
      "args": ["--repo", "/opt/erp-conecta-mais"]
    }
  }
}
```

**Capacidades:**
- git status
- git diff
- git log
- git add/commit
- git branch
- git merge

---

### 4. MCP Docker
**Funcao:** Gerenciar containers
**Instalacao:**
```bash
npm install -g @anthropic/mcp-server-docker
```

**Configuracao:**
```json
{
  "mcpServers": {
    "docker": {
      "command": "mcp-server-docker"
    }
  }
}
```

**Capacidades:**
- Listar containers
- Ver logs
- Restart containers
- Build images
- Docker compose

---

### 5. MCP HTTP/REST
**Funcao:** Testar APIs
**Instalacao:**
```bash
npm install -g @anthropic/mcp-server-fetch
```

**Configuracao:**
```json
{
  "mcpServers": {
    "fetch": {
      "command": "mcp-server-fetch",
      "args": ["--allowed-domains", "localhost,api.exemplo.com"]
    }
  }
}
```

**Capacidades:**
- Fazer requests HTTP
- GET, POST, PUT, DELETE
- Headers customizados
- Autenticacao

---

### 6. MCP Pytest
**Funcao:** Executar testes
**Instalacao:**
```bash
npm install -g @anthropic/mcp-server-pytest
```

**Configuracao:**
```json
{
  "mcpServers": {
    "pytest": {
      "command": "mcp-server-pytest",
      "args": ["--workdir", "/opt/erp-conecta-mais/backend"]
    }
  }
}
```

**Capacidades:**
- Rodar testes
- Ver cobertura
- Filtrar por padrao
- Ver falhas detalhadas

---

## CONFIGURACAO COMPLETA RECOMENDADA

### Arquivo: ~/.claude/settings.json

```json
{
  "model": "claude-opus-4-5-20251101",
  "maxTokens": 8192,
  "language": "pt-BR",
  "mcpServers": {
    "postgres": {
      "command": "mcp-server-postgres",
      "args": [
        "--connection-string",
        "postgresql://conecta_user:conecta_pass_2024@localhost:5432/conecta_db"
      ]
    },
    "filesystem": {
      "command": "mcp-server-filesystem",
      "args": ["--root", "/opt/erp-conecta-mais"]
    },
    "git": {
      "command": "mcp-server-git",
      "args": ["--repo", "/opt/erp-conecta-mais"]
    },
    "docker": {
      "command": "mcp-server-docker"
    },
    "fetch": {
      "command": "mcp-server-fetch",
      "args": [
        "--allowed-domains",
        "localhost,127.0.0.1,api.conectamais.com.br"
      ]
    },
    "pytest": {
      "command": "mcp-server-pytest",
      "args": ["--workdir", "/opt/erp-conecta-mais/backend"]
    }
  }
}
```

---

## SERVIDORES MCP CUSTOMIZADOS

### MCP Auditor de Codigo
**Funcao:** Rodar pylint, mypy, black, isort automaticamente
**Localizacao:** `/opt/erp-conecta-mais/tools/mcp-auditor/`

**Criar servidor:**

```python
# /opt/erp-conecta-mais/tools/mcp-auditor/server.py
"""
MCP Server para auditoria de codigo.

Executa pylint, mypy, black, isort e retorna resultados.
"""

import subprocess
import json
from typing import Any

from mcp import Server, Tool

server = Server("code-auditor")


@server.tool("audit_file")
async def audit_file(file_path: str) -> dict[str, Any]:
    """
    Audita um arquivo Python.

    Args:
        file_path: Caminho do arquivo

    Returns:
        Resultados de pylint, mypy, black, isort
    """
    results = {}

    # Pylint
    pylint_result = subprocess.run(
        ["pylint", "--rcfile=.pylintrc", file_path, "--output-format=json"],
        capture_output=True,
        text=True,
        cwd="/opt/erp-conecta-mais/backend"
    )
    results["pylint"] = json.loads(pylint_result.stdout) if pylint_result.stdout else []

    # Mypy
    mypy_result = subprocess.run(
        ["mypy", file_path, "--ignore-missing-imports"],
        capture_output=True,
        text=True,
        cwd="/opt/erp-conecta-mais/backend"
    )
    results["mypy"] = mypy_result.stdout

    # Black check
    black_result = subprocess.run(
        ["black", "--check", file_path],
        capture_output=True,
        text=True
    )
    results["black"] = "OK" if black_result.returncode == 0 else "Needs formatting"

    # Isort check
    isort_result = subprocess.run(
        ["isort", "--check-only", file_path],
        capture_output=True,
        text=True
    )
    results["isort"] = "OK" if isort_result.returncode == 0 else "Needs sorting"

    return results


@server.tool("audit_module")
async def audit_module(module_path: str) -> dict[str, Any]:
    """
    Audita um modulo inteiro.

    Args:
        module_path: Caminho do modulo (ex: modules/crm)

    Returns:
        Resultados agregados
    """
    results = {}

    # Pylint com score
    pylint_result = subprocess.run(
        ["pylint", "--rcfile=.pylintrc", module_path, "--score=y"],
        capture_output=True,
        text=True,
        cwd="/opt/erp-conecta-mais/backend"
    )
    results["pylint_output"] = pylint_result.stdout

    # Extrair score
    for line in pylint_result.stdout.split("\n"):
        if "rated at" in line:
            score = line.split("rated at")[1].split("/")[0].strip()
            results["pylint_score"] = float(score)
            break

    return results


@server.tool("format_file")
async def format_file(file_path: str) -> dict[str, str]:
    """
    Formata arquivo com black e isort.

    Args:
        file_path: Caminho do arquivo

    Returns:
        Status da formatacao
    """
    # Black
    subprocess.run(["black", file_path], capture_output=True)

    # Isort
    subprocess.run(["isort", file_path], capture_output=True)

    return {"status": "formatted", "file": file_path}


if __name__ == "__main__":
    server.run()
```

**Configuracao:**
```json
{
  "mcpServers": {
    "auditor": {
      "command": "python",
      "args": ["/opt/erp-conecta-mais/tools/mcp-auditor/server.py"]
    }
  }
}
```

---

### MCP Gerador de Codigo
**Funcao:** Gerar boilerplate (models, schemas, etc)

```python
# /opt/erp-conecta-mais/tools/mcp-generator/server.py
"""
MCP Server para geracao de codigo.
"""

from mcp import Server, Tool

server = Server("code-generator")


@server.tool("generate_model")
async def generate_model(
    name: str,
    fields: list[dict],
    module: str = "crm"
) -> str:
    """
    Gera model SQLAlchemy.

    Args:
        name: Nome da entidade (ex: Proposal)
        fields: Lista de campos [{"name": "x", "type": "str", "nullable": False}]
        module: Modulo destino

    Returns:
        Codigo Python do model
    """
    # Template de model
    template = f'''"""
Model para {name}.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class {name}(Base):
    """Representa {name.lower()} no sistema."""

    __tablename__ = "{name.lower()}s"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
'''

    # Adicionar campos
    for field in fields:
        field_name = field["name"]
        field_type = field["type"]
        nullable = field.get("nullable", True)

        sql_type = {
            "str": "String(200)",
            "text": "Text",
            "int": "Integer",
            "decimal": "Numeric(15, 2)",
            "bool": "Boolean",
            "datetime": "DateTime",
            "uuid": "UUID(as_uuid=True)"
        }.get(field_type, "String(200)")

        template += f"    {field_name} = Column({sql_type}, nullable={nullable})\n"

    # Timestamps
    template += """
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"
"""

    return template


@server.tool("generate_schema")
async def generate_schema(name: str, fields: list[dict]) -> str:
    """Gera schemas Pydantic."""
    # Implementacao similar...
    pass


@server.tool("generate_repository")
async def generate_repository(name: str) -> str:
    """Gera repository."""
    # Implementacao similar...
    pass


@server.tool("generate_controller")
async def generate_controller(name: str) -> str:
    """Gera controller FastAPI."""
    # Implementacao similar...
    pass


if __name__ == "__main__":
    server.run()
```

---

## VERIFICACAO DA CONFIGURACAO

### Script de Verificacao

```bash
#!/bin/bash
# /opt/erp-conecta-mais/scripts/verify-mcp.sh

echo "=== Verificando Servidores MCP ==="

# Verificar instalacao
echo -n "PostgreSQL MCP: "
which mcp-server-postgres > /dev/null && echo "OK" || echo "NAO INSTALADO"

echo -n "Filesystem MCP: "
which mcp-server-filesystem > /dev/null && echo "OK" || echo "NAO INSTALADO"

echo -n "Git MCP: "
which mcp-server-git > /dev/null && echo "OK" || echo "NAO INSTALADO"

echo -n "Docker MCP: "
which mcp-server-docker > /dev/null && echo "OK" || echo "NAO INSTALADO"

echo -n "Fetch MCP: "
which mcp-server-fetch > /dev/null && echo "OK" || echo "NAO INSTALADO"

# Verificar config
echo ""
echo "=== Verificando Configuracao ==="
if [ -f ~/.claude/settings.json ]; then
    echo "Settings file: OK"
    cat ~/.claude/settings.json | python -m json.tool > /dev/null && echo "JSON valido: OK" || echo "JSON valido: ERRO"
else
    echo "Settings file: NAO ENCONTRADO"
fi

echo ""
echo "=== Verificacao Concluida ==="
```

---

## COMANDOS MCP NO CLAUDE CODE

### Exemplos de Uso

```
# Banco de dados
"Use o MCP postgres para listar as tabelas"
"Execute a query: SELECT * FROM leads LIMIT 5"
"Descreva o schema da tabela proposals"

# Arquivos
"Use o MCP filesystem para listar arquivos em modules/crm"
"Leia o conteudo de models/lead.py"

# Git
"Use o MCP git para ver o status"
"Mostre os ultimos 5 commits"
"Faca commit com mensagem 'feat: adiciona model proposal'"

# Docker
"Liste os containers rodando"
"Veja os logs do container postgres"

# Testes
"Use o MCP pytest para rodar tests/test_lead.py"
"Mostre a cobertura de testes"

# Auditoria
"Audite o arquivo models/proposal.py"
"Formate todos os arquivos em modules/crm"
```

---

## TROUBLESHOOTING

### Problema: MCP nao conecta

```bash
# Verificar se o servidor inicia manualmente
mcp-server-postgres --help

# Verificar logs do Claude Code
tail -f ~/.claude/logs/mcp.log

# Verificar permissoes
ls -la ~/.claude/settings.json
```

### Problema: Erro de autenticacao no Postgres

```bash
# Testar conexao direta
psql postgresql://conecta_user:conecta_pass_2024@localhost:5432/conecta_db

# Verificar pg_hba.conf
sudo cat /etc/postgresql/16/main/pg_hba.conf
```

### Problema: MCP lento

```bash
# Aumentar timeout
# Em settings.json:
{
  "mcpServers": {
    "postgres": {
      "timeout": 30000
    }
  }
}
```

---

*Configuracao MCP - ERP Conecta Mais Fase 2*
*"Ferramentas certas para o trabalho certo"*
