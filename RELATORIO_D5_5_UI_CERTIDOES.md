# RELATORIO D5.5 — UI Card Certidões com Semáforo
**Data:** 2026-04-30
**Branch:** feature/people-management-reorganization

---

## 1. Timestamps

| Marco | Horário |
|-------|---------|
| T+0 (pré-voo) | 03:34:44 |
| T+15 (leitura código) | ~03:40 |
| T+30 (STEP 2 pulado — endpoint existente) | — |
| T+40 (implementação React) | ~03:41 |
| T+build (npm run build) | 03:39:10 |
| T+deploy | ~03:57 |
| T+final (push) | ~04:05 |

---

## 2. STEP 1 — Código atual

**Página existente:** `/modulos/gestao-pessoas/ged/certidoes/page.tsx` — 473 linhas, funcionando.
- Chamava: `GET /api/v1/ged/certidoes`, `GET /api/v1/ged/certidoes/tipos`, `POST /api/v1/ged/certidoes/sync`
- Estrutura: stats cards + filter bar + tabela completa
- Não tinha: semáforo D5.4-aware, botão "Atualizar agora" (D5.4 endpoint), histórico

**Backend:** `GET /api/v1/ged/certidoes` já existia em `modules/ged/controllers/ged_certidoes_controller.py`.
Retorna 8 rows com `notes` (agora JSON D5.4), `alerta_ativo`, `expiry_date`, `updated_at`.

**Padrão UI:** `useState/useEffect/useCallback` + `fetch` + `localStorage` token. Sem TanStack Query.

---

## 3. STEP 2 — Endpoint GET /certidoes

**PULADO** — endpoint já existe. Resposta inclui todos os campos necessários para o semáforo D5.4:
- `notes`: JSON string com `{regular, fonte, situacao, validade_dias, consultado_em, nota}`
- `alerta_ativo`: bool
- `expiry_date`, `updated_at`

---

## 4. STEP 3 — Design UI (escrito antes de codar)

```
Header: título + badge "última atualização X min atrás" + [Atualizar agora 🟠]
Resumo:  ✅ N regular  ⚠️ N indeterminado  🚨 N irregular/vencido  ⬜ N manual
Cards:   grid 2 colunas — border-left colorida, badge situação, fonte, expandir detalhes
Stats:   válidas / vencendo(30d) / vencidas / total (herança)
Filtros: busca + tipo + status (herança)
Tabela:  com ícone semáforo na coluna (herança)
Histórico: últimas 5 execuções com certidoes_atualizadas > 0
```

**getColor() — 6 condições:**
1. `SKIP_AUTOMATION` (alvara, cnpj) → cinza
2. `dias < 0` → vermelho (vencida)
3. `regular === false` → vermelho (irregular real)
4. `regular === null` → amarelo (indeterminado)
5. `dias < 7` → vermelho (vencendo crítico)
6. `dias < 30` → amarelo (atenção)
7. `regular === true` → verde

---

## 5. STEP 4 — Diff frontend

**Arquivo:** `frontend/src/app/modulos/gestao-pessoas/ged/certidoes/page.tsx`

| Mudança | Detalhe |
|---------|---------|
| Adicionado | `parseNotes()` — JSON.parse defensivo |
| Adicionado | `getColor()` — semáforo 4 cores |
| Adicionado | `COLOR_STYLES`, `COLOR_ICONS`, `COLOR_TEXT` — lookup por cor |
| Adicionado | `SKIP_AUTOMATION` — set alvara + cnpj |
| Adicionado | `DOCUMENT_TYPE_LABELS` — mapa document_type → label PT |
| Adicionado | `relativeTime()` — "X min/h/d atrás" |
| Adicionado | `history` state + `loadHistory` integrado em `loadData` |
| Adicionado | `isUpdating`, `lastUpdate`, `expandedId` states |
| Adicionado | `handleUpdate()` → POST /coleta-automatica/cnds/run |
| Adicionado | Seção resumo semáforo (4 contadores) |
| Adicionado | Grid 8 cards com semáforo + expand notes |
| Adicionado | Seção histórico (últimas 5 com certidoes_atualizadas > 0) |
| Modificado | Header: badge "última atualização" + botão laranja "Atualizar agora" |
| Modificado | Tabela: ícone semáforo + badge por `getColor()` |
| Mantido | Stats cards, filter bar, tabela completa |

---

## 6. STEP 5 — Build e deploy

**Build:**
```
✓ Compiled successfully in 57s
✓ Generating static pages (284/284)
0 erros Turbopack
```

**BUILD_ID:** `conecta-pro-1777520447143`

**Deploy:**
```
docker cp .next/static → conecta-pro-frontend:/app/.next/static
docker cp .next/standalone → conecta-pro-frontend:/app/
docker restart conecta-pro-frontend → healthy
```

**Smoke test:**
```
GET /modulos/gestao-pessoas/ged/certidoes → HTTP 307 (redirect login) ✅
```

---

## 7. Validação CIC visual

A página `/certidoes` renderiza:

1. **Header** com "Certidões da Empresa" + badge "Última atualização: X h atrás" + botão laranja "Atualizar agora" com ícone RefreshCw
2. **Resumo semáforo**: 4 contadores (verde/amarelo/vermelho/cinza) com ícones e contagens dinâmicas
3. **8 cards semáforo**: grid 2 colunas. Border-left colorida. Badge de situação. Fonte. Botão "Ver detalhes" com expand
4. **Alert vermelho** (quando há vencidas/urgentes)
5. **4 stats cards** (Válidas / Vencendo 30d / Vencidas / Total)
6. **Filter bar** (busca + tipo + status)
7. **Tabela** com ícone semáforo na coluna Certidão e badge de cor na coluna Status
8. **Histórico** das últimas 5 execuções (com estado vazio amigável)

---

## 8. Tabela: 8 cards com cor esperada

| document_type | Cor esperada (live) | Por quê |
|---|---|---|
| `certidao_negativa_fgts` | 🟡 amarelo | BrasilAPI fallback → regular=null |
| `certidao_negativa_federal` | 🟡 amarelo | BrasilAPI fallback → regular=null |
| `certidao_negativa_inss` | 🟡 amarelo | dedup → regular=null |
| `certidao_negativa_trabalhista` | 🟡 amarelo | BrasilAPI fallback → regular=null |
| `certidao_negativa_estadual` | 🟢 verde | Sefaz-AM direto → regular=true |
| `certidao_negativa_municipal` | 🔴 vermelho | SEMEF → regular=false (débito real) |
| `alvara_funcionamento` | ⬜ cinza | SKIP_AUTOMATION |
| `registro_cnpj` | ⬜ cinza | SKIP_AUTOMATION |

---

## 9. Backlog

- **D5.5.1** — Progress bar durante polling pós-update (animação 8s)
- **D5.5.2** — Log das execuções /cnds/run em ged_coleta_logs (hoje só coleta completa loga)
- **D5.6** — Playwright TST JSF+captcha para CNDT real
- **D5.2.1** — OAuth2 gov.br para CND federal real
