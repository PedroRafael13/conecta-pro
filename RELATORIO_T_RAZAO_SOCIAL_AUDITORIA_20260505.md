# T_RAZAO_SOCIAL — Auditoria Completa
**Data:** 2026-05-05
**Executor:** Claude Sonnet 4.6 [session: t5] [module: ged]

---

## Resumo Executivo

Razão social atualizada de **Jordan Santos de Jesus Ltda** → **CONECTAMAIS ELETRONICA LTDA**
em TODAS as ocorrências no repositório.

CNPJ: 35.710.481/0001-03 (inalterado)

---

## Banco de Dados

| Tabela | Campo | Resultado |
|--------|-------|-----------|
| empresas | razao_social | ✅ CONECTAMAIS ELETRONICA LTDA |
| tenants | nome | ✅ já estava correto |
| tenants | endereco_logradouro/bairro/cep | ✅ Rua Adalberto Pinto Borges, Crespo, 69073-488 |
| bidding_certificates (8 linhas) | razao_social | ✅ CONECTAMAIS ELETRONICA LTDA |
| ged_clients | contact_name | ✅ Jordan Jesus |
| cashflow_entries / bank_transactions / nfses | — | ✅ preservados (histórico) |

Backup: `/tmp/backup_razao_social_20260505_213121.sql`

---

## Código Backend (30+ arquivos)

| Arquivo | Resultado |
|---------|-----------|
| templates/contrato_trabalho.html | ✅ |
| templates/aviso_previo_ferias.html | ✅ |
| modules/ged/controllers/kit_pdf_controller.py | ✅ |
| modules/ged/controllers/kit_real_controller.py (3x) | ✅ |
| modules/financial/integrations/nfe_provider.py | ✅ |
| modules/hr/employee_portal/services/payslip_service.py | ✅ |
| modules/operacional/disciplinary/services/disciplinary_service.py | ✅ |
| modules/people_management/hr/controllers/esocial_controller.py | ✅ |
| modules/people_management/hr/controllers/vacation_controller.py | ✅ |
| modules/people_management/hr/services/contract_service.py | ✅ |
| modules/people_management/sst/controllers/sst_controller.py (2x) | ✅ |
| modules/government_integrations/controllers/esocial_controller.py | ✅ |
| modules/government_integrations/controllers/nfce_controller.py | ✅ |
| modules/government_integrations/core/credentials/file_credential_provider.py (2x) | ✅ |
| modules/government_integrations/services/efd_reinf_service.py | ✅ |
| modules/government_integrations/services/nfse_entrada_sync_service.py | ✅ |
| modules/fiscal_contabil/notas_fiscais/nfe/controller.py (3x) | ✅ |
| modules/fiscal/services/nfse_multi_empresa_service.py | ✅ |
| modules/bidding/agents/assessor_agent.py | ✅ |
| modules/bidding/agents/compiler_agent.py | ✅ |
| modules/bidding/agents/pdf_renderer.py | ✅ |
| modules/integrations/banking/adapters/inter.py | ✅ |
| modules/integrations/banking/controllers/payment_controller.py | ✅ |
| modules/integrations/connectors/dominio/connector.py | ✅ |
| modules/document_kits/scheduler.py | ✅ |
| modules/document_kits/services/kit_monthly_generator_service.py | ✅ |
| modules/document_kits/services/kit_operational_service.py | ✅ |
| tests/test_nfe_transmitter.py | ✅ |
| folhas-validacao/gerar_relatorio_divergencias.py | ✅ |
| backend/scripts/seed_bidding.sql | ✅ |

## Variável de Ambiente

| Arquivo | Variável | Resultado |
|---------|----------|-----------|
| .env | NFSE_NACIONAL_RAZAO_SOCIAL | ✅ "CONECTAMAIS ELETRONICA LTDA" |

## Frontend (5 arquivos)

| Arquivo | Resultado |
|---------|-----------|
| frontend/src/app/layout.tsx | ✅ |
| frontend/src/app/modulos/financeiro/contratos/page.tsx | ✅ |
| frontend/src/app/modulos/financeiro/dashboard/page.tsx | ✅ |
| frontend/src/app/modulos/licitacoes/ia/page.tsx | ✅ |
| frontend/src/app/modulos/relatorios/central/page.tsx | ✅ |

## Documentação (8 arquivos)

BRIEFING_SESSION.md, CHANGELOG.md, CONTRACTS_CRM_VENDAS.md,
GED_README.md, MODULO_GED_DOCUMENTACAO.md, README_INTEGRACAO_FASE1.md,
FINANCEIRO_STATUS_2026-03-23.md, agents/assistant_system_prompt.md

## Skills (12 arquivos)

skills/financeiro/grupo-e/ (4 arquivos), skills/financeiro/juridico/ (8 arquivos)

## Outros

| Arquivo | Resultado |
|---------|-----------|
| FUNCIONARIOS_S2200_2026-03-23.csv | ✅ |
| scripts/seed_clientes_reais_2026-03-23.sql | ✅ |
| CONTRACTS_GEDEON.md §106 | ✅ (referência histórica preservada) |

---

## Hot-copy

8/8 workers Celery atualizados com todos os módulos modificados.

---

## Commits

| Commit | Descrição |
|--------|-----------|
| af5be3ce | docs(contracts): §106 |
| 265ba3a3 | fix(data): DB + relatório |
| a748b837 | fix(data): folhas-validacao |
| 3c25344c | fix(data): docs + skills + frontend + seeds |

---

## Verificação Final

```
git grep "JORDAN SANTOS DE JESUS LTDA|Jordan Santos de Jesus Ltda" -- *.py *.html *.ts *.tsx *.md *.sql *.csv
→ ZERO ocorrências (exceto §106 histórico em CONTRACTS_GEDEON.md)
```

**T_RAZAO_SOCIAL 100% COMPLETO**

[session: t5] [module: ged]
