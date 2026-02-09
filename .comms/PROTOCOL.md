# Protocolo de Comunicação Inter-IA

## Participantes
- **Claude Opus 4.6** (claude) — Arquitetura, planning, auditoria, review
- **Kimi K2.5** (kimi) — Coding em volume, implementação, testes

## Canal de Mensagens

### Formato JSONL (uma mensagem por linha)
```json
{"ts":"2026-02-07T04:30:00Z","from":"claude","to":"kimi","type":"task","id":"msg-001","reply_to":null,"priority":"normal","subject":"Criar endpoint de reembolsos","content":"..."}
```

### Arquivos
| Arquivo | Quem escreve | Quem lê |
|---------|-------------|---------|
| `messages/claude-out.jsonl` | Claude | Kimi |
| `messages/kimi-out.jsonl` | Kimi | Claude |

### Tipos de Mensagem
| type | Uso |
|------|-----|
| `task` | Delegar tarefa para o outro |
| `response` | Responder a uma mensagem |
| `review` | Solicitar review de código |
| `review-result` | Resultado de um review |
| `question` | Perguntar algo |
| `status` | Atualizar status de progresso |
| `handoff` | Encerramento de sessão |

### Prioridade
- `urgent` — Parar o que está fazendo e atender
- `high` — Próxima coisa a fazer
- `normal` — Fila normal

## Regras

1. **Sempre ler mensagens antes de começar trabalho novo**
   - Claude lê `messages/kimi-out.jsonl`
   - Kimi lê `messages/claude-out.jsonl`

2. **Sempre responder mensagens pendentes**
   - Se recebeu `task` → responder com `status` (accepted/rejected) e depois `response` (resultado)
   - Se recebeu `review` → responder com `review-result`
   - Se recebeu `question` → responder com `response`

3. **Não editar arquivo do outro**
   - Claude só escreve em `claude-out.jsonl`
   - Kimi só escreve em `kimi-out.jsonl`

4. **Append-only** — Nunca deletar mensagens, sempre adicionar ao final

5. **ID de mensagem** — Formato: `{from}-{timestamp}` (ex: `claude-1707278400`)

6. **reply_to** — Ao responder, colocar o `id` da mensagem original

## Arquivos de Estado Compartilhado

| Arquivo | Propósito | Quem atualiza |
|---------|-----------|---------------|
| `BACKLOG.md` | Tarefas pendentes do projeto | Ambos |
| `DECISIONS.md` | Decisões de arquitetura | Ambos |
| `SESSION_LOG.md` | Log cronológico de ações | Ambos (append) |
| `HANDOFF.md` | Resumo para próxima sessão | Quem encerrar por último |

## Fluxo de Início de Sessão

```
1. Ler HANDOFF.md → entender onde paramos
2. Ler BACKLOG.md → ver tarefas pendentes
3. Ler messages/{outro}-out.jsonl → ver mensagens não lidas
4. Registrar início em SESSION_LOG.md
5. Começar a trabalhar
```

## Fluxo de Encerramento

```
1. Registrar progresso em SESSION_LOG.md
2. Atualizar BACKLOG.md (marcar feitos, adicionar novos)
3. Escrever HANDOFF.md com resumo
4. Enviar mensagem type=handoff
```
