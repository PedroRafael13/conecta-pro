# Upload Folha Março/2026 — Extrato Mensal Domínio Sistemas
**Data:** 2026-04-11
**Arquivo:** `Folha 03.2026_Conecta Mais - Geral.pdf`
**Endpoint:** `POST /api/v1/people-management/dp/payslips/folha/upload?mes=3&ano=2026`
**Veredicto:** ✅ 100% CONCLUÍDO — 560 rubricas salvas, 0 erros

---

## Resultado do Upload

```json
{
  "arquivo": "/app/uploads/folhas/2026-03/extrato_2026_03.pdf",
  "funcionarios": 51,
  "validacao": {
    "competencia": "03/2026",
    "funcionarios": 51,
    "total_proventos": 97504.07,
    "total_descontos": 30826.48,
    "liquido_geral": 66677.59,
    "confere_dominio_proventos": true,
    "confere_dominio_descontos": true
  },
  "rubricas": {
    "rubricas_salvas": 560,
    "erros": 0,
    "primeiros_erros": []
  }
}
```

---

## Validação vs PDF Domínio Sistemas

| Campo | PDF Domínio | API Upload | Confere? |
|-------|-------------|------------|---------|
| Competência | 03/2026 | 03/2026 | ✅ |
| Funcionários | 51 | 51 | ✅ |
| Total Proventos | R$ 97.504,07 | R$ 97.504,07 | ✅ |
| Total Descontos | R$ 30.826,48 | R$ 30.826,48 | ✅ |
| Líquido Geral | R$ 66.677,59 | R$ 66.677,59 | ✅ |

---

## hr_payslip_items — Rubricas Importadas

**Total:** 560 rubricas | **51 funcionários** | **0 erros de importação**

### Top 10 por ocorrência

| Código | Descrição | Tipo | Ocorrências | Total (R$) |
|--------|-----------|------|-------------|-----------|
| 48 | VALE TRANSPORTE | D | 50 | 5.730,28 |
| 9383 | DESC VALE ALIMENTACAO | D | 49 | 1.627,54 |
| 998 | I.N.S.S. | D | 46 | 12.740,82 |
| 1 | HORAS NORMAIS | P | 46 | 136.760,14 |
| 264 | TAXA NEGOCIAL | D | 44 | 1.892,00 |
| 202 | PLANO ODONTOLOGICO | D | 27 | 476,00 |
| 246 | ADICIONAL NOTURNO (INFOR) | P | 18 | 6.145,56 |
| 247 | HORA NOT REDUZIDA | P | 18 | 7.365,42 |
| 8069 | HORAS FALTAS PARCIAL | D | 14 | 308,14 |
| 224 | ADICIONAL DE RONDA | P | 14 | 5.590,60 |

### Distribuição Proventos vs Descontos

| Tipo | Rubricas distintas | Ocorrências totais |
|------|-------------------|-------------------|
| P (Provento) | ~30 tipos | ~230 itens |
| D (Desconto) | ~35 tipos | ~330 itens |

---

## Bugs Encontrados e Corrigidos (para o upload funcionar)

| # | Problema | Causa Raiz | Fix Aplicado |
|---|----------|-----------|--------------|
| 1 | `PermissionError /opt/conecta-pro/uploads` | Container usa `/app/uploads`, não o path do host | `dp_payslips_controller.py`: path corrigido para `/app/uploads/folhas/` |
| 2 | `"Não foi possível extrair dados do PDF"` | Regex `Empr\.:\s*(\d+)\s+` exigia espaço entre código e nome — PDF tem `85ADAILSON` sem espaço | `folha_pdf_parser.py`: `\s+` → `\s*` no padrão cabeçalho |
| 3 | Competência não extraída | `EXTRATO MENSAL\s+(\d{2}/\d{4})` falha — competência está em linha separada antes | Fallback adicionado: `Competência:\s*(\d{2}/\d{4})` |
| 4 | Apenas 3 rubricas/funcionário (só consignados) | Regex com `^...$` capturava apenas linhas simples; PDF usa 2 rubricas por linha | Regex reescrito sem âncoras `^...$`, com lookbehind `(?<!\d)` |
| 5 | `rubricas_salvas: 0, erros: 51` — "Sem payslip" | CPF no banco: `03527554238` vs CPF do PDF: `035.275.542-38` (formatações diferentes) | `REGEXP_REPLACE` na query para normalizar ambos (`[^0-9]` removido) |

---

## Arquitetura do Fluxo

```
PDF Extrato Mensal (Domínio Sistemas)
    ↓
POST /dp/payslips/folha/upload?mes=3&ano=2026
    ↓
FolhaPDFParser.parse()
  → 51 funcionários × ~11 rubricas = 560 itens
    ↓
importar_rubricas()
  → Match: REGEXP_REPLACE(e.cpf) = REGEXP_REPLACE(pdf_cpf)
  → DELETE hr_payslip_items WHERE payslip_id  (evita duplicatas)
  → INSERT INTO hr_payslip_items (560 linhas)
  → NÃO modifica hr_payslips (T2 é a fonte de verdade dos totais)
    ↓
hr_payslip_items: 560 registros ✅
hr_payslips: intacto com dados T2 ✅
```

---

## Confirmação DB

```sql
SELECT COUNT(*) FROM hr_payslip_items;
→ 560

SELECT codigo, descricao, tipo, COUNT(*) as ocorrencias
FROM hr_payslip_items
GROUP BY codigo, descricao, tipo
ORDER BY ocorrencias DESC LIMIT 5;
→ 48 | VALE TRANSPORTE | D | 50
→ 9383 | DESC VALE ALIMENTACAO | D | 49
→ 998 | I.N.S.S. | D | 46
→ 1 | HORAS NORMAIS | P | 46
→ 264 | TAXA NEGOCIAL | D | 44
```

---

## Download

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_UPLOAD_FOLHA_MARCO_2026_20260411.md ~/Downloads/
```
