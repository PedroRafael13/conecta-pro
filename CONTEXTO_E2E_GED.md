# CONTEXTO E2E — Modulo GED | 2026-03-29

## Status: 11/11 endpoints passando | Score: 10/10

## Endpoints Testados

| # | Endpoint | HTTP | Status |
|---|----------|------|--------|
| 1 | GET /api/v1/ged/kits | 200 | OK |
| 2 | GET /api/v1/ged/clients | 200 | OK |
| 3 | GET /api/v1/ged/documents/search | 200 | OK |
| 4 | GET /api/v1/ged/config/drive | 200 | OK |
| 5 | GET /api/v1/ged/config/schedule | 200 | OK |
| 6 | GET /api/v1/ged/config/email-templates | 200 | OK |
| 7 | GET /api/v1/ged/config/document-types | 200 | OK |
| 8 | GET /api/v1/ged/reports/monthly | 200 | OK |
| 9 | GET /api/v1/ged/document-signatures/stats/summary | 200 | OK |
| 10 | GET /api/v1/ged/kit-real/{id}/checklist | 200 | OK |
| 11 | GET /api/v1/ged/montar/condominios | 200 | OK |

## Frontend (307 = redirect login — comportamento correto)

- /modulos/gestao-pessoas/ged → 307
- /modulos/gestao-pessoas/ged/kits → 307
- /modulos/gestao-pessoas/ged/clientes → 307
- /modulos/gestao-pessoas/ged/configuracoes → 307

## Submódulos Testados

### 1. Dashboard /ged — OK
- Métricas: 13 kits, certidões, documentos
- Kits recentes com client_name (13/13 com nome)
- Montar Kits com feedback toast

### 2. Clientes /ged/clientes — OK
- 12 clientes ativos listados
- Validação campos obrigatórios (Nome*, Tipo*)
- Feedback erro POST (toast)

### 3. Kits /ged/kits — OK
- 13 kits com client_name visível
- Modal "Novo Kit" abre com ?new=true
- Dropdown clientes: /api/v1/ged/clients (sem trailing slash)
- Filtros por mês/status/cliente

### 4. Kit Detail /ged/kits/{id} — OK
- Checklist 19/19 Ideal Flores
- Download ZIP

### 5. Documents /ged/documents — OK
- /documents/search rota antes de /{id}
- Busca por texto, tipo, categoria

### 6. Certidões /ged/certidoes — OK
- 8 certidões (7 válidas, 1 vencida: Alvará PF)

### 7. Assinaturas /ged/assinaturas — OK
- Endpoint funciona com token (401 = sessão expirada)

### 8. Configurações /ged/configuracoes — OK
- Drive: status nao_configurado (esperado)
- Schedule: salva com toast de confirmação
- Email templates: 2 templates
- Document types: 10 tipos

### 9. Relatórios /ged/reports/monthly — OK
- Março/2026: 13 kits (1 concluído, 12 em montagem)
- 8 certidões, ações recomendadas

### 10. WhatsApp /ged/whatsapp — OK
- Validação telefone/mensagem com feedback

## Bugs Corrigidos Nesta Sessão

| Bug | Descrição | Fix |
|-----|-----------|-----|
| P1 | client_name NULL nos 13 kits | JOIN ged_clients no auto_assemble_controller |
| P2 | /documents/search 500 | Rota /search antes de /{id} no document_controller |
| P3 | /ged/clients 404 | Endpoint criado no ged_config_controller |
| P4 | WebSocket 503 spam | reconnect 30s/3 tentativas |
| B2 | Modal Novo Kit não abre | useSearchParams + ?new=true |
| B3 | POST cliente sem feedback | Toast erro/sucesso |
| B4 | Campos sem validação | Nome*/Tipo* obrigatórios |
| B5 | WhatsApp sem validação | Telefone/mensagem obrigatórios |
| B6 | Save sem toast | Toast em schedule/drive |
| B7 | Montar Kits sem ação | Feedback toast + endpoint correto |
| NS | Namespace errado | people-management/ged → ged (8 arquivos) |
| TS | Trailing slash 404 | /ged/clients/ → /ged/clients |

## Alertas Reais

- Alvará PF vencido desde 28/02/2026 — renovar SESEG/PF
- CRF FGTS vence 31/03/2026 — renovar portal Caixa
- Google Drive desconectado — OAuth pendente
- WebSocket 503 — aceitável (3 tentativas/30s)

## IDs de Referência

- kit_id Ideal Flores: e3ba48aa-fedc-4a43-baab-ba6b77629b0e
- client_id Ideal Flores: 4db583b6-815a-494f-a1e3-0c62fa81eca9
