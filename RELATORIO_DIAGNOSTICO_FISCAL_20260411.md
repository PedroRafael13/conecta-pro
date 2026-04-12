# Relatório de Diagnóstico — Módulos Fiscais
**Data:** 2026-04-11
**Auditor:** Claude Sonnet 4.6
**Script:** Diagnóstico fiscal (módulos + endpoints + tabelas + Bling)

---

## 1. Módulos Fiscais Existentes

| Módulo | Status |
|---|---|
| `modules/fiscal/` | Básico (controllers + services) |
| `modules/fiscal_contabil/` | Completo — 10 sub-módulos |
| `fiscal_contabil/notas_fiscais/nfe/` | **VAZIO** — só `__init__.py` |
| `fiscal_contabil/notas_fiscais/nfse/` | **VAZIO** — só `__init__.py` |
| `fiscal_contabil/notas_fiscais/nfce/` | **VAZIO** — só `__init__.py` |
| `fiscal_contabil/sped/` | Diretório existe |
| `fiscal_contabil/obrigacoes/` | Diretório existe |
| `fiscal_contabil/impostos/` | Diretório existe |
| `fiscal_contabil/contabilidade/` | Diretório existe |
| `fiscal_contabil/demonstracoes/` | Diretório existe |
| `fiscal_contabil/faturamento/` | Diretório existe |
| `fiscal_contabil/exportacao/` | Diretório existe |
| `fiscal_contabil/agents/` | Diretório existe |
| `government_integrations/extractors/sefaz/` | Extractor SEFAZ presente |
| `government_integrations/extractors/sefaz_am/` | Extractor SEFAZ-AM presente |

---

## 2. Endpoints Fiscais Ativos

| Método | Endpoint | Descrição | Status |
|---|---|---|---|
| `POST` | `/api/v1/financial/nfse/emitir` | NFS-e saída ABRASF 2.04 | ✅ Funcional |
| `POST` | `/api/v1/government/nfse-nacional/emitir` | NFS-e Padrão Nacional | ✅ Funcional (E0006 semântico) |
| `GET` | `/api/v1/financial/nfse-entrada` | Listar NFS-e recebidas | ✅ |
| `GET` | `/api/v1/financial/nfse-entrada/resumo-fiscal` | Resumo fiscal | ✅ |
| `GET` | `/api/v1/financial/fiscal/stats-real` | Stats fiscais reais | ✅ |
| `POST` | `/api/v1/government/sefaz/nfe/emitir` | Emitir NFe layout 4.00 | ⚠️ Stub |
| `*` | `/api/v1/government/sefaz-am/*` | SEFAZ-AM (Amazonas) | ⚠️ A validar |
| `*` | `/api/v1/government/sped-fiscal/*` | SPED Fiscal | ⚠️ A validar |
| `GET` | `/api/v1/fiscal/*` | NFS-e Multi-Empresa | ⚠️ A validar |

---

## 3. Tabelas Fiscais no Banco

### 3a. NFS-e

| Tabela | Registros | Campos principais |
|---|---|---|
| `nfse_entrada` | **9** | prestador_cnpj, prestador_nome, valor_servico, valor_iss, iss_retido, retencao_inss, retencao_irrf, retencao_csll, arquivo_pdf_path, payable_id, status, categoria |
| `nfses` (saída) | 27 | numero_nfse, codigo_verificacao, xml_enviado, xml_retorno, status, data_processamento |

### 3b. NF-e Produto

| Tabela | Campos principais |
|---|---|
| `nfes` | emitente_cnpj, destinatario_cpf_cnpj, chave_acesso (44), serie, numero, natureza_operacao, data_emissao, crt, uf, transportadora |
| `nfe_itens` | nfe_id, codigo_produto, descricao, ncm (8), cfop (4), unidade, quantidade, valor_unitario, valor_total, icms_cst, icms_csosn, icms_base_calculo |

### 3c. Compras e Estoque

| Tabela | Descrição |
|---|---|
| `suppliers` | Fornecedores |
| `purchase_requisitions` + `_items` | Requisições de compra |
| `purchase_quotations` + `_items` | Cotações |
| `purchase_orders` + `_items` | Pedidos de compra |
| `goods_receipts` + `_items` | Recebimento de mercadorias |
| `fin_stock_items` | Estoque WMS (qty on hand, reserved, committed, avg cost, unit cost) |
| `fin_stock_inventory_items` | Inventário de estoque |

### 3d. Obrigações Fiscais

| Tipo | Registros |
|---|---|
| IRRF | 3 |
| INSS | 3 |
| ESOCIAL | 3 |
| EFD_REINF | 3 |
| ISS | 3 |
| FGTS | 3 |
| DCTFWEB | 3 |
| DIRF | 1 |
| RAIS | 1 |

---

## 4. Bling — Status Real

A migration `sprint32_create_integrations_tables.py` registra `bling` como valor no enum `integration_type` (ao lado de `tiny`, `netsuite`, `salesforce`, `hubspot`, `pipedrive`).

**Não existe código Python de integração com Bling.** É um placeholder no schema do banco para implementação futura.

---

## 5. Gaps Identificados

| Item | Gap | Impacto |
|---|---|---|
| NF-e produto | Módulo `notas_fiscais/nfe/` vazio — tabelas `nfes` e `nfe_itens` existem mas sem endpoints | Não é possível emitir/consultar NF-e de produto via API |
| NFC-e | Módulo `notas_fiscais/nfce/` vazio | Sem emissão de cupom fiscal eletrônico |
| Bling | Apenas placeholder no enum | Sem sincronização de produtos/estoque/NF-e com Bling |
| `goods_receipts` | Tabela existe, endpoint não verificado | Recebimento de mercadorias pode estar parcial |
| SEFAZ `/nfe/emitir` | Controller existe mas `SEFAZService.emitir_nfe()` não foi validado | Pode ser stub sem integração real |

---

## 6. Conclusão

```
✅ NFS-e SAÍDA (serviços): funcional — ABRASF 2.04 + Portal Nacional
✅ NFS-e ENTRADA: 9 registros + endpoint listagem + tabela completa
✅ Compras: tabelas purchase_orders/quotations/requisitions/goods_receipts presentes
✅ Estoque WMS: tabela fin_stock_items completa (qty, cost, warehouse)
✅ Obrigações: 22 registros em fiscal_obligations (eSocial, FGTS, DCTFWEB, ISS...)
⚠️  NF-e PRODUTO: tabelas existem, módulo vazio — sem endpoints funcionais
⚠️  Bling: apenas placeholder no enum — sem integração implementada
⚠️  SEFAZ /nfe/emitir: controller presente, mas emissão real não validada
```

---

*Relatório gerado por Claude Sonnet 4.6 em 2026-04-11*
