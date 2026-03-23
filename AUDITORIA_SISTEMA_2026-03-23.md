# AUDITORIA COMPLETA — CONECTA PRO
**Gerado em:** 2026-03-23 04:48
**Sessão:** 2026-03-23 — Auditoria de Estado

---

## 1. INFRAESTRUTURA

### Servidor
- **VPS:** srv1134814.hstgr.cloud (82.25.75.74) — Hostinger KV4
- **OS:** Ubuntu 24
- **Branch:** feature/people-management-reorganization
- **GitHub:** https://github.com/jjesus1982/conecta-pro

### Stack
- **Backend:** FastAPI + PostgreSQL 16 + Redis + Celery
- **Frontend:** Next.js 16 + React 19 + TypeScript + Tailwind
- **Infra:** Docker, PM2, 10 subdomínios SSL

### Health Check
```
{
    "status": "healthy",
    "app": "Conecta PRO",
    "version": "2.0.0",
    "environment": "production"
}
```

### Containers Docker
```
NAMES                                         STATUS                   PORTS
conecta-pro-backend                           Up 3 minutes (healthy)   0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp
erp-postgres-exporter                         Up 2 days                0.0.0.0:9187->9187/tcp, [::]:9187->9187/tcp
conecta-pro-celery-beat                       Up 2 hours (unhealthy)   8080/tcp
conecta-pro-flower                            Up 2 days (healthy)      0.0.0.0:5555->5555/tcp, [::]:5555->5555/tcp, 8080/tcp
conecta-pro-celery-integrations               Up 2 days (healthy)      8080/tcp
34bbe0bcda76_conecta-pro-celery-priority      Up 2 days (healthy)      8080/tcp
a853a3056bf9_conecta-pro-celery-sefaz         Up 2 days (healthy)      8080/tcp
8f30da3e29ad_conecta-pro-celery-nfse          Up 2 days (healthy)      8080/tcp
conecta-pro-celery-batch                      Up 2 days (healthy)      8080/tcp
297439d0453a_conecta-pro-celery-operacional   Up 2 hours (healthy)     8080/tcp
conecta-pro-postgres                          Up 2 days (healthy)      5432/tcp
erp-node-exporter                             Up 2 days                0.0.0.0:9100->9100/tcp, [::]:9100->9100/tcp
erp-redis-exporter                            Up 3 days                0.0.0.0:9121->9121/tcp, [::]:9121->9121/tcp
conecta-pro-redis                             Up 2 days (healthy)      6379/tcp
conecta-pro-redis-staging                     Up 13 days (healthy)     6379/tcp
conecta-pro-postgres-staging                  Up 13 days (healthy)     5432/tcp
erp-alertmanager                              Up 2 days (healthy)      0.0.0.0:9093->9093/tcp, [::]:9093->9093/tcp
erp-promtail                                  Up 13 days
erp-loki                                      Up 13 days (healthy)     0.0.0.0:3100->3100/tcp, [::]:3100->3100/tcp
erp-prometheus                                Up 2 days                0.0.0.0:9090->9090/tcp, [::]:9090->9090/tcp
erp-grafana                                   Up 13 days               0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp
```

### PM2 Processos
```
┌────┬─────────────────────────┬─────────────┬─────────┬─────────┬──────────┬────────┬──────┬───────────┬──────────┬──────────┬──────────┬──────────┐
│ id │ name                    │ namespace   │ version │ mode    │ pid      │ uptime │ ↺    │ status    │ cpu      │ mem      │ user     │ watching │
├────┼─────────────────────────┼─────────────┼─────────┼─────────┼──────────┼────────┼──────┼───────────┼──────────┼──────────┼──────────┼──────────┤
│ 0  │ conecta-pro-frontend    │ default     │ N/A     │ fork    │ 12669    │ 101s   │ 181  │ online    │ 0%       │ 66.6mb   │ root     │ disabled │
│ 1  │ telegram-assistant      │ default     │ N/A     │ fork    │ 10730    │ 47h    │ 0    │ online    │ 0%       │ 49.7mb   │ root     │ disabled │
└────┴─────────────────────────┴─────────────┴─────────┴─────────┴──────────┴────────┴──────┴───────────┴──────────┴──────────┴──────────┴──────────┘
```

---

## 2. BANCO DE DADOS

### Tabelas com Dados (top 40)
```
schemaname |           tabela            | registros
------------+-----------------------------+-----------
 public     | sst_cipa_reunioes           |      1133
 public     | ged_kit_documents           |       351
 public     | gp_epi_deliveries           |       220
 public     | employee_benefits           |       157
 public     | hr_payroll_events           |       109
 public     | rh_onboarding_checklist     |       102
 public     | gp_asos                     |        96
 public     | users                       |        52
 public     | hr_vacation_periods         |        52
 public     | employees                   |        52
 public     | cct_cargos                  |        50
 public     | solides_entity_mapping      |        44
 public     | posts                       |        32
 public     | geofence_zones              |        31
 public     | document_kit_items          |        29
 public     | nfses                       |        27
 public     | rubricas_folha              |        24
 public     | fiscal_obligations          |        23
 public     | bidding_opportunities       |        20
 public     | allocations                 |        20
 public     | training_enrollments        |        20
 public     | training_certificates       |        20
 public     | time_bank                   |        18
 public     | gp_clock_punches            |        16
 public     | ged_folders                 |        16
 public     | gp_risks                    |        15
 public     | ged_document_tags           |        15
 public     | performance_reviews         |        15
 public     | occurrences                 |        15
 public     | candidate_skills            |        15
 public     | rh_onboarding_templates     |        14
 public     | ged_document_kits           |        14
 public     | ged_clients                 |        14
 public     | contracts                   |        13
 public     | communication_notifications |        12
 public     | reimbursement_requests      |        12
 public     | openclaw_interventions      |        12
 public     | condominiums                |        11
 public     | client_contracts            |        11
 public     | clients                     |        11
(40 rows)
```

### Clientes Ativos (13)
```
name                    | document_number | status
-------------------------------------------+-----------------+--------
 CONDOMINIO DO EDIFICIO MICHELANGELO       | 04911208000113  | active
 CONDOMINIO IDEAL FLORES DA CIDADE         | 23147782000191  | active
 CONDOMINIO LIFE CENTRO                    | 19865917000187  | active
 CONDOMINIO MIRANTE DAS FLORES             | 52605708000170  | active
 CONDOMINIO PARQUE RESIDENCIAL GELAIN      | 00736037000182  | active
 CONDOMINIO PRIME ARENA                    | 47405340000166  | active
 CONDOMINIO RESIDENCIAL GREEN HILLS        | 08063476000183  | active
 CONDOMINIO RESIDENCIAL PARISE VILLAGE     | 34857941000168  | active
 CONDOMINIO RESIDENCIAL VILLA DOS PASSAROS | 13221953000121  | active
 CONDOMINIO VILLA DEI FIORI                | 02153384000108  | active
 Conecta Mais - Segurança e Tecnologia     | 00000000000000  | active
 Matriz escritório                         | 00000000000000  | active
 RESIDENCIAL LARANJEIRAS VILLAGE           | 24632786000128  | active
(13 rows)
```

### Contratos Ativos (11)
```
name                    | monthly_value |   contract_type   | status
-------------------------------------------+---------------+-------------------+--------
 CONDOMINIO IDEAL FLORES DA CIDADE         |      65842.42 | prestacao_servico | ativo
 RESIDENCIAL LARANJEIRAS VILLAGE           |      42544.50 | prestacao_servico | ativo
 CONDOMINIO MIRANTE DAS FLORES             |      42255.80 | prestacao_servico | ativo
 CONDOMINIO PRIME ARENA                    |      40466.50 | prestacao_servico | ativo
 CONDOMINIO RESIDENCIAL VILLA DOS PASSAROS |      37338.33 | prestacao_servico | ativo
 CONDOMINIO VILLA DEI FIORI                |      25592.71 | prestacao_servico | ativo
 CONDOMINIO DO EDIFICIO MICHELANGELO       |       8346.70 | prestacao_servico | ativo
 CONDOMINIO PARQUE RESIDENCIAL GELAIN      |       6000.00 | prestacao_servico | ativo
 CONDOMINIO RESIDENCIAL PARISE VILLAGE     |       1700.00 | prestacao_servico | ativo
 CONDOMINIO LIFE CENTRO                    |       1500.00 | prestacao_servico | ativo
 CONDOMINIO RESIDENCIAL GREEN HILLS        |        500.00 | prestacao_servico | ativo
(11 rows)
```

### Funcionários
```
total | folha_bruta
-------+-------------
    52 |    87410.15
(1 row)
```

### NFS-e Emitidas
```
data_competencia | qtd |   total
------------------+-----+-----------
 2026-01-01       |  14 | 272086.96
 2026-02-01       |  13 | 270586.96
(2 rows)
```

### Kits GED
```
client | reference_month | status | total_documents | completion_percentage
--------+-----------------+--------+-----------------+-----------------------
(0 rows)
```

### Obrigações Fiscais Pendentes
```
nome         | data_vencimento |  status  | valor_devido
----------------------+-----------------+----------+--------------
 eSocial S-1200 Folha | 2026-04-07      | pendente |         0.00
 FGTS/GFIP            | 2026-04-07      | pendente |      7676.02
 DCTFWeb              | 2026-04-15      | pendente |         0.00
 EFD-Reinf            | 2026-04-15      | pendente |         0.00
 ISS Manaus           | 2026-04-15      | pendente |     13529.38
 DARF IRRF            | 2026-04-20      | pendente |         0.00
 INSS Patronal        | 2026-04-20      | pendente |     19190.04
(7 rows)
```

---

## 3. ENDPOINTS POR MÓDULO (contagem de rotas no código)
```
516 financial
    397 ai
    273 hr
    259 operacional
    237 people_management
    217 government_integrations
    149 ged
    125 campo
    111 notifications
    100 crm
     96 bidding
     93 equipment_management
     79 recruitment
     75 integrations
     70 retention
     63 services
     54 document_kits
     51 clients
     47 config
     40 health_occupational
     38 reports
     35 empresas
     32 analytics
     31 audit
     26 scheduler
     26 reimbursement
     25 monitoring
     25 cct
     21 security_lgpd
     17 mobile
     17 client_portal
     16 documents
     11 fase5
      9 automation
      5 fiscal
      3 lgpd
```

---

## 4. INTEGRAÇÕES GOVERNAMENTAIS — Dashboard
```json
{
    "periodo_inicio": "2026-03-16T04:41:14.210983",
    "periodo_fim": "2026-03-23T04:41:14.210983",
    "resumo_geral": {
        "total_documentos": 0,
        "documentos_novos": 0,
        "documentos_atualizados": 0,
        "documentos_erro": 0,
        "extracoes_executadas": 0,
        "extracoes_sucesso": 0,
        "extracoes_falha": 0,
        "ultima_extracao": null
    },
    "servicos": [
        {
            "servico": "sefaz_nfe",
            "nome_exibicao": "NF-e/NFC-e",
            "status": "online",
            "documentos_processados": 0,
            "documentos_erro": 0,
            "ultima_sincronizacao": null,
            "tempo_medio_resposta_ms": null,
            "taxa_sucesso": 100.0
        },
        {
            "servico": "sefaz_cte",
            "nome_exibicao": "CT-e",
            "status": "online",
            "documentos_processados": 0,
            "documentos_erro": 0,
            "ultima_sincronizacao": null,
            "tempo_medio_resposta_ms": null,
            "taxa_sucesso": 100.0
        },
        {
            "servico": "sefaz_mdfe",
            "nome_exibicao": "MDF-e",
            "status": "online",
            "documentos_processados": 0,
            "documentos_erro": 0,
            "ultima_sincronizacao": null,
            "tempo_medio_resposta_ms": null,
            "taxa_sucesso": 100.0
        },
        {
            "servico": "esocial",
            "nome_exibicao": "eSocial",
            "status": "online",
            "documentos_processados": 0,
            "documentos_erro": 0,
            "ultima_sincronizacao": null,
            "tempo_medio_resposta_ms": null,
            "taxa_sucesso": 100.0
        },
        {
            "servico": "fgts_digital",
            "nome_exibicao": "FGTS Digital",
            "status": "online",
            "documentos_processados": 0,
            "documentos_erro": 0,
            "ultima_sincronizacao": null,
            "tempo_medio_resposta_ms": null,
            "taxa_sucesso": 100.0
        },
        {
            "servico": "nfse_manaus",
            "nome_exibicao": "NFS-e Manaus",
            "status": "online",
            "documentos_processados": 0,
            "documentos_erro": 0,
            "ultima_sincronizacao": null,
            "tempo_medio_resposta_ms": null,
            "taxa_sucesso": 100.0
        },
        {
            "servico": "receita_federal",
            "nome_exibicao": "Receita Federal",
            "status": "online",
            "documentos_processados": 0,
            "documentos_erro": 0,
            "ultima_sincronizacao": null,
            "tempo_medio_resposta_ms": null,
            "taxa_sucesso": 100.0
        },
        {
            "servico": "simples_nacional",
            "nome_exibicao": "Simples Nacional",
            "status": "online",
            "documentos_processados": 0,
            "documentos_erro": 0,
            "ultima_sincronizacao": null,
            "tempo_medio_resposta_ms": null,
            "taxa_sucesso": 100.0
        }
    ],
    "endpoints_indisponiveis": [
        {
            "uf": "AM",
            "servico": "nfe",
            "endpoint": "N/A",
            "disponivel": false,
            "tempo_resposta_ms": 0.618,
            "ultimo_check": "2026-03-23T04:41:14.211793",
            "falhas_consecutivas": 0
        }
    ],
    "alertas_certificados": [],
    "eventos_recentes": [],
    "atualizado_em": "2026-03-23T04:41:14.211836"
}
```

---

## 5. GIT — ÚLTIMOS 30 COMMITS
```
a3adb411 feat(relatorios): central de relatorios PDF com dados reais
5642d537 fix(esocial): corrige ESocialService — remove dependência de transmitter dict
95da6101 fix(crm): corrige bug router Comercial — desbloqueia CRM + Clients + Bidding
eb585d0f feat(dashboard): home executiva com alertas e status dos modulos
44959a4b feat(bi-analytics): dashboard BI com KPIs reais + calendario fiscal 2026
f0c752fc fix(gov): corrige 7 bugs integrações governamentais + ativa NFS-e Manaus
0983314d feat(propagacao-dados): 11 clientes reais em contratos, postos, condominios e CRM
6c13e948 feat(financeiro): dashboard com dados reais dos 11 clientes
fc14bd13 feat(rh-clientes): vincula 57 funcionarios aos 11 clientes reais + headcount API
70ebe414 feat(nfse-reais): 27 NFS-e jan/fev 2026 + dashboard financeiro
2d83ed54 fix(ged): corrige pydantic datetime 500 + envio email kits
91070674 feat(ged-certidoes): reescreve pagina certidoes com endpoints reais
4fc6c187 feat(clientes-reais): substitui dados fictícios pelos 11 clientes reais das NFS-e
bb95a914 feat(ged-kits): workflow completo kit mensal + dashboard
d2b4de1a fix(scheduler): substitui APScheduler por Celery Beat + cron
37649ce3 feat(ged-frontend): upload com IA + assinaturas digitais
4ec69137 feat(ged-workflow): auto-assemble kits + dashboard + fix import circular
7257ac98 feat(ged-ia): classificacao automatica no upload + alertas expiracao
79b67bd4 fix(api): corrige trailing slash em 39 controllers — 66 endpoints desbloqueados
7c1db561 fix(ged): corrige trailing slash em 5 controllers GED — 404 → 200
b2fa929e fix(ged-core): corrige 500s nos endpoints GED Core — 31/31 OK
b29af503 feat(ged): registra tasks Celery GED no worker operacional + beat schedule
13107e66 fix(ged): registra Document Kits + Documents/OCR + cria storage
9ad7f2eb fix(epi): corrige endpoint GET /health-occupational/epi — 404 → 200
bd86f388 fix(area-cliente): credenciais provisionadas usam CNPJ ou username no login
792cf506 fix(clima+epi): corrige texto invisivel clima e erro listagem EPI
ed675b88 fix(ltcat): cria pagina LTCAT em /gestao-pessoas/saude-ocupacional/ltcat
cb8dda5d fix(gestao-pessoas): correcoes pos-QA ciclo 2 - saude ocupacional e ux
c234d4b8 feat(area-cliente): painel admin gerenciamento de acessos com React Query
256b4df8 fix(ux): corrige bugs pos-QA ciclo 2
```

### Status Atual
```
M backend/modules/government_integrations/controllers/esocial_controller.py
 M backend/modules/government_integrations/core/esocial_transmitter.py
 M backend/scripts/seed_real_data.sql
 M frontend/src/config/modules.ts
 M frontend/tsconfig.tsbuildinfo
?? GED_AUDITORIA_2026-03-22.md
?? frontend/src/app/modulos/bi/
?? frontend/src/app/modulos/financeiro/contratos/
?? uploads/ged/73b6de2ca5bbe8336ca047da4c5435fd4f017a42729bbbef4950a857012c59be.pdf
?? uploads/ged/fe070d4bf6b1ab799291a88e9240369d06882b71b6e2be5ff15e17662162fe7b.pdf
```

### Branch
```
audit/20260211-234159
  feature/openclaw-v2
* feature/people-management-reorganization
  master
  remotes/origin/audit/20260211-234159
```

---

## 6. MÓDULOS E SCORES ATUAIS

| Módulo | Score | Observação |
|--------|-------|-----------|
| Gestão de Pessoas | 10/10 | Completo, auditado |
| GED — Gestão Documental | 8/10 | Falta WhatsApp + Google Drive |
| Integrações Governamentais | 7/10 | Dashboard OK, eSocial homologação |
| CRM / Comercial | 7/10 | 13 clientes, pipeline ativo |
| Financeiro | 8/10 | Dashboard real, NFS-e populadas |
| BI / Analytics | 8/10 | KPIs reais, Recharts |
| RH / Folha | 8/10 | 52 func, folha R$ 87.410,15 |
| Contratos | 7/10 | 11 contratos ativos, R$ 272K/mês |
| Operacional | 6/10 | 32 postos, campo pendente |
| Área do Cliente | 7/10 | 13 provisionados, portal ativo |
| Compliance | 7/10 | Calendário fiscal 2026 |
| Relatórios | 7/10 | PDF ReportLab, 5 tipos |

---

## 7. DADOS FINANCEIROS RESUMIDOS

| Métrica | Valor |
|---------|-------|
| Faturamento mensal (contratos) | R$ 272.086,96 |
| Folha bruta | R$ 87.410,15 |
| FGTS mensal (8%) | R$ 7.676,02 |
| INSS Patronal | R$ 19.190,04 |
| ISS Manaus | R$ 13.529,38 |
| Funcionários ativos | 52 |
| Clientes ativos | 13 |
| Contratos ativos | 11 |
| NFS-e emitidas Jan/2026 | 14 (R$ 272.086,96) |
| NFS-e emitidas Fev/2026 | 13 (R$ 270.586,96) |

---

## 8. ALERTAS CRÍTICOS

🔴 **CRF FGTS vence 31/03/2026** — Renovar no portal Caixa
🔴 **Alvará PF vencido 28/02/2026** — Regularizar na prefeitura
🟡 **Gov.br OAuth2** — Registrar app em gov.br/login-unico (CLIENT_ID)
🟡 **eSocial** — Transmitir S-1000/S-2200 em homologação
🟡 **NFS-e Março/2026** — Não emitida ainda
🟡 **Kits GED** — 0 kits montados (tabela vazia)

---

## 9. PRÓXIMAS TAREFAS (FILA)

### Alta Prioridade
1. eSocial: transmitir em homologação → validar → produção
2. Gov.br: registrar aplicação → CLIENT_ID → ativar OAuth2
3. SPED Fiscal: popular com dados contábeis reais
4. DCTFWeb: gerar com dados reais março 2026
5. NFS-e Março: emitir para os 11 contratos ativos
6. WhatsApp Evolution API: integrar envio de kits

### Média Prioridade
7. Google Drive: configurar service account → export automático kits
8. GED score 8/10 → 10/10
9. Operacional: módulo campo completo
10. QA completo do sistema inteiro
11. Merge feature → main + tag release

### Baixa Prioridade
12. Certificado A3 (se necessário)
13. SERPRO/Dataprev integração
14. NFC-e: implementar 7 TODOs do controller

---

## 10. CREDENCIAIS E ACESSOS

- **Sistema:** jjesus@conectamais.pro / Jordan0612
- **VPS SSH:** root@82.25.75.74
- **CNPJ Empresa:** 35.710.481/0001-03
- **Inscrição Municipal:** 45177801
- **Inscrição SUFRAMA:** 210140500
- **Certificado A1:** instalado, válido até 2027-01-13
- **NFS-e Portal:** https://www.nfse.gov.br (desde 01/01/2026)
- **SMTP:** Hostinger porta 465 SSL
- **Gov.br:** pendente registro OAuth2
- **Backend port:** 8080 (IPv4: 127.0.0.1:8080)
- **Login:** POST form-urlencoded (NÃO JSON)

---

## 11. COMANDOS ESSENCIAIS
```bash
# Token de autenticação (usar 127.0.0.1, NÃO localhost)
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Health check
curl -sf http://127.0.0.1:8080/health | python3 -m json.tool

# Gov dashboard (trailing slash obrigatória)
curl -sf "http://127.0.0.1:8080/api/v1/government/dashboard/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Build frontend (SERIALIZADO — nunca simultâneo)
export NODE_OPTIONS=--max-old-space-size=4096
cd /opt/conecta-pro/frontend && npx next build 2>&1 | tail -8
PORT=3001 pm2 restart conecta-pro-frontend --update-env && pm2 save

# Backend hot copy
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)
docker cp /opt/conecta-pro/backend/[arquivo] $CONTAINER:/app/[arquivo]

# Ver logs
docker logs conecta-pro-backend 2>&1 | tail -20
pm2 logs conecta-pro-frontend --lines 20
```

---

## 12. ESTRUTURA DE MÓDULOS

### Backend (10 módulos + agregadores)
1. comercial/ (crm + clients + bidding + services)
2. operacoes/ (operacional + campo + todos submodulos)
3. tecnico/ (equipment_management + document_kits)
4. pessoas/ (recruitment + retention + reimbursement + ged)
5. financeiro/ (financial completo + bi_dashboard)
6. fiscal_contabil/ (empresas + fiscal + government_integrations)
7. inteligencia/ (ai/bartolo + analytics + reports + monitoring)
8. gestao/ (config + audit + notifications + mobile + workflows + integrations)
9. cadastros/ (reservado para dados mestres — futuro)
10. people_management/ (hr DP + human_resources RH + operations + employee_portal)

### Frontend (9 módulos no sidebar)
1. Comercial (CRM + Servicos + Licitacoes)
2. Operacoes (Operacional + Campo + IA)
3. Pessoas (Recrutamento + Saude + Reembolso)
4. Financeiro (Financial + Suprimentos + Boletos)
5. Fiscal (Multi-Empresa + Obrigacoes + NF-e)
6. Juridico (Contratos + Compliance + LGPD)
7. Facilities (Predial + Limpeza + Jardinagem)
8. Tecnologia (TI + Telecom + Integracao)
9. Gestao (Admin + BI + Config)

---

## 13. NOTAS TÉCNICAS IMPORTANTES

- **IPv6 issue:** `localhost` resolve para `::1` e backend retorna empty reply. Usar SEMPRE `127.0.0.1`
- **OpenAPI /openapi.json:** retorna 404 (docs desabilitado em produção)
- **Gov dashboard:** requer trailing slash `/api/v1/government/dashboard/`
- **Backend code baked into Docker:** usar docker cp + docker restart
- **DB has 472 tabelas** no schema public (muitas com 0 registros)
- **Pre-commit:** tsconfig.tsbuildinfo no exclude do detect-secrets

---

*Gerado automaticamente — Sessão 2026-03-23*
*Auditor: Claude Code*
