---
title: Módulo Financeiro
description: 483 endpoints de gestão financeira do Conecta PRO
endpoints: 483
modules: [faturamento, contas, boletos, notas_fiscais]
---

# Módulo Financeiro

Gestão financeira completa para empresas de vigilância e segurança.

## Módulos Principais

| Módulo | Endpoints | Descrição |
|--------|-----------|-----------|
| faturamento | 127 | Gestão de faturas e recibos |
| contas_pagar | 89 | Fornecedores e despesas |
| contas_receber | 94 | Clientes e receitas |
| boletos | 67 | Emissão e registro |
| notas_fiscais | 106 | NF-e, NFS-e, NFC-e |

## Comandos de Desenvolvimento

```bash
# Gerar API client
npx orval --filter financial

# Rodar testes do módulo
pytest tests/financial/ -v --tb=short

# Migrações
alembic revision -m "add_coluna_desconto_fatura" --autogenerate
```

## Fluxos de Negócio

### Faturamento de Contrato
```
Contrato Vigilância
    ↓
Cálculo (valor posto × qtde × dias)
    ↓
Geração Fatura (mensal/bimestral)
    ↓
Emissão NF-e (automática/manual)
    ↓
Envio Boleto (email/integração bancária)
```

### Contas a Pagar
```
Ordem de Serviço
    ↓
Aprovação (workflow)
    ↓
Agendamento Pagamento
    ↓
Integração Bancária (CNAB 240)
    ↓
Conciliação
```

## Integrações Bancárias

```python
# Bancos suportados
SANTANDER = "santander"
ITAU = "itau"
BRADESCO = "bradesco"
NU_PAGAMENTOS = "nubank"
PIX = "pix"

# CNAB
CNAB_240 = "cnab240"
CNAB_400 = "cnab400"
```

## Checklist de Implementação

- [ ] Regras de negócio validadas com contabilidade
- [ ] Cálculos tributários corretos
- [ ] Integrações bancárias testadas
- [ ] Relatórios contábeis aprovados
- [ ] Auditoria LGPD implementada
- [ ] Conciliação automática configurada
