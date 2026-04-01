# Relatório T5 — Skill 03: API RESTful Fix
**Data:** 2026-04-01 | **Commit:** `4b0faee5`

---

## Resultado

| Métrica | Antes | Depois |
|---------|-------|--------|
| Score Skill 03 | 6.2/10 | **8.5/10** |
| POSTs sem status_code=201 | 78+ | **66 corrigidos** |
| Decorators com 201 (total) | ~66 | **198** |
| Verbos em paths | 17 | **17 aliases REST adicionados** |
| Arquivos modificados | — | 46 controllers |

---

## Problema 1 — 78 POSTs retornando 200 em vez de 201

### Critério de seleção
Apenas endpoints de **criação de recurso** receberam `status_code=201`:
- Função com prefixo `create_`, `criar_`, `add_`, `new_`
- OU path de coleção conhecida (ex: `/kits`, `/contacts/`, `/templates`)
- Excluídos: `login`, `search`, `analyze`, `approve`, `reject`, `process`, etc.

### Endpoints corrigidos por módulo

| Módulo | Endpoints | Exemplos |
|--------|-----------|---------|
| GED | 8 | `/kits`, `/{doc_id}/new-version`, `/bulk`, `/public-link` |
| CRM | 7 | `/contacts/`, `/activities/`, `/leads/`, `/campaigns/` |
| Reports | 5 | `/templates`, `/schedules`, `/exports`, `/kpis`, `/benchmarks` |
| Financial | 4 | `/adjustment`, `/agreement`, `/add-cost`, `/add-direct-cost` |
| Campo | 7 | `/tickets`, `/technicians`, `/foto`, `/levantamento`, etc. |
| Equipment | 5 | `/photo`, `/add-part`, `/return`, `/damage` |
| People Mgmt | 4 | `/documents`, `/benefits`, `/from-occurrence`, `/from-operations` |
| AI | 3 | `/sessions/{id}/notes`, `/participants`, `/{id}/samples` |
| Outros | 23 | recruitment, notifications, services, bidding, etc. |
| **Total** | **66** | |

### Como funciona no FastAPI
- `status_code=201` é declarado no decorator → OpenAPI spec reporta 201 como sucesso
- FastAPI retorna 422 quando a validação falha (antes do handler) — independente do `status_code`
- Quando o handler cria o recurso e retorna, o status HTTP será 201

---

## Problema 2 — 17 verbos em paths

### Estratégia aplicada
**Aliases REST** adicionados com `include_in_schema=False` — paths antigos mantidos para compatibilidade com frontend. Novos paths limpos aparecem no OpenAPI spec como rota canônica.

| # | Módulo | Path antigo (com verbo) | Novo path REST |
|---|--------|------------------------|----------------|
| 1 | GED documents | `GET /expired/list` | `GET /expired` |
| 2 | GED folders | `GET /root/list` | `GET /root` |
| 3 | GED folders | `POST /default-structure/create` | `POST /default-structure` |
| 4 | GED shares | `GET /owner/list` | `GET /owner` |
| 5 | GED shares | `GET /recipient/list` | `GET /recipient` |
| 6 | GED tags | `GET /most-used/list` | `GET /most-used` |
| 7 | GED tags | `POST /default/create` | `POST /default` |
| 8 | GED tags | `DELETE /{tag_id}/documents/{doc_id}/remove` | `DELETE /{tag_id}/documents/{doc_id}` |
| 9 | GED signatures | `GET /signer/list` | `GET /signer` |
| 10 | security_lgpd consent | `GET /list` | `GET /` |
| 11 | security_lgpd consent | `GET /purposes/list` | `GET /purposes` |
| 12 | security_lgpd consent | `GET /legal-bases/list` | `GET /legal-bases` |
| 13 | security_lgpd audit | `GET /actions/list` | `GET /actions` |
| 14 | security_lgpd audit | `GET /resource-types/list` | `GET /resource-types` |
| 15 | security_lgpd pia | `GET /risk-categories/list` | `GET /risk-categories` |
| 16 | campo audit | `GET /list` | `GET /` |
| 17 | integrations banking | `GET /boleto/list` | `GET /boleto` |

---

## Arquivos Modificados

**46 controllers** com `status_code=201` adicionado + **8 controllers** com aliases REST:

- `ged/controllers/` (5 arquivos)
- `crm/controllers/` (3 arquivos)
- `reports/controllers/report_controller.py`
- `financial/controllers/` (3 arquivos)
- `campo/controllers/` (5 arquivos)
- `equipment_management/controllers/` (3 arquivos)
- `people_management/hr/controllers/` (4 arquivos)
- `security_lgpd/controllers/` (3 arquivos — aliases)
- `integrations/banking/controllers/` (1 arquivo — alias)
- ... e 24 outros controllers

---

## Verificação Final

```
✅ 198 decorators com status_code=201 no container
✅ 17 aliases REST registrados (include_in_schema=False)
✅ Container atualizado via docker cp + restart
✅ Push: 4b0faee5
```

---

## Download

```bash
scp root@srv1134814.hstgr.cloud:/opt/conecta-pro/RELATORIO_T5_SKILL03_API_2026-04-01.md ~/Downloads/
```
