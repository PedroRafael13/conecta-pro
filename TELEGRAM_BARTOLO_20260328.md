# TELEGRAM → BARTOLO — RELATÓRIO DE INTEGRAÇÃO
## Data: 2026-03-28 | Commit: 91dbe131

---

## 1. O QUE FOI FEITO

### Integração via Tool (não substituição)

O bot Telegram já era robusto — 19 tools, system prompt executivo,
histórico de conversa, tool chaining recursivo. Em vez de substituir
a arquitetura, adicionei o **Bartolo como mais uma tool** do Claude.

```
ANTES:
  Jordan manda msg → Claude Sonnet → tools SQL/DevOps → resposta

DEPOIS:
  Jordan manda msg → Claude Sonnet → tools SQL/DevOps → resposta
                                    → ask_bartolo → 12 skills + 11 agents
```

Claude decide automaticamente quando usar o Bartolo (operacional)
vs as tools SQL diretas (financeiro) vs DevOps (containers).

### Modificações no telegram_assistant.py

**1. Nova tool na lista TOOLS:**
```python
{
    "name": "ask_bartolo",
    "description": "Conversa com o Bartolo, assistente de IA operacional...",
    "input_schema": {
        "type": "object",
        "properties": {
            "mensagem": {"type": "string", "description": "Pergunta..."}
        },
        "required": ["mensagem"]
    }
}
```

**2. Nova função ask_bartolo():**
```python
def ask_bartolo(mensagem: str) -> str:
    # 1. Login via API (obtém JWT)
    # 2. POST /api/v1/ai/bartolo/send
    # 3. Retorna resposta + model_used + data_results
```

**3. Registro em TOOL_FUNCTIONS:**
```python
"ask_bartolo": lambda mensagem="", **_: ask_bartolo(mensagem),
```

### O que NÃO foi mudado

- System prompt (já excelente)
- Tools existentes (19 tools de negócio + DevOps)
- Histórico de conversa
- Loop de polling
- Lógica de tool chaining
- Autorização por chat_id
- Todas as functions existentes (saldo, inadimplentes, etc.)

---

## 2. O QUE O BARTOLO ADICIONA VIA TELEGRAM

### 12 Skills agora acessíveis
| Skill | Exemplo de pergunta |
|-------|-------------------|
| escala | "quais escalas estão publicadas?" |
| posto | "quantos postos ativos temos?" |
| ronda | "tem ronda agendada para hoje?" |
| diarista | "quem está escalado como diarista amanhã?" |
| ocorrencia | "tem ocorrência aberta nas últimas 24h?" |
| disciplinar | "quantas advertências temos este mês?" |
| banco_horas | "qual saldo de banco de horas do setor?" |
| comunicado | "tem comunicado pendente de leitura?" |
| substituto | "quem pode cobrir o posto Vila Flores?" |
| alerta | "tem alerta crítico ativo?" |
| cobertura | "relatório de cobertura da semana" |
| briefing | "me dá o briefing do dia" |

### 11 Agents com detecção de intenção
O Bartolo classifica a intenção via Claude Anthropic e direciona
para o agent correto (escala, posto, ronda, etc.).

### 10 Wizards guiados
Jordan pode iniciar fluxos step-by-step via Telegram:
- "quero criar uma escala" → EscalaWizard (8 steps)
- "preciso admitir um funcionário" → AdmissaoWizard (8 steps)
- "gera uma proposta comercial" → PropostaWizard (9 steps)

---

## 3. COMO FUNCIONA O ROTEAMENTO

Claude Sonnet decide automaticamente:

| Tipo de pergunta | Tool escolhida | Fonte de dados |
|-----------------|---------------|---------------|
| "qual meu saldo?" | get_saldo_bancario | SQL direto |
| "quantos postos ativos?" | ask_bartolo | DataConnector |
| "quem não pagou?" | get_inadimplentes | SQL direto |
| "tem ronda hoje?" | ask_bartolo | DataConnector |
| "reinicia o backend" | restart_container | Docker CLI |
| "gera o kit do Mirante" | gerar_kit_cliente | API GED |
| "como está a escala?" | ask_bartolo | DataConnector |
| "meu briefing" | get_briefing | API Briefing |

O Claude mantém o contexto de conversa (10 trocas) e pode
encadear múltiplas tools na mesma resposta.

---

## 4. ARQUITETURA FINAL DO BOT

```
Jordan (Telegram)
  ↓
@conectapro_alertas_bot (PM2)
  ↓
Claude Sonnet 4 (Anthropic API)
  ↓ decide qual tool usar
  ├── get_saldo_bancario()     → SQL direto (PostgreSQL)
  ├── get_inadimplentes()      → SQL direto
  ├── get_recebimentos()       → SQL direto
  ├── get_folha_pagamento()    → SQL direto
  ├── get_equipe()             → SQL direto
  ├── get_status_kits()        → SQL direto
  ├── get_nfse_status()        → SQL direto
  ├── get_analise_cliente()    → SQL direto
  ├── gerar_kit_cliente()      → API GED
  ├── get_briefing()           → API Briefing
  ├── ask_bartolo()            → API Bartolo (12 skills)  ← NOVO
  ├── get_system_status()      → Docker + system
  ├── run_tests()              → pytest
  ├── get_logs()               → Docker logs
  ├── restart_container()      → Docker restart
  ├── get_interventions()      → OpenClaw DB
  ├── force_backup()           → pg_dump
  ├── get_coverage()           → pytest
  ├── get_alerts()             → Alertmanager
  └── run_command()            → Shell
```

**20 tools** (era 19) — 10 negócio + 1 Bartolo + 9 DevOps.

---

## 5. TESTES

### Bot reiniciou sem erro
```
[02:22:33] Assistente Conecta PRO iniciando...
[02:22:33] Claude model: claude-sonnet-4-20250514
[02:22:34] Online. Aguardando mensagens...
```

### Para testar no Telegram
Mande estas mensagens para @conectapro_alertas_bot:

1. "quantos postos ativos temos?" → deve usar ask_bartolo
2. "qual meu saldo?" → deve usar get_saldo_bancario (SQL direto)
3. "como está a escala da semana?" → deve usar ask_bartolo
4. "status dos containers" → deve usar get_system_status

---

## 6. NOTA SOBRE ADMIN_PASS

A função ask_bartolo usa `os.getenv("ADMIN_PASS")` para autenticar
no Bartolo. Para funcionar, adicionar no .env:

```env
ADMIN_USER=jjesus@conectamais.pro
ADMIN_PASS=Jordan0612
```

Se não estiver configurado, o Bartolo retorna erro de autenticação
e Claude usa as tools SQL diretas como fallback.

---

## DOWNLOAD

```bash
scp root@82.25.75.74:/opt/conecta-pro/TELEGRAM_BARTOLO_20260328.md ~/Desktop/
```
