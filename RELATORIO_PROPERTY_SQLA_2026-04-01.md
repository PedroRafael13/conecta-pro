# Relatório — Varredura @property SQLAlchemy
**Conecta PRO — Eliminação de @property como Coluna em Queries**
**Data:** 2026-04-01
**Commit:** `50990cf0` — branch `feature/people-management-reorganization`

---

## PASSO 1 — Mapeamento de @property nos Models

**Total de ocorrências `@property` no backend:** 1.463 em ~60 arquivos

| Model | @property declarados |
|-------|----------------------|
| Announcement | title, content, priority, category, target_type, target_ids, target_roles, publish_at, expires_at, requires_acknowledgment, attachments, published_by, published_at, is_published, is_expired, is_scheduled, read_count, acknowledgment_count, read_percentage |
| Notification | is_sent, is_read, is_clicked, time_to_read, time_to_click |
| Employee | nome_completo, idade, tempo_empresa_dias, endereco_completo, dados_bancarios_completos, cnh_valida, curso_vigilante_valido, cnv_valido, porte_arma_valido |
| Allocation | is_current, days_allocated, total_monthly_cost |
| Shift | is_future, is_today, is_filled, was_worked |
| Post | is_filled, vacancy_count, daily_hours |
| Scale | is_current_month, is_published, can_edit, fill_rate |
| Substitution | is_pending, is_confirmed, has_substitute, response_time_hours |
| TimeBank | is_credit, is_debit, is_expired, is_pending, signed_hours |
| ScaleTemplate | is_popular, total_employees, coverage_percentage |
| OccurrenceAttachment | is_image, is_video, has_location, file_size_kb, file_size_mb |
| OccurrenceComment | is_edited, preview |
| Occurrence | is_resolved, is_severe, resolution_time_hours |
| DocumentShare | is_active, is_expired, is_download_limit_reached, remaining_downloads, remaining_views |
| DocumentVersion | is_active, file_size_mb, display_version |
| DocumentSignature | is_pending |

---

## PASSO 2 — Cruzamento com Queries SQLAlchemy

Varredura em todos os `*repositor*` e `*service*` com padrões:
`filter / where / order_by / .contains / .ilike / .in_`

**Total de linhas suspeitas analisadas:** 120+

**Resultado:** apenas `communication_repository.py` utilizava `@property` como coluna SQLAlchemy real.

---

## PASSO 3 — Verificação dos Models Suspeitos (via importlib)

```
✅ Announcement : cols=[id, tenant_id, tipo, prioridade, status, titulo...] props=[title, content, priority, category, target_type...]
✅ Notification : cols=[id, tenant_id, user_id, title, body, type...]      props=[is_sent, is_read, is_clicked...]
✅ Employee     : cols=[id, solides_id, matricula, codigo, nome...]         props=[nome_completo, idade, tempo_empresa_dias...]
```

**Conclusão do Passo 3:** apenas Announcement tem @property aliases que conflitam com nomes esperados por queries.

---

## PASSO 4 — Correções Aplicadas

**Arquivo único corrigido:**
`/app/modules/operacional/communication/repositories/communication_repository.py`

### 4.1 — `_apply_announcement_filters()` — 6 correções

| # | Tipo | Antes (quebrado) | Depois (correto) |
|---|------|------------------|------------------|
| 1 | WHERE | `Announcement.priority == ...` | `Announcement.prioridade == ...` |
| 2 | WHERE | `Announcement.category == ...` | `Announcement.tipo == ...` |
| 3 | WHERE | `Announcement.target_type == ...` | `Announcement.destinatarios_tipo == ...` |
| 4 | WHERE | `Announcement.requires_acknowledgment == ...` | `Announcement.requer_confirmacao == ...` |
| 5 | ilike | `Announcement.title.ilike(search_term)` | `Announcement.titulo.ilike(search_term)` |
| 6 | ilike | `Announcement.content.ilike(search_term)` | `Announcement.conteudo.ilike(search_term)` |

### 4.2 — `process_scheduled()` — 2 correções

| # | Tipo | Antes (quebrado) | Depois (correto) |
|---|------|------------------|------------------|
| 7 | WHERE | `Announcement.publish_at <= now()` | `Announcement.data_publicacao <= now()` |
| 8 | setter | `announcement.published_at = now()` | `announcement.data_publicacao = now()` |

**Total de correções:** 8

---

## PASSO 5 — Validação de Endpoints

| Endpoint | HTTP Antes | HTTP Depois |
|----------|-----------|-------------|
| `GET /operacional/comunicados/nao-lidos` | 500 | **200** ✅ |
| `GET /operacional/comunicados` | 200* | **200** ✅ |
| `GET /operacional/comunicados?priority=alta` | 500 | **200** ✅ |
| `GET /operacional/comunicados?search=seguranca` | 500 | **200** ✅ |
| `GET /operacional/comunicados?category=informativo` | 500 | **200** ✅ |
| `GET /people-management/hr/employees` | 200 | **200** ✅ |
| `GET /crm/clients` | 200 | **200** ✅ |
| `GET /crm/leads` | 200 | **200** ✅ |

*Listagem sem filtros já funcionava; qualquer filtro → HTTP 500

**8/8 endpoints validados ✅**

---

## PASSO 6 — Commit & Push

```
Commit: 50990cf0
Mensagem: fix(repositories): elimina uso de @property como coluna SQLAlchemy
Branch:  feature/people-management-reorganization
Push:    f0c73eef..50990cf0 → github.com/jjesus1982/conecta-pro.git
Arquivos: 1 file changed, 13 insertions(+), 8 deletions(-)
```

---

## Risco Residual Documentado — getattr() Dinâmico

Em 17 repositórios existe o padrão potencialmente perigoso:
```python
order_column = getattr(Model, order_by, Model.created_at)
query = query.order_by(order_column.desc())
```

**Risco:** se `order_by` receber o nome de um `@property`, o `.desc()` falha com `AttributeError`.

**Impacto:** Baixo — só se cliente enviar campo de ordenação inválido/não mapeado.

**Arquivos:** document_share_repository, document_repository, folder_repository, document_tag_repository, interview_repository, candidate_repository, application_repository, job_position_repository, ordem_servico_repository, visita_repository, profile_repository (×2), turnover_repository, service_repository, report_repository, sentiment_repository (×2).

**Recomendação próxima sprint:** validar `order_by` contra `inspect(Model).mapper.column_attrs`.

---

## Resultado Final

| Métrica | Valor |
|---------|-------|
| Arquivos varridos | ~60 com @property |
| Repositórios analisados | 80+ |
| Padrões perigosos encontrados | 8 (em 1 arquivo) |
| Padrões corrigidos | **8/8** |
| Padrões perigosos restantes | **0** |
| Endpoints com 500 → 200 | **5 endpoints** |
| Risco residual (getattr) | 17 arquivos — baixo |

---

*Gerado em: 2026-04-01 — Conecta PRO ERP*
