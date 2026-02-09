# API Reference - Módulo Financeiro Conecta PRO

Documentação completa dos endpoints do módulo Financeiro do Conecta PRO.

**Base URL:** `/api/v1/financial`

---

## 📑 Índice

1. [Contas a Pagar](#-contas-a-pagar)
2. [Contas a Receber](#-contas-a-receber)
3. [Notas Fiscais (NF-e / NFS-e)](#-notas-fiscais)
4. [Relatórios BI](#-relatórios-bi)
5. [Fiscal - SPED e Retenções](#-fiscal)
6. [Contabilidade](#-contabilidade)

---

## 💰 Contas a Pagar

**Prefixo:** `/payables`

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/payables` | Criar conta a pagar |
| `GET` | `/payables` | Listar contas a pagar |
| `GET` | `/payables/{id}` | Obter conta específica |
| `PUT` | `/payables/{id}` | Atualizar conta |
| `DELETE` | `/payables/{id}` | Excluir conta |
| `POST` | `/payables/{id}/approve` | Aprovar conta |
| `POST` | `/payables/{id}/reject` | Rejeitar conta |
| `POST` | `/payables/{id}/cancel` | Cancelar conta |
| `POST` | `/payables/{id}/restore` | Restaurar conta |
| `POST` | `/payables/{id}/duplicate` | Duplicar conta |
| `GET` | `/payables/{id}/installments` | Listar parcelas |
| `POST` | `/payables/{id}/installments` | Gerar parcelas |
| `PUT` | `/payables/{id}/installments/{installment_id}` | Atualizar parcela |
| `POST` | `/payables/{id}/installments/{installment_id}/pay` | Pagar parcela |
| `POST` | `/payables/{id}/installments/{installment_id}/renegotiate` | Renegociar parcela |
| `POST` | `/payables/bulk/approve` | Aprovação em lote |
| `POST` | `/payables/bulk/pay` | Pagamento em lote |
| `GET` | `/payables/stats/summary` | Estatísticas resumidas |
| `GET` | `/payables/stats/aging` | Relatório aging |
| `GET` | `/payables/stats/by-category` | Estatísticas por categoria |
| `POST` | `/payables/schedule` | Agendamento de pagamentos |

### Exemplo: Criar Conta a Pagar

```http
POST /api/v1/financial/payables
Content-Type: application/json
Authorization: Bearer {token}

{
  "condominio_id": "550e8400-e29b-41d4-a716-446655440000",
  "description": "Serviço de Limpeza - Janeiro 2026",
  "document_number": "NF-001234",
  "payable_type": "AVULSA",
  "priority": "MEDIA",
  "supplier_id": "660e8400-e29b-41d4-a716-446655440001",
  "category_id": "770e8400-e29b-41d4-a716-446655440002",
  "gross_value": "5000.00",
  "discount_value": "0.00",
  "addition_value": "0.00",
  "withhold_iss": "250.00",
  "withhold_ir": "0.00",
  "withhold_pis": "0.00",
  "withhold_cofins": "0.00",
  "withhold_csll": "0.00",
  "withhold_inss": "0.00",
  "due_date": "2026-02-10",
  "issue_date": "2026-01-15",
  "competence_date": "2026-01-01",
  "total_installments": 1,
  "is_recurring": false,
  "cost_center": "ADMINISTRATIVO",
  "project": "MANUTENCAO_2026",
  "fiscal_document_type": "NFSE",
  "fiscal_document_key": "12345678901234567890123456789012345678901234",
  "payment_method_id": "880e8400-e29b-41d4-a716-446655440003",
  "bank_account_id": "990e8400-e29b-41d4-a716-446655440004",
  "requires_approval": true,
  "tags": ["limpeza", "janeiro", "fornecedor-regular"],
  "notes": "Pagamento referente ao serviço de limpeza do mês de janeiro"
}
```

**Resposta (201 Created):**

```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440005",
  "condominio_id": "550e8400-e29b-41d4-a716-446655440000",
  "code": "CP-2026-0001",
  "description": "Serviço de Limpeza - Janeiro 2026",
  "document_number": "NF-001234",
  "status": "PENDENTE",
  "payable_type": "AVULSA",
  "priority": "MEDIA",
  "supplier_id": "660e8400-e29b-41d4-a716-446655440001",
  "category_id": "770e8400-e29b-41d4-a716-446655440002",
  "gross_value": "5000.00",
  "discount_value": "0.00",
  "addition_value": "0.00",
  "net_value": "5000.00",
  "total_withholdings": "250.00",
  "paid_value": "0.00",
  "remaining_value": "4750.00",
  "due_date": "2026-02-10",
  "issue_date": "2026-01-15",
  "competence_date": "2026-01-01",
  "entry_date": "2026-01-20",
  "current_installment": 1,
  "total_installments": 1,
  "is_recurring": false,
  "requires_approval": true,
  "created_at": "2026-01-20T10:30:00Z",
  "updated_at": "2026-01-20T10:30:00Z"
}
```

### Exemplo: Listar Contas com Filtros

```http
GET /api/v1/financial/payables?condominio_id=550e8400-e29b-41d4-a716-446655440000&status=PENDENTE&is_overdue=true&limit=50
Authorization: Bearer {token}
```

**Parâmetros de Query:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `condominio_id` | UUID | **Obrigatório** - ID do condomínio |
| `search` | string | Busca na descrição |
| `supplier_id` | UUID | Filtrar por fornecedor |
| `category_id` | UUID | Filtrar por categoria |
| `status` | string | Status (PENDENTE, APROVADO, PAGO, CANCELADO) |
| `due_date_start` | date | Vencimento inicial (YYYY-MM-DD) |
| `due_date_end` | date | Vencimento final (YYYY-MM-DD) |
| `is_recurring` | boolean | Apenas recorrentes |
| `is_overdue` | boolean | Apenas vencidas |
| `min_value` | number | Valor mínimo |
| `max_value` | number | Valor máximo |
| `skip` | integer | Registros a pular (padrão: 0) |
| `limit` | integer | Limite de registros (padrão: 100, max: 500) |

---

## 💳 Contas a Receber

**Prefixo:** `/receivables`

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/receivables` | Criar conta a receber |
| `GET` | `/receivables` | Listar contas a receber |
| `GET` | `/receivables/{id}` | Obter conta específica |
| `PUT` | `/receivables/{id}` | Atualizar conta |
| `DELETE` | `/receivables/{id}` | Excluir conta |
| `POST` | `/receivables/{id}/approve` | Aprovar conta |
| `POST` | `/receivables/{id}/cancel` | Cancelar conta |
| `POST` | `/receivables/{id}/restore` | Restaurar conta |
| `POST` | `/receivables/{id}/duplicate` | Duplicar conta |
| `GET` | `/receivables/{id}/installments` | Listar parcelas |
| `POST` | `/receivables/{id}/installments/{installment_id}/boleto` | Gerar boleto |
| `POST` | `/receivables/{id}/installments/{installment_id}/pix` | Gerar PIX |
| `POST` | `/receivables/{id}/installments/{installment_id}/pay` | Registrar pagamento |
| `POST` | `/receivables/{id}/installments/{installment_id}/renegotiate` | Renegociar |
| `POST` | `/receivables/{id}/installments/{installment_id}/protest` | Protestar |
| `POST` | `/receivables/{id}/installments/{installment_id}/write-off` | Baixa por perda |
| `POST` | `/receivables/bulk/boleto` | Geração em lote de boletos |
| `POST` | `/receivables/bulk/notify` | Notificação em lote |
| `POST` | `/receivables/bulk/pay` | Recebimento em lote |
| `GET` | `/receivables/stats/summary` | Estatísticas resumidas |
| `GET` | `/receivables/stats/inadimplencia` | Relatório de inadimplência |
| `GET` | `/receivables/stats/aging` | Análise aging |
| `POST` | `/receivables/agreement` | Acordo de pagamento |

### Exemplo: Criar Conta a Receber

```http
POST /api/v1/financial/receivables
Content-Type: application/json
Authorization: Bearer {token}

{
  "condominio_id": "550e8400-e29b-41d4-a716-446655440000",
  "description": "Taxa Condominial - Janeiro 2026",
  "document_number": "COBRANCA-001",
  "receivable_type": "MENSALIDADE",
  "priority": "ALTA",
  "customer_id": "660e8400-e29b-41d4-a716-446655440001",
  "unidade_id": "770e8400-e29b-41d4-a716-446655440002",
  "category_id": "880e8400-e29b-41d4-a716-446655440003",
  "gross_value": "850.00",
  "discount_value": "0.00",
  "addition_value": "25.00",
  "interest_rate": "0.033",
  "fine_rate": "0.02",
  "due_date": "2026-02-10",
  "issue_date": "2026-01-25",
  "competence_date": "2026-01-01",
  "total_installments": 1,
  "is_recurring": true,
  "recurrence_type": "MENSAL",
  "recurrence_end_date": "2026-12-31",
  "cost_center": "ADMINISTRATIVO",
  "generate_boleto": true,
  "boleto_config_id": "990e8400-e29b-41d4-a716-446655440004",
  "auto_notify": true,
  "tags": ["taxa-condominial", "janeiro", "apto-101"],
  "notes": "Taxa condominial referente ao mês de janeiro de 2026"
}
```

**Resposta (201 Created):**

```json
{
  "id": "bb0e8400-e29b-41d4-a716-446655440006",
  "condominio_id": "550e8400-e29b-41d4-a716-446655440000",
  "code": "CR-2026-0001",
  "description": "Taxa Condominial - Janeiro 2026",
  "document_number": "COBRANCA-001",
  "status": "PENDENTE",
  "receivable_type": "MENSALIDADE",
  "priority": "ALTA",
  "customer_id": "660e8400-e29b-41d4-a716-446655440001",
  "unidade_id": "770e8400-e29b-41d4-a716-446655440002",
  "category_id": "880e8400-e29b-41d4-a716-446655440003",
  "gross_value": "850.00",
  "discount_value": "0.00",
  "addition_value": "25.00",
  "interest_rate": "0.033",
  "fine_rate": "0.02",
  "net_value": "875.00",
  "paid_value": "0.00",
  "remaining_value": "875.00",
  "due_date": "2026-02-10",
  "issue_date": "2026-01-25",
  "competence_date": "2026-01-01",
  "entry_date": "2026-01-25",
  "current_installment": 1,
  "total_installments": 1,
  "is_recurring": true,
  "recurrence_type": "MENSAL",
  "recurrence_end_date": "2026-12-31",
  "auto_notify": true,
  "created_at": "2026-01-25T14:00:00Z",
  "updated_at": "2026-01-25T14:00:00Z"
}
```

### Exemplo: Gerar Boleto

```http
POST /api/v1/financial/receivables/bb0e8400-e29b-41d4-a716-446655440006/installments/cc0e8400-e29b-41d4-a716-446655440007/boleto
Content-Type: application/json
Authorization: Bearer {token}

{
  "instruction_line_1": "Não receber após o vencimento",
  "instruction_line_2": "Multa de 2% após o vencimento",
  "instruction_line_3": "Juros de 0,033% ao dia",
  "expiration_days": 30
}
```

---

## 📄 Notas Fiscais

**Prefixo:** `/fiscal`

### NF-e (Nota Fiscal Eletrônica)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/fiscal/nfe` | Criar NF-e |
| `GET` | `/fiscal/nfe` | Listar NF-e |
| `GET` | `/fiscal/nfe/{nfe_id}` | Obter NF-e |
| `GET` | `/fiscal/nfe/chave/{chave_acesso}` | Buscar por chave |
| `PATCH` | `/fiscal/nfe/{nfe_id}` | Atualizar NF-e |
| `POST` | `/fiscal/nfe/emitir` | Emitir NF-e |
| `POST` | `/fiscal/nfe/cancelar` | Cancelar NF-e |
| `POST` | `/fiscal/nfe/inutilizar` | Inutilizar numeração |

### NFS-e (Nota Fiscal de Serviços Eletrônica)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/fiscal/nfse` | Criar NFS-e |
| `GET` | `/fiscal/nfse` | Listar NFS-e |
| `GET` | `/fiscal/nfse/{nfse_id}` | Obter NFS-e |
| `PATCH` | `/fiscal/nfse/{nfse_id}` | Atualizar NFS-e |
| `POST` | `/fiscal/nfse/emitir` | Emitir NFS-e |
| `POST` | `/fiscal/nfse/cancelar` | Cancelar NFS-e |
| `GET` | `/fiscal/nfse/retencoes/competencia` | Retenções por competência |

### CFOP e NCM

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/fiscal/cfop` | Criar CFOP |
| `GET` | `/fiscal/cfop` | Listar CFOPs |
| `GET` | `/fiscal/cfop/{cfop_id}` | Obter CFOP |
| `GET` | `/fiscal/cfop/codigo/{codigo}` | Buscar por código |
| `PATCH` | `/fiscal/cfop/{cfop_id}` | Atualizar CFOP |
| `POST` | `/fiscal/ncm` | Criar NCM |
| `GET` | `/fiscal/ncm` | Listar NCMs |
| `GET` | `/fiscal/ncm/{ncm_id}` | Obter NCM |
| `GET` | `/fiscal/ncm/codigo/{codigo}` | Buscar por código |
| `PATCH` | `/fiscal/ncm/{ncm_id}` | Atualizar NCM |

### Exemplo: Emitir NF-e

```http
POST /api/v1/financial/fiscal/nfe/emitir
Content-Type: application/json
Authorization: Bearer {token}

{
  "condominio_id": "550e8400-e29b-41d4-a716-446655440000",
  "natureza_operacao": "Venda de mercadoria",
  "forma_pagamento": "0",
  "modelo": "55",
  "serie": "1",
  "numero": 1234,
  "data_emissao": "2026-01-20T10:00:00-04:00",
  "data_saida_entrada": "2026-01-20T10:00:00-04:00",
  "tipo_documento": "1",
  "finalidade_emissao": "1",
  "consumidor_final": "1",
  "presenca_comprador": "1",
  "emitente": {
    "cnpj": "12345678000195",
    "razao_social": "CONDOMINIO RESIDENCIAL EXEMPLO",
    "nome_fantasia": "CONDOMINIO EXEMPLO",
    "endereco": {
      "logradouro": "Rua das Flores",
      "numero": "100",
      "complemento": "Bloco A",
      "bairro": "Centro",
      "codigo_municipio": "1302603",
      "municipio": "Manaus",
      "uf": "AM",
      "cep": "69000000",
      "codigo_pais": "1058",
      "pais": "BRASIL",
      "fone": "92999999999"
    }
  },
  "destinatario": {
    "cnpj": "98765432000196",
    "razao_social": "EMPRESA COMPRADORA LTDA",
    "endereco": {
      "logradouro": "Av. Principal",
      "numero": "500",
      "bairro": "Industrial",
      "codigo_municipio": "1302603",
      "municipio": "Manaus",
      "uf": "AM",
      "cep": "69000001"
    }
  },
  "itens": [
    {
      "numero_item": 1,
      "codigo": "PROD-001",
      "descricao": "Produto de Exemplo",
      "ncm": "8471.60.10",
      "cfop": "5102",
      "unidade_comercial": "UN",
      "quantidade_comercial": 10.0000,
      "valor_unitario_comercial": 100.0000,
      "valor_total": 1000.00,
      "impostos": {
        "icms": {
          "origem": "0",
          "cst": "00",
          "modalidade_bc": "3",
          "valor_bc_icms": 1000.00,
          "aliquota_icms": 18.00,
          "valor_icms": 180.00
        },
        "ipi": {
          "cst": "50",
          "valor_bc_ipi": 1000.00,
          "aliquota_ipi": 5.00,
          "valor_ipi": 50.00
        },
        "pis": {
          "cst": "01",
          "valor_bc_pis": 1000.00,
          "aliquota_pis": 1.65,
          "valor_pis": 16.50
        },
        "cofins": {
          "cst": "01",
          "valor_bc_cofins": 1000.00,
          "aliquota_cofins": 7.60,
          "valor_cofins": 76.00
        }
      }
    }
  ],
  "total_icms": 180.00,
  "total_ipi": 50.00,
  "total_pis": 16.50,
  "total_cofins": 76.00,
  "total_produtos": 1000.00,
  "total_impostos": 322.50,
  "total_nota": 1000.00,
  "informacoes_adicionais": "Documento emitido em ambiente de teste"
}
```

**Resposta (200 OK):**

```json
{
  "success": true,
  "nfe_id": "dd0e8400-e29b-41d4-a716-446655440008",
  "chave_acesso": "13260123456780001965550010000012341234567890",
  "numero_protocolo": "113200123456789",
  "data_protocolo": "2026-01-20T10:05:30-04:00",
  "status": "AUTORIZADA",
  "xml_autorizado": "<?xml version=\"1.0\"...",
  "danfe_url": "https://api.conecta.pro/danfe/13260123456780001965550010000012341234567890.pdf"
}
```

### Exemplo: Emitir NFS-e

```http
POST /api/v1/financial/fiscal/nfse/emitir
Content-Type: application/json
Authorization: Bearer {token}

{
  "condominio_id": "550e8400-e29b-41d4-a716-446655440000",
  "prestador": {
    "cnpj": "12345678000195",
    "inscricao_municipal": "123456",
    "razao_social": "CONDOMINIO RESIDENCIAL EXEMPLO"
  },
  "tomador": {
    "cnpj": "98765432000196",
    "razao_social": "EMPRESA TOMADORA LTDA",
    "endereco": {
      "logradouro": "Av. Principal",
      "numero": "500",
      "bairro": "Industrial",
      "cidade": "Manaus",
      "uf": "AM",
      "cep": "69000001"
    }
  },
  "servico": {
    "codigo": "17.22",
    "descricao": "Serviços de vigilância, segurança ou monitoramento de bens e pessoas",
    "aliquota": 5.0,
    "valor_servicos": 5000.00,
    "valor_deducoes": 0.00,
    "valor_pis": 0.00,
    "valor_cofins": 0.00,
    "valor_inss": 0.00,
    "valor_ir": 0.00,
    "valor_csll": 0.00,
    "iss_retido": false,
    "valor_iss": 250.00,
    "outras_retencoes": 0.00,
    "base_calculo": 5000.00,
    "valor_liquido": 5000.00
  },
  "competencia": "2026-01",
  "data_emissao": "2026-01-20",
  "discriminacao": "Serviços de vigilância prestados no período de janeiro/2026",
  "observacao": "Zona Franca de Manaus - Isenção conforme Lei 10.637/2002"
}
```

---

## 📊 Relatórios BI

**Prefixo:** `/bi`

### Dashboards

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/bi/dashboards` | Criar dashboard |
| `GET` | `/bi/dashboards` | Listar dashboards |
| `GET` | `/bi/dashboards/{dashboard_id}` | Obter dashboard |
| `PUT` | `/bi/dashboards/{dashboard_id}` | Atualizar dashboard |
| `DELETE` | `/bi/dashboards/{dashboard_id}` | Excluir dashboard |
| `POST` | `/bi/dashboards/{dashboard_id}/publish` | Publicar dashboard |
| `POST` | `/bi/dashboards/{dashboard_id}/archive` | Arquivar dashboard |
| `POST` | `/bi/dashboards/{dashboard_id}/favorite` | Favoritar dashboard |
| `POST` | `/bi/dashboards/{dashboard_id}/set-default` | Definir como padrão |
| `GET` | `/bi/dashboards/default` | Dashboard padrão |
| `POST` | `/bi/dashboards/{dashboard_id}/duplicate` | Duplicar dashboard |
| `GET` | `/bi/dashboards/{dashboard_id}/widgets` | Listar widgets do dashboard |

### Widgets

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/bi/widgets` | Criar widget |
| `GET` | `/bi/widgets` | Listar widgets |
| `GET` | `/bi/widgets/{widget_id}` | Obter widget |
| `PUT` | `/bi/widgets/{widget_id}` | Atualizar widget |
| `DELETE` | `/bi/widgets/{widget_id}` | Excluir widget |
| `GET` | `/bi/widgets/{widget_id}/data` | Obter dados do widget |
| `POST` | `/bi/widgets/{widget_id}/refresh` | Atualizar dados |
| `PUT` | `/bi/widgets/{widget_id}/position` | Atualizar posição |
| `PUT` | `/bi/widgets/{widget_id}/visibility` | Alterar visibilidade |
| `POST` | `/bi/widgets/{widget_id}/clone` | Clonar widget |

### KPIs

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/bi/kpis` | Criar KPI |
| `GET` | `/bi/kpis` | Listar KPIs |
| `GET` | `/bi/kpis/{kpi_id}` | Obter KPI |
| `PUT` | `/bi/kpis/{kpi_id}` | Atualizar KPI |
| `DELETE` | `/bi/kpis/{kpi_id}` | Excluir KPI |
| `POST` | `/bi/kpis/{kpi_id}/calculate` | Calcular KPI |
| `GET` | `/bi/kpis/{kpi_id}/history` | Histórico do KPI |
| `GET` | `/bi/kpis/summary` | Resumo de KPIs |
| `GET` | `/bi/kpis/alerts` | KPIs com alertas |
| `GET` | `/bi/kpis/stats` | Estatísticas de KPIs |
| `POST` | `/bi/kpis/calculate-all` | Calcular todos os KPIs |

### Relatórios Agendados

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/bi/reports` | Criar relatório |
| `GET` | `/bi/reports` | Listar relatórios |
| `GET` | `/bi/reports/{report_id}` | Obter relatório |
| `PUT` | `/bi/reports/{report_id}` | Atualizar relatório |
| `DELETE` | `/bi/reports/{report_id}` | Excluir relatório |
| `POST` | `/bi/reports/{report_id}/pause` | Pausar relatório |
| `POST` | `/bi/reports/{report_id}/resume` | Retomar relatório |
| `POST` | `/bi/reports/{report_id}/execute` | Executar relatório |
| `GET` | `/bi/reports/due` | Relatórios pendentes |

### Analytics e Previsões

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/bi/analytics/anomalies` | Detectar anomalias |
| `POST` | `/bi/analytics/trend` | Análise de tendência |
| `POST` | `/bi/analytics/distribution` | Análise de distribuição |
| `POST` | `/bi/analytics/growth-rate` | Taxa de crescimento |
| `POST` | `/bi/analytics/suggest-targets` | Sugerir metas |
| `POST` | `/bi/analytics/variance` | Análise de variância |
| `POST` | `/bi/forecast/generate` | Gerar previsão |
| `POST` | `/bi/forecast/moving-average` | Média móvel |
| `POST` | `/bi/forecast/break-even` | Ponto de equilíbrio |
| `POST` | `/bi/forecast/cash-flow-projection` | Projeção de fluxo de caixa |
| `POST` | `/bi/forecast/npv` | Valor presente líquido |
| `POST` | `/bi/forecast/payback` | Payback |
| `GET` | `/bi/summary/financial` | Resumo financeiro |
| `GET` | `/bi/summary/compare` | Comparativo |

### Exemplo: Criar Dashboard

```http
POST /api/v1/financial/bi/dashboards
Content-Type: application/json
Authorization: Bearer {token}

{
  "condominio_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Dashboard Financeiro - Gestão de Caixa",
  "description": "Visão geral do fluxo de caixa e indicadores financeiros",
  "type": "FINANCEIRO",
  "layout": "GRID",
  "widgets": [
    {
      "type": "KPICARD",
      "title": "Saldo em Caixa",
      "position": {"x": 0, "y": 0, "w": 3, "h": 2},
      "config": {
        "kpi_id": "saldo-caixa",
        "refresh_interval": 300
      }
    },
    {
      "type": "CHART_LINE",
      "title": "Fluxo de Caixa - 12 Meses",
      "position": {"x": 3, "y": 0, "w": 9, "h": 4},
      "config": {
        "data_source": "cashflow_monthly",
        "series": ["receitas", "despesas", "saldo"]
      }
    }
  ]
}
```

**Resposta (201 Created):**

```json
{
  "id": "ee0e8400-e29b-41d4-a716-446655440009",
  "condominio_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Dashboard Financeiro - Gestão de Caixa",
  "description": "Visão geral do fluxo de caixa e indicadores financeiros",
  "type": "FINANCEIRO",
  "layout": "GRID",
  "status": "DRAFT",
  "is_default": false,
  "is_favorite": false,
  "created_at": "2026-01-20T15:00:00Z",
  "updated_at": "2026-01-20T15:00:00Z"
}
```

### Exemplo: Obter Dados de Widget

```http
GET /api/v1/financial/bi/widgets/ff0e8400-e29b-41d4-a716-446655440010/data
Authorization: Bearer {token}
```

**Resposta (200 OK):**

```json
{
  "widget_id": "ff0e8400-e29b-41d4-a716-446655440010",
  "title": "Receitas vs Despesas",
  "type": "CHART_BAR",
  "data": {
    "labels": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"],
    "datasets": [
      {
        "label": "Receitas",
        "data": [45000, 48000, 47000, 51000, 49000, 52000],
        "color": "#4CAF50"
      },
      {
        "label": "Despesas",
        "data": [38000, 40000, 39000, 42000, 41000, 43000],
        "color": "#F44336"
      }
    ]
  },
  "generated_at": "2026-01-20T15:30:00Z"
}
```

### Exemplo: Projeção de Fluxo de Caixa

```http
POST /api/v1/financial/bi/forecast/cash-flow-projection
Content-Type: application/json
Authorization: Bearer {token}

{
  "condominio_id": "550e8400-e29b-41d4-a716-446655440000",
  "months": 12,
  "consider_seasonality": true,
  "confidence_level": 0.95,
  "include_scenarios": ["optimistic", "realistic", "pessimistic"]
}
```

**Resposta (200 OK):**

```json
{
  "projection_period": {
    "start": "2026-02-01",
    "end": "2027-01-31"
  },
  "scenarios": {
    "realistic": {
      "opening_balance": 125000.00,
      "total_receivables": 584000.00,
      "total_payables": 498000.00,
      "closing_balance": 211000.00,
      "min_monthly_balance": 98000.00,
      "months": [
        {
          "month": "2026-02",
          "opening": 125000.00,
          "receivables": 48000.00,
          "payables": 41000.00,
          "closing": 132000.00
        }
      ]
    },
    "optimistic": {
      "closing_balance": 245000.00
    },
    "pessimistic": {
      "closing_balance": 175000.00
    }
  },
  "alerts": [
    {
      "type": "LOW_BALANCE",
      "month": "2026-06",
      "message": "Saldo projetado abaixo do mínimo recomendado"
    }
  ]
}
```

---

## 🏛️ Fiscal

### SPED Fiscal

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/fiscal/sped` | Criar arquivo SPED |
| `GET` | `/fiscal/sped` | Listar arquivos |
| `GET` | `/fiscal/sped/{sped_id}` | Obter arquivo |
| `POST` | `/fiscal/sped/gerar` | Gerar arquivo |
| `POST` | `/fiscal/sped/{sped_id}/validar` | Validar arquivo |
| `POST` | `/fiscal/sped/{sped_id}/transmitir` | Transmitir arquivo |

### Obrigações Fiscais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/fiscal/obrigacao` | Criar obrigação |
| `GET` | `/fiscal/obrigacao` | Listar obrigações |
| `GET` | `/fiscal/obrigacao/pendentes` | Obrigações pendentes |
| `GET` | `/fiscal/obrigacao/atrasadas` | Obrigações atrasadas |
| `GET` | `/fiscal/obrigacao/{obrigacao_id}` | Obter obrigação |
| `PATCH` | `/fiscal/obrigacao/{obrigacao_id}` | Atualizar obrigação |

### Retenções

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/fiscal/retencao` | Criar retenção |
| `GET` | `/fiscal/retencao` | Listar retenções |
| `GET` | `/fiscal/retencao/{retencao_id}` | Obter retenção |
| `PATCH` | `/fiscal/retencao/{retencao_id}` | Atualizar retenção |
| `POST` | `/fiscal/retencao/calcular` | Calcular retenção |

### DAS Simples Nacional

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/fiscal/das` | Criar DAS |
| `GET` | `/fiscal/das` | Listar DAS |
| `GET` | `/fiscal/das/competencia` | DAS por competência |
| `POST` | `/fiscal/das/calcular` | Calcular DAS |
| `GET` | `/fiscal/das/faixas` | Faixas do Simples |
| `GET` | `/fiscal/das/receita-12-meses` | Receita 12 meses |

### SUFRAMA (ZFM)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/fiscal/suframa/config` | Configurar SUFRAMA |
| `GET` | `/fiscal/suframa/config` | Obter configuração |
| `POST` | `/fiscal/suframa/operacoes` | Registrar operação |
| `GET` | `/fiscal/suframa/operacoes` | Listar operações |
| `GET` | `/fiscal/suframa/economia` | Economia gerada |

### Exemplo: Calcular Retenções

```http
POST /api/v1/financial/fiscal/retencao/calcular
Content-Type: application/json
Authorization: Bearer {token}

{
  "valor_bruto": 10000.00,
  "tipo_servico": "LIMPEZA",
  "retencao_iss": true,
  "retencao_inss": true,
  "retencao_ir": true,
  "retencao_pis": true,
  "retencao_cofins": true,
  "retencao_csll": true,
  "regime_tributario": "SIMPLES_NACIONAL"
}
```

**Resposta (200 OK):**

```json
{
  "valor_bruto": 10000.00,
  "retencoes": {
    "iss": 500.00,
    "inss": 110.00,
    "ir": 150.00,
    "pis": 65.00,
    "cofins": 300.00,
    "csll": 100.00
  },
  "total_retencoes": 1225.00,
  "valor_liquido": 8775.00,
  "aliquotas_aplicadas": {
    "iss": 5.0,
    "inss": 11.0,
    "ir": 1.5,
    "pis": 0.65,
    "cofins": 3.0,
    "csll": 1.0
  }
}
```

---

## 📒 Contabilidade

**Prefixo:** `/accounting`

### Plano de Contas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/accounting/charts` | Listar planos de contas |
| `GET` | `/accounting/charts/active` | Plano ativo |
| `GET` | `/accounting/charts/stats` | Estatísticas |
| `POST` | `/accounting/charts` | Criar plano |
| `GET` | `/accounting/charts/{chart_id}` | Obter plano |
| `PATCH` | `/accounting/charts/{chart_id}` | Atualizar plano |
| `POST` | `/accounting/charts/{chart_id}/activate` | Ativar plano |

### Contas Contábeis

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/accounting/accounts` | Listar contas |
| `GET` | `/accounting/accounts/tree` | Estrutura em árvore |
| `GET` | `/accounting/accounts/stats` | Estatísticas |
| `POST` | `/accounting/accounts` | Criar conta |
| `GET` | `/accounting/accounts/{account_id}` | Obter conta |
| `PATCH` | `/accounting/accounts/{account_id}` | Atualizar conta |
| `GET` | `/accounting/accounts/{account_id}/balance` | Saldo da conta |

### Lançamentos Contábeis

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/accounting/journal-entries` | Listar lançamentos |
| `GET` | `/accounting/journal-entries/pending-approval` | Pendentes |
| `GET` | `/accounting/journal-entries/stats` | Estatísticas |
| `POST` | `/accounting/journal-entries` | Criar lançamento |
| `GET` | `/accounting/journal-entries/{entry_id}` | Obter lançamento |
| `GET` | `/accounting/journal-entries/{entry_id}/lines` | Linhas do lançamento |
| `POST` | `/accounting/journal-entries/{entry_id}/post` | Efetivar |
| `POST` | `/accounting/journal-entries/{entry_id}/approve` | Aprovar |
| `POST` | `/accounting/journal-entries/{entry_id}/reject` | Rejeitar |
| `POST` | `/accounting/journal-entries/{entry_id}/reverse` | Estornar |

### Períodos Contábeis

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/accounting/periods` | Listar períodos |
| `GET` | `/accounting/periods/current` | Período atual |
| `GET` | `/accounting/periods/stats` | Estatísticas |
| `POST` | `/accounting/periods` | Criar período |
| `GET` | `/accounting/periods/{period_id}` | Obter período |
| `POST` | `/accounting/periods/{period_id}/open` | Abrir |
| `POST` | `/accounting/periods/{period_id}/close` | Fechar |
| `POST` | `/accounting/periods/{period_id}/reopen` | Reabrir |

---

## 🔐 Autenticação

Todos os endpoints requerem autenticação via Bearer Token JWT:

```http
Authorization: Bearer <access_token>
```

## ⚠️ Códigos de Erro

| Código | Descrição |
|--------|-----------|
| `400` | Requisição inválida |
| `401` | Não autorizado |
| `403` | Proibido (sem permissão) |
| `404` | Recurso não encontrado |
| `409` | Conflito (recurso já existe) |
| `422` | Erro de validação |
| `429` | Muitas requisições |
| `500` | Erro interno do servidor |

## 📄 Paginação

Endpoints de listagem retornam resultados paginados:

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}
```

---

**Documentação gerada em:** 2026-01-20
**Versão da API:** 1.0.0
