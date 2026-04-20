# RELATÓRIO — FASE 4 BLOCO 3 §27: Contrato de API (Pioneiro)
**Data:** 2026-04-20
**Agente:** Engenheiro Backend Sênior — FASE 4 BLOCO 3 PIONEIRO
**Branch:** feature/people-management-reorganization
**Commit §27:** `2444299c` | **Commit auditoria 1:** `e196c5b2` | **Commit auditoria 2:** `(ver abaixo)`

---

## 1. STEP 0 — Pré-voo

**Versão contrato:** 1.22 (lida no início) → 1.23 (após este commit)

**Princípios citados:**
- §13.1 Chesterton: validar KitBuilderService v1.22 ANTES de escrever §27
- §13.3 Docs antes de código: §27 commitado ANTES de T2 e T3
- §13.4 Escopo sagrado: APENAS §27 no Contrato. ZERO código Python. 1 commit único.

**Em 3 linhas:**
Escrever §27 do CONTRACTS_GEDEON.md com contrato compartilhado entre T2 (endpoints FastAPI)
e T3 (dashboard Next.js). §27 inclui URLs, response JSON literal, schemas Pydantic, UI spec
com cores/modal, error handling e 10 testes de integração. Pioneiro — T2 e T3 dependem deste.

**Verificações STEP 0:**
```
Versão contrato: **Versão:** 1.22  ✅
§26 presente: ## §26 — FASE 4 BLOCO 3 / T1 — KitBuilderService  ✅
git log: 4299b4bc docs(gedeon): relatório T1 BLOCO3 [HEAD]
```

---

## 2. STEP 1 — Investigações H1-H7 (outputs reais)

### 1.1 — Convenção de URL (H1)
```
api_router = APIRouter(prefix="/api/v1")  [main_production.py:305]
router = APIRouter(prefix="/gedeon", tags=["GEDEON"])  [gedeon_controller.py:22]
→ /api/v1/gedeon + /kits/... = /api/v1/gedeon/kits/...

Existentes:
  @router.get("/kits/status")  → /api/v1/gedeon/kits/status
  @router.get("/kits/config")  → /api/v1/gedeon/kits/config
```
**Resultado CENÁRIO B:** prompt sugeria `/gedeon/kit/` (singular) mas padrão real usa
`/gedeon/kits/` (plural). §27 ajustado para `/gedeon/kits/completude/{id}` e
`/gedeon/kits/lote`. ✅

### 1.2 — Auth pattern (H2)
```
backend/modules/gedeon/controllers/gedeon_controller.py:
  from core.auth.dependencies import get_current_user
  current_user=Depends(get_current_user)  [linhas 44, 66, 94, 110, 132, ...]
```
**Resultado:** `from core.auth.dependencies import get_current_user` + `Depends(get_current_user)` ✅

### 1.3 — Pydantic version (H3)
```
requirements.txt: pydantic==2.10.4
docker exec: Name: pydantic / Version: 2.10.4
```
**Resultado:** Pydantic v2 confirmado → usar `BaseModel`, `ConfigDict(from_attributes=True)` ✅

### 1.4 — Router gedeon (H4)
```
Pasta: backend/modules/gedeon/controllers/  (não routers/)
gedeon_controller.py  → prefix="/gedeon"
onvio_controller.py   → prefix="/onvio"
Sem subpasta schemas/  → T2 cria backend/modules/gedeon/schemas/kit_completude.py
```
**Resultado:** router em controllers/, T2 cria kit_controller.py em controllers/ ✅

### 1.5 — Error handling (H5)
```
onvio_controller.py:
  raise HTTPException(status_code=500, detail=str(exc))  [linhas 123, 275, 303]
```
**Resultado:** `raise HTTPException(status_code=XXX, detail=str(exc))` é o padrão ✅

### 1.6 — §26 do contrato (H6)
```
grep "Versão:" → **Versão:** 1.22  ✅
grep "^## §26" → ## §26 — FASE 4 BLOCO 3 / T1 — KitBuilderService  ✅
§26.2 tem DTOs @dataclass corretos
§26.5 tem performance confirmada (9.6ms, 0.07s)
```
**Resultado:** §26 v1.22 presente e correto ✅

### 1.7 — KitBuilderService interface exata (§13.1 Chesterton)
```
CategoriaToTipoDocumento: dict[str, str] = {   # 20 entradas
TIPOS_DOCUMENTO_AGUARDA_FASE_1_CND: frozenset[str]
TIPOS_DOCUMENTO_AGUARDA_FASE_2_BANCO: frozenset[str]
TIPOS_DOCUMENTO_SEM_SINCRONIZACAO: frozenset[str]
@dataclass class DocumentoPresente
@dataclass class DocumentoFaltante
@dataclass class MetricasKit
@dataclass class CompletudeKit
def _validate_mes_ref(mes_ref: str) -> None
def _determinar_motivo_faltante(tipo_documento: str) -> str
class KitBuilderService:
    def __init__(self, db: Session) -> None
    def build_completude(self, condominio_id: UUID, mes_ref: str) -> CompletudeKit
    def build_lote_condominios(self, mes_ref: str) -> list[CompletudeKit]
```
**Resultado:** interface completa catalogada ✅

---

## 3. STEP 2 — §27 adicionado (excerto)

**Versão:** 1.22 → 1.23
**Seção adicionada:** §27 com 9 subseções (§27.1 a §27.9)

```markdown
## §27 — FASE 4 BLOCO 3 / CONTRATO DE API (endpoints + dashboard)
**Status:** PIONEIRO — T2 e T3 consomem este §27 em paralelo

### §27.1 — Escopo
  Endpoint 1: GET /api/v1/gedeon/kits/completude/{condominio_id}
  Endpoint 2: GET /api/v1/gedeon/kits/lote

### §27.2 — URL + Método + Autenticação
  from core.auth.dependencies import get_current_user
  Depends(get_current_user) em ambos os endpoints

### §27.3 — Parâmetros
  condominio_id (path, UUID), mes_ref (query, ^(0[1-9]|1[0-2])\.d{4}$)

### §27.4 — Response Schema (JSON LITERAL 19 campos)
  { "condominio_id", "condominio_nome", "tipo_servico", "mes_ref",
    "gerado_em", "docs_presentes": [...], "docs_faltantes": [...],
    "metricas": { 6 campos } }

### §27.5 — Error Handling (400/401/404/422/500 + padrão ValueError→HTTPException)
### §27.6 — Pydantic Schemas (4 classes + helper dataclasses.asdict)
### §27.7 — Dashboard UI (componentes, cores, modal, tradução motivos)
### §27.8 — 10 testes T2 + 6 testes T3
### §27.9 — Próximo passo após T2+T3
```

**Contagem de subseções:** 9 (§27.1 a §27.9) ✅
**Exemplo JSON literal:** presente no §27.4 ✅
**UI spec completa:** §27.7 com cores hex+tailwind, modal tabs, tradução PT-BR ✅

---

## 4. STEP 3 — Validações Chesterton (5/5 PASS)

### 3.1 — CompletudeKit fields 1:1 com §27.4
```
condominio_id: UUID          ✅ = json.condominio_id
condominio_nome: str         ✅ = json.condominio_nome
tipo_servico: str            ✅ = json.tipo_servico
mes_ref: str                 ✅ = json.mes_ref
docs_presentes: list[...]    ✅ = json.docs_presentes
docs_faltantes: list[...]    ✅ = json.docs_faltantes
metricas: MetricasKit | None ✅ = json.metricas
gerado_em: datetime          ✅ = json.gerado_em (ISO8601)
```
8/8 campos ✅

### 3.2 — MetricasKit fields 1:1 com §27.4
```
total_esperado: int                    ✅
total_presente_confirmado: int         ✅
total_presente_pendente_revisao: int   ✅
total_faltante: int                    ✅
pct_completude_confirmada: float       ✅
pct_completude_total: float            ✅
```
6/6 campos ✅

### 3.3 — Motivos faltantes batem?
```
return "aguarda_fase_1_cnd"    ✅ = §27.4 motivo
return "aguarda_fase_2_banco"  ✅ = §27.4 motivo
return "nao_sincronizado"      ✅ = §27.4 motivo
return "nao_encontrado_onvio"  ✅ = §27.4 motivo
```
4/4 motivos ✅

### 3.4 — Auth decorator confirmado
```
from core.auth.dependencies import get_current_user  [linha 13]
router = APIRouter(prefix="/gedeon")  [linha 22]
→ §27.2 cita exatamente esse import e decorator ✅
```

### 3.5 — Sem conflito com rotas existentes
```
Existentes: /kits/status, /kits/config
Novas:      /kits/completude/{id}, /kits/lote
→ Zero conflito ✅
```

**5/5 validações Chesterton PASS** ✅

---

## 5. STEP 4 — Commit

```
hash: 2444299c
docs(gedeon): CONTRATO v1.23 — §27 Contrato de API (pioneiro BLOCO 3)
1 file changed, 287 insertions(+), 1 deletion(-)
push: 61035824..2444299c → origin/feature/people-management-reorganization  ✅
```

---

## 6. Self-check 10/10

| # | Item | Status |
|---|------|--------|
| 1 | STEP 0 — contrato v1.22 lido + princípios §13.1/§13.3/§13.4 citados | ✅ |
| 2 | STEP 1 — 7 sub-investigações (H1-H6 + kit service interface) | ✅ |
| 3 | STEP 2 — §27 adicionado com 9 subseções (§27.1 a §27.9) | ✅ |
| 4 | STEP 2 — CHANGELOG incrementado v1.22 → v1.23 | ✅ |
| 5 | STEP 3 — 5 validações Chesterton executadas (campos batem 1:1 com KitBuilderService v1.22) | ✅ |
| 6 | STEP 4 — 1 único commit (docs) push OK, hash `2444299c` | ✅ |
| 7 | Zero código Python criado neste prompt | ✅ |
| 8 | Zero toques em zonas proibidas | ✅ |
| 9 | §27.4 tem exemplo JSON LITERAL (não descrição) | ✅ |
| 10 | §27.7 tem spec UI completa (componentes + cores hex/tailwind + modal + tradução motivos) | ✅ |

---

## 7. Cenário Identificado

**CENÁRIO B aplicado no STEP 1:** URL pattern era `/gedeon/kit/` (singular) no prompt,
mas investigação H1 revelou que padrão real usa `/gedeon/kits/` (plural) — confirmado por
`@router.get("/kits/status")` e `@router.get("/kits/config")` no gedeon_controller.py.
§27 ajustado para `/gedeon/kits/completude/{id}` e `/gedeon/kits/lote` antes do commit.

**Resultado final: CENÁRIO A — 10/10** ✅

---

## 8. Conclusão

### §27 COMMITADO — LIBERAR T2 + T3 EM PARALELO

**T2 (endpoints FastAPI):** criar `kit_controller.py` + `schemas/kit_completude.py`,
importar `KitBuilderService`, expor `/kits/completude/{id}` e `/kits/lote` conforme §27.

**T3 (dashboard Next.js):** criar página `/modulos/gestao-pessoas/ged/kits`,
consumir endpoint /lote para grid de cards, /completude/{id} para modal,
aplicar cores por faixa % e traduzir motivos para PT-BR conforme §27.

Ambos citam `CONTRACTS_GEDEON.md §27` como única fonte de verdade.

---

## 9. Auditorias pós-entrega

### Auditoria 1 (e196c5b2)
Gap: §27.7 traduções de `motivo` divergiam do prompt.
- `nao_encontrado_onvio`: "Não encontrado no Onvio" → **"Não sincronizado do Onvio"** ✅
- `nao_sincronizado`: "Tipo sem sincronização configurada" → **"Não sincronizado"** ✅
CONTRATO: v1.23 → v1.24

### Auditoria 2 (ver commit final)
Gap: §27.7 labels das tabs do modal divergiam do prompt.
- "Presentes" | "Faltantes" → **"Docs Presentes" | "Docs Faltantes"** ✅
CONTRATO: v1.24 → v1.25

**Self-check pós-auditorias: 10/10 — PROMPT 100% IMPLEMENTADO** ✅
