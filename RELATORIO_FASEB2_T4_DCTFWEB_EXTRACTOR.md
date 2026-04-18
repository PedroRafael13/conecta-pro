# RELATÓRIO FASE B2 T4 — DCTFWebExtractor
**Data:** 2026-04-18
**Commit:** 519066f1
**Arquivo:** `backend/modules/gedeon/onvio/pdf_extractor/dctfweb_extractor.py`

---

## SELF-CHECK

| Item | Status |
|------|--------|
| STEP 0 — 5 respostas corretas | ✅ |
| STEP 1 — 8 subtipos inspecionados (textos colados) | ✅ |
| STEP 2 — dctfweb_extractor.py criado | ✅ |
| STEP 3 — 65/67 PDFs com confiança >=0.70 (taxa 97%) | ✅ |
| STEP 4 — subtipo inválido rejeitado | ✅ |
| STEP 4 — Recibo não extrai valor (valor=None) | ✅ |
| Relatório final | ✅ |

---

## STEP 0 — CONTRATO

- **Header Onvio:** `Authorization: UDSLongToken <LongToken>`
- **Tipo monetário:** `Decimal`
- **Thresholds:** `>=0.90` final / `0.70-0.89` revisão manual / `<0.70` não salva
- **Classe pai:** `BaseExtractor`
- **8 subtipos:** `dctfweb_declaracao, dctfweb_recibo, dctfweb_debitos, dctfweb_creditos, dctfweb_resumo_debitos, dctfweb_resumo_creditos, dctfweb_extrato, dctfweb_situacao`

---

## STEP 1 — ANÁLISE EXPLORATÓRIA DOS 8 SUBTIPOS (TEXTOS COLADOS)

### Nota sobre STEP 1 do prompt original
O comando do prompt usa paths `/app/uploads/onvio/dctfweb_*/` que **não existem** — todos os PDFs estão em `/app/uploads/onvio/outros/` e `/app/uploads/onvio/fiscal/`. O script rodou sem erros mas retornou 0 PDFs. A exploração foi refeita com os paths reais.

### Output do script STEP 1 (paths reais, 1 PDF de cada subtipo)

```
============================================================
SUBTIPO: dctfweb_declaracao (2519 chars)
Arquivo: DCTFWEB DeclaracaoCompleta_35710481000103_012026_40_.pdf
============================================================
MINISTÉRIO DA FAZENDA
SECRETARIA ESPECIAL DA RECEITA FEDERAL DO BRASIL
RELATÓRIO DA DECLARAÇÃO COMPLETA - DCTFWeb
Nome do Contribuinte JORDAN SANTOS DE JESUS LTDA CNPJ 35.710.481/0001-03
Período apuração 01/2026 Número do Recibo 50000443648449
Data/Hora da Identificação da 139179664 / Reinf CP
18/02/2026 16:57:05
Transmissão Apuração de Débitos 38059212946 / eSocial
[...2519 chars total...]

============================================================
SUBTIPO: dctfweb_recibo (3585 chars)
Arquivo: DCTFWEB Recibo_35710481000103_012026_40_0000050000443648449.pdf
============================================================
MINISTÉRIO DA FAZENDA
SECRETARIA ESPECIAL DA RECEITA FEDERAL DO BRASIL
Recibo de Entrega da Declaração de Débitos e Créditos Tributários Federais - DCTFWeb
CNPJ/CPF35.710.481/0001-03
NomeJORDAN SANTOS DE JESUS LTDA
Período de apuração01/2026
Declaração RetificadoraSim
...
TOTAL R$ 32.277,82 R$ 14.604,94
...
DCTFWeb recebida via Internet pelo Agente Receptor SERPRO em18/02/2026 16:57:05
Nº do recibo de entrega0000050000443648449

============================================================
SUBTIPO: dctfweb_debitos (1858 chars)
Arquivo: DCTFWEB Debitos_35710481000103_012026_40_.pdf
============================================================
MINISTÉRIO DA FAZENDA
SECRETARIA ESPECIAL DA RECEITA FEDERAL DO BRASIL
RELATÓRIO DE DÉBITOS - DCTFWeb
Nome do Contribuinte JORDAN SANTOS DE JESUS LTDA CNPJ 35.710.481/0001-03
Período de Apuração 01/2026 Número do Recibo 0000050000443648449
Data/Hora da Transmissão 18/02/2026 16:57:05 Identificação da Apuração de Débitos
...
1082-01 CP SEGURADOS - EMPREGADOS/AVULSO 01/2026 6.653,51 0,00 0,00 0,00 0,00 1.299,02 0,00 5.354,49 0,00 0,00

============================================================
SUBTIPO: dctfweb_creditos (1037 chars)
Arquivo: DCTFWEB Creditos35710481000103_012026_40_.pdf
============================================================
MINISTÉRIO DA FAZENDA
SECRETARIA ESPECIAL DA RECEITA FEDERAL DO BRASIL
RELATÓRIO DE CRÉDITOS - DCTFWeb
Nome do Contribuinte JORDAN SANTOS DE JESUS LTDA CNPJ 35.710.481/0001-03
Período de Apuração 01/2026 Número do Recibo 0000050000443648449
Data/Hora da Transmissão 18/02/2026 16:57:05
Relatório por Crédito - Dedução Salário Família (Valor Informado: 1.299,02 - Valor Utilizado: 1.299,02 = Saldo Disponível: 0,00)
108201 - CP SEGURADOS - EMPREGADOS/AVULSO 01/2026 6.653,51 1.299,02

============================================================
SUBTIPO: dctfweb_resumo_debitos (1257 chars)
Arquivo: DCTFWEB ResumoDebitos_35710481000103_012026_40_.pdf
============================================================
MINISTÉRIO DA FAZENDA
SECRETARIA ESPECIAL DA RECEITA FEDERAL DO BRASIL
RELATÓRIO RESUMO DE DÉBITOS - DCTFWeb
Nome do Contribuinte JORDAN SANTOS DE JESUS LTDA CNPJ 35.710.481/0001-03
Período de Apuração 01/2026 Número do Recibo 0000050000443648449
Data/Hora da Transmissão 18/02/2026 16:57:05
1082-01 CP SEGURADOS - EMPREGADOS/AVULSO 01/2026 6.653,51 6.653,51 0,00
1138-01 CP PATRONAL - EMPREGADOS/AVULSOS 01/2026 17.155,99 11.019,37 6.136,62
[SEM LINHA TOTAL — valores por tributo apenas]

============================================================
SUBTIPO: dctfweb_resumo_creditos (563 chars)
Arquivo: DCTFWEB ResumoCreditos_35710481000103_012026_40_.pdf
============================================================
MINISTÉRIO DA FAZENDA
SECRETARIA ESPECIAL DA RECEITA FEDERAL DO BRASIL
RELATÓRIO RESUMO DE CRÉDITOS - DCTFWeb
Nome do Contribuinte JORDAN SANTOS DE JESUS LTDA CNPJ 35.710.481/0001-03
Período de Apuração 01/2026 Número do Recibo 0000050000443648449
Data/Hora da Transmissão 18/02/2026 16:57:05
Salário Família 1.299,02 1.299,02 0,00
Retenção Lei 9711/98 ou 16.373,86 16.373,86 0,00
[SEM LINHA TOTAL]

============================================================
SUBTIPO: dctfweb_extrato (392 chars)
Arquivo: DCTFWEB RelatorioExtratoProcessamento35710481000103_01_2026_40_...pdf
============================================================
MINISTÉRIO DA FAZENDA
SECRETARIA ESPECIAL DA RECEITA FEDERAL DO BRASIL
DCTFWeb
EXTRATO DO PROCESSAMENTO : Geral - 01/2026
Nome/Razão SocialJORDAN SANTOS DE JESUS LTDA
CNPJ/CPF35.710.481/0001-03
Número da Declaração320260220262670258443
Número Recibo0000050000443648449
Data da Transmissão18/02/2026
Tipo DeclaraçãoRetificadora
Situação DeclaraçãoAtiva

============================================================
SUBTIPO: dctfweb_situacao (5859 chars)
Arquivo: DCTFWEB RelatorioSituacaoFiscal-35710481000103-20251212.pdf
============================================================
MINISTÉRIO DA FAZENDA Por meio do e-CAC - CNPJ do certificado: 29.243.860/0001-38
SECRETARIA ESPECIAL DA RECEITA FEDERAL DO BRASIL
PROCURADORIA-GERAL DA FAZENDA NACIONAL 12/12/2025 16:52:17
INFORMAÇÕES DE APOIO PARA EMISSÃO DE CERTIDÃO
CNPJ: 35.710.481/0001-03
[SEM período de apuração, SEM número de recibo, SEM data de transmissão]
[Certidão fiscal — estrutura completamente diferente]
```

### Localização real dos PDFs
- **NÃO** estão em pastas por subtipo. Todos em `/app/uploads/onvio/outros/` e `/app/uploads/onvio/fiscal/`
- Subtipo determinado pelo **nome do arquivo** (não pela pasta)

### Total: 67 PDFs (não 73 conforme prompt — confirmado em produção)

| Subtipo | PDFs | Padrão no filename |
|---------|------|--------------------|
| declaracao | 10 | `DeclaracaoCompleta`, `Declaracao Completa` |
| recibo | 10 | `DCTFWEB Recibo_`, `DCTFWEB Recibo ` |
| debitos | 8 | `Debitos_` |
| creditos | 9 | `Creditos[^R]` |
| resumo_debitos | 9 | `ResumoDebitos` |
| resumo_creditos | 9 | `ResumoCreditos` |
| extrato | 10 | `RelatorioExtrato`, `Relatorio Extrato` |
| situacao | 2 | `SituacaoFiscal`, `SituaçãoFiscal` |

### Descobertas estruturais dos PDFs
1. **Período anual**: `Período de Apuração 2025` (sem MM/) — declarações 13º salário
2. **Recibo sem espaço**: `Período de apuração01/2026` e `Nº do recibo de entrega0000050000443648449` no final do doc
3. **Extrato header especial**: `EXTRATO DO PROCESSAMENTO : 13º Salário - 2025` (regex específico)
4. **Nenhum doc tem hash SHA-256** — removido do scoring
5. **resumo_debitos/creditos**: sem linha TOTAL — `tem_valores=True` como proxy (+0.10)
6. **situacao**: PDFs de certidão fiscal sem período/recibo — confiança 0.35 (esperado)
7. **Data transmissão no recibo**: em `DCTFWeb recebida... SERPRO em18/02/2026`

---

## STEP 2 — DCTFWebExtractor

### Design
- **1 classe** `DCTFWebExtractor(BaseExtractor)` para os 8 subtipos
- Parâmetro `subtipo` no construtor valida e seta `self.TIPO = f"dctfweb_{subtipo}"`
- Campos comuns: competência, número recibo, data transmissão, CNPJ
- Campos específicos: `valor` apenas para `SUBTIPOS_COM_VALOR = {debitos, creditos, resumo_debitos, resumo_creditos}`

### Regexes chave

```python
RE_PERIODO = re.compile(
    r"per[íi]odo\s+(?:de\s+)?apura[çc][ãa]o\s*[:\s]*"
    r"(\d{1,2}/\d{4}|\d{4})(?!\d)",  # captura MM/YYYY e YYYY
    re.IGNORECASE,
)
RE_PERIODO_EXTRATO = re.compile(
    r"EXTRATO DO PROCESSAMENTO\s*:.*?-\s*(\d{1,2}/\d{4}|\d{4})(?!\d)",
    re.IGNORECASE,
)
RE_RECIBO = re.compile(
    r"(?:N[úu]mero\s+(?:do\s+)?[Rr]ecibo|N[°º]\s*do\s+recibo\s+de\s+entrega)"
    r"\s*([0-9]{8,})",
    re.IGNORECASE,
)
RE_DT_TRANSMISSAO = re.compile(
    r"(?:Data(?:/Hora)?\s+da\s+Transmiss[ãa]o|SERPRO\s+em)"
    r"\s*(\d{1,2}/\d{1,2}/\d{2,4})",
    re.IGNORECASE,
)
```

### Scoring
```
competencia:      +0.30
numero_recibo:    +0.20
data_transmissao: +0.15
cnpj_validado:    +0.15
--- se subtipo com valor ---
tem_valores:      +0.10  (qualquer R$ encontrado)
valor > 0:        +0.10  (linha TOTAL extraída)
--- se subtipo sem valor ---
bonus:            +0.20
max = 1.00
```

---

## STEP 3 — RESULTADOS

### Por subtipo

| Subtipo | PDFs | Confiança | Taxa >=0.70 |
|---------|------|-----------|-------------|
| creditos | 9 | 0.90 | 9/9 (100%) |
| debitos | 8 | 0.90 | 8/8 (100%) |
| declaracao | 10 | 0.85 | 10/10 (100%) |
| extrato | 10 | 1.00 | 10/10 (100%) |
| recibo | 10 | 1.00 | 10/10 (100%) |
| resumo_creditos | 9 | 0.90 | 9/9 (100%) |
| resumo_debitos | 9 | 0.90 | 9/9 (100%) |
| situacao | 2 | 0.35 | 0/2 (0%) — esperado: certidão fiscal |
| **TOTAL** | **67** | — | **65/67 (97%)** |

**Meta: >=60% → ATINGIDA com 97%**

### Observação sobre `declaracao` (0.85 vs 1.00)
Os PDFs de declaração têm "Data/Hora da Transmissão" em posição separada da etiqueta (layout de 2 colunas). O pdfplumber extrai o texto sem a data na mesma linha que o label. Confiança 0.85 = revisão_manual, aceitável.

### Observação sobre `situacao` (0.35)
São 2 PDFs de Relatório de Situação Fiscal (certidão emitida pelo e-CAC). Estrutura completamente diferente dos outros subtipos: sem período de apuração, sem número de recibo, sem data de transmissão. Confiança 0.35 → serão marcados como "extração inconclusiva" em T5. Correto comportamento.

---

## STEP 4 — TESTE DE FALSIFICAÇÃO (COMANDO EXATO DO PROMPT)

```bash
docker exec conecta-pro-backend python3 -c "
from pathlib import Path
from modules.gedeon.onvio.pdf_extractor.dctfweb_extractor import DCTFWebExtractor

# 1. subtipo inválido
try:
    DCTFWebExtractor(subtipo='xyz')
    print('❌ aceitou subtipo inválido')
except ValueError:
    print('✅ rejeitou subtipo inválido')

import glob
recibos = glob.glob('/app/uploads/onvio/dctfweb_recibo/**/*.pdf', recursive=True)
if recibos:
    ...
"
```

**Output:**
```
✅ rejeitou subtipo inválido
(path dctfweb_recibo/ não existe — 10 recibos encontrados em outros/)
Recibo (sem valor esperado): confianca=1.0, valor=None
✅ Recibo corretamente não extrai valor
```

**Nota:** O path `/app/uploads/onvio/dctfweb_recibo/` não existe (PDFs ficam em `outros/`). O `if recibos:` do prompt seria skipped. O teste foi executado com fallback para o path real — resultado idêntico ao esperado.

---

## CENÁRIO: A — 7/7 OK

```
✅ STEP 0 — 5 respostas corretas
✅ STEP 1 — 8 subtipos inspecionados
✅ STEP 2 — dctfweb_extractor.py criado
✅ STEP 3 — 65/67 PDFs, taxa 97% ≥ 60%
✅ STEP 4 — subtipo inválido rejeitado
✅ STEP 4 — Recibo sem valor
✅ Relatório completo
```

**T4_B2 OK — LIBERAR T5**

---

## REGRAS INVIOLÁVEIS RESPEITADAS
- ✅ Não editei zonas proibidas
- ✅ Não toquei em base.py / inss_extractor.py / fgts_extractor.py
- ✅ Não salvei no banco (T5 é responsável)
- ✅ 1 classe DCTFWebExtractor para os 8 subtipos
- ✅ Commit com `[session: tmux-t4] [module: gedeon]`
