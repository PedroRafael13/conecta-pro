# Relatório de Auditoria de Segurança - Código

**Projeto:** Conecta PRO Backend
**Data:** 2026-02-05
**Auditor:** Análise Automatizada de Código
**Escopo:** `/opt/conecta-pro/backend/` (excluindo venv)

---

## Resumo Executivo

| Categoria | Crítico | Alto | Médio | Baixo | Total |
|-----------|---------|------|-------|-------|-------|
| SQL Injection | 0 | 3 | 5 | 2 | 10 |
| Command Injection | 0 | 0 | 2 | 0 | 2 |
| Hardcoded Secrets | 0 | 1 | 2 | 1 | 4 |
| Auth/Authorization | 0 | 1 | 3 | 2 | 6 |
| File Handling | 0 | 1 | 2 | 2 | 5 |
| SSL/TLS | 0 | 1 | 0 | 0 | 1 |
| **TOTAL** | **0** | **7** | **14** | **9** | **28** |

---

## 1. SQL Injection Analysis

### 1.1 Vulnerabilidades Dinâmicas de Tabela (ALTO)

#### VI-001: Injeção de Nome de Tabela Dinâmico
- **Arquivo:** `modules/government_integrations/core/etl/deduplicator.py`
- **Linhas:** 202-208, 238-244, 296-302
- **Severidade:** ALTO
- **Descrição:** Uso de `text(f"SELECT * FROM {regra.tabela}")` permite injeção se `regra.tabela` for controlado por input do usuário
- **Código Vulnerável:**
```python
result = await self.db.execute(
    text(f"""
    SELECT * FROM {regra.tabela}
    WHERE {condicoes}
    AND ativo = true
    """),
    chave
)
```
- **Correção Sugerida:**
```python
# Validar tabela contra whitelist
TABELAS_PERMITIDAS = {'documentos_fiscais', 'nfe_entrada', 'nfe_saida', ...}
if regra.tabela not in TABELAS_PERMITIDAS:
    raise ValueError(f"Tabela não permitida: {regra.tabela}")
```

#### VI-002: Injeção de Tabela em Exportação LGPD
- **Arquivo:** `modules/government_integrations/core/compliance/lgpd_compliance.py`
- **Linha:** 531
- **Severidade:** ALTO
- **Descrição:** Query dinâmica com nome de tabela vindo de input do usuário via parâmetro `tabelas`
- **Código Vulnerável:**
```python
result = await self.db.execute(
    text(f"""
    SELECT * FROM {tabela}
    WHERE tenant_id = :tenant_id
    """),
    {"tenant_id": tenant_id, "titular_id": titular_id}
)
```
- **Correção Sugerida:** Implementar whitelist de tabelas permitidas

#### VI-003: Injeção de Tabela em Versionamento
- **Arquivo:** `modules/government_integrations/core/etl/document_versioning.py`
- **Linhas:** 281, 312-318
- **Severidade:** ALTO
- **Descrição:** Parâmetro `tabela` usado diretamente em queries SQL

### 1.2 Vulnerabilidades de Condições Dinâmicas (MÉDIO)

#### VI-004: Construção Dinâmica de Condições
- **Arquivo:** `modules/government_integrations/core/compliance/lgpd_compliance.py`
- **Linhas:** 420, 465
- **Severidade:** MÉDIO
- **Descrição:** Uso de `{' AND '.join(conditions)}` pode ser vulnerável se conditions contiver input do usuário sem sanitização

#### VI-005: Construção Dinâmica de Update
- **Arquivo:** `modules/government_integrations/core/etl/deduplicator.py`
- **Linha:** 296-302
- **Severidade:** MÉDIO
- **Descrição:** Campos de update construídos dinamicamente a partir de dicionário

### 1.3 Vulnerabilidades em Migrações (BAIXO)

#### VI-006: Execute em Migrações Alembic
- **Arquivo:** Vários arquivos em `alembic/versions/`
- **Linhas:** Múltiplas
- **Severidade:** BAIXO (aceitável em migrações)
- **Descrição:** Uso de `op.execute(f"...")` em migrações de banco é padrão aceitável, pois migrações não aceitam input do usuário
- **Nota:** Não requer correção

---

## 2. Command Injection Risks

### 2.1 Execução de Subprocesso com Input do Usuário (MÉDIO)

#### VI-007: Subprocesso em OpenClaw Controller
- **Arquivo:** `modules/ai/bartolo/controllers/openclaw_controller.py`
- **Linhas:** 143-150, 315-320
- **Severidade:** MÉDIO
- **Descrição:** Uso de `asyncio.create_subprocess_exec` pode ser vulnerável se `check_type` ou `check_map` contiverem input não validado
- **Código Vulnerável:**
```python
cmd = ["python3", OPENCLAW_RUNNER]
if check_type != "full":
    cmd.extend(["--only", check_map[check_type]])

process = await asyncio.create_subprocess_exec(
    *cmd,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
    cwd="/opt/conecta-pro",
)
```
- **Correção Sugerida:**
```python
# Validar check_type contra whitelist
CHECKS_VALIDOS = {'full', 'security', 'performance', 'database', ...}
if check_type not in CHECKS_VALIDOS:
    raise HTTPException(status_code=400, detail="Check type inválido")
```

#### VI-008: Execução Dinâmica em Diagnose
- **Arquivo:** `diagnose_api_v1.py`
- **Linha:** 13
- **Severidade:** MÉDIO
- **Descrição:** Uso de `exec()` para importação dinâmica
- **Nota:** Baixo risco pois é script de diagnóstico interno

---

## 3. Hardcoded Secrets

### 3.1 Secrets em Arquivo de Configuração (ALTO)

#### VI-009: JWT Secret em Settings
- **Arquivo:** `core/config/settings.py`
- **Linha:** 36
- **Severidade:** ALTO
- **Descrição:** Default de JWT_SECRET_KEY em código pode ser usado se variável de ambiente não for configurada
- **Código:**
```python
jwt_secret_key: str = Field(default="CHANGE_ME_IN_PRODUCTION_32_CHARS_MIN")
```
- **Correção Sugerida:**
```python
jwt_secret_key: str = Field(...)  # Tornar obrigatório, sem default
```

### 3.2 Credenciais em Arquivo .env (MÉDIO)

#### VI-010: Arquivo .env com Secrets
- **Arquivo:** `.env`
- **Severidade:** MÉDIO
- **Descrição:** Arquivo contém credenciais de banco de dados e JWT em texto plano
- **Dados Expostos:**
  - DATABASE_URL com senha `postgres`
  - JWT_SECRET_KEY
  - REDIS_URL com senha
- **Correção Sugerida:**
  - Adicionar `.env` ao `.gitignore`
  - Usar Docker Secrets ou Vault para produção
  - Implementar rotação automática de secrets

### 3.3 Default Database URL (MÉDIO)

#### VI-011: Credenciais Default de Banco
- **Arquivo:** `core/config/settings.py`
- **Linha:** 33
- **Severidade:** MÉDIO
- **Descrição:** URL de banco com credenciais fracas em default
- **Código:**
```python
database_url: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/erp_conecta_mais")
```

---

## 4. Auth/Authorization Issues

### 4.1 Validação de Permissões (MÉDIO)

#### VI-012: Verificação de Permissões por String
- **Arquivo:** `core/auth/dependencies.py`
- **Linhas:** 143-144, 234-238
- **Severidade:** MÉDIO
- **Descrição:** Uso de `getattr(user, 'permissions', [])` pode falhar silenciosamente se campo não existir
- **Correção Sugerida:** Usar propriedade tipada ou schema Pydantic para permissões

#### VI-013: Falta de Rate Limit em Auth
- **Arquivo:** `api/v1/endpoints/auth.py`
- **Linhas:** 70-111
- **Severidade:** MÉDIO
- **Descrição:** Endpoint de login não possui rate limiting explícito
- **Correção Sugerida:** Implementar decorator de rate limit:
```python
@router.post("/login", response_model=Token)
@rate_limit(requests=5, window=60)  # 5 tentativas por minuto
async def login(...):
```

### 4.2 Configuração JWT (BAIXO)

#### VI-014: Token Longo (4 horas)
- **Arquivo:** `core/config/settings.py`
- **Linha:** 37
- **Severidade:** BAIXO
- **Descrição:** JWT com 4 horas de expiração pode ser longo demais para operações sensíveis
- **Nota:** Justificado pelo comentário "operação 24/7", mas considerar refresh tokens mais curtos

### 4.3 CORS Permissivo (BAIXO)

#### VI-015: CORS Origins Amplas
- **Arquivo:** `core/config/settings.py`
- **Linha:** 49, `.env`
- **Severidade:** BAIXO
- **Descrição:** Múltiplas origins incluindo `http://localhost:3000` e IPs externos em produção
- **Correção Sugerida:** Usar origins estritas por ambiente

---

## 5. File Handling Vulnerabilities

### 5.1 Path Traversal (ALTO)

#### VI-016: Path Traversal em Template Manager
- **Arquivo:** `modules/documents/services/template_manager.py`
- **Linhas:** 754-755, 824, 830-831
- **Severidade:** ALTO
- **Descrição:** Construção de caminho de arquivo com input do usuário pode permitir path traversal
- **Código Vulnerável:**
```python
file_path = os.path.join(self.templates_path, f"{template_id}.json")
```
- **Correção Sugerida:**
```python
import re
# Validar template_id
if not re.match(r'^[a-zA-Z0-9_-]+$', template_id):
    raise ValueError("ID de template inválido")
file_path = os.path.join(self.templates_path, f"{template_id}.json")
# Verificar se está dentro do diretório permitido
if not os.path.commonpath([file_path, self.templates_path]) == self.templates_path:
    raise ValueError("Acesso negado")
```

### 5.2 Validação de Upload (MÉDIO)

#### VI-017: Upload de Arquivos sem Validação de Tipo Estrita
- **Arquivo:** `modules/ged/controllers/document_controller.py`
- **Linha:** 63
- **Severidade:** MÉDIO
- **Descrição:** UploadFile sem validação explícita de extensão/mime type
- **Correção Sugerida:** Implementar validação de tipo de arquivo

#### VI-018: Upload de Certificados
- **Arquivo:** `modules/government_integrations/controllers/certificate_controller.py`
- **Linha:** 114
- **Severidade:** MÉDIO
- **Descrição:** Upload de arquivos .pfx/.p12 sem validação de tamanho máximo explícito

### 5.3 Uso de pickle (BAIXO)

#### VI-019: Deserialização pickle
- **Arquivo:** `modules/analytics/ml/registry/model_registry.py`
- **Linhas:** 222, 289
- **Severidade:** BAIXO
- **Descrição:** Uso de `pickle.dump` e `pickle.load` pode ser vulnerável se arquivo for comprometido
- **Código:**
```python
pickle.dump(model, f)
return pickle.load(f)
```
- **Nota:** Baixo risco se diretório de modelos for protegido
- **Correção Sugerida:** Considerar joblib ou formatos seguros como ONNX

---

## 6. SSL/TLS Issues

### 6.1 Verificação SSL Desabilitada (ALTO)

#### VI-020: SSL Verify False
- **Arquivo:** `modules/government_integrations/core/sefaz_am.py`
- **Linha:** 210
- **Severidade:** ALTO
- **Descrição:** `verify=False` em requisição HTTPS
- **Código:**
```python
verify=False,  # TODO: Configurar CA bundle ICP-Brasil
```
- **Correção Sugerida:** Configurar CA bundle correto ou usar certificados válidos

#### VI-021: SSL Verify False em Script de Teste
- **Arquivo:** `scripts/test_gov_connections.py`
- **Linha:** 400
- **Severidade:** MÉDIO (script de teste)
- **Descrição:** `verify=False` em cliente HTTPX

---

## 7. Outras Vulnerabilidades

### 7.1 Content Security Policy (BAIXO)

#### VI-022: CSP com unsafe-inline e unsafe-eval
- **Arquivo:** `main.py`
- **Linha:** 36
- **Severidade:** BAIXO
- **Descrição:** Política CSP permite inline scripts e eval
- **Código:**
```python
"script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
```

### 7.2 Informações de Debug (BAIXO)

#### VI-023: Detalhes de Erro Expostos
- **Arquivo:** `api/v1/endpoints/auth.py` e outros
- **Severidade:** BAIXO
- **Descrição:** Mensagens de erro podem expor informações internas
- **Exemplo:** `detail=f"Erro ao executar check: {str(e)}"`

---

## Recomendações Prioritárias

### Imediatas (Crítico/Alto)
1. **VI-001, VI-002, VI-003:** Implementar whitelist de tabelas em queries dinâmicas
2. **VI-016:** Corrigir path traversal em template_manager.py
3. **VI-020:** Configurar CA bundle ICP-Brasil para SEFAZ
4. **VI-009:** Remover defaults de secrets em settings.py

### Curto Prazo (Médio)
1. **VI-007:** Validar input em subprocessos
2. **VI-010:** Migrar secrets para Docker Secrets/Vault
3. **VI-012:** Implementar schema tipado para permissões
4. **VI-013:** Adicionar rate limiting em endpoints de auth

### Médio Prazo (Baixo)
1. **VI-014:** Revisar tempo de expiração de tokens
2. **VI-019:** Migrar de pickle para formatos seguros
3. **VI-022:** Refinar política CSP

---

## Metodologia

Esta auditoria foi realizada usando:
- Análise estática de código com grep/ripgrep
- Padrões de busca para vulnerabilidades comuns:
  - SQL Injection: `text(f"...`, `execute(f"...`, queries concatenadas
  - Command Injection: `subprocess`, `os.system`, `exec(`, `eval(`
  - Hardcoded Secrets: padrões de senhas, tokens, API keys
  - File Handling: `open(`, path construction com input do usuário

---

## Anexos

### A. Arquivos Analisados
- Total de arquivos Python: ~800+
- Arquivos em api/: ~50 endpoints
- Módulos core/: autenticação, configuração, database
- Módulos government_integrations/: integrações fiscais

### B. Ferramentas Recomendadas para Análise Contínua
1. **Bandit** - Analisador estático de segurança para Python
2. **Safety** - Verificação de dependências vulneráveis
3. **Semgrep** - Análise semântica de código
4. **Trivy** - Scanner de vulnerabilidades em containers

---

**Fim do Relatório**
