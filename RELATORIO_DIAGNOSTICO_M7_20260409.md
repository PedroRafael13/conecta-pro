# Relatório de Diagnóstico M7 — Contrato de Trabalho e Aviso Prévio
**Data:** 2026-04-09
**Branch:** feature/people-management-reorganization
**Executado por:** Claude Code (session tmux-t1)

---

## Status de Execução do Script de Diagnóstico

| Seção | Comando | Status | Observação |
|-------|---------|--------|-----------|
| TEMPLATES EXISTENTES | `find $BACKEND -name "*.py" -o -name "*.docx" ...` | ✅ OK | Executado completo |
| ENDPOINTS EXISTENTES | `grep -rn "@router\." ...` | ✅ OK | Executado completo |
| MODELOS/SERVIÇOS RH | `find ... xargs grep -l ...` | ✅ OK | Executado completo |
| TABELAS NO BANCO | `docker exec ... psql ...` | ⚠️ → ✅ | 1ª tentativa falhou: `docker ps \| grep postgres \| awk '{print $NF}'` retornou vazio. Corrigido: container é `conecta-pro-postgres` |
| FRONTEND PAGES RH | `find $FRONTEND/app -name "*.tsx" ...` | ✅ OK | Executado completo |
| ENUM DocumentType | `grep -rn "contrato\|aviso_previo\|ferias..."` | ⚠️ → ✅ | 1ª tentativa vazia: pattern multiline com `\` + espaços no shell produziu regex inválido. Corrigido com pattern numa linha |

---

## Resultados Completos por Seção

### 1. TEMPLATES EXISTENTES

Templates relevantes encontrados (excluindo venv/htmlcov):

```
backend/modules/bidding/templates/carta_proposta.docx
backend/modules/bidding/templates/declaracao_me_epp.docx
backend/modules/bidding/templates/declaracao_menor.docx
backend/modules/bidding/templates/proposta_comercial.docx
backend/modules/comercial/contratos/__init__.py              ← stub vazio
backend/modules/pessoas/departamento_pessoal/contrato_trabalho/__init__.py  ← stub vazio
backend/modules/pessoas/departamento_pessoal/ferias/__init__.py             ← stub vazio
backend/modules/operacional/models/scale_template.py
backend/modules/operacional/services/scale_template_service.py
backend/modules/operacional/disciplinary/models/disciplinary_template.py
backend/modules/operacional/disciplinary/services/template_service.py
backend/modules/ai/ocr/models/document_template.py
backend/modules/ai/report_generator/services/template_engine.py
backend/modules/ai/signature/models/signature_template.py
```

**Observação:** Não há nenhum arquivo `.docx`, `.html` ou `.jinja2` para contrato de trabalho ou aviso prévio CLT. Os templates de contratos trabalhistas existem apenas na tabela `contract_templates` do banco (texto puro com variáveis).

---

### 2. ENDPOINTS EXISTENTES — Contratos/Férias/Aviso

Endpoints de contrato de trabalho (`/people-management/hr/contracts`):
```
GET    /contracts                          — lista paginada todos os contratos
GET    /contracts/employee/{id}            — histórico de um funcionário
GET    /contracts/employee/{id}/current    — contrato vigente
POST   /contracts                          — criar novo contrato
GET    /contracts/{id}                     — detalhe
PATCH  /contracts/{id}                     — atualizar
POST   /contracts/{id}/document            — gerar dados do documento
```

Endpoints de férias (`/people-management/hr/vacations`):
```
GET    /vacations                          — lista paginada
GET    /vacations/employee/{id}            — por funcionário
POST   /vacations                          — criar solicitação
PATCH  /vacations/{id}/approve             — aprovar (DP)
PATCH  /vacations/{id}/reject              — rejeitar
GET    /vacations/{id}/balance             — saldo de férias do funcionário
```

Endpoints de rescisão/aviso prévio (`/people-management/hr/terminations`):
```
GET    /terminations                       — lista
POST   /terminations                       — abrir processo de rescisão
GET    /terminations/{id}                  — detalhe
PATCH  /terminations/{id}                  — atualizar (inclui notice_period_days)
POST   /terminations/{id}/calculate        — calcular verbas rescisórias
POST   /terminations/{id}/complete         — concluir processo
```

Outros (operacional):
```
POST   /cct/ferias                         — via módulo CCT
GET    /operacional/ferias (aliases)       — re-export
```

---

### 3. TABELAS NO BANCO

| Tabela | Descrição | Colunas Relevantes |
|--------|-----------|-------------------|
| `employment_contracts` | Contratos de trabalho | type, start_date, end_date, base_salary, work_schedule, weekly_hours, hazard_pay_percent, unhealthy_pay_percent, is_current, document_path, signed_at |
| `contract_templates` | Templates de texto contratual | name, service_type, content_template (TEXT), clauses (JSONB), variables (JSONB), approved_by_legal |
| `termination_processes` | Rescisão + Aviso Prévio | type, notice_period_days, notice_start_date, last_working_day, status, severance_amount, fgts_amount, total_amount, documents_generated (JSONB) |
| `vacation_requests` | Férias (operacional, simples) | type, status, start_date, end_date, days, approved_by |
| `hr_vacation_requests` | Férias (DP, completo) | condominio_id, period_id, sell_days, advance_13th, gross_value, net_value, calculation_details, manager_approved, hr_approved |
| `hr_vacation_periods` | Períodos aquisitivos | — |

---

### 4. FRONTEND PAGES RH

| Arquivo | Descrição | Estado |
|---------|-----------|--------|
| `dp/contratos/page.tsx` | Gestão de contratos de trabalho | ✅ Completa: lista, cria, edita, "gerar documento" |
| `dp/ferias/layout.tsx` | Layout férias DP | ✅ |
| `dp/ferias/page.tsx` | Gestão de férias (aprovar/rejeitar) | ✅ Completa |
| `portal-funcionario/ferias/page.tsx` | Portal do funcionário — férias | ✅ |
| `operacional/ferias/page.tsx` | Férias operacional | ✅ |
| `portal/ferias/page.tsx` | Portal cliente — férias | ✅ |

**Ausente:** Não há `dp/aviso-previo/page.tsx` separado. O aviso prévio é gerenciado dentro da tela de rescisão.

---

### 5. ENUM DocumentType — o que existe

| Módulo | Enum/Valor | Localização |
|--------|-----------|-------------|
| `documents/models/document.py` | `CONTRATO_TRABALHO = "contrato_trabalho"` | DocumentType enum |
| `documents/models/document.py` | `FERIAS = "ferias"` | DocumentType enum |
| `documents/models/document.py` | `CONTRATO = "contrato"` | DocumentType enum |
| `ged/models/document.py` | `CONTRATO = "contrato"` | DocumentType enum |
| `ged/models/folder.py` | `CONTRATO = "contrato"` | FolderType enum |
| `operacional/diaristas/models/diarist.py` | `FERIAS = "ferias"` | StatusEnum |
| `fase5/cct_compliance/enums.py` | `FERIAS = "ferias"` | EventType |
| `hr/time_tracking/models/work_schedule.py` | `FERIAS = "ferias"` | AbsenceType |

**Ausente:** Nenhum enum tem `AVISO_PREVIO` como DocumentType. O aviso prévio é tratado como campo numérico (`notice_period_days`) no `TerminationProcess`.

---

## Mapa de Implementação — Completo vs Faltante

### Contrato de Trabalho

| Componente | Estado |
|-----------|--------|
| Model `EmploymentContract` | ✅ Completo |
| Tabela `employment_contracts` | ✅ Existe no banco |
| CRUD service + controller | ✅ 7 endpoints funcionais |
| Frontend `dp/contratos/page.tsx` | ✅ Completo |
| Tabela `contract_templates` | ✅ Existe com conteúdo |
| **Geração real de PDF/DOCX** | ❌ AUSENTE — `generate_contract_document()` retorna dict JSON, não arquivo |
| **Uso da tabela `contract_templates`** | ❌ AUSENTE — tabela existe mas nenhum service a lê para preencher o documento |
| Publicação de evento `contrato_criado` | ✅ `publish_contrato_criado()` chamado no controller |

### Férias

| Componente | Estado |
|-----------|--------|
| Tabela `vacation_requests` (operacional) | ✅ |
| Tabela `hr_vacation_requests` (DP completo) | ✅ |
| `calcular_ferias()` no clt_calculator | ✅ |
| Service + Controller de férias | ✅ |
| Frontend DP + Portal | ✅ |
| **Rota duplicada** | ⚠️ `VacationController` inclui o router operacional → `/hr/vacations/vacations/` |
| **Fragmentação de tabelas** | ⚠️ Dois modelos paralelos sem unificação (`vacation_requests` vs `hr_vacation_requests`) |

### Aviso Prévio

| Componente | Estado |
|-----------|--------|
| Campos no `TerminationProcess` | ✅ `notice_period_days`, `notice_start_date`, `last_working_day` |
| `calcular_aviso_previo_dias()` (art. 487 CLT) | ✅ 30d + 3d/ano, máx 90d |
| Cálculo incluso em `calcular_rescisao()` | ✅ `aviso_previo_indenizado`, `aviso_previo_dias` |
| Controller de rescisão com aviso | ✅ |
| **Endpoint dedicado `/aviso-previo/`** | ❌ AUSENTE — aviso prévio só existe dentro da rescisão |
| **Frontend dedicado `dp/aviso-previo/`** | ❌ AUSENTE |
| **Fluxo trabalhado vs indenizado** | ⚠️ Calculado mas sem tela de acompanhamento do período de aviso trabalhado |

---

## Stubs Vazios (legado da reorganização)

```
backend/modules/pessoas/departamento_pessoal/contrato_trabalho/__init__.py  — vazio
backend/modules/pessoas/departamento_pessoal/ferias/__init__.py             — vazio
backend/modules/comercial/contratos/__init__.py                             — vazio
```

Não causam erro, mas indicam módulos não implementados na estrutura `pessoas/`.

---

## GAPs Ordenados por Impacto

| # | GAP | Impacto | Esforço |
|---|-----|---------|---------|
| 1 | Geração real de PDF para contrato de trabalho (usar `contract_templates`) | Alto | Médio |
| 2 | Tela dedicada de Aviso Prévio (`dp/aviso-previo/`) com fluxo trabalhado/indenizado | Alto | Médio |
| 3 | Rota duplicada `/hr/vacations/vacations/` | Médio | Baixo |
| 4 | Unificação dos dois modelos de férias | Médio | Alto |
| 5 | Stubs vazios em `pessoas/departamento_pessoal/` | Baixo | Baixo |

---

## Conclusão

O script de diagnóstico foi executado **100%** (todas as 6 seções), com 2 correções aplicadas (container postgres e pattern grep).

O M7 tem a **base implementada** (models, tabelas, CRUD, frontend) mas possui **2 GAPs de funcionalidade relevante**: geração de documento de contrato real (PDF/DOCX a partir da tabela `contract_templates`) e tela dedicada de Aviso Prévio com acompanhamento de período trabalhado vs indenizado.
