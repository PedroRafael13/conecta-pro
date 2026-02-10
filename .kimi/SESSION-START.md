# SESSION START — LEIA ISTO PRIMEIRO

**OBRIGATÓRIO:** Leia este arquivo INTEIRO antes de fazer QUALQUER coisa.

## Passo 1: Contexto
```bash
cat /opt/conecta-pro/.comms/HANDOFF.md
cat /opt/conecta-pro/.comms/BACKLOG.md
tail -20 /opt/conecta-pro/.comms/messages/claude-out.jsonl
```

## Passo 2: Baseline atual
```bash
cat /opt/conecta-pro/.comms/BASELINE.json
```
Estes são os números REAIS verificados pelo Claude. Sua meta é melhorá-los.

## Passo 3: Estado do ambiente
```bash
cat /opt/conecta-pro/.kimi/ENVIRONMENT.md
```

## Passo 4: Regras operacionais
```bash
cat /opt/conecta-pro/.kimi/REGRAS-OPERACIONAIS.md
```

## Passo 5: Registrar início de sessão
```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","from":"kimi","to":"claude","type":"status","id":"kimi-'$(date +%s)'","reply_to":null,"priority":"normal","subject":"Session Start","content":"Sessão iniciada. Baseline lido. Ambiente verificado."}' >> /opt/conecta-pro/.comms/messages/kimi-out.jsonl
```

## Passo 6: Verificação pré-trabalho
```bash
/opt/conecta-pro/scripts/verify-all.sh
```
Guardar este output. É seu ANTES. Ao final, comparar com o DEPOIS.

---

**SÓ DEPOIS de completar todos os 6 passos, comece a trabalhar.**
