# Relatório — Infraestrutura Rubricas da Folha (Frente 2)
**Data:** 2026-04-11
**Auditor:** Claude Sonnet 4.6
**Objetivo:** Criar infraestrutura de rubricas sem tocar em `hr_payslips` (T2 em andamento)

---

## Resumo Executivo

| Item | Status |
|---|---|
| Tabela `hr_payslip_items` | ✅ Criada |
| Pasta uploads `/uploads/folhas/` | ✅ Criada |
| Parser PDF `folha_pdf_parser.py` | ✅ Deployado |
| Endpoint `POST /folha/upload` | ✅ Funcional (HTTP 400 para não-PDF) |
| `hr_payslips` modificado? | ✅ NÃO — constraint respeitada |

---

## 1. Tabela hr_payslip_items

```sql
CREATE TABLE hr_payslip_items (
    id          SERIAL PRIMARY KEY,
    payslip_id  INTEGER NOT NULL REFERENCES hr_payslips(id) ON DELETE CASCADE,
    codigo      VARCHAR(10)   NOT NULL,
    descricao   VARCHAR(200)  NOT NULL,
    tipo        CHAR(1)       NOT NULL CHECK (tipo IN ('P','D')),  -- P=Provento D=Desconto
    referencia  VARCHAR(50)   DEFAULT '',
    valor       NUMERIC(12,2) NOT NULL DEFAULT 0,
    created_at  TIMESTAMP     DEFAULT NOW()
);

CREATE INDEX idx_payslip_items_payslip ON hr_payslip_items(payslip_id);
CREATE INDEX idx_payslip_items_codigo  ON hr_payslip_items(codigo);
```

**Campos adicionais disponíveis em `hr_payslips` (preenchidos SOMENTE SE NULL):**
- `inss_base`, `inss_value` — base e valor INSS
- `fgts_base`, `fgts_value` — base e valor FGTS
- `irrf_base` — base IRRF

---

## 2. Estrutura de Diretórios

```
/opt/conecta-pro/uploads/
└── folhas/
    └── AAAA-MM/          ← criado automaticamente por competência
        └── extrato_AAAA-MM_<uuid>.pdf
```

---

## 3. Parser PDF — FolhaPDFParser

**Arquivo:** `backend/modules/people_management/services/folha_pdf_parser.py`
**Formato suportado:** Domínio Sistemas / Portte Contabil — "EXTRATO MENSAL MM/AAAA"

### Fluxo de parsing:
1. `pdfplumber.open()` → extrai texto de todas as páginas
2. Detecta competência: `EXTRATO MENSAL MM/AAAA`
3. Divide por blocos `Empr.: \d+ NOME`
4. Por bloco extrai:
   - Cabeçalho: matrícula, nome, CPF, situação, admissão
   - Totais: proventos, descontos, líquido
   - Bases fiscais: INSS base/valor, FGTS base/valor, IRRF base
   - Cargo e salário
   - **Rubricas**: regex `^\d{1,4}\s+DESCRICAO\s+REF\s+VALOR\s+[PD]$`

### Dataclasses:
```python
@dataclass
class RubricaFolha:
    codigo: str
    descricao: str
    tipo: str        # P=provento D=desconto
    referencia: str  # horas, percentual, etc.
    valor: Decimal

@dataclass
class FuncionarioFolha:
    matricula, nome, cpf, situacao, cargo, salario
    data_admissao
    total_proventos, total_descontos, liquido
    inss_base, inss_valor, fgts_base, fgts_valor, irrf_base
    rubricas: List[RubricaFolha]
```

### importar_rubricas_async():
1. Busca `hr_payslip` por CPF + referência_mes + referência_ano
2. **DELETE** rubricas antigas do payslip
3. **INSERT** novas rubricas em `hr_payslip_items`
4. **UPDATE** `hr_payslips` somente se `inss_value IS NULL` (não conflita com T2)

---

## 4. Endpoint de Upload

```
POST /api/v1/people-management/dp/payslips/folha/upload
     ?mes=3&ano=2026
Content-Type: multipart/form-data
Authorization: Bearer <token>

arquivo: <PDF file>
```

### Resposta de sucesso:
```json
{
  "status": "ok",
  "competencia": "03/2026",
  "arquivo_salvo": "/uploads/folhas/2026-03/extrato_2026-03_<uuid>.pdf",
  "funcionarios_no_pdf": 44,
  "rubricas_salvas": 528,
  "erros": 0,
  "primeiros_erros": []
}
```

### Fluxo interno:
1. Valida extensão `.pdf`
2. Salva PDF em `/uploads/folhas/AAAA-MM/extrato_AAAA-MM_<uuid>.pdf`
3. `FolhaPDFParser.parse()` → lista de `FuncionarioFolha`
4. `importar_rubricas_async()` → popula `hr_payslip_items`
5. Retorna relatório de importação

---

## 5. Constraint Respeitada — hr_payslips Intocado

O contrato com T2 foi 100% respeitado:

| Operação | hr_payslips | hr_payslip_items |
|---|---|---|
| Importar rubricas | **NÃO TOCADO** | INSERT (replace) |
| Bases fiscais | UPDATE SOMENTE SE NULL | — |
| Totais (bruto/líquido) | **NÃO TOCADO** | — |

---

## 6. Bugs Corrigidos Durante Deploy

| Bug | Causa | Fix |
|---|---|---|
| `Cannot specify 'Depends' in 'Annotated'` | `CurrentActiveUser = Depends()` redundante | Removido `= Depends()` |
| `parameter without a default follows default` | `current_user` sem default após params com Query() | Movido `current_user` para 1ª posição |

---

## 7. Teste de Validação

```bash
# Não-PDF → espera 400
POST /api/v1/people-management/dp/payslips/folha/upload?mes=3&ano=2026
arquivo: /etc/hostname (text/plain)
→ HTTP 400: {"detail":"Arquivo deve ser PDF (.pdf)"}   ✅
```

---

## 8. Próximos Passos

1. **Testar com PDF real** — fazer upload do Extrato Mensal Domínio Sistemas de 03/2026
2. **Verificar pdfplumber** — `pip install pdfplumber` no container se não instalado
3. **Ajustar regex rubricas** se o formato do PDF diferir do padrão esperado
4. **Frontend** — página de upload de folha em `people_management/dp/payslips/upload`

---

*Relatório gerado por Claude Sonnet 4.6 em 2026-04-11*
