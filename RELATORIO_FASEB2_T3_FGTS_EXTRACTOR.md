# RELATÓRIO FASE B2 T3 — FGTSExtractor
**Data:** 2026-04-18
**Agente:** Engenheiro Backend Sênior — T3_B2
**Branch:** feature/people-management-reorganization
**Dependência:** T1_B2 (commit e5e8baa6) — BaseExtractor disponível

---

## RESPOSTAS ÀS 5 QUESTÕES DE ANÁLISE (bloco thinking do prompt)

1. **Como diferenciar guia FGTS de relatório FGTS pelo conteúdo?**
   Guia → header `GFD - Guia do FGTS Digital` + `Pagar este documento até` + data vencimento
   na linha "Razão Social do Empregador XX/XX/XXXX". Relatório → `Detalhe da Guia Emitida` +
   `Vencimento da Guia: DD/MM/YYYY` explícito + listão de trabalhadores com CPF/matrícula.

2. **FGTS Consignado tem estrutura igual a FGTS normal?**
   Sim. Mesma estrutura de guia. A única diferença: a seção de composição diz
   "Informações de recolhimentos do Consignado" (em vez de FGTS) e a label na tabela
   é `Competência Consignado Total` (em vez de `FGTS Mensal`). O pattern `Total da Guia:` é idêntico.

3. **Valor FGTS aparece como "Valor a Recolher", "Total FGTS", ou "FGTS Devido"?**
   Nenhum dos três. O campo mais confiável e unificado é **`Total da Guia: X.XXX,XX`**
   (presente nos 4 subtipos). "Valor a recolher" existe mas o valor está na mesma linha
   do cabeçalho da tabela (não isolado), tornando a extração frágil. `Total da Guia[^:]*:`
   cobre guia (`: 6.009,93`), relatorio (` (FGTS): 5.803,72`) e consignado (` (Consignado): 5.222,96`).

4. **Código de barras FGTS começa com que dígito? (geralmente 8 = arrecadação)**
   GFD (Guia do FGTS Digital) **não usa boleto** — usa exclusivamente PIX (QR Code e
   Copia e Cola). Nenhum dos 42 PDFs tem código de barras de boleto. O check
   `barcode_alerta` para início ≠ "8" foi implementado como alerta de segurança,
   mas nunca disparou (código_barras = None em todos os documentos).

5. **Qual estratégia para RELATÓRIO (que não tem valor único)?**
   O relatório TEM valor único: `Total da Guia (FGTS): X.XXX,XX` ou
   `Total da Guia (Consignado): X.XXX,XX` no cabeçalho. Este total agrega todos os
   trabalhadores. A estratégia adotada: extrair via regex unificado `Total da Guia[^:]*:`,
   confiança calculada normalmente (não reduzida). Resultado: 12/12 relatórios = 1.0.

---

## CONTRATO DE ENTREGA — Testes GIVEN/WHEN/THEN

```
GIVEN  "GFD FGTS 03.2026_Conecta Mais.pdf"
WHEN   FGTSExtractor(subtipo="guia").extract(pdf_path)
THEN   tipo="fgts_guia" ✅ | valor=6972.84 (>0) ✅ | vencimento=2026-04-20 ✅ | confianca=1.0 (>=0.85) ✅
→ PASS ✅

GIVEN  "RELATORIO GFD FGTS 03.2026_Conecta Mais.pdf"
WHEN   FGTSExtractor(subtipo="relatorio").extract(pdf_path)
THEN   tipo="fgts_relatorio" ✅ | valor=6972.84 ✅ | confianca=1.0 (>=0.70) ✅
→ PASS ✅
```

---

## STEP 0 — Contrato GEDEON

| Item | Valor |
|------|-------|
| Header Onvio | `Authorization: UDSLongToken <LongToken>` |
| Tipo valores monetários | `Decimal` |
| Thresholds confiança | >=0.90 / 0.70-0.89 / <0.70 |
| Classe pai | `BaseExtractor` |
| 4 subtipos FGTS parser v2 | `fgts_guia` / `fgts_consignado` / `fgts_relatorio` / `fgts_consignado_relatorio` |

---

## STEP 1 — Análise Exploratória dos 4 Subtipos

### Output do comando exato do prompt (subdirs por nome de categoria)

```
============================================================
SUBTIPO: fgts_guia (0 PDFs)
============================================================
(diretório não existe ou sem PDFs — ver caminho_local no banco)

============================================================
SUBTIPO: fgts_consignado (18 PDFs)
============================================================
Arquivo: GFD FGTS - CONSIGNADO 07.2025.pdf
Tamanho: 1011 chars
Primeiros 2000 chars:
GFD - Guia do FGTS Digital
Pagar este documento até
CPF/CNPJ do Empregador Nome/Razão Social do Empregador 20/08/2025
35.710.481 JORDAN SANTOS DE JESUS LTDA
às 21:59:59 (Brasília)
Valor a recolher
Núm. de Pág. Identificador Tag 1.205,66
1 0125080685072399-2 GFD FGTS - CONSIGNADO 072025
Composição do Documento
Informações de recolhimentos do FGTS
Não há informações de recolhimentos do FGTS
Informações de recolhimentos do Consignado
Competência Consignado Total
07/2025 1.205,66 1.205,66
Total Consignado: 1.205,66 1.205,66
Total da Guia: 1.205,66
...

============================================================
SUBTIPO: fgts_relatorio (0 PDFs)
============================================================
(diretório não existe ou sem PDFs — ver caminho_local no banco)

============================================================
SUBTIPO: fgts_consignado_relatorio (0 PDFs)
============================================================
(diretório não existe ou sem PDFs — ver caminho_local no banco)
```

**Observação:** Apenas `fgts_consignado` existe como diretório. Os outros 3 subtipos
(`fgts_guia`, `fgts_relatorio`, `fgts_consignado_relatorio`) têm PDFs em outros
paths (`/app/uploads/onvio/outros/` ou misturados em `fgts_consignado/`).
A exploração foi complementada via `caminho_local` no banco para cobrir todos os 42 PDFs.

### Descoberta crítica: estrutura real do storage

Os PDFs não estão em diretórios nomeados por subtipo. Os caminhos reais vêm de
`caminho_local` no banco `onvio_documents`. Distribuição real:

| Categoria DB | PDFs | Path real |
|---|---|---|
| fgts_guia | 12 | `/app/uploads/onvio/outros/YYYY-MM/` |
| fgts_consignado | 9 | `/app/uploads/onvio/fgts_consignado/YYYY-MM/` |
| fgts_relatorio | 12 | `/app/uploads/onvio/outros/YYYY-MM/` |
| fgts_consignado_relatorio | 9 | `/app/uploads/onvio/fgts_consignado/YYYY-MM/` |

### fgts_guia (GFD FGTS 02.2026_Conecta Mais.pdf — 1114 chars)
```
GFD - Guia do FGTS Digital
Pagar este documento até
CPF/CNPJ do Empregador Nome/Razão Social do Empregador 20/03/2026
35.710.481 JORDAN SANTOS DE JESUS LTDA
às 21:59:59 (Brasília)
Valor a recolher
Núm. de Pág. Identificador Tag 6.009,93
...
Total da Guia: 6.009,93
```
**Padrões:** `Total da Guia:`, vencimento em "Razão Social do Empregador XX/XX/XXXX",
competência em tabela "Competência ... 02/2026", GFD marker, PIX (sem boleto).

### fgts_consignado (GFD FGTS - CONSIGNADO 09.2025.pdf — 1001 chars)
```
GFD - Guia do FGTS Digital
...Tag 3.301,67
Competência Consignado Total
09/2025 3.301,67 3.301,67
Total da Guia: 3.301,67
```
**Padrões:** idênticos à guia; "Consignado" em vez de "FGTS" na tabela.

### fgts_relatorio (RELATORIO GFD FGTS 09.2025_Conecta Mais.pdf — 19317 chars)
```
Detalhe da Guia Emitida
Vencimento da Guia: 20/10/2025 Total da Guia (FGTS): 5.803,72
Relação de Trabalhadores
09/2025 FRANCISCO RAMON FARIAS DE SOUZA 138 ... 173,44
```
**Padrões:** `Total da Guia (FGTS):`, `Vencimento da Guia:`, competência no início das linhas.
**Bug encontrado e corrigido:** CNPJ "29.243.860/0001-38" gerava "60/0001" via regex
simples → fix: `(?<![/\d])((?:0[1-9]|1[0-2])/\d{4})\b` (mês válido + lookbehind).

### fgts_consignado_relatorio (RELATORIO GFD FGTS - CONSIGNADO 02.2026.pdf — 2812 chars)
```
Detalhe da Guia Emitida
Vencimento da Guia: 20/03/2026 Total da Guia (Consignado): 5.222,96
02/2026 20/03/2026 ADAILSON SERRA ALVES ...
```
**Padrões:** idênticos a relatorio; "Consignado" em vez de "FGTS" no Total.

---

## STEP 2 — FGTSExtractor criado

**Arquivo:** `backend/modules/gedeon/onvio/pdf_extractor/fgts_extractor.py`

### Regexes principais

| Campo | Regex | Cobre subtipos |
|---|---|---|
| Valor | `Total\s+da\s+Guia[^:\n]*:\s*([\d\.\,]+)` | Todos 4 |
| Vencimento | `(?:Vencimento\s+da\s+Guia:\s*\|Razão\s+Social\s+do\s+Empregador\s+)(\d{1,2}/\d{1,2}/\d{2,4})` | Todos 4 |
| Competência | `(?<![/\d])((?:0[1-9]\|1[0-2])/\d{4})\b` | Todos 4 |
| GFD marker | `(?:GFD\b\|Guia\s+do\s+FGTS\s+Digital\|Detalhe\s+da\s+Guia\s+Emitida)` | Todos 4 |
| CNPJ CM | `35[\.\s]*710[\.\s]*481` | Todos 4 |

### Scoring

| Critério | Peso | Justificativa |
|---|---|---|
| is_gfd | +0.20 | Diferenciador vs INSS/DAR |
| valor > 0 | +0.40 | Campo crítico |
| vencimento | +0.20 | Obrigatório para pagamento |
| competência | +0.10 | Referência temporal |
| cnpj Conecta Mais | +0.10 | Validação de pertencimento |

---

## STEP 3 — Resultados Reais (42 PDFs)

| Subtipo | Total | ≥0.90 | ≥0.70 | Taxa |
|---|---|---|---|---|
| guia | 12 | 12 | 12 | 100% |
| consignado | 9 | 9 | 9 | 100% |
| relatorio | 12 | 12 | 12 | 100% |
| consignado_relatorio | 9 | 9 | 9 | 100% |
| **TOTAL** | **42** | **42** | **42** | **100%** |

**Meta contratual:** ≥70% → **SUPERADA (100%)**

---

## STEP 4 — Testes de Falsificação

| Teste | Resultado |
|---|---|
| `FGTSExtractor(subtipo='invalido')` | ✅ ValueError lançado |
| 34 PDFs INSS em FGTSExtractor(subtipo='guia') | ✅ confiança máxima = 0.2 (nenhum ≥0.90) |

**Explicação:** PDFs INSS não contêm GFD markers → `is_gfd=False` (+0.0) +
`Total da Guia` não aparece → `valor=None` (+0.0) → score máximo ≈ 0.2 (apenas CNPJ).

---

## SELF-CHECK

- [x] STEP 0 — 5 respostas do contrato corretas
- [x] STEP 1 — análise dos 4 subtipos feita (textos colados acima)
- [x] STEP 2 — fgts_extractor.py criado (classe única, 4 subtipos via parâmetro)
- [x] STEP 3 — rodou nos 42 PDFs, taxa 100% (meta ≥70%)
- [x] STEP 4 — subtipo inválido rejeitado (ValueError)
- [x] STEP 4 — INSS em FGTSExtractor não retorna ≥0.90 (máx 0.2)
- [x] Relatório final completo

**CENÁRIO A — 7/7 OK → T3_B2 OK — LIBERAR T5**
