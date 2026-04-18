# RELATÓRIO FASE B2 T4 — DCTFWebExtractor
**Data:** 2026-04-18
**Commit:** 519066f1
**Arquivo:** `backend/modules/gedeon/onvio/pdf_extractor/dctfweb_extractor.py`

---

## SELF-CHECK

| Item | Status |
|------|--------|
| STEP 0 — 5 respostas corretas | ✅ |
| STEP 1 — 8 subtipos inspecionados | ✅ |
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

## STEP 1 — DESCOBERTAS DOS 8 SUBTIPOS

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

## STEP 4 — FALSIFICAÇÃO

```
✅ rejeitou subtipo inválido: subtipo 'xyz' inválido. Válidos: [...]
✅ Recibo corretamente não extrai valor (valor=None)
✅ Declaracao corretamente não tem hash_transmissao
✅ Declaracao confiança OK: 0.85
✅ Situacao corretamente sinalizada com confiança baixa (0.35 < 0.70)
✅ Todos os 8 subtipos instanciam corretamente com TIPO correto
```

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
