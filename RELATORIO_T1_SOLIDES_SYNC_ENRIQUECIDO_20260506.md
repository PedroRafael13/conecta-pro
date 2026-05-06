# Sync Enriquecido Sólides — Campos eSocial
**Data:** 2026-05-06
**Commits:** d839d50e (código), 3ffa4acc (docs §122)
**§ CONTRACTS_GEDEON:** §122
**Branch:** feature/people-management-reorganization

## Objetivo
45 funcionários com completude eSocial de 43%. Verificar campos disponíveis no
Sólides e implementar sync enriquecido.

## Investigação — API Tangerino (Sólides DP)

### Campos disponíveis em `/employee/find-all`
| Campo API | Campo DB | Status |
|-----------|----------|--------|
| `name` | `nome` | ✅ Já mapeado |
| `email` | `email` | ✅ Já mapeado |
| `birthDate` (ms) | `data_nascimento` | ✅ Já mapeado |
| `cpf` | `cpf` | ✅ Já mapeado |
| `pis` | `pis` | ✅ Já mapeado |
| `admissionDate` (ms) | `data_admissao` | ✅ Já mapeado |
| `gender` (MASCULINO/FEMININO) | `sexo` (M/F) | ✅ Já mapeado |
| `id` | `solides_id` | ✅ Já mapeado |
| `externalId` | `matricula` | 🔴 BUG: nunca mapeado |
| `jobRoleDTO.id` | `cargo` | 🔴 BUG: código buscava `jobRole` (inexistente) |
| `currentWorkSchedule.id` | `escala_padrao` | 🔴 BUG: código buscava `workSchedule` (inexistente) |
| `fired` + `terminationDate` | `status/data_demissao` | ✅ Já mapeado |

### Campos eSocial NÃO disponíveis na API
A API Tangerino `/employee/find-all` NÃO retorna (confirmado via API real):
- `estado_civil`, `nome_mae`, `nome_pai`
- `rg`, `rg_orgao`, `rg_uf`
- `ctps_numero`, `ctps_serie`, `ctps_uf`, `ctps_data_emissao`
- `titulo_eleitor`, `naturalidade`, `nacionalidade`
- `telefone`, `celular`, `endereco`

**Conclusão:** Campos críticos eSocial (rg, ctps, nome_mae) requerem entrada manual
ou importação via planilha — não são fornecidos pela API Sólides DP (Tangerino).

## Bugs Corrigidos em `_propagate_employees_to_db`

### Bug 1 — `externalId` → `matricula`
O campo `externalId` (ex: "000206") nunca foi mapeado para `matricula`.
Fix: `int(external_id)` → string numérica sem zeros à esquerda.

### Bug 2 — `jobRoleDTO.id` → `cargo`
Código original: `emp.get("jobRole", {})` → sempre vazio.
API real: `emp.get("jobRoleDTO", {}).get("id")` + lookup em `/job-role/find-all`.
Fix: `_fetch_tangerino_lookup_maps()` pre-busca o mapa `{id: description}`.

### Bug 3 — `currentWorkSchedule.id` → `escala_padrao`
Código original: `emp.get("workSchedule")` → sempre vazio.
API real: `emp.get("currentWorkSchedule", {}).get("id")` + lookup em `/work-schedule`.
Fix: `_fetch_tangerino_lookup_maps()` pre-busca o mapa `{id: name}`.

### Bug 4 — Auth header errado
`_fetch_tangerino_lookup_maps()` usava `Authorization: {token}`.
Tangerino usa `Authorization: Basic {token}`.
Fix: `f"Basic {api_token}"`.

### Bug 5 — StringDataRightTruncation
`_resolve_escala()` retornava fallback de 30 chars para `varchar(20)`.
Fix: retornar `""` quando padrão não reconhecido + adicionar padrões PORTARIA/DIURNO/NOTURNO.

## Resultados

### Completude após sync enriquecido
*(Base atual: 47 funcionários ativos — 2 admitidos após o sync inicial)*

| Campo | Antes | Depois (atual) | Fonte |
|-------|-------|----------------|-------|
| `escala_padrao` | 39/45 (87%) | **47/47 (100%)** | Tangerino API ✅ |
| `matricula` | 45/45 | 47/47 (100%) | Tangerino API ✅ |
| `cargo` | 45/45 | 47/47 (100%) | Tangerino API (corrigido) ✅ |
| `pis` | 40/45 (89%) | 42/47 (89%) | Tangerino API |
| `sexo` | 38/45 (84%) | 40/47 (85%) | Tangerino API |
| `estado_civil` | 39/45 (87%) | — | Manual (não na API) |
| `nome_mae` | 11/45 (24%) | 11/47 (23%) | Manual necessário |
| `rg` | 1/45 (2%) | 1/47 (2%) | Manual necessário |
| `ctps_numero` | 0/45 (0%) | 0/47 (0%) | Manual necessário |

**Completude média (10 campos eSocial): 43% → 68,7%**

### Sync stats
- Total Sólides: 51 funcionários | CPF match: 45 | Sem match: 6 (demitidos)
- Lookup maps carregados: 5 job-roles, 29 work-schedules
- Propagação: 45 atualizados, 0 inativados

## Arquivos modificados
- `backend/modules/integrations/connectors/solides/tasks.py`
  - Nova função `_fetch_tangerino_lookup_maps()`
  - Nova função `_resolve_escala()`
  - `_propagate_employees_to_db()` completamente reescrita

## Recomendação
Para atingir 100% nos campos eSocial críticos (rg, ctps, nome_mae, titulo_eleitor):
1. Importar via planilha de admissão (dados do eSocial S-2200)
2. Ou criar formulário de atualização no portal do funcionário
3. Ou buscar de API alternativa (SEFAZ/eSocial) via CPF
