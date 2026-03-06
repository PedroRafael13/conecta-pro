# Discord Webhook - Guia de Configuracao

## Estado atual

A variavel `DISCORD_WEBHOOK` **nao esta configurada** no `.env` de producao.
O campo existe no `.env.example` (linha 103) mas esta vazio.
O campo foi adicionado ao `backend/core/config/settings.py` como opcional (`None` por padrao).

## Onde o Discord Webhook e usado

| Arquivo | Contexto |
|---|---|
| `.github/workflows/ci.yml` | Notifica resultado do CI (sucesso/falha) com embed colorido |
| `.github/workflows/deploy.yml` | Notifica sucesso ou falha de deploy |
| `.github/workflows/security-schedule.yml` | Notifica alertas de segurança agendados |
| `.github/workflows/openclaw.yml` | Notifica falhas do OpenClaw quality monitor (usa `DISCORD_WEBHOOK_OPENCLAW`) |
| `scripts/notify.sh` | Script generico `./notify.sh discord "<mensagem>"` |

**Importante:** Os workflows do GitHub Actions leem `DISCORD_WEBHOOK` de **GitHub Secrets**
(nao do `.env` do servidor). O `.env` e o `settings.py` sao relevantes apenas para
notificacoes enviadas diretamente pela aplicacao FastAPI via `scripts/notify.sh`.

## Como criar um Webhook no Discord

1. Abra o servidor Discord desejado
2. Va em **Configuracoes do Canal** (engrenagem ao lado do canal)
3. Clique em **Integracoes** > **Webhooks** > **Novo Webhook**
4. Dê um nome (ex: `Conecta PRO Alertas`) e selecione o canal
5. Clique em **Copiar URL do Webhook** - a URL tem o formato:
   ```
   https://discord.com/api/webhooks/XXXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

## Configuracao no servidor (.env)

Edite `/opt/conecta-pro/.env` e preencha:

```env
DISCORD_WEBHOOK=https://discord.com/api/webhooks/SEU_ID/SEU_TOKEN
```

**Nao coloque aspas ao redor da URL.**

## Configuracao no GitHub Actions (GitHub Secrets)

Os workflows leem o secret diretamente do GitHub, nao do servidor.

1. Acesse o repositorio no GitHub
2. Va em **Settings** > **Secrets and variables** > **Actions**
3. Clique em **New repository secret**
4. Crie os seguintes secrets:

| Secret | Descricao |
|---|---|
| `DISCORD_WEBHOOK` | Webhook principal (CI, deploy, security) |
| `DISCORD_WEBHOOK_OPENCLAW` | Webhook para alertas do OpenClaw (pode ser o mesmo canal ou um canal separado) |

**Nota:** `DISCORD_WEBHOOK_OPENCLAW` e configurado como **variable** (vars.), nao secret,
no workflow `openclaw.yml`. Ajuste conforme preferencia de segurança.

## Testar apos configurar

```bash
# Teste via script local (requer .env preenchido no servidor)
cd /opt/conecta-pro
source .env
./scripts/notify.sh discord "Teste de notificacao Conecta PRO"
```

Esperado: mensagem aparece no canal Discord e o script retorna `Discord: OK (HTTP 204)`.

## Canais sugeridos

- `#alertas-ci` - para notificacoes de CI/CD
- `#alertas-criticos` - para falhas de deploy e segurança
- `#openclaw` - para relatorios de qualidade automaticos

Cada canal pode ter seu proprio webhook. Nesse caso, configure secrets distintos
(`DISCORD_WEBHOOK`, `DISCORD_WEBHOOK_OPENCLAW`, etc.) nos GitHub Secrets.
