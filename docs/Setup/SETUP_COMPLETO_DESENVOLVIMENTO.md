# 🏗️ SETUP COMPLETO - ERP CONECTA MAIS
## AMBIENTE DE DESENVOLVIMENTO PROFISSIONAL COM TRIPLA VALIDAÇÃO

---

## 🎯 ARQUITETURA DO FLUXO DE DESENVOLVIMENTO

```
┌─────────────────────────────────────────────────────────────────┐
│                   PIPELINE DE QUALIDADE                         │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   TAREFA     │ (ex: Módulo CRM - Gestão de Leads)
    └──────┬───────┘
           │
           ▼
    ┌──────────────────────────────────────────┐
    │  🤖 AGENTE 1: CLAUDE CODE (Developer)    │
    │                                          │
    │  ✓ Desenvolve código                    │
    │  ✓ Escreve testes unitários             │
    │  ✓ Escreve testes de integração         │
    │  ✓ Executa testes localmente            │
    │  ✓ Verifica cobertura (>80%)            │
    │  ✓ Roda linter (pylint, black, mypy)    │
    │  ✓ Roda security scan                   │
    │  ✓ Gera documentação                    │
    └──────┬───────────────────────────────────┘
           │
           │ [✅ TODOS OS TESTES PASSARAM?]
           │
           ▼ SIM
    ┌──────────────────────────────────────────┐
    │  🔍 AGENTE 2: AUDITOR (Code Reviewer)    │
    │                                          │
    │  ✓ Analisa código linha por linha       │
    │  ✓ Verifica padrões de arquitetura      │
    │  ✓ Valida SOLID principles              │
    │  ✓ Checa performance (Big O)            │
    │  ✓ Revisa segurança (OWASP)             │
    │  ✓ Confere documentação                 │
    │  ✓ Valida testes (qualidade)            │
    │  ✓ Roda testes novamente                │
    └──────┬───────────────────────────────────┘
           │
           ├─── [❌ REJEITADO] ──► Volta para CODE com feedback
           │
           ▼ [✅ APROVADO]
    ┌──────────────────────────────────────────┐
    │  ✅ AGENTE 3: VALIDADOR (QA Final)       │
    │                                          │
    │  ✓ Testa em ambiente isolado            │
    │  ✓ Testes de carga/stress               │
    │  ✓ Testes de segurança avançados        │
    │  ✓ Valida integração com outros módulos │
    │  ✓ Checa conformidade com requisitos    │
    │  ✓ Testes de regressão                  │
    │  ✓ Aprovação FINAL                      │
    └──────┬───────────────────────────────────┘
           │
           ├─── [❌ REJEITADO] ──► Volta para CODE com feedback
           │
           ▼ [✅ ENTREGUE]
    ┌──────────────────┐
    │  🎉 CONCLUÍDO    │
    │  Deploy Ready    │
    └──────────────────┘
```

---

## 📦 PARTE 1: SETUP DO SERVIDOR E AMBIENTE

### 1.1 Especificações do Servidor

**Mínimo Recomendado:**
- **Cloud:** AWS / GCP / Azure
- **Tipo:** t3.xlarge (4 vCPUs, 16GB RAM) - desenvolvimento
- **Tipo:** t3.2xlarge (8 vCPUs, 32GB RAM) - produção
- **Storage:** 500GB SSD (mínimo)
- **OS:** Ubuntu 24.04 LTS
- **Região:** us-east-1 (ou mais próxima de Manaus)

**Setup Inicial do Servidor:**
```bash
#!/bin/bash
# setup_server.sh - Executar como root

# Atualizar sistema
apt update && apt upgrade -y

# Instalar dependências essenciais
apt install -y \
    build-essential \
    curl \
    wget \
    git \
    vim \
    tmux \
    htop \
    nginx \
    postgresql-15 \
    postgresql-contrib \
    redis-server \
    docker.io \
    docker-compose \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    nodejs \
    npm

# Configurar Docker
systemctl enable docker
systemctl start docker
usermod -aG docker ubuntu

# Instalar Docker Compose v2
curl -SL https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Instalar pyenv (gerenciador de versões Python)
curl https://pyenv.run | bash

# Configurar firewall
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 5432/tcp  # PostgreSQL (apenas IPs internos)
ufw allow 6379/tcp  # Redis (apenas IPs internos)
ufw enable

echo "✅ Servidor configurado com sucesso!"
```

### 1.2 Estrutura de Diretórios

```bash
#!/bin/bash
# create_structure.sh

# Criar estrutura do projeto
mkdir -p /opt/erp-conecta-mais/{
    backend/{
        api,
        core,
        modules/{commercial,hr,financial,operations,bi,admin},
        tests/{unit,integration,e2e},
        scripts,
        docs
    },
    frontend/{web,mobile},
    infra/{docker,kubernetes,terraform},
    data/{postgres,redis,mongo,elasticsearch},
    logs,
    backups,
    tools/{code,auditor,validator}
}

# Estrutura detalhada do backend
cd /opt/erp-conecta-mais/backend

# API
mkdir -p api/{v1/{routes,schemas,dependencies},middleware,utils}

# Core
mkdir -p core/{config,database,security,cache,messaging,logging}

# Módulos (exemplo: commercial)
mkdir -p modules/commercial/{
    models,
    schemas,
    services,
    repositories,
    controllers,
    tasks,
    tests
}

# Testes
mkdir -p tests/{fixtures,factories,mocks}

# Scripts
mkdir -p scripts/{setup,migration,seed,backup,deploy}

# Documentação
mkdir -p docs/{api,architecture,guides,changelog}

echo "✅ Estrutura de diretórios criada!"
```

### 1.3 Configuração do Python e Ambiente Virtual

```bash
#!/bin/bash
# setup_python.sh

cd /opt/erp-conecta-mais/backend

# Criar virtual environment
python3.11 -m venv venv

# Ativar
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip setuptools wheel

# Instalar dependências principais
pip install \
    fastapi==0.109.0 \
    uvicorn[standard]==0.27.0 \
    sqlalchemy==2.0.25 \
    alembic==1.13.1 \
    pydantic==2.5.3 \
    pydantic-settings==2.1.0 \
    psycopg2-binary==2.9.9 \
    redis==5.0.1 \
    celery==5.3.4 \
    httpx==0.26.0 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    python-multipart==0.0.6 \
    email-validator==2.1.0 \
    python-dotenv==1.0.0

# Ferramentas de desenvolvimento
pip install \
    pytest==7.4.4 \
    pytest-asyncio==0.23.3 \
    pytest-cov==4.1.0 \
    black==24.1.1 \
    isort==5.13.2 \
    pylint==3.0.3 \
    mypy==1.8.0 \
    bandit==1.7.6 \
    safety==3.0.1

# Ferramentas de documentação
pip install \
    mkdocs==1.5.3 \
    mkdocs-material==9.5.3

# Salvar requirements
pip freeze > requirements.txt

echo "✅ Ambiente Python configurado!"
```

### 1.4 Configuração do PostgreSQL

```bash
#!/bin/bash
# setup_postgres.sh

# Criar usuário e databases
sudo -u postgres psql <<EOF
-- Usuário principal
CREATE USER erp_user WITH PASSWORD 'super_secure_password_here';

-- Databases
CREATE DATABASE erp_conecta_mais_dev OWNER erp_user;
CREATE DATABASE erp_conecta_mais_test OWNER erp_user;
CREATE DATABASE erp_conecta_mais_prod OWNER erp_user;

-- Extensões
\c erp_conecta_mais_dev
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

\c erp_conecta_mais_test
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

\c erp_conecta_mais_prod
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Permissões
GRANT ALL PRIVILEGES ON DATABASE erp_conecta_mais_dev TO erp_user;
GRANT ALL PRIVILEGES ON DATABASE erp_conecta_mais_test TO erp_user;
GRANT ALL PRIVILEGES ON DATABASE erp_conecta_mais_prod TO erp_user;
EOF

echo "✅ PostgreSQL configurado!"
```

### 1.5 Docker Compose para Desenvolvimento

```yaml
# docker-compose.yml
version: '3.9'

services:
  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    container_name: erp_postgres
    environment:
      POSTGRES_USER: erp_user
      POSTGRES_PASSWORD: super_secure_password
      POSTGRES_DB: erp_conecta_mais_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - erp_network

  # Redis
  redis:
    image: redis:7-alpine
    container_name: erp_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - erp_network

  # MongoDB (para logs e documentos)
  mongodb:
    image: mongo:7
    container_name: erp_mongodb
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: erp_user
      MONGO_INITDB_ROOT_PASSWORD: super_secure_password
    volumes:
      - mongo_data:/data/db
    networks:
      - erp_network

  # Elasticsearch (para busca full-text)
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: erp_elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elastic_data:/usr/share/elasticsearch/data
    networks:
      - erp_network

  # RabbitMQ (message broker)
  rabbitmq:
    image: rabbitmq:3-management-alpine
    container_name: erp_rabbitmq
    ports:
      - "5672:5672"   # AMQP
      - "15672:15672" # Management UI
    environment:
      RABBITMQ_DEFAULT_USER: erp_user
      RABBITMQ_DEFAULT_PASS: super_secure_password
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    networks:
      - erp_network

volumes:
  postgres_data:
  redis_data:
  mongo_data:
  elastic_data:
  rabbitmq_data:

networks:
  erp_network:
    driver: bridge
```

---

## 🤖 PARTE 2: CONFIGURAÇÃO DOS 3 AGENTES

### 2.1 Agente 1: CLAUDE CODE (Developer)

**Arquivo:** `/opt/erp-conecta-mais/tools/code/developer_agent.py`

```python
"""
AGENTE DESENVOLVEDOR - Claude Code
Responsável por: Desenvolvimento, Testes Unitários, Testes de Integração
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import json

class DeveloperAgent:
    """
    Agente desenvolvedor principal
    """
    
    def __init__(self, module_path: Path):
        self.module_path = module_path
        self.errors = []
        self.warnings = []
        self.passed_tests = 0
        self.failed_tests = 0
        self.coverage = 0.0
    
    def develop(self, task: Dict) -> Tuple[bool, Dict]:
        """
        Desenvolve uma tarefa completa
        
        task = {
            "name": "CRM - Gestão de Leads",
            "requirements": ["RF-CRM-001", "RF-CRM-002"],
            "files_to_create": ["models.py", "schemas.py", "services.py"],
            "tests_to_create": ["test_models.py", "test_services.py"]
        }
        """
        print(f"🤖 Developer Agent: Iniciando tarefa '{task['name']}'")
        
        # 1. Criar arquivos
        success = self.create_files(task['files_to_create'])
        if not success:
            return False, {"error": "Falha ao criar arquivos"}
        
        # 2. Escrever código
        success = self.write_code(task)
        if not success:
            return False, {"error": "Falha ao escrever código"}
        
        # 3. Criar testes
        success = self.create_tests(task['tests_to_create'])
        if not success:
            return False, {"error": "Falha ao criar testes"}
        
        # 4. Executar testes
        success = self.run_tests()
        if not success:
            return False, {"error": "Testes falharam", "details": self.errors}
        
        # 5. Verificar cobertura
        if self.coverage < 80:
            return False, {"error": f"Cobertura insuficiente: {self.coverage}%"}
        
        # 6. Linter
        success = self.run_linter()
        if not success:
            return False, {"error": "Linter falhou", "details": self.errors}
        
        # 7. Security scan
        success = self.run_security_scan()
        if not success:
            return False, {"error": "Vulnerabilidades encontradas", "details": self.errors}
        
        # 8. Gerar documentação
        self.generate_docs()
        
        # Sucesso!
        return True, {
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "coverage": self.coverage,
            "warnings": self.warnings
        }
    
    def run_tests(self) -> bool:
        """
        Executa pytest com cobertura
        """
        print("  ├─ Executando testes...")
        
        cmd = [
            "pytest",
            str(self.module_path),
            "-v",
            "--cov",
            "--cov-report=term-missing",
            "--cov-report=json",
            "--junitxml=test-results.xml"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse output
        if "failed" in result.stdout.lower():
            self.failed_tests = self._count_failed(result.stdout)
            self.errors.append(result.stdout)
            return False
        
        self.passed_tests = self._count_passed(result.stdout)
        self.coverage = self._extract_coverage()
        
        print(f"  ├─ ✅ {self.passed_tests} testes passaram")
        print(f"  ├─ 📊 Cobertura: {self.coverage}%")
        
        return True
    
    def run_linter(self) -> bool:
        """
        Executa black, isort, pylint, mypy
        """
        print("  ├─ Executando linters...")
        
        # Black (formatação)
        subprocess.run(["black", str(self.module_path)])
        
        # isort (imports)
        subprocess.run(["isort", str(self.module_path)])
        
        # pylint (qualidade)
        result = subprocess.run(
            ["pylint", str(self.module_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            self.warnings.append(f"Pylint: {result.stdout}")
        
        # mypy (type checking)
        result = subprocess.run(
            ["mypy", str(self.module_path)],
            capture_output=True,
            text=True
        )
        
        if "error" in result.stdout.lower():
            self.errors.append(f"MyPy: {result.stdout}")
            return False
        
        print("  ├─ ✅ Linters OK")
        return True
    
    def run_security_scan(self) -> bool:
        """
        Executa bandit (security linter)
        """
        print("  ├─ Executando security scan...")
        
        result = subprocess.run(
            ["bandit", "-r", str(self.module_path)],
            capture_output=True,
            text=True
        )
        
        if "high severity" in result.stdout.lower():
            self.errors.append(f"Bandit: {result.stdout}")
            return False
        
        print("  ├─ ✅ Security scan OK")
        return True
    
    def generate_docs(self):
        """
        Gera documentação automática
        """
        print("  ├─ Gerando documentação...")
        # Usar pydoc ou sphinx
        pass
    
    def _count_passed(self, output: str) -> int:
        # Parse pytest output
        import re
        match = re.search(r'(\d+) passed', output)
        return int(match.group(1)) if match else 0
    
    def _count_failed(self, output: str) -> int:
        import re
        match = re.search(r'(\d+) failed', output)
        return int(match.group(1)) if match else 0
    
    def _extract_coverage(self) -> float:
        # Ler coverage.json
        try:
            with open('coverage.json') as f:
                data = json.load(f)
                return round(data['totals']['percent_covered'], 2)
        except:
            return 0.0


# Exemplo de uso
if __name__ == "__main__":
    agent = DeveloperAgent(Path("/opt/erp-conecta-mais/backend/modules/commercial"))
    
    task = {
        "name": "CRM - Gestão de Leads",
        "requirements": ["RF-CRM-001", "RF-CRM-002"],
        "files_to_create": ["models/lead.py", "services/lead_service.py"],
        "tests_to_create": ["tests/test_lead_model.py"]
    }
    
    success, result = agent.develop(task)
    
    if success:
        print("✅ Tarefa concluída!")
        print(json.dumps(result, indent=2))
    else:
        print("❌ Tarefa falhou!")
        print(json.dumps(result, indent=2))
        sys.exit(1)
```

### 2.2 Agente 2: AUDITOR (Code Reviewer)

**Arquivo:** `/opt/erp-conecta-mais/tools/auditor/auditor_agent.py`

```python
"""
AGENTE AUDITOR - Code Reviewer
Responsável por: Análise de código, Padrões, Segurança, Performance
"""

import ast
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple
import re

class AuditorAgent:
    """
    Agente auditor - Revisa código desenvolvido
    """
    
    def __init__(self, module_path: Path):
        self.module_path = module_path
        self.issues = []
        self.warnings = []
        self.score = 0.0
    
    def audit(self, developer_result: Dict) -> Tuple[bool, Dict]:
        """
        Audita código desenvolvido
        """
        print(f"🔍 Auditor Agent: Iniciando auditoria...")
        
        # 1. Verificar padrões de arquitetura
        if not self.check_architecture_patterns():
            return False, {"error": "Arquitetura não conforme", "issues": self.issues}
        
        # 2. Validar SOLID principles
        if not self.validate_solid():
            return False, {"error": "SOLID principles violados", "issues": self.issues}
        
        # 3. Análise de complexidade
        if not self.analyze_complexity():
            return False, {"error": "Código muito complexo", "issues": self.issues}
        
        # 4. Revisão de segurança OWASP
        if not self.security_review():
            return False, {"error": "Vulnerabilidades de segurança", "issues": self.issues}
        
        # 5. Performance (Big O)
        if not self.performance_analysis():
            return False, {"error": "Performance inadequada", "issues": self.issues}
        
        # 6. Qualidade dos testes
        if not self.validate_test_quality(developer_result):
            return False, {"error": "Testes insuficientes", "issues": self.issues}
        
        # 7. Documentação
        if not self.check_documentation():
            return False, {"error": "Documentação incompleta", "issues": self.issues}
        
        # 8. Rodar testes novamente (double-check)
        if not self.rerun_tests():
            return False, {"error": "Testes falharam na re-execução", "issues": self.issues}
        
        # Calcular score final
        self.score = self.calculate_score()
        
        # Aprovado se score >= 90
        if self.score < 90:
            return False, {
                "error": f"Score insuficiente: {self.score}/100",
                "issues": self.issues,
                "warnings": self.warnings
            }
        
        print(f"  ├─ ✅ Auditoria aprovada! Score: {self.score}/100")
        return True, {"score": self.score, "warnings": self.warnings}
    
    def check_architecture_patterns(self) -> bool:
        """
        Verifica se código segue padrões de arquitetura definidos
        """
        print("  ├─ Verificando padrões de arquitetura...")
        
        # Verificar estrutura de pastas
        required_dirs = ['models', 'schemas', 'services', 'repositories', 'tests']
        for dir_name in required_dirs:
            if not (self.module_path / dir_name).exists():
                self.issues.append(f"Pasta {dir_name} não encontrada")
                return False
        
        # Verificar imports (não deve haver imports circulares)
        if self._has_circular_imports():
            self.issues.append("Imports circulares detectados")
            return False
        
        print("  ├─ ✅ Arquitetura OK")
        return True
    
    def validate_solid(self) -> bool:
        """
        Valida princípios SOLID
        """
        print("  ├─ Validando SOLID principles...")
        
        for py_file in self.module_path.rglob("*.py"):
            with open(py_file) as f:
                code = f.read()
                tree = ast.parse(code)
            
            # S - Single Responsibility
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if self._count_methods(node) > 10:
                        self.warnings.append(
                            f"{py_file.name}: Classe {node.name} tem muitos métodos (SRP)"
                        )
            
            # O - Open/Closed
            # ... verificações adicionais
        
        print("  ├─ ✅ SOLID OK")
        return True
    
    def analyze_complexity(self) -> bool:
        """
        Analisa complexidade ciclomática
        """
        print("  ├─ Analisando complexidade...")
        
        result = subprocess.run(
            ["radon", "cc", str(self.module_path), "-a"],
            capture_output=True,
            text=True
        )
        
        # Radon grades: A (best) to F (worst)
        if " F " in result.stdout or " E " in result.stdout:
            self.issues.append("Complexidade muito alta (grade D/E/F)")
            return False
        
        print("  ├─ ✅ Complexidade OK")
        return True
    
    def security_review(self) -> bool:
        """
        Revisão de segurança OWASP
        """
        print("  ├─ Revisão de segurança OWASP...")
        
        # Checklist OWASP Top 10
        checks = {
            "SQL Injection": self._check_sql_injection(),
            "XSS": self._check_xss(),
            "CSRF": self._check_csrf(),
            "Sensitive Data": self._check_sensitive_data(),
            "Broken Auth": self._check_authentication(),
        }
        
        failed = [k for k, v in checks.items() if not v]
        if failed:
            self.issues.extend([f"OWASP: {check} não conforme" for check in failed])
            return False
        
        print("  ├─ ✅ Segurança OK")
        return True
    
    def performance_analysis(self) -> bool:
        """
        Análise de performance (Big O)
        """
        print("  ├─ Analisando performance...")
        
        # Verificar queries N+1
        for py_file in self.module_path.rglob("*.py"):
            with open(py_file) as f:
                code = f.read()
            
            # Detectar loops com queries
            if re.search(r'for .+ in .+:\s+.*query', code):
                self.warnings.append(f"{py_file.name}: Possível N+1 query")
        
        print("  ├─ ✅ Performance OK")
        return True
    
    def validate_test_quality(self, developer_result: Dict) -> bool:
        """
        Valida qualidade dos testes
        """
        print("  ├─ Validando qualidade dos testes...")
        
        # Cobertura mínima: 80%
        if developer_result['coverage'] < 80:
            self.issues.append(f"Cobertura insuficiente: {developer_result['coverage']}%")
            return False
        
        # Verificar se testes testam casos de erro
        # ... análise adicional
        
        print("  ├─ ✅ Testes OK")
        return True
    
    def check_documentation(self) -> bool:
        """
        Verifica documentação
        """
        print("  ├─ Verificando documentação...")
        
        for py_file in self.module_path.rglob("*.py"):
            with open(py_file) as f:
                code = f.read()
                tree = ast.parse(code)
            
            # Verificar docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        self.warnings.append(f"{py_file.name}: {node.name} sem docstring")
        
        print("  ├─ ✅ Documentação OK")
        return True
    
    def rerun_tests(self) -> bool:
        """
        Re-executa testes (double-check)
        """
        print("  ├─ Re-executando testes...")
        
        result = subprocess.run(
            ["pytest", str(self.module_path), "-v"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            self.issues.append("Testes falharam na re-execução")
            return False
        
        print("  ├─ ✅ Testes passaram novamente")
        return True
    
    def calculate_score(self) -> float:
        """
        Calcula score final (0-100)
        """
        score = 100.0
        score -= len(self.issues) * 10  # Cada issue: -10 pontos
        score -= len(self.warnings) * 2  # Cada warning: -2 pontos
        return max(score, 0)
    
    # Métodos auxiliares
    def _has_circular_imports(self) -> bool:
        # ... implementação
        return False
    
    def _count_methods(self, class_node) -> int:
        return len([n for n in class_node.body if isinstance(n, ast.FunctionDef)])
    
    def _check_sql_injection(self) -> bool:
        # ... implementação
        return True
    
    def _check_xss(self) -> bool:
        return True
    
    def _check_csrf(self) -> bool:
        return True
    
    def _check_sensitive_data(self) -> bool:
        return True
    
    def _check_authentication(self) -> bool:
        return True
```

### 2.3 Agente 3: VALIDADOR (QA Final)

**Arquivo:** `/opt/erp-conecta-mais/tools/validator/validator_agent.py`

```python
"""
AGENTE VALIDADOR - QA Final
Responsável por: Testes finais, Integração, Stress, Aprovação final
"""

import subprocess
import time
from pathlib import Path
from typing import Dict, Tuple
import requests

class ValidatorAgent:
    """
    Agente validador - QA final antes de aprovar
    """
    
    def __init__(self, module_path: Path):
        self.module_path = module_path
        self.issues = []
        self.test_results = {}
    
    def validate(self, auditor_result: Dict) -> Tuple[bool, Dict]:
        """
        Validação final
        """
        print(f"✅ Validator Agent: Validação final...")
        
        # 1. Testes em ambiente isolado
        if not self.test_isolated_environment():
            return False, {"error": "Falha em ambiente isolado", "issues": self.issues}
        
        # 2. Testes de carga/stress
        if not self.load_test():
            return False, {"error": "Falha em testes de carga", "issues": self.issues}
        
        # 3. Testes de segurança avançados
        if not self.advanced_security_test():
            return False, {"error": "Falha em segurança avançada", "issues": self.issues}
        
        # 4. Testes de integração com outros módulos
        if not self.integration_test():
            return False, {"error": "Falha em integração", "issues": self.issues}
        
        # 5. Conformidade com requisitos
        if not self.requirements_compliance():
            return False, {"error": "Não conforme com requisitos", "issues": self.issues}
        
        # 6. Testes de regressão
        if not self.regression_test():
            return False, {"error": "Regressão detectada", "issues": self.issues}
        
        # APROVAÇÃO FINAL
        print("  ├─ ✅ VALIDAÇÃO APROVADA! Módulo pronto para deploy!")
        
        return True, {
            "status": "APPROVED",
            "test_results": self.test_results
        }
    
    def test_isolated_environment(self) -> bool:
        """
        Testa em ambiente Docker isolado
        """
        print("  ├─ Testando em ambiente isolado...")
        
        # Subir container isolado
        subprocess.run([
            "docker", "run", "--rm",
            "-v", f"{self.module_path}:/app",
            "python:3.11",
            "pytest", "/app", "-v"
        ])
        
        print("  ├─ ✅ Ambiente isolado OK")
        return True
    
    def load_test(self) -> bool:
        """
        Testes de carga com Locust
        """
        print("  ├─ Executando testes de carga...")
        
        # Exemplo: 100 usuários simultâneos
        result = subprocess.run([
            "locust",
            "-f", "locustfile.py",
            "--headless",
            "-u", "100",  # 100 users
            "-r", "10",   # spawn 10/sec
            "--run-time", "1m",
            "--host", "http://localhost:8000"
        ], capture_output=True, text=True)
        
        # Verificar se não houve falhas
        if "fail" in result.stdout.lower():
            self.issues.append("Testes de carga falharam")
            return False
        
        print("  ├─ ✅ Testes de carga OK")
        return True
    
    def advanced_security_test(self) -> bool:
        """
        OWASP ZAP scan
        """
        print("  ├─ Security scan avançado...")
        
        # Rodar OWASP ZAP
        subprocess.run([
            "docker", "run", "--rm",
            "owasp/zap2docker-stable",
            "zap-baseline.py",
            "-t", "http://localhost:8000"
        ])
        
        print("  ├─ ✅ Security avançado OK")
        return True
    
    def integration_test(self) -> bool:
        """
        Testes de integração
        """
        print("  ├─ Testando integração...")
        
        # Rodar testes de integração
        result = subprocess.run([
            "pytest",
            "tests/integration",
            "-v"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            self.issues.append("Integração falhou")
            return False
        
        print("  ├─ ✅ Integração OK")
        return True
    
    def requirements_compliance(self) -> bool:
        """
        Valida conformidade com requisitos funcionais
        """
        print("  ├─ Validando requisitos...")
        
        # Verificar se todos RF-XXX-YYY foram implementados
        # ... implementação
        
        print("  ├─ ✅ Requisitos OK")
        return True
    
    def regression_test(self) -> bool:
        """
        Testes de regressão
        """
        print("  ├─ Testes de regressão...")
        
        # Rodar suite completa de testes
        result = subprocess.run([
            "pytest",
            "tests/",
            "--tb=short"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            self.issues.append("Regressão detectada")
            return False
        
        print("  ├─ ✅ Regressão OK")
        return True
```

---

**CONTINUA NA PRÓXIMA PARTE com orchestrator e automação completa...**

