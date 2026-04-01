---
title: Inter-AI Communication
description: Protocolo de comunicação com Claude Opus 4.6 via filesystem
partner: claude-opus-4.6
---

# Comunicação com Claude Opus 4.6

Sistema de comunicação bidirecional entre Kimi K2.5 e Claude Opus 4.6.
Ambos operam no mesmo servidor VPS no projeto Conecta PRO.

## Início de Sessão (OBRIGATÓRIO)

Ao iniciar qualquer sessão, SEMPRE execute:

```bash
# 1. Ler onde paramos
cat /opt/conecta-pro/.comms/HANDOFF.md

# 2. Ler tarefas pendentes
cat /opt/conecta-pro/.comms/BACKLOG.md

# 3. Ler mensagens do Claude não respondidas
cat /opt/conecta-pro/.comms/messages/claude-out.jsonl | tail -20

# 4. Registrar início da sessão
echo "" >> /opt/conecta-pro/.comms/SESSION_LOG.md
echo "## Sessão $(date '+%Y-%m-%d') #N" >> /opt/conecta-pro/.comms/SESSION_LOG.md
echo "**Participante:** Kimi K2.5" >> /opt/conecta-pro/.comms/SESSION_LOG.md
echo "**Início:** $(date '+%H:%M') UTC" >> /opt/conecta-pro/.comms/SESSION_LOG.md
```

## Enviar Mensagem para Claude

Adicionar uma linha JSONL ao arquivo de saída:

```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","from":"kimi","to":"claude","type":"TYPE","id":"kimi-'$(date +%s)'","reply_to":null,"priority":"normal","subject":"ASSUNTO","content":"CONTEÚDO"}' >> /opt/conecta-pro/.comms/messages/kimi-out.jsonl
```

### Tipos de mensagem:
- `status` — Atualizar Claude sobre progresso
- `response` — Responder a tarefa/pergunta do Claude
- `question` — Perguntar algo ao Claude
- `review` — Solicitar review de código
- `review-result` — Resultado de review solicitado
- `handoff` — Ao encerrar sessão

## Ler Mensagens do Claude

```bash
# Últimas mensagens
tail -5 /opt/conecta-pro/.comms/messages/claude-out.jsonl

# Mensagens não respondidas (sem reply_to correspondente)
cat /opt/conecta-pro/.comms/messages/claude-out.jsonl
```

## Checkar Mensagens Periodicamente

A cada tarefa completada ou a cada ~10 minutos:

```bash
# Ver se há mensagens novas
wc -l /opt/conecta-pro/.comms/messages/claude-out.jsonl
```

## Atualizar Estado Compartilhado

### Ao completar tarefa:
```bash
# Registrar no session log
echo "- [$(date '+%H:%M')] Kimi: Completou TAREFA" >> /opt/conecta-pro/.comms/SESSION_LOG.md
```

### Ao tomar decisão de arquitetura:
```bash
# Adicionar em DECISIONS.md
echo "" >> /opt/conecta-pro/.comms/DECISIONS.md
echo "## DEC-NNN: Título (vigente)" >> /opt/conecta-pro/.comms/DECISIONS.md
echo "- **Data:** $(date '+%Y-%m-%d')" >> /opt/conecta-pro/.comms/DECISIONS.md
echo "- **Decisão:** ..." >> /opt/conecta-pro/.comms/DECISIONS.md
```

## Encerramento de Sessão

```bash
# 1. Atualizar HANDOFF.md com resumo
# 2. Atualizar BACKLOG.md (marcar feitos)
# 3. Enviar mensagem handoff
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","from":"kimi","to":"claude","type":"handoff","id":"kimi-'$(date +%s)'","reply_to":null,"priority":"normal","subject":"Encerramento de sessão","content":"RESUMO DO QUE FOI FEITO"}' >> /opt/conecta-pro/.comms/messages/kimi-out.jsonl
```

## Arquivos de Referência

| Arquivo | Propósito |
|---------|-----------|
| `.comms/PROTOCOL.md` | Regras completas do protocolo |
| `.comms/HANDOFF.md` | Onde paramos (ler ao iniciar) |
| `.comms/BACKLOG.md` | Tarefas pendentes |
| `.comms/DECISIONS.md` | Decisões de arquitetura |
| `.comms/SESSION_LOG.md` | Log cronológico |
| `.comms/messages/claude-out.jsonl` | Mensagens do Claude (ler) |
| `.comms/messages/kimi-out.jsonl` | Suas mensagens (escrever) |
