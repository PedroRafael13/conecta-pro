# AUDITORIA DEFINITIVA — M7: Contrato PDF + Aviso Prévio
**Data:** 2026-04-09
**Branch:** feature/people-management-reorganization
**Commits:** a5a4d09d → b9e44c25 → fbc8f985 (pushed)
**Score final:** 100% — todos os gaps fechados

---

## O que foi encontrado em cada rodada de auditoria

### Rodada 1 (auditoria inicial)
3 itens faltando, todos corrigidos:

| Gap | Problema | Correção |
|-----|----------|----------|
| Nav card | `dp/page.tsx` sem card "Aviso Prévio" | Adicionado `Bell / /modulos/dp/aviso-previo` |
| Deploy | `docker cp .next/standalone/` não executado | Executado + `docker restart conecta-pro-frontend` |
| git push | Push não realizado | Executado: `a5a4d09d..b9e44c25` |

### Rodada 2 (auditoria final)
1 gap real encontrado e corrigido:

| Gap | Problema | Correção |
|-----|----------|----------|
| `notice_type` ignorado | Frontend envia `notice_type: 'trabalhado'/'indenizado'`, backend ignorava (campo não existe no modelo). `status` era hardcoded como `INITIATED` | Adicionado `notice_type` e `status` ao `TerminationCreate`; service armazena `notice_type` em `reason` com prefixo `notice_type:<val>`; controller expõe no response; commit fbc8f985 |

---

## Checklist Final Completo

### PASSO 1 — Diagnóstico
| # | Item | Status |
|---|------|--------|
| 1 | Script diagnóstico executado, libs verificadas | ✅ |
| 2 | jinja2=❌ ausente / reportlab=✅ / weasyprint=❌ ausente | ✅ identificado |

### PASSO 2 — GAP 1: Geração Real de PDF
| # | Item | Status |
|---|------|--------|
| 3 | `gerar_pdf_contrato(db, contract_id) -> bytes` implementada | ✅ |
| 4 | JOIN `employment_contracts JOIN employees` | ✅ |
| 5 | Busca nome, CPF, PIS, cargo do funcionário | ✅ |
| 6 | Consulta `contract_templates WHERE is_active=true` | ✅ |
| 7 | Fallback template padrão CLT (6 cláusulas) quando tabela vazia | ✅ |
| 8 | Lib: reportlab (jinja2 ausente — seleção correta) | ✅ |
| 9 | Retorna `buffer.getvalue()` — bytes reais | ✅ |
| 10 | Endpoint `GET /{contract_id}/pdf` no controller | ✅ |
| 11 | `Response(media_type="application/pdf")` | ✅ |
| 12 | `Content-Disposition: attachment` | ✅ |
| 13 | GET /contracts/{id}/pdf → HTTP 200, PDF válido (version 1.4) | ✅ |
| 14 | Frontend `contratos/page.tsx` baixa via blob + download | ✅ |
| 15 | Fix `generate_contract_document` para enum legado 'CLT' | ✅ |

### PASSO 3 — GAP 2: Tela Aviso Prévio
| # | Item | Status |
|---|------|--------|
| 16 | `dp/aviso-previo/page.tsx` criada (535 linhas) | ✅ |
| 17 | `calcularDiasAviso(anos) = Math.min(90, 30 + anos*3)` — Art. 487 CLT | ✅ |
| 18 | Tipos `'trabalhado'` / `'indenizado'` | ✅ |
| 19 | Modal "Novo Aviso Prévio" com Dialog + state | ✅ |
| 20 | Select funcionário + recálculo automático de dias | ✅ |
| 21 | Select tipo trabalhado/indenizado | ✅ |
| 22 | Cálculo automático `last_working_day` via `somarDias()` | ✅ |
| 23 | `concluirAviso(id)` → `POST /terminations/{id}/complete` | ✅ |
| 24 | `fetchAvisos()` via `GET /terminations` | ✅ |
| 25 | `fetchFuncionarios()` via `GET /employees?status=ativo` | ✅ |
| 26 | `dias_restantes` calculados e exibidos | ✅ |
| 27 | `StatusBadge` (ativo/concluido/cancelado) | ✅ |
| 28 | `TipoBadge` (trabalhado/indenizado) | ✅ |
| 29 | 3 cards stats (em andamento / vencendo 7d / concluídos) | ✅ |
| 30 | NAV card `Bell / Aviso Prévio` em `dp/page.tsx` | ✅ |
| 31 | `notice_type` persistido no backend (`reason` field) | ✅ |
| 32 | `status: notice_period` respeitado no create | ✅ |
| 33 | `notice_type` exposto no `GET /terminations` response | ✅ |

### PASSO 4 — Deploy
| # | Item | Status |
|---|------|--------|
| 34 | `docker cp modules/ → conecta-pro-backend` | ✅ |
| 35 | `docker restart conecta-pro-backend` | ✅ |
| 36 | Build Next.js 279/279 pages — 0 erros | ✅ |
| 37 | `docker cp .next/standalone/ → conecta-pro-frontend` (Apr 9 18:38) | ✅ |
| 38 | `docker restart conecta-pro-frontend` | ✅ |
| 39 | Frontend UP HTTP 200 | ✅ |
| 40 | `aviso-previo/page.js` compilado no container frontend | ✅ |

### Fix extra: serialização termination_controller
| # | Item | Status |
|---|------|--------|
| 41 | `list_terminations` serializa `str(t.id)` (fix PydanticSerializationError) | ✅ |
| 42 | `GET /terminations` HTTP 200 | ✅ |

### Loop N/N original (14 checks do prompt)
| # | Check | Status |
|---|-------|--------|
| 43–56 | Todos os 14 checks: 14/14 | ✅ |

### Commit + Push
| # | Item | Status |
|---|------|--------|
| 57 | `git push origin feature/people-management-reorganization` | ✅ fbc8f985 |

---

## Nota técnica: jinja2 vs reportlab

O prompt pede jinja2 + weasyprint para gerar HTML→PDF.
**Resultado do PASSO 1:** jinja2=❌ ausente, weasyprint=❌ ausente, reportlab=✅ disponível.
A lógica do prompt seleciona a primeira lib disponível (jinja2→docxtpl→fpdf→reportlab).
**reportlab foi a seleção correta.** PDF gerado: version 1.4, 2 páginas, `application/pdf` real.

---

## Arquivos modificados/criados

| Arquivo | Operação |
|---------|----------|
| `hr/services/contract_service.py` | `gerar_pdf_contrato()` + fix safe enum lookup |
| `hr/controllers/contract_controller.py` | Endpoint `GET /{id}/pdf` |
| `hr/controllers/termination_controller.py` | Fix serialização + expõe `notice_type` |
| `hr/schemas/termination.py` | Adiciona `notice_type` e `status` ao `TerminationCreate` |
| `hr/services/termination_service.py` | Persiste `notice_type` em `reason`, respeita `status` |
| `dp/contratos/page.tsx` | Download PDF blob |
| `dp/aviso-previo/page.tsx` | **NOVO** — 535 linhas |
| `dp/page.tsx` | Nav card Aviso Prévio |

---

**Score definitivo: 100% — nenhum gap restante**
*Gerado em 2026-04-09 — sessão tmux-t1*
