# 📡 CANAL DE COMUNICAÇÃO IA-to-IA
## Kimi K2.5 ↔️ Claude Opus 4.6

### Protocolo de Comunicação

```
/opt/conecta-pro/.comm/
├── kimi-to-opus/          # Kimi escreve, Opus lê
│   ├── inbox/             # Mensagens pendentes
│   └── archive/           # Mensagens processadas
├── opus-to-kimi/          # Opus escreve, Kimi lê
│   ├── inbox/
│   └── archive/
└── shared-state/          # Estado compartilhado
    ├── current-task.json
    └── session-log.md
```

### Formato de Mensagem

```json
{
  "from": "kimi|opus",
  "to": "opus|kimi",
  "timestamp": "2026-02-07T04:00:00Z",
  "type": "request|response|notification|handoff",
  "priority": "low|normal|high|critical",
  "id": "uuid-v4",
  "in_reply_to": "uuid-v4|null",
  "payload": {
    "content": "...",
    "context": {...},
    "files": ["path/to/file"],
    "expected_response": true|false
  }
}
```

### Comandos de Verificação

```bash
# Verificar novas mensagens
ls -la /opt/conecta-pro/.comm/opus-to-kimi/inbox/

# Ler mensagem
cat /opt/conecta-pro/.comm/opus-to-kimi/inbox/*.json

# Mover para archive após processar
mv msg.json archive/

# Escrever resposta
cat > /opt/conecta-pro/.comm/kimi-to-opus/inbox/response.json << 'RESP'
{...}
RESP
```
