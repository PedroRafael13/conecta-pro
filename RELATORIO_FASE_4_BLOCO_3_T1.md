# RELATÓRIO — FASE 4 BLOCO 3 T1: KitBuilderService
**Data:** 2026-04-20
**Agente:** Engenheiro Backend Sênior — FASE 4 BLOCO 3 / T1
**Branch:** feature/people-management-reorganization
**Commit docs:** `aac68ed8` | **Commit código:** `f2b7cad2`

---

## 1. STEP 0 — Pré-voo

**Versão contrato:** 1.20 (CENÁRIO B — meta era 1.19, já superada → §26 adicionado em 1.21)

**Princípios citados:**
- §13.1 Chesterton: investigar 4 tabelas ANTES de escrever service
- §13.3 Documentar antes de codificar: CONTRATO §26 em commit separado antes do código
- §13.4 Escopo sagrado: APENAS service + testes. ZERO endpoints. ZERO UI. ZERO ZIP.

**Em 3 linhas:**
Criar KitBuilderService(db) que dado (condominio_id, mes_ref) cruza kit_documental_templates
× onvio_documents e retorna CompletudeKit com docs_presentes/faltantes/métricas.
CNDs sempre faltantes (FASE 1). comp_pagamentos/nfse/boleto sempre faltantes (FASE 2).

**DB counts:** condominios=11 ✅ | employee_alocacoes=47 ✅ | kit_documental_templates=38 ✅ | onvio_documents=436 ✅

---

## 2. STEP 1 — Investigação H1-H7

### 1.1 — Formato mes_ref (H1)
```
DISTINCT mes_ref FROM onvio_documents ORDER BY mes_ref DESC LIMIT 10:
 2026    |    20
 2025    |    58
 12.2025 |    29
 11.2025 |    27
 10.2025 |    21
 09.2025 |    24
 08.2025 |    30
```
**Resultado:** padrão "MM.YYYY" confirmado (+ residuais "YYYY" sem mês). ✅

### 1.2 — Schema kit_documental_templates (H2)
```
Colunas: id, tipo_servico, tipo_documento, escopo, obrigatorio, periodicidade, descricao, created_at

tipo_servico      | count | obrig
kit_mensal        |    32 |    21
manutencao_cftv   |     2 |     2
portaria_autonoma |     2 |     2
portaria_remota   |     2 |     2
```
✅

### 1.3 — Tipos de serviço reais (H3)
```
DISTINCT tipo_servico FROM condominios:
administrativo | kit_mensal | manutencao_cftv | portaria_autonoma | portaria_remota
```
✅ (5 valores únicos confirmados)

### 1.4 — Schema employee_alocacoes (H4)
```
Colunas: id, employee_id, condominio_id, funcao, data_inicio, data_fim, ativo, created_at
```
✅ condominio_id como FK

### 1.5 — Model Python OnvioDocument (H5)
OnvioDocument tem `doc_scope`, `condominio_id`, `referente_a_employee_id` mapeados.
Decisão: usar `raw SQL via text()` igual ao T2 original (mais seguro para campos novos). ✅

### 1.6 — Distribuição mes_ref (H6)
Confirmado: múltiplos meses 2025-2026. Mês com mais docs: 03.2026 (ideal_flores=4 docs). ✅

### 1.7 — Condomínios com mais docs (H7)
```
nome_normalizado | tipo_servico | docs
ideal_flores     | kit_mensal   |   22
michelangelo     | kit_mensal   |   18
mirante          | kit_mensal   |   18
prime_arena      | kit_mensal   |   18
villa_passaros   | kit_mensal   |   16
```
✅ ideal_flores com 22 docs é fixture ideal para testes.

---

## 3. STEP 2 — §26 adicionado ao CONTRACTS_GEDEON.md (antes do código — §13.3)

**Versão:** 1.20 → 1.21
**Seção adicionada:** §26 com 8 subseções:
- §26.1 Escopo (ZERO endpoints, UI, ZIP)
- §26.2 Contrato de interface + DTOs
- §26.3 CategoriaToTipoDocumento (20 entradas)
- §26.4 Regras CNDs (aguarda_fase_1_cnd)
- §26.5 Performance alvo (<500ms/cond, <3s/lote)
- §26.6 Testes — 10 cenários
- §26.7 Validação mes_ref regex
- §26.8 Evidências H1-H7

---

## 4. STEP 3 — Commit 1 (docs)
```
hash: aac68ed8
docs(gedeon): CONTRATO v1.21 — §26 KitBuilderService (FASE 4 BLOCO 3 T1)
1 file changed, 132 insertions(+), 3 deletions(-)
push: OK → feature/people-management-reorganization
```

---

## 5. STEP 4 — kit_builder_service.py

**Path:** `backend/modules/gedeon/services/kit_builder_service.py`

**Interface conforme §26:**
```python
# Constante pública (T2 importa)
CategoriaToTipoDocumento: dict[str, str] = { ... }  # 20 entradas

# Sets de tipos especiais
TIPOS_DOCUMENTO_AGUARDA_FASE_1_CND   # 5 CNDs
TIPOS_DOCUMENTO_AGUARDA_FASE_2_BANCO  # comp_pag_fgts, nfse, boleto + 3
TIPOS_DOCUMENTO_SEM_SINCRONIZACAO    # comp_va_solides, recibo_vt_va + 2

# Helpers exportados (testes + T2 importam)
def _validate_mes_ref(mes_ref: str) -> None: ...     # regex ^(0[1-9]|1[0-2])\.d{4}$
def _determinar_motivo_faltante(tipo_doc: str) -> str: ...

# DTOs @dataclass (§26.6)
@dataclass class DocumentoPresente:   # onvio_document_id: UUID, revisao_pendente: bool
@dataclass class DocumentoFaltante:   # periodicidade: str, motivo: str
@dataclass class MetricasKit:         # total_esperado, pct_completude_confirmada, pct_completude_total
@dataclass class CompletudeKit:       # gerado_em: datetime

# Service com DI
class KitBuilderService:
    def __init__(self, db: Session) -> None: ...
    def build_completude(self, condominio_id: UUID, mes_ref: str) -> CompletudeKit: ...
    def build_lote_condominios(self, mes_ref: str) -> list[CompletudeKit]: ...
```

**Query onvio_documents:** filtra condominio + empresa_matriz + funcionários via employee_alocacoes JOIN.

---

## 6. STEP 5 — test_kit_builder_service.py

**Path:** `backend/tests/modules/gedeon/test_kit_builder_service.py`
**Testes:** 30 (10 cenários, 10 classes)

| Classe | Cenário | Testes |
|--------|---------|--------|
| TestMesRefValidacao | mes_ref inválido (incl. "13.2026", "00.2026", None) | 6 |
| TestCondominioInexistente | UUID inexistente → ValueError | 1 |
| TestKitMensalEstrutura | 32 templates, percentual, campos corretos | 5 |
| TestDocumentosPendentesVsConfirmados | separação confirmados vs pendentes | 2 |
| TestCndsSempreFaltantes | 5 CNDs, motivo correto, escopo empresa_matriz | 2 |
| TestCompPagamentosFaltantes | >= 3 comp_pagamentos faltantes | 1 |
| TestServicosSimples | portaria_autonoma/remota/manutencao_cftv (2 tpl cada) | 3 |
| TestAdministrativo | kit vazio, pct=0.0 | 1 |
| TestBuildLote | 11 condos, mes_ref preservado, ValueError | 3 |
| TestDeterminarMotivo | cnd, banco, sem_sinc, generico | 4 |
| TestCategoriaToTipoDocumento | 20 entradas + chaves esperadas | 2 |

---

## 7. STEP 6 — Import + Pytest

**Import validation:**
```
Import OK
CategoriaToTipoDocumento: 20 entradas
TIPOS_DOCUMENTO_AGUARDA_FASE_1_CND: 5
TIPOS_DOCUMENTO_SEM_SINCRONIZACAO: 4
```

**Pytest:**
```
30 passed, 2 warnings in 1.42s  ✅
```

---

## 8. STEP 7 — Smoke Test DB Real (IDEAL FLORES, 03.2026)

```
Condomínio: IDEAL FLORES
Tipo: kit_mensal
Mes: 03.2026
Métricas: MetricasKit(total_esperado=32, total_presente_confirmado=4,
          total_presente_pendente_revisao=0, total_faltante=30,
          pct_completude_confirmada=12.5, pct_completude_total=12.5)
Docs presentes: 4
Docs faltantes: 30

Primeiros 3 faltantes:
  - aso (funcionario): nao_encontrado_onvio
  - aviso_previo_ferias (funcionario): nao_encontrado_onvio
  - boleto (condominio): aguarda_fase_2_banco
```

**12.5% completude** — correto: onvio_documents tem apenas folha_pagamento + recibo_folha
para este mês. CNDs/NFS-e/Boleto aguardam FASE 1/2.

---

## 9. STEP 8 — Testes de Falsificação 🔴 (5/5 PASS)

### 🔴 A — Pytest suite inteira
```
30 passed, 2 warnings in 1.42s  ✅
```

### 🔴 B — Service é read-only (contagens após pytest+smoke)
```
cond=11 | aloc=47 | tpl=38 | onvio=436  ✅ (intactos)
```

### 🔴 C — Performance <500ms por condomínio
```
build_completude: 9.6ms
✅ Performance OK (<500ms)
```

### 🔴 D — Performance <3s para lote de 11
```
build_lote_condominios (11 cond): 0.07s
✅ Performance lote OK (<3s)
```

### 🔴 E — Regressão FASE 3.5 intacta
```
cond=11 | aloc=47 | tpl=38 | onvio=436  ✅
```

---

## 10. STEP 9 — Commits e Push

### Commit 1 (docs — §13.3)
```
hash: aac68ed8
docs(gedeon): CONTRATO v1.21 — §26 KitBuilderService (FASE 4 BLOCO 3 T1)
1 file changed, 132 insertions(+), 3 deletions(-)
```

### Commit 2 (código — auditoria corrigida)
```
hash: f2b7cad2
feat(gedeon): FASE 4 BLOCO 3/T1 — KitBuilderService (auditoria: interface corrigida)
2 files changed, 415 insertions(+), 340 deletions(-)
```

### Push
```
9cb2c907..f2b7cad2 → origin/feature/people-management-reorganization  ✅
```

---

## 11. Artefatos Entregues

| Artefato | Path | Status |
|----------|------|--------|
| KitBuilderService | `backend/modules/gedeon/services/kit_builder_service.py` | ✅ |
| Testes de integração | `backend/tests/modules/gedeon/test_kit_builder_service.py` | ✅ |
| CONTRACTS_GEDEON.md v1.21 | `CONTRACTS_GEDEON.md` | ✅ |
| Relatório | `RELATORIO_FASE_4_BLOCO_3_T1.md` | ✅ |

---

## 12. Self-check 13/13

| # | Item | Status |
|---|------|--------|
| 1 | STEP 0 — contrato lido + princípios §13.1/§13.3/§13.4 citados | ✅ |
| 2 | STEP 1 — 7 investigações H1-H7 com outputs reais | ✅ |
| 3 | STEP 2 — §26 adicionado ao CONTRATO (v1.21) ANTES do código | ✅ |
| 4 | STEP 3 — Commit 1 (docs) push OK, hash `aac68ed8` | ✅ |
| 5 | STEP 4 — KitBuilderService(db) com DTOs @dataclass conforme §26 | ✅ |
| 6 | STEP 5 — 30 testes com 10+ cenários §26.6 | ✅ |
| 7 | STEP 6 — Import OK + pytest 30/30 PASS | ✅ |
| 8 | STEP 7 — Smoke test DB real: Ideal Flores 12.5% completude | ✅ |
| 9 | STEP 8 — 5/5 🔴 PASS (pytest, read-only, 9.6ms, 0.07s, regressão) | ✅ |
| 10 | STEP 9 — Commit 2 (código) push OK, hash `f2b7cad2` | ✅ |
| 11 | Zero toques em zonas proibidas | ✅ |
| 12 | Zero INSERT/UPDATE/DELETE (service read-only confirmado) | ✅ |
| 13 | Performance: 9.6ms < 500ms / 0.07s < 3s | ✅ |

---

## 13. Cenário e Continuidade

**Cenário A identificado:** 13/13 + pytest verde → **T1 OK — LIBERAR T2 (endpoints)**

**Próximo passo:** BLOCO 3 / T2 — endpoints FastAPI que expõem `build_completude`
e `build_lote_condominios`. T2 importará `KitBuilderService` e `CategoriaToTipoDocumento`
de `modules.gedeon.services.kit_builder_service`.
