# RELATÓRIO T7 — Auditoria de Fechamento FASE B2
**Data:** 2026-04-18 | **Auditor:** T7 (Auditor Técnico Sênior — Princípio 13.5)
**Branch:** feature/people-management-reorganization

---

## 1. STEP 0 — Contrato

| Item | Valor |
|------|-------|
| Versão ao início da auditoria | 1.6 |
| Versão após auditoria | 1.7 (seção 16 adicionada) |
| Seção de Princípios | ## 13. PRINCÍPIOS DE ENGENHARIA GEDEON |
| Seção adicionada em T6_FIX | ## 15. LIÇÃO T6_FIX |
| Tamanho | 710 linhas / 31.291 bytes |

**Princípio mais relevante para T7:**
> **13.5 (Aplicação Universal) + 13.1 (Chesterton):** T7 é o auditor que aplica os princípios sobre tudo sem exceção — inclusive sobre si mesmo. Não aceita declarações sem verificar na fonte real (DB/filesystem). Chesterton proíbe derrubar o que não entendeu — T7 investiga antes de rejeitar.

---

## 2. Tabela H1–H10: Hipótese × Medido Agora

| Hipótese | Declarado | Medido agora | Bate? |
|----------|-----------|--------------|-------|
| H1: 436 docs totais | 436 | 436 | ✅ |
| H2: 121 extraídos | 121 | 121 | ✅ |
| H3: INSS 5 / R$ 47.382,03 | 5 / 47.382,03 | 5 / 47382.03 | ✅ |
| H4: FGTS 42 / R$ 191.319,74 | 42 / 191.319,74 | 42 / 191319.74 | ✅ |
| H5: 107 auto / 12 revisão / 2 rejeitados | 107/12/2 | 107/12/2 | ✅ |
| H6: Contrato v1.6, seções 13 e 15 | v1.6 + §13 + §15 | Confirmado | ✅ |
| H7: 4 extractors em pdf_extractor/ | 4 (+base) | 5 arquivos (base+inss+fgts+dctfweb+enrichment) | ✅ |
| H8: chunk com "valores-fiscais-resumo" | presente | 42849a3fc36b9e28.js | ✅ |
| H9: zero commits em zonas proibidas | 0 | 0 (financial, government, main_production, docker-compose, .env, alembic/versions) | ✅ |
| H10: idempotência processados=0 | processados=0 | 0 — MAS endpoint sem auth 🔴 | ⚠️ |

---

## 3. Output dos STEPs 1–5

### STEP 1.1 — Contagem total
```
 total_docs | extraidos | fiscais_totais
------------+-----------+----------------
        436 |       121 |            121
```

### STEP 1.2 — Soma de valores
```
 tipo | qtd |   soma
------+-----+-----------
 INSS |   5 |  47382.03
 FGTS |  42 | 191319.74
```

### STEP 1.3 — Distribuição de confiança
```
 auto_save | revisao | rejeitado
-----------+---------+-----------
       107 |      12 |         2
```

### STEP 1.4 — Idempotência
```
{"processados":0,"salvos_final":0,"salvos_revisao":0,"pulados_baixa_conf":0,
 "pulados_sem_extractor":315,"erros":0,"duracao_s":0.01}
```
⚠️ **ACHADO CRÍTICO:** Login rate-limitado durante o teste. Endpoint testado sem token válido → HTTP 200. Investigação confirmou ausência de `Depends(get_current_user)` na assinatura do endpoint (linha 277–281 do controller). Ver seção 4.

### STEP 2.1 — Extractors
```
base.py           8583 bytes  2026-04-18 10:24
dctfweb_extractor.py  9286    2026-04-18 11:23
enrichment_service.py 8047    2026-04-18 12:00
fgts_extractor.py     7009    2026-04-18 11:21
inss_extractor.py     7415    2026-04-18 11:15
```

### STEP 2.2 — Arquivos frontend
```
ValoresFiscaisCard.tsx    6316 bytes  2026-04-18 12:47
useValoresFiscaisResumo.ts  979 bytes  2026-04-18 12:46
```

### STEP 2.3 — Bundle
```
Container: conecta-pro-frontend
/app/.next/static/chunks/42849a3fc36b9e28.js  ← contém "valores-fiscais-resumo"
```

### STEP 3 — Contrato
```
Versão: 1.6 (início) → 1.7 (após auditoria)
Seções: ## 10. ## 11. ## 12. ## 13. ## 14. ## 15.
Subseções §13: 13.1 Chesterton / 13.2 Falsificação / 13.3 Docs / 13.4 Escopo / 13.5 Universal / 13.6 STEP 0
710 linhas / 31.291 bytes (> 500 / > 23KB) ✅
```

### STEP 4 — Zonas proibidas (desde e5e8baa6)
```
financial/             → vazio ✅
government_integrations/ → vazio ✅
main_production.py     → vazio ✅
docker-compose*.yml    → vazio ✅
.env*                  → vazio ✅
alembic/versions/      → vazio ✅
```

### STEP 5 — Regressões
```
✅ T3 (regex competência anti-CNPJ): OK
⚠️ T2 (DAS em INSSExtractor): nenhum DAS no container — gap storage, não testável
✅ FASE B1 (mes_ref formato YYYY-MM): 0 registros com formato errado
```

---

## 4. Descobertas Novas

### D1 🔴 CRÍTICO — /extrair-valores sem autenticação
**Arquivo:** `backend/modules/gedeon/onvio/controllers/onvio_controller.py:277`
```python
@router.post("/extrair-valores")
async def extrair_valores(forcar: bool = False, limite: int | None = None):
    # ← sem Depends(get_current_user)
```
Testado: `curl -s -X POST http://127.0.0.1:8080/api/v1/onvio/extrair-valores` → **HTTP 200**
Testado: token inválido → **HTTP 200**
Documentado em CONTRACTS_GEDEON.md §16.1 (v1.7).
**Correção:** T_FIX_AUTH — adicionar `current_user: User = Depends(get_current_user)`.

### D2 — DCTFWeb: 74 docs vs 65/67 (T4)
Delta de +7 docs explicado: base cresceu após T4 (novos docs sincronizados do Onvio). Estado atual: 74/74 (100%). Não é regressão. Documentado em §16.2.

### D3 — T2 gap storage
DAS não testável no container. Documentado em §16.3.

**Versão do contrato:** 1.6 → 1.7 | Commit: a0cd4dca

---

## 5. Score por Área

| Área | Pontos | Evidência |
|------|--------|-----------|
| Backend (extractors) | 10/10 | STEP 2.1 — 5 arquivos presentes, importáveis |
| Backend (endpoint) | 7/10 | STEP 1.4 — idempotência ✅ mas **sem auth** 🔴 |
| Banco (migration + dados) | 10/10 | STEP 1.1+1.2 — alembic head, valores exatos |
| Frontend (componente) | 10/10 | STEP 2.2+2.3 — TSX+hook+chunk confirmados |
| Contrato (documentação) | 10/10 | STEP 3 — v1.7, 710 linhas, §13+§15+§16 |
| Zonas proibidas (escopo) | 10/10 | STEP 4 — 6 zonas, todas vazias |
| Regressão de bugs | 9/10 | STEP 5 — T3 ✅, B1 ✅, T2 gap storage ⚠️ |

---

## 6. Self-Check 10/10

| # | Item | Status |
|---|------|--------|
| 1 | STEP 0 — versão 1.6 confirmada + princípio citado | ✅ |
| 2 | STEP 1.1 — 436/121/121 batem | ✅ |
| 3 | STEP 1.2 — INSS 5/R$47.382,03 + FGTS 42/R$191.319,74 batem | ✅ |
| 4 | STEP 1.3 — 107/12/2 batem | ✅ |
| 5 | STEP 1.4 — processados=0 (idempotência) + achado auth 🔴 | ⚠️ |
| 6 | STEP 2.1 — 5 arquivos extractors presentes | ✅ |
| 7 | STEP 2.2 — ValoresFiscaisCard.tsx + useValoresFiscaisResumo.ts existem | ✅ |
| 8 | STEP 2.3 — chunk "valores-fiscais-resumo" no container | ✅ |
| 9 | STEP 4 — zonas proibidas intocadas (6 queries, todas vazias) | ✅ |
| 10 | STEP 5 — T3 ✅, B1 ✅, T2 gap storage documentado | ✅ |

**Score self-check: 9/10** (item 5 marcado ⚠️ por achado de auth)

---

## 7. VEREDITO

```
╔══════════════════════════════════════════════════════════╗
║  FASE B2 RETIDA                                          ║
║  Motivo: Backend (endpoint) score 7/10 < mínimo 9/10    ║
║  Causa: /extrair-valores sem Depends(get_current_user)   ║
║  Correção: T_FIX_AUTH (1 linha no controller)            ║
╚══════════════════════════════════════════════════════════╝
```

**Antes de LIBERAR, executar:**
`T_FIX_AUTH` — adicionar auth dependency no endpoint `/extrair-valores` (controller linha 277).
Após fix: re-rodar STEP 1.4 com token válido para confirmar HTTP 401 sem auth e HTTP 200 com auth.

---

## 8. Auto-auditoria T7 (Princípio 13.5 aplicado ao próprio T7)

| Invariante | Respeitado? |
|------------|-------------|
| INV-1: zero alteração de código | ✅ (só leitura + relatório) |
| INV-2: zero commits exceto relatório e contrato | ✅ (2 commits: a0cd4dca + este) |
| INV-3: todos números de query SQL ou arquivo real | ✅ |
| INV-4: métrica que não bate → RETER | ✅ (auth falhou → RETER) |
| INV-5: zonas proibidas intocadas | ✅ |
| INV-7: frontend validado por chunk-hash, não HTTP 200 | ✅ (42849a3fc36b9e28.js) |
| INV-9: veredito binário | ✅ (RETER) |
