# RELATÓRIO T3 — Investigação USE_FIXTURE no Frontend
**Data:** 2026-04-21
**Terminal:** T3 (read-only, zero deploy)
**Branch:** feature/people-management-reorganization

---

## Hipótese investigada

> "Frontend usa USE_FIXTURE=true — dados estáticos. Se verdade, completude da UI
> Kits Documentais NUNCA vai sair de 0,0% mesmo após Onvio voltar."

---

## Output dos 8 Steps

### STEP 1 — USE_FIXTURE no frontend

```
frontend/src/hooks/useKitsCompletude.ts:6:  import { FIXTURE_KITS_04_2026 } from '@/fixtures/kits-completude';
frontend/src/hooks/useKitsCompletude.ts:9:  const USE_FIXTURE = false;
frontend/src/hooks/useKitsCompletude.ts:14: if (USE_FIXTURE) {
frontend/src/hooks/useKitsCompletude.ts:28: if (USE_FIXTURE) {
frontend/src/fixtures/kits-completude.ts:6: * USE_FIXTURE=true em useKitsCompletude.ts enquanto T2 não sobe endpoints.
```

**USE_FIXTURE = false** — já estava desativado.

### STEP 2 — Fixtures e mocks de kits

```
frontend/src/fixtures/        ← diretório existe
frontend/src/test/fixtures/   ← diretório existe
frontend/src/test/mocks/      ← diretório existe
```

Nenhum arquivo de fixture referenciado pela página de kits (USE_FIXTURE=false).

### STEP 3 — Página Kits Documentais (68 linhas)

```typescript
import { useKitsLote } from '@/hooks/useKitsCompletude';
// ...
const { data: kits, isLoading, error } = useKitsLote(mesRef);
```

Página chama `useKitsLote` → hook → customInstance → API real.

### STEP 4 — useKitsCompletude.ts completo

```typescript
const USE_FIXTURE = false;  // ← DESATIVADO

async function fetchLote(mesRef: string): Promise<CompletudeKit[]> {
  if (USE_FIXTURE) { return FIXTURE_KITS_04_2026; }  // nunca entra aqui
  return customInstance<CompletudeKit[]>({
    url: '/api/v1/gedeon/kits/lote',
    method: 'GET',
    params: { mes_ref: mesRef },
  });
}
```

### STEP 5 — Endpoint backend

```
GET /kits/completude/{condominio_id}  → KitBuilderService.build_completude()
GET /kits/lote                        → KitBuilderService.build_lote_condominios()
```

Ambos implementados, autenticados via `get_current_user`.

### STEP 6 — Curl direto no backend

**04.2026 — amostra (GREEN HILLS):**
```json
{
  "condominio_nome": "GREEN HILLS",
  "tipo_servico": "manutencao_cftv",
  "mes_ref": "04.2026",
  "docs_presentes": [],
  "docs_faltantes": [
    {"tipo_documento": "nfse",   "motivo": "aguarda_fase_2_banco"},
    {"tipo_documento": "boleto", "motivo": "aguarda_fase_2_banco"}
  ],
  "metricas": {"pct_completude_confirmada": 0.0}
}
```

**05.2026:** mesma estrutura, pct=0.0 em todos os condomínios.

### STEP 7 — pct_completude todos os condomínios (04.2026)

```
ESCRITÓRIO               pct=  0.0%  docs_presentes=0
GREEN HILLS              pct=  0.0%  docs_presentes=0
IDEAL FLORES             pct=  0.0%  docs_presentes=0
LARANJEIRAS              pct=  0.0%  docs_presentes=0
MICHELANGELO             pct=  0.0%  docs_presentes=0
MIRANTE                  pct=  0.0%  docs_presentes=0
P. GELAIN                pct=  0.0%  docs_presentes=0
PARISE                   pct=  0.0%  docs_presentes=0
PRIME ARENA              pct=  0.0%  docs_presentes=0
VILLA DEI FIORI          pct=  0.0%  docs_presentes=0
VILLA PÁSSAROS           pct=  0.0%  docs_presentes=0
```

→ **Backend retorna 0,0% REAL para todos — não é fixture.**

### STEP 8 — Variáveis de ambiente

```
NEXT_PUBLIC_API_URL=https://erp.conectamais.pro
NEXT_PUBLIC_VAPID_PUBLIC_KEY=BBQz...
NEXT_PUBLIC_ENABLE_PUSH_NOTIFICATIONS=true
```

**Nenhuma variável USE_FIXTURE, MOCK ou NEXT_PUBLIC_FIXTURE** no `.env.local`.
O controle é exclusivamente via constante hardcoded no hook (linha 9).

---

## DECISÃO

| Questão | Resposta |
|---|---|
| USE_FIXTURE encontrado em código? | **SIM** — `useKitsCompletude.ts:9` |
| USE_FIXTURE está ativo (true)? | **NÃO** — `const USE_FIXTURE = false` |
| Backend retorna dados reais? | **SIM** — 11 condomínios, API respondendo |
| Backend retorna pct > 0? | **NÃO** — todos com 0,0%, docs_presentes=0 |
| Frontend consume backend ou fixture? | **BACKEND** (USE_FIXTURE=false) |
| 0,0% na UI é fixture ou dado real? | **DADO REAL** do backend |

---

## VEREDICTO

**Hipótese REFUTADA.** O frontend já consome a API real.

O 0,0% exibido na UI Kits Documentais é o valor real retornado pelo backend —
nenhum documento foi associado às competências 04.2026 e 05.2026 pelo pipeline
Onvio. A causa raiz do 0,0% está no pipeline de sync (docs_presentes vazio),
não na camada frontend.

**Próximo passo:** investigar por que `ged_onvio_documents` não alimenta
`docs_presentes` no `KitBuilderService.build_completude()` para esses meses.
