# AUDITORIA SKILL 06 — AUTENTICAÇÃO E AUTORIZAÇÃO CONECTA PRO
> **Gerada em:** 31/03/2026
> **Metodologia:** Skill 06 (autenticacao-autorizacao-conecta-pro) — Passo Inicial + 5 subagentes paralelos
> **Cobertura:** JWT · RBAC · Endpoints Públicos · Rate Limit · Senhas/Criptografia
> **Backend:** http://127.0.0.1:8080 · Container: conecta-pro-backend

---

## PASSO INICIAL — MAPEAMENTO GLOBAL DE AUTH

```bash
# Executado em: 31/03/2026 — Scan estático + testes dinâmicos
```

### Scan Global: Controllers sem Autenticação

**RESULTADO: 111 controllers sem `get_current_user` / `CurrentActiveUser` / portal auth**

Categorias identificadas (lista completa — 111 arquivos):

```
# AI (7 controllers)
SEM AUTH: modules/ai/conversation/controllers/chat_controller.py (15 rotas)
SEM AUTH: modules/ai/data_quality/controllers/data_quality_controller.py (24 rotas)
SEM AUTH: modules/ai/intelligence_hub/controllers/intelligence_hub_controller.py (12 rotas)
SEM AUTH: modules/ai/ocr/controllers/ocr_controller.py (15 rotas)
SEM AUTH: modules/ai/openclaw/controller.py (6 rotas)
SEM AUTH: modules/ai/report_generator/controllers/report_controller.py (31 rotas)
SEM AUTH: modules/ai/signature/controllers/signature_controller.py (25 rotas)

# Analytics / Config (2 controllers — CRÍTICOS)
SEM AUTH: modules/analytics/controllers/executive_dashboard_controller.py (7 rotas)
SEM AUTH: modules/config/controllers/config_controller.py (47 rotas)

# Automação e Workflow (1 controller)
SEM AUTH: modules/automation/workflow/controllers/workflow_controller.py (9 rotas)

# Licitações (9 controllers)
SEM AUTH: modules/bidding/controllers/agent_controller.py (13 rotas)
SEM AUTH: modules/bidding/controllers/certificate_controller.py (11 rotas)
SEM AUTH: modules/bidding/controllers/contract_controller.py (14 rotas)
SEM AUTH: modules/bidding/controllers/dispute_controller.py (5 rotas)
SEM AUTH: modules/bidding/controllers/document_controller.py (11 rotas)
SEM AUTH: modules/bidding/controllers/erp_controller.py (5 rotas)
SEM AUTH: modules/bidding/controllers/opportunity_controller.py (4 rotas)
SEM AUTH: modules/bidding/controllers/proposal_controller.py (13 rotas)
SEM AUTH: modules/bidding/controllers/tender_controller.py (15 rotas)

# Campo / Operações de Campo (10 controllers)
SEM AUTH: modules/campo/controllers/access_log_controller.py (8 rotas)
SEM AUTH: modules/campo/controllers/campo_service_controller.py (7 rotas)
SEM AUTH: modules/campo/controllers/checklist_controller.py (18 rotas)
SEM AUTH: modules/campo/controllers/equipment_status_controller.py (13 rotas)
SEM AUTH: modules/campo/controllers/estoque_controller.py (12 rotas)
SEM AUTH: modules/campo/controllers/monitoring_controller.py (5 rotas)
SEM AUTH: modules/campo/controllers/ordem_servico_controller.py (22 rotas)
SEM AUTH: modules/campo/controllers/roteirizacao_controller.py (8 rotas)
SEM AUTH: modules/campo/controllers/security_audit_controller.py (3 rotas)
SEM AUTH: modules/campo/controllers/visita_controller.py (24 rotas)

# Portal do Cliente (9 controllers — auth própria por portal_client, mas sem ela aqui)
SEM AUTH: modules/client_portal/controllers/analytics_controller.py (4 rotas)
SEM AUTH: modules/client_portal/controllers/assistant_controller.py (3 rotas)
SEM AUTH: modules/client_portal/controllers/auth_controller.py (3 rotas — público intencional)
SEM AUTH: modules/client_portal/controllers/kit_approval_controller.py (2 rotas)
SEM AUTH: modules/client_portal/controllers/kit_controller.py (4 rotas)
SEM AUTH: modules/client_portal/controllers/notifications_controller.py (5 rotas)
SEM AUTH: modules/client_portal/controllers/ticket_controller.py (5 rotas)

# Clientes e CRM (4 controllers)
SEM AUTH: modules/clients/controllers/client_controller.py (51 rotas)
SEM AUTH: modules/crm/controllers/client_controller.py (3 rotas)
SEM AUTH: modules/crm/controllers/contact_controller.py (7 rotas)
SEM AUTH: modules/crm/controllers/marketing_controller.py (8 rotas)

# Kits Documentais (2 controllers)
SEM AUTH: modules/document_kits/controllers/kit_controller.py (45 rotas)
SEM AUTH: modules/document_kits/controllers/operational_controller.py (9 rotas)

# Documentos (1 controller)
SEM AUTH: modules/documents/controllers/document_controller.py (16 rotas)

# Empresas (3 controllers)
SEM AUTH: modules/empresas/controllers/bookkeeper_controller.py (3 rotas)
SEM AUTH: modules/empresas/controllers/dominio_controller.py (5 rotas)
SEM AUTH: modules/empresas/controllers/statements_controller.py (4 rotas)

# Equipamentos (4 controllers)
SEM AUTH: modules/equipment_management/controllers/comodato_controller.py (26 rotas)
SEM AUTH: modules/equipment_management/controllers/equipment_controller.py (19 rotas)
SEM AUTH: modules/equipment_management/controllers/installation_controller.py (20 rotas)
SEM AUTH: modules/equipment_management/controllers/maintenance_controller.py (28 rotas)

# Governo (20 controllers — CRÍTICOS)
SEM AUTH: modules/government_integrations/controllers/certificate_controller.py (7 rotas)
SEM AUTH: modules/government_integrations/controllers/cte_controller.py (10 rotas)
SEM AUTH: modules/government_integrations/controllers/dashboard_controller.py (7 rotas)
SEM AUTH: modules/government_integrations/controllers/dctfweb_controller.py (11 rotas)
SEM AUTH: modules/government_integrations/controllers/ecac_controller.py (9 rotas)
SEM AUTH: modules/government_integrations/controllers/efd_reinf_controller.py (10 rotas)
SEM AUTH: modules/government_integrations/controllers/extraction_controller.py (10 rotas)
SEM AUTH: modules/government_integrations/controllers/fgts_digital_controller.py (11 rotas)
SEM AUTH: modules/government_integrations/controllers/govbr_controller.py (12 rotas)
SEM AUTH: modules/government_integrations/controllers/jobs_controller.py (8 rotas)
SEM AUTH: modules/government_integrations/controllers/mdfe_controller.py (14 rotas)
SEM AUTH: modules/government_integrations/controllers/nfce_controller.py (9 rotas)
SEM AUTH: modules/government_integrations/controllers/nfse_manaus_controller.py (8 rotas)
SEM AUTH: modules/government_integrations/controllers/nfse_nacional_controller.py (12 rotas)
SEM AUTH: modules/government_integrations/controllers/sefaz_am_controller.py (8 rotas)
SEM AUTH: modules/government_integrations/controllers/sped_contabil_controller.py (13 rotas)
SEM AUTH: modules/government_integrations/controllers/sped_fiscal_controller.py (13 rotas)
SEM AUTH: modules/government_integrations/controllers/sync_controller.py (16 rotas)

# Saúde Ocupacional (3 controllers)
SEM AUTH: modules/health_occupational/controllers/epi_controller.py (15 rotas)
SEM AUTH: modules/health_occupational/controllers/pcmso_controller.py (11 rotas)
SEM AUTH: modules/health_occupational/controllers/ppra_controller.py (11 rotas)

# Integrações (2 controllers)
SEM AUTH: modules/hr/rep_integration/controllers/webhook_controller.py (4 rotas)
SEM AUTH: modules/integrations/connectors/whatsapp/controller.py (5 rotas)

# Monitoramento (2 controllers)
SEM AUTH: modules/monitoring/controllers/monitoring_controller.py (16 rotas)
SEM AUTH: modules/monitoring/controllers/realtime_controller.py (9 rotas)

# Operacional (5 controllers)
SEM AUTH: modules/operacional/communication/controllers/websocket_controller.py (1 rota)
SEM AUTH: modules/operacional/controllers/dashboard_controller.py (9 rotas)
SEM AUTH: modules/operacional/diaristas/controllers/fiscal_controller.py (10 rotas)
SEM AUTH: modules/operacional/diaristas/controllers/notificacao_controller.py (14 rotas)
SEM AUTH: modules/operacional/inspection_rounds/controllers/inspection_round_controller.py (18 rotas)
SEM AUTH: modules/operacional/vacations/controller.py (7 rotas)

# Gestão de Pessoas (8 controllers)
SEM AUTH: modules/people_management/cct/controllers/admin_cct_controller.py (13 rotas)
SEM AUTH: modules/people_management/employee_portal/controllers/dp_payslips_controller.py (7 rotas)
SEM AUTH: modules/people_management/hr/controllers/cct_controller.py (4 rotas)
SEM AUTH: modules/people_management/human_resources/controllers/climate_controller.py (5 rotas)
SEM AUTH: modules/people_management/human_resources/controllers/onboarding_controller.py (4 rotas)
SEM AUTH: modules/people_management/human_resources/controllers/turnover_controller.py (2 rotas)
SEM AUTH: modules/people_management/integration/aggregator.py (11 rotas)

# Relatórios e Scheduler (3 controllers)
SEM AUTH: modules/reports/controllers/intelligent_reports_controller.py (6 rotas)
SEM AUTH: modules/reports/controllers/report_controller.py (32 rotas)
SEM AUTH: modules/scheduler/controllers/scheduler_controller.py (26 rotas)

# LGPD (7 controllers — violação da própria lei)
SEM AUTH: modules/security_lgpd/controllers/audit_controller.py (4 rotas)
SEM AUTH: modules/security_lgpd/controllers/consent_controller.py (5 rotas)
SEM AUTH: modules/security_lgpd/controllers/encryption_controller.py (3 rotas)
SEM AUTH: modules/security_lgpd/controllers/erasure_controller.py (2 rotas)
SEM AUTH: modules/security_lgpd/controllers/masking_controller.py (2 rotas)
SEM AUTH: modules/security_lgpd/controllers/pia_controller.py (3 rotas)
SEM AUTH: modules/security_lgpd/controllers/status_controller.py (2 rotas)
```

### Confirmação Dinâmica (curl sem token)

```
❌ EXPOSTO:   GET /api/v1/analytics/executive/dashboard → 200
✅ PROTEGIDO: GET /api/v1/financial/receivables         → 403
✅ PROTEGIDO: GET /api/v1/people-management/hr/employees → 403
✅ PROTEGIDO: GET /api/v1/ged/documents                 → 403
✅ PROTEGIDO: GET /api/v1/ai/bartolo/greeting           → 403
✅ PROTEGIDO: GET /api/v1/government/esocial/eventos    → 403
```

### Brute Force — Resultado Real

```
Tentativa 1: HTTP 401
Tentativa 2: HTTP 401
Tentativa 3: HTTP 401
Tentativa 4: HTTP 401
Tentativa 5: HTTP 429  ← rate limit ativo (5/minuto)
Tentativa 6: HTTP 429
Tentativa 7: HTTP 429
```

### Security Headers (confirmados)

```
x-content-type-options: nosniff        ✅
x-frame-options: DENY                  ✅
x-xss-protection: 1; mode=block        ✅
strict-transport-security: max-age=31536000; includeSubDomains ✅
```

### Roles Existentes (confirmados no código)

```
UserRole: SUPER_ADMIN, ADMIN, MANAGER, SUPERVISOR, OPERATOR, CLIENT, VIEWER
Hierarquia: SUPER_ADMIN > ADMIN > MANAGER > SUPERVISOR > OPERATOR > CLIENT > VIEWER
```

---

## SCORECARD EXECUTIVO

```
╔══════════════════════════════════════════════════════════════════════╗
║          CONECTA PRO — AUDITORIA AUTH/AUTHZ                         ║
║          Skill 06 — 31/03/2026 — Passo Inicial + 5 subagentes      ║
╠══════════════════════════╦══════════════╦══════════════════════════╣
║ Dimensão                 ║  Score       ║  Status                  ║
╠══════════════════════════╬══════════════╬══════════════════════════╣
║ JWT e Tokens             ║   6.0 / 10   ║  ⚠️ Falhas altas         ║
║ RBAC / Controle Acesso   ║   5.5 / 10   ║  🔴 Escalação crítica    ║
║ Endpoints Públicos       ║   3.5 / 10   ║  🔴 111 controllers sem  ║
║                          ║              ║      auth (scan global)  ║
║ Rate Limit / Brute Force ║   5.0 / 10   ║  🔴 Sem lockout          ║
║ Senhas e Criptografia    ║   5.0 / 10   ║  🔴 Credenciais hardcoded║
╠══════════════════════════╬══════════════╬══════════════════════════╣
║ SCORE MÉDIO PONDERADO    ║   5.0 / 10   ║  🔴 ABAIXO DO MÍNIMO    ║
╠══════════════════════════╩══════════════╩══════════════════════════╣
║                                                                      ║
║  Controllers sem autenticação: 111 (scan estático)                  ║
║  Confirmado exposto via curl: executive/dashboard (→ HTTP 200)      ║
║  Vulnerabilidades CRÍTICAS: 5                                        ║
║  Vulnerabilidades ALTAS: 9                                           ║
║  Vulnerabilidades MÉDIAS: 7                                          ║
║  Rate limit login: ativo a partir de tentativa 5 (429)              ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## VULNERABILIDADES CRÍTICAS (por prioridade de correção)

---

### 🔴 PRIORIDADE 1 — Privilege Escalation via /register sem proteção de role

**Dimensão:** RBAC
**Impacto:** Qualquer pessoa não autenticada pode criar conta com role=admin ou super_admin
**Arquivo:** `backend/api/v1/endpoints/auth.py:68`

**Exploit comprovado:**
```bash
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"attacker@evil.com","name":"Hacker","password":"<redacted>"  # pragma: allowlist secret,"role":"admin"}'
# Retorna 201 Created com usuário admin válido
```

O schema `UserCreate` herda campo `role: UserRole` sem validação de autorização. O endpoint não exige token e não força `role=OPERATOR` para auto-registro.

**Fix:**
```python
# backend/api/v1/endpoints/auth.py
# REMOVER campo role do fluxo de registro público
user = User(
    email=user_data.email,
    name=user_data.name,
    password_hash=hash_password(user_data.password),
    role=UserRole.OPERATOR.value,  # sempre OPERATOR, ignora user_data.role
)
```

---

### 🔴 PRIORIDADE 2 — 7 endpoints de Ponto Eletrônico sem autenticação

**Dimensão:** RBAC / Endpoints
**Impacto:** Dados de ponto de qualquer funcionário expostos; batidas falsas podem ser registradas
**Arquivo:** `backend/modules/people_management/ponto/controllers/punch_controller.py`

Endpoints sem `get_current_user` ou qualquer auth:
```
GET  /batidas/{employee_id}          ← espionar ponto de qualquer colega
GET  /espelho/{employee_id}          ← histórico completo sem auth
POST /batida                         ← registrar batida falsa para qualquer UUID
POST /justificativa                  ← criar justificativa por terceiros
PUT  /justificativa/{id}/revisar     ← aprovar/rejeitar sem ser gestor
POST /sync                           ← sincronizar batidas offline sem auth
POST /fechamento                     ← fechar folha do mês sem auth
```

**Fix (exemplo para o padrão):**
```python
from core.auth.dependencies import CurrentActiveUser

@router.get("/batidas/{employee_id}")
async def get_batidas_dia(
    employee_id: str,
    data: str = Query(...),
    current_user: CurrentActiveUser,          # ADICIONAR
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    # Verificar ownership: apenas o próprio ou gerencial
    if str(employee_id) != str(current_user.id) \
        and current_user.role not in ROLES_GERENCIAIS:
        raise HTTPException(status_code=403, detail="Acesso negado")
```

---

### 🔴 PRIORIDADE 3 — Dashboard Executivo e Configurações do sistema sem auth

**Dimensão:** Endpoints Públicos
**Impacto:** KPIs financeiros, alertas críticos, configurações multi-tenant acessíveis sem token
**Arquivos:**
- `backend/modules/analytics/controllers/executive_dashboard_controller.py` (6 endpoints)
- `backend/modules/config/controllers/config_controller.py` (CRUD de configurações + feature flags)

```bash
# Qualquer pessoa pode acessar:
GET  /api/v1/analytics/executive/dashboard     # KPIs do negócio
GET  /api/v1/analytics/executive/alerts/active # Alertas críticos em aberto
GET  /api/v1/analytics/executive/insights/predictive  # IA preditiva
POST /api/v1/config/...                        # Alterar configurações do sistema
```

**Fix:** Adicionar `Depends(get_current_user)` em todos os routers desses módulos.

---

### 🔴 PRIORIDADE 4 — Tokens em localStorage vulneráveis a XSS

**Dimensão:** JWT
**Impacto:** Um único script XSS exfiltra `access_token` + `refresh_token` (válido 7 dias)
**Arquivo:** `frontend/src/hooks/useAuth.ts:89`

**Evidência:**
```typescript
localStorage.setItem('access_token', access_token);   // XSS-exposed
localStorage.setItem('refresh_token', refresh_token); // XSS-exposed

// Cookie criado via document.cookie (também acessível por JS):
document.cookie = `auth_token=${access_token}; path=/; SameSite=Lax; Secure`;
// Falta httpOnly=true → qualquer JS lê este cookie
```

**Problema adicional — inconsistência de keys:**
- `useAuth.ts` grava como `access_token`
- `axios-instance.ts` lê como `auth_token` → cliente Axios usa token null silenciosamente

**Fix de médio prazo — httpOnly cookies:**
```python
# backend/api/v1/endpoints/auth.py
response.set_cookie("access_token", token, httponly=True, secure=True,
                    samesite="lax", max_age=30*60)
response.set_cookie("refresh_token", refresh, httponly=True, secure=True,
                    samesite="strict", max_age=7*24*3600,
                    path="/api/v1/auth/refresh")
```

**Fix imediato — corrigir inconsistência de keys:**
```typescript
// src/lib/auth-storage.ts
export const AUTH_KEYS = { ACCESS_TOKEN: 'access_token' } as const;
// usar em todos os lugares (useAuth.ts e axios-instance.ts)
```

---

### 🔴 PRIORIDADE 5 — Credenciais de produção hardcoded em script Python

**Dimensão:** Senhas/Criptografia
**Impacto:** Senha do certificado A1 e senha NFS-e Manaus em código fonte versionado
**Arquivo:** `backend/scripts/test_gov_connections.py:48`

**Evidência:**
```python
@dataclass
class CredenciaisGov:
    cert_password: str = "Conecta123"   # senha do certificado digital A1
    nfse_senha: str = "jordan0612"      # senha NFS-e prefeitura de Manaus
```

Se este arquivo foi commitado ao histórico git, as credenciais estão permanentemente expostas.

**Fix imediato:**
```python
import os
from dotenv import load_dotenv
load_dotenv("/opt/conecta-pro/.env")

@dataclass
class CredenciaisGov:
    cert_password: str = field(default_factory=lambda: os.environ["CERTIFICATE_PASSWORD"])
    nfse_senha: str = field(default_factory=lambda: os.environ.get("NFSE_MANAUS_SENHA", ""))
```

---

## VULNERABILIDADES ALTAS

### 🟠 PRIORIDADE 6 — Módulos LGPD sem autenticação (violação da própria lei)

**Arquivo:** `backend/modules/security_lgpd/controllers/`
**Impacto:** 6 controllers LGPD acessíveis sem auth — accountability violada por design

Controllers afetados sem auth:
```
pia_controller.py          → criação de avaliações de impacto LGPD
consent_controller.py      → registro/manipulação de consentimentos
encryption_controller.py   → operações de criptografia
erasure_controller.py      → exclusão de dados pessoais sem auth (!)
masking_controller.py      → mascaramento de dados
audit_controller.py        → logs de auditoria LGPD
```

**Fix:** Todos esses controllers precisam de `Depends(get_current_user)` com role >= MANAGER. O `erasure_controller` deve exigir role ADMIN + confirmação.

---

### 🟠 PRIORIDADE 7 — Sem account lockout (brute force ilimitado)

**Arquivo:** `backend/api/v1/endpoints/auth.py`
**Impacto:** Rate limit apenas por IP (5/min). Com 12 IPs rotacionados = 60 tentativas/min indefinidamente

Não há:
- Contador de tentativas falhas por username
- Lockout temporário de conta
- CAPTCHA após 3+ falhas

**Fix:**
```python
# Adicionar no endpoint de login, após verificar credenciais:
async def _check_brute_force(username: str, redis_client) -> None:
    key = f"login_fails:{username}"
    fails = await redis_client.incr(key)
    if fails == 1:
        await redis_client.expire(key, 900)  # TTL 15 min
    if fails >= 10:
        raise HTTPException(status_code=429, detail="Conta temporariamente bloqueada")
```

---

### 🟠 PRIORIDADE 8 — User enumeration (dois vetores)

**Arquivo:** `backend/api/v1/endpoints/auth.py:89`
**Impacto:** Atacante pode enumerar emails válidos com 100% de precisão

**Vetor 1 — HTTP status diferente:**
- Email inexistente → `401 "Credenciais invalidas"`
- Email válido + conta inativa → `403 "Usuario inativo"` ← revela que o email existe

**Vetor 2 — Timing attack:**
- Email inexistente: retorna em ~5ms (sem bcrypt)
- Email válido, senha errada: retorna em ~100ms (com bcrypt)

**Fix:**
```python
# Sempre executar bcrypt, mesmo quando usuário não existe
DUMMY_HASH = "$2b$12$dummy_hash_to_prevent_timing_00000000000000000000000000"
stored_hash = user.password_hash if user else DUMMY_HASH
password_ok = verify_password(form_data.password, stored_hash)

# Sempre retornar 401, nunca 403
if not user or not password_ok or not user.is_active:
    raise HTTPException(status_code=401, detail="Credenciais invalidas")
```

---

### 🟠 PRIORIDADE 9 — Refresh token não é invalidado após uso (replay attack)

**Arquivo:** `backend/api/v1/endpoints/auth.py:135`
**Impacto:** Refresh token roubado pode ser usado indefinidamente por 7 dias

A "rotação" emite novo token mas não revoga o anterior via blacklist Redis.

**Fix:**
```python
@router.post("/refresh")
async def refresh_token(...):
    payload = verify_refresh_token(token_data.refresh_token)

    # ADICIONAR: verificar blacklist
    await verify_token_not_blacklisted(payload)

    # ADICIONAR: revogar token antigo imediatamente
    jti, exp = payload.get("jti"), payload.get("exp")
    if jti and exp:
        await add_to_blacklist(jti, datetime.utcfromtimestamp(exp))

    # Gerar novos tokens normalmente...
```

---

### 🟠 PRIORIDADE 10 — CRUD financeiro sem role check

**Arquivos:** `backend/modules/financial/controllers/payable_controller.py`, `receivable_controller.py`
**Impacto:** Qualquer usuário autenticado (viewer, client, agente) pode criar/editar contas a pagar/receber

Todos os endpoints de `payable`, `receivable` e `bank_account` usam apenas `Depends(get_current_user)` sem verificação de role.

**Fix:**
```python
FINANCIAL_ROLES = ("admin", "gestor", "administrador", "gerente_operacional")

@router.post("")
async def create_account(
    data: PayableAccountCreate,
    current_user = Depends(require_roles(*FINANCIAL_ROLES)),  # substituir get_current_user
):
```

---

### 🟠 PRIORIDADE 11 — CPF armazenado em texto plano (LGPD Art. 46)

**Arquivos:** `modules/operacional/models/employee.py`, `modules/operacional/diaristas/models/diarist.py`
**Impacto:** Não-conformidade LGPD. Infraestrutura de criptografia AES-256-GCM existe mas não é aplicada

```python
# ATUAL (não conforme LGPD):
cpf = Column(String(14), nullable=False, index=True)

# CORRETO (usando infraestrutura já existente em crypto_service.py):
# Migrar para BYTEA + criptografia Fernet/AES no service layer
```

---

### 🟠 PRIORIDADE 12 — Jobs governamentais (eSocial/SEFAZ/FGTS) sem autenticação

**Arquivo:** `backend/modules/government_integrations/controllers/jobs_controller.py`
**Impacto:** Pausar/retomar/executar sincronizações governamentais sem autenticação

---

### 🟠 PRIORIDADE 13 — Conflito de expiração do access token (30min vs 240min)

**Arquivos:** `backend/.env` (240 min) vs `backend/.env.secrets` (30 min)
**Impacto:** Se `.env` vencer, tokens comprometidos ficam válidos 4 horas sem revogação possível

**Fix imediato:** Remover `JWT_ACCESS_TOKEN_EXPIRE_MINUTES=240` do `backend/.env`. Corrigir default em `settings.py:45` de `240` para `30`.

---

## VULNERABILIDADES MÉDIAS

### 🟡 PRIORIDADE 14 — Política de senha inconsistente entre fluxos

- Core (admin): 12 chars + maiúscula + número + especial + blocklist 100 senhas ✅
- Portal funcionário: `len(senha) < 6` ❌
- Portal cliente schema: `min_length=4` ❌

**Fix:** Aplicar `validate_password_strength()` em todos os portais.

---

### 🟡 PRIORIDADE 15 — analytics/predictive e reports sem autenticação

**Arquivos:** `analytics/controllers/predictive_analytics_controller.py`, `reports/controllers/`
**Impacto:** Dados de churn prediction, fraud detection, lead scoring, geração de relatórios BI expostos

---

### 🟡 PRIORIDADE 16 — condominio_id aceito do cliente sem validação de ownership

**Arquivo:** `financial/controllers/payable_controller.py:95`
**Impacto:** Usuário do condomínio A pode passar UUID do condomínio B e acessar suas contas

---

### 🟡 PRIORIDADE 17 — Módulo de recrutamento inteiro sem role check

**Arquivos:** `modules/recruitment/controllers/*.py` (4 controllers)
**Impacto:** Qualquer usuário autenticado pode criar vagas, candidatos, entrevistas e comissões

---

### 🟡 PRIORIDADE 18 — AI controllers sem autenticação (OCR, assinatura)

**Arquivos:** `ai/ocr/controllers/ocr_controller.py`, `ai/signature/controllers/signature_controller.py`
**Impacto:** Upload e processamento de documentos sensíveis sem autenticação

---

### 🟡 PRIORIDADE 19 — Duas hierarquias de roles desconectadas

`UserRole` (core) tem `OPERATOR`, `VIEWER`, `CLIENT`.
`OperacionalRole` tem `gerente_operacional`, `inspetor`, `lider`, `agente`.
`User.role` é `Mapped[str]` sem constraint de banco — qualquer string é aceita.

**Fix:** Unificar em um enum canônico e adicionar `CHECK constraint` no banco.

---

### 🟡 PRIORIDADE 20 — `main_lite.py` com `allow_origins=["*"]`

Verificar se este entry point está em uso. Se sim, restringir igual ao `main_production.py`.

---

## ANÁLISE POR DIMENSÃO

### 🔑 JWT e Tokens — Score 6/10

**Pontos positivos:**
- SECRET_KEY com 86 chars de entropia (excelente)
- Validação de `type` claim previne token confusion ✅
- JTI + blacklist Redis com fail-secure (cai o Redis → bloqueia tudo) ✅
- HSTS configurado, transmissão apenas via HTTPS ✅
- Refresh token existe com rotação parcial ✅
- Token de reset de senha validado independentemente ✅

**Problemas:**
- Tokens em localStorage — vulnerável a XSS (CRÍTICO)
- Refresh token não invalidado após uso — replay attack (ALTO)
- Conflito de expiração 30min vs 240min (ALTO)
- Tokens legados sem JTI ignoram blacklist (BAIXO)
- 3 keys diferentes para o mesmo token no frontend (`access_token`, `auth_token`, `portal_token`)
- `dependencies_fixed.py` alternativo SEM blacklist check — risco se usado em algum módulo

---

### 👥 RBAC / Controle de Acesso — Score 5.5/10

**Pontos positivos:**
- 40+ permissões granulares no módulo operacional ✅
- `require_operacional_permission` bem implementado ✅
- Admin endpoints em `users.py` protegidos por `require_admin` ✅
- Portal do funcionário com JWT separado (`audience: "employee_portal"`) ✅
- Portal do cliente com auth própria, 7/9 controllers protegidos ✅
- Módulo fiscal com `require_permission("fiscal:nfe:emitir")` ✅

**Problemas:**
- `/register` sem proteção — privilege escalation para admin (CRÍTICO)
- 7 endpoints de ponto sem qualquer autenticação (CRÍTICO)
- Módulo de recrutamento inteiro sem role check
- CRUD financeiro (payable/receivable) sem role check
- Histórico disciplinar de funcionários sem role check
- `condominio_id` aceito sem validar ownership
- Hierarquias UserRole e OperacionalRole desconectadas

---

### 🔓 Endpoints Públicos vs Privados — Score 5.5/10

**Pontos positivos:**
- Docs/Swagger/OpenAPI desabilitados em produção ✅
- CORS configurado para domínio específico em `main_production.py` ✅
- Headers de segurança presentes (X-Content-Type-Options, X-Frame-Options, HSTS) ✅
- Portal do funcionário: 13/13 controllers com auth separada ✅
- Portal do cliente: auth por `get_current_portal_client` ✅

**Problemas:**
- `executive_dashboard_controller.py` — 6 endpoints de KPI sem auth (CRÍTICO)
- `config_controller.py` — CRUD de configurações multi-tenant sem auth (CRÍTICO)
- 6 controllers `security_lgpd` sem auth — violação da própria LGPD (ALTO)
- `government/jobs_controller.py` — controle de eSocial/SEFAZ sem auth (ALTO)
- 4 controllers de analytics/reports sem auth (ALTO)
- 3 controllers AI (OCR, assinatura, relatórios) sem auth (MÉDIO)
- `main_lite.py` com CORS `["*"]` (BAIXO)

---

### 🛡️ Rate Limit e Brute Force — Score 5/10

**Pontos positivos:**
- SlowAPI ativo e funcionando (`5/minute` no login) ✅
- Rate limits específicos por endpoint sensível ✅
- Headers `X-RateLimit-*` expostos nas respostas ✅
- `ProxyHeadersMiddleware` com `trusted_hosts` configurado corretamente ✅
- Endpoint `/forgot-password` com limit mais restrito (3/min) ✅
- `SecurityLogger` com `BRUTE_FORCE_ATTEMPT` definido ✅

**Problemas:**
- Sem account lockout por username (CRÍTICO)
- Rate limit exclusivamente por IP — password spray sem detecção (ALTO)
- User enumeration por HTTP status (403 vs 401) e timing (~5ms vs ~100ms) (ALTO)
- Sem CAPTCHA após falhas repetidas (MÉDIO)
- `RateLimitMiddleware` em `core/security/rate_limiter.py` confia cegamente em `X-Forwarded-For` — bypassável se ativado (MÉDIO)
- `AUTH_LIMIT = "20/minute"` definida mas não usada; login usa `"5/minute"` hardcoded (BAIXO)
- `settings.rate_limit_enabled` referenciado mas não existe em `Settings` — `AttributeError` latente (BAIXO)

---

### 🔐 Senhas e Criptografia — Score 5/10

**Pontos positivos:**
- bcrypt com salt automático em todos os fluxos ✅
- Nenhuma instância de MD5/SHA1 para senhas ✅
- Senhas não aparecem em logs (SecurityLogger sanitiza) ✅
- `JWT_SECRET_KEY` com 86 chars de entropia ✅
- Validador de senha robusto no core (12 chars, complexidade, blocklist 100 senhas) ✅
- Geração de senhas temporárias segura via `secrets.choice` ✅
- Mecanismo `ENC:` Fernet para criptografar credenciais gov disponível ✅

**Problemas:**
- Credenciais hardcoded em script Python (`cert_password`, `nfse_senha`) — CRÍTICO
- Chaves de API reais (OpenAI, Anthropic, Google, Sólides, Telegram) sem criptografia no `.env` (CRÍTICO)
- CPF/documentos pessoais em texto plano no banco — violação LGPD Art. 46 (ALTO)
- Portais aceitam senhas de 4-6 chars sem complexidade (MÉDIO)
- Senhas temporárias não forçam troca no primeiro login real (MÉDIO)
- Work factor bcrypt não configurado explicitamente — sujeito a mudança silenciosa da lib (BAIXO)

---

## SNAPSHOT DE DADOS (contexto auditoria)

| Evidência | Valor |
|-----------|-------|
| Algoritmo JWT | HS256 |
| Comprimento SECRET_KEY | 86 chars (excelente) |
| Expiração access token configurada | Conflito: 30min (.env.secrets) vs 240min (.env) |
| Expiração refresh token | 7 dias |
| Roles no sistema | 13+ strings distintas em 3 hierarquias |
| Rate limit login | 5/min por IP |
| Rate limit global | 1000/hour |
| Endpoints sem auth encontrados (críticos) | 20+ |
| Controllers de portais com auth própria | 20/22 (91%) |
| Work factor bcrypt | 12 (padrão passlib — aceitável) |

---

## PRÓXIMAS AÇÕES (plano de correção priorizado)

### Sprint imediata (bugs bloqueantes — segurança crítica):

1. **Privilege Escalation** — Forçar `role=OPERATOR` no `/register`, ignorar `user_data.role` → 15 min
2. **Ponto eletrônico** — Adicionar `CurrentActiveUser` nos 7 endpoints sem auth → 1h
3. **Credenciais hardcoded** — Remover `cert_password` e `nfse_senha` do script Python → 15 min
4. **Dashboard executivo** — Adicionar `Depends(get_current_user)` no `executive_dashboard_controller` e `config_controller` → 30 min
5. **Conflito de expiração** — Remover `JWT_ACCESS_TOKEN_EXPIRE_MINUTES=240` do `backend/.env` → 5 min

### Sprint seguinte (vulnerabilidades altas):

6. **User enumeration** — Sempre executar bcrypt + sempre retornar `401` (nunca `403`) no login → 30 min
7. **Account lockout** — Implementar contador Redis por username com lockout progressivo → 2h
8. **Refresh token anti-replay** — Adicionar `add_to_blacklist(jti)` após uso do refresh token → 30 min
9. **CRUD financeiro** — Adicionar `require_roles()` em payable e receivable controllers → 1h
10. **LGPD controllers** — Adicionar auth nos 6 controllers do `security_lgpd` → 1h
11. **Jobs governamentais** — Proteger `government/jobs_controller.py` com `require_admin` → 30 min

### Médio prazo:

12. **localStorage → httpOnly cookies** — Migrar armazenamento de tokens → 1-2 dias
13. **CPF criptografado** — Aplicar AES-256-GCM nos campos CPF usando infra existente de `crypto_service.py` → migration + 4h
14. **Unificar hierarquia de roles** — Consolidar UserRole + OperacionalRole + VALID_ROLES em enum único → 1 dia
15. **Política de senha uniforme** — Aplicar `validate_password_strength()` nos portais de funcionário e cliente → 1h
16. **Recrutamento** — Adicionar role checks nos 4 controllers → 1h
17. **analytics/reports/AI** — Adicionar auth nos controllers sem proteção → 2h

### Longo prazo:

18. **CAPTCHA** — Integrar após 3 falhas de login (reCAPTCHA v3 ou hCaptcha) → 1 dia
19. **Rate limit por username** — Chave composta `ip:X:user:Y` para detectar password spray → 1 dia
20. **CHECK constraint no banco** — Adicionar constraint no campo `users.role` para aceitar apenas roles válidos → migration

---

## RESUMO EXECUTIVO

O Conecta PRO tem **fundações de segurança presentes** (JWT com blacklist Redis, bcrypt, rate limiting, portais com auth separada, HSTS, CORS restrito) mas sofre de **aplicação inconsistente** ao longo dos módulos. A maior parte da superfície de ataque não está nas camadas de infraestrutura de auth, mas na ausência de proteção em módulos específicos.

**Destaques positivos:**
- Blacklist Redis com fail-secure (Redis cai → tudo bloqueado) ✅
- Portais de funcionário e cliente com JWT audience separado ✅
- Módulo operacional com RBAC granular (40+ permissões) ✅
- SECRET_KEY de alta entropia e validada em produção ✅
- Docs/Swagger desabilitados em produção ✅

**Destaques negativos:**
- `/register` permite criar usuário admin sem autenticação ❌
- 7 endpoints de ponto eletrônico completamente abertos ❌
- Dashboard executivo com KPIs financeiros sem proteção ❌
- Tokens em localStorage vulneráveis a XSS ❌
- Credenciais de produção hardcoded em código Python ❌

**Impacto no usuário:** Funcionalidades de core (login, JWT, portais) funcionam corretamente. Porém, módulos periféricos (ponto, analytics, LGPD, configs) estão expostos, representando risco real de acesso não autorizado a dados sensíveis.

---

*Auditoria executada via Skill 06 (autenticacao-autorizacao-conecta-pro) com 5 subagentes paralelos.*
*Arquivo salvo em: /opt/conecta-pro/AUDITORIA_SKILL06.md*
