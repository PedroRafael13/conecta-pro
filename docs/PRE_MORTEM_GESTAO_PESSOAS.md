# PRE-MORTEM - GESTAO DE PESSOAS
Data: 2026-03-13
Executor: Claude Code Opus

## Cenario
> "Estamos em 30 dias. A implementacao de Gestao de Pessoas falhou.
> O ponto eletronico nao funciona offline, documentos se perdem,
> a folha de pagamento esta errada, funcionarios nao conseguem bater ponto.
> O que deu errado?"

## RISCOS IDENTIFICADOS

### Categoria: Event Bus (6)
| # | Risco | Prob | Impacto | Mitigacao |
|---|-------|------|---------|-----------|
| 1 | Redis cai e eventos se perdem | M | A | Persistencia AOF, retry queue, dead letter |
| 2 | WebSocket desconecta sem aviso | A | M | Reconnect automatico, heartbeat 30s |
| 3 | Evento duplicado processado 2x | M | A | Idempotencia via event_id, dedup SET no Redis |
| 4 | Deadlock entre agents | B | A | Timeout 5s, circuit breaker pattern |
| 5 | Fila de eventos cresce infinito | M | A | Backpressure, max queue 10k, alertas |
| 6 | Evento chega fora de ordem | M | M | Timestamp + sequence number, reordering no orchestrator |

### Categoria: Ponto Eletronico (7)
| # | Risco | Prob | Impacto | Mitigacao |
|---|-------|------|---------|-----------|
| 7 | Facial nao reconhece funcionario | M | A | Threshold ajustavel 0.6, fallback PIN manual |
| 8 | Geolocalizacao imprecisa | A | M | Aceitar accuracy ate 100m, log para auditoria |
| 9 | IndexedDB cheio no celular | B | A | Limite 500 registros, cleanup apos sync |
| 10 | Sync falha e perde batidas | M | A | Retry infinito com backoff, notifica admin |
| 11 | Batida duplicada no sync | M | M | Dedup por timestamp+employee+tipo |
| 12 | Horario do dispositivo errado | M | A | Usar server timestamp, validar delta max 5min |
| 13 | Modelo facial pesado no celular antigo | A | M | Modelo tiny 190KB, lazy loading, timeout 10s |

### Categoria: Offline/Sync (6)
| # | Risco | Prob | Impacto | Mitigacao |
|---|-------|------|---------|-----------|
| 14 | Service Worker nao instala | M | A | Fallback localStorage, detectar suporte |
| 15 | Cache corrompido | B | A | Versioning, invalidacao por hash |
| 16 | Conflito de dados no sync | M | M | Server wins, log conflito, notifica usuario |
| 17 | Ordem de sync incorreta | M | A | Ordenar por timestamp, prioridade batidas |
| 18 | Sync parcial interrompido | M | M | Transacional por batch, resume point |
| 19 | Dispositivo perde dados (reset/limpar cache) | B | A | Backup localStorage redundante, alerta "X pendentes" |

### Categoria: Agents (6)
| # | Risco | Prob | Impacto | Mitigacao |
|---|-------|------|---------|-----------|
| 20 | Agent nao inicia | B | A | Health check, restart automatico via Celery |
| 21 | Agent processa lento | M | M | Queue separada por agent, paralelismo asyncio |
| 22 | Circular dependency entre agents | M | A | Routing via Orchestrator, nunca direto |
| 23 | Agent ignora evento importante | B | A | Logging completo, wildcard handler no Orchestrator |
| 24 | Estado inconsistente entre agents | M | A | Event sourcing, reconciliacao periodica |
| 25 | Orchestrator cai e ninguem coordena | B | A | Agents funcionam autonomos para ops basicas, auto-restart |

### Categoria: Integracoes (5)
| # | Risco | Prob | Impacto | Mitigacao |
|---|-------|------|---------|-----------|
| 26 | API Solides fora do ar | M | M | Cache local, retry 3x, fallback manual |
| 27 | Google Drive quota excedida | B | M | Monitorar uso, alertas 80%, compressao |
| 28 | eSocial rejeita evento | M | A | Validacao previa schemas oficiais, fila de erros |
| 29 | Formato Dominio Sistemas muda | B | M | Parser flexivel, validacao pre-import |
| 30 | Timeout em upload grande | M | M | Chunked upload 5MB, retry, progress bar |

### Categoria: Performance (5)
| # | Risco | Prob | Impacto | Mitigacao |
|---|-------|------|---------|-----------|
| 31 | Listagem lenta com muitos funcionarios | M | M | Paginacao 50/page, indices compostos |
| 32 | Calculo de folha demora muito | M | A | Async Celery task, progress bar, cache parcial |
| 33 | WebSocket com muitas conexoes | M | M | Connection pooling, max 500 conexoes |
| 34 | face-api.js lento no celular antigo | A | M | Modelo otimizado tiny, timeout 10s, fallback |
| 35 | IndexedDB lento com muitos registros | M | M | Indices por employee_id+date, cleanup semanal |

### Categoria: Seguranca (5)
| # | Risco | Prob | Impacto | Mitigacao |
|---|-------|------|---------|-----------|
| 36 | Token JWT expira durante batida | M | M | Refresh automatico, offline nao depende de JWT |
| 37 | Foto facial vazada | B | A | Criptografia AES em repouso, acesso RBAC |
| 38 | Funcionario frauda geolocalizacao (GPS fake) | M | A | Validacao server-side, cruzar com IP, flag suspeito |
| 39 | XSS em campos de texto (justificativa) | M | A | Sanitizacao DOMPurify, CSP headers |
| 40 | Acesso nao autorizado a contracheques | B | A | RBAC por funcionario, audit log em toda visualizacao |

## RESUMO
- **Total de riscos:** 40
- **Categorias cobertas:** 7/7
- **Riscos criticos (Impacto A):** 22
- **Mitigacoes definidas:** 40/40
