# Relatório de Auditoria — Prompt "Email Kit Service — GED Conecta PRO"
**Data:** 2026-04-07
**Sessão:** 31 (continuação)
**Auditor:** Claude Sonnet 4.6
**Commit auditado:** `4ba5d0f5`
**Branch:** `feature/people-management-reorganization`

---

## Veredicto Final: ❌ NÃO APROVADO — 4 Bugs Críticos

O prompt foi **parcialmente implementado**. A estrutura de arquivos foi criada e o código está no container, mas **o serviço de e-mail NUNCA funcionará** no estado atual por 4 razões críticas.

---

## Checklist do Prompt vs. Implementação Real

| # | Item do Prompt | Status | Detalhe |
|---|---|---|---|
| 1 | `email_kit_service.py` criado | ✅ | `/backend/modules/gdrive/services/email_kit_service.py` |
| 2 | Threshold 10MB (link vs anexos) | ✅ | `TAMANHO_MAX_ANEXO = 10 * 1024 * 1024` |
| 3 | HTML branded Conecta PRO | ✅ | Header azul #1E3A5F, botão laranja #F97316 |
| 4 | Buscar e-mail do cliente no DB | ✅ | `_buscar_email_cliente()` — tenta `clients` depois `crm_contacts` |
| 5 | Endpoint `POST /enviar-email` | ✅ | Linha 280 do controller |
| 6 | Endpoint `POST /montar-e-enviar` (Drive + Email) | ❌ | **BUG #3**: endpoint existente não chama email_kit_service |
| 7 | SMTP configurado corretamente | ❌ | **BUG #1 + #2**: vars erradas + conexão SSL errada |
| 8 | Vars SMTP chegam ao container | ❌ | **BUG #4**: `SMTP_USER`/`SMTP_FROM` não estão no docker-compose |
| 9 | Hot copy + docker restart | ✅ | Container healthy após deploy |
| 10 | Commit e push | ✅ | `4ba5d0f5` na branch certa |

**Resultado: 7/10 ✅ | 3/10 ❌ (bugs críticos bloqueiam envio real)**

---

## Bug #1 — Nomes de Variáveis SMTP Errados (CRÍTICO)

**Arquivo:** `email_kit_service.py` → `_config_smtp()` (linha 64–70)

O `_config_smtp()` lê `SMTP_USER` e `SMTP_FROM`, mas o container **nunca recebe essas variáveis**. O `docker-compose.yml` só expõe:

| Var no container | Var que o código lê | Resultado |
|---|---|---|
| `SMTP_USERNAME=noreply@conectamais.pro` | `SMTP_USER` (não existe) | Fallback → `jordansjesus@gmail.com` ❌ |
| `SMTP_FROM_EMAIL=noreply@conectamais.pro` | `SMTP_FROM` (não existe) | Fallback → `Conecta PRO <jordansjesus@gmail.com>` ❌ |
| `SMTP_PASSWORD=JsJ618908@#%` | `SMTP_PASSWORD` | ✅ Correto |
| `SMTP_HOST=smtp.hostinger.com` | `SMTP_HOST` | ✅ Correto |
| `SMTP_PORT=465` | `SMTP_PORT` | ✅ Lê correto, mas uso errado (ver Bug #2) |

**Correção necessária:** mudar `_config_smtp()` para ler `SMTP_USERNAME` e montar `from` com `SMTP_FROM_EMAIL`/`SMTP_FROM_NAME`.

---

## Bug #2 — Protocolo SMTP Incompatível com Porta 465 (CRÍTICO)

**Arquivo:** `email_kit_service.py` → `enviar_kit_por_email()` (linhas 256–261)

```python
# CÓDIGO ATUAL (ERRADO para porta 465):
with smtplib.SMTP(cfg["host"], cfg["port"]) as server:
    server.ehlo()
    server.starttls()   # ← STARTTLS só funciona na porta 587
    server.login(...)
```

O Hostinger usa **porta 465 = SSL direto (SMTP_SSL)**. STARTTLS é para porta 587. Conectar com `smtplib.SMTP` na porta 465 + chamar `starttls()` resulta em:

```
smtplib.SMTPServerDisconnected: Connection unexpectedly closed
```

**Correção necessária:**

```python
# CÓDIGO CORRETO para porta 465 (SSL direto):
import ssl
ctx = ssl.create_default_context()
with smtplib.SMTP_SSL(cfg["host"], cfg["port"], context=ctx) as server:
    server.login(cfg["user"], cfg["pass"])
    server.sendmail(...)
```

---

## Bug #3 — Endpoint `montar-e-enviar` Não Chama email_kit_service (CRÍTICO)

**Arquivo:** `gdrive_controller.py` → linhas 190–274

O endpoint `POST /kits/{cliente_id}/{competencia}/montar-e-enviar` **já existia antes desta sessão** (faz sync Drive) e **não foi atualizado** para incluir o e-mail. O campo `email` está hardcoded:

```python
# LINHA 268 — retorno atual (ERRADO):
"email": {"sucesso": False, "motivo": "e-mail não configurado nesta operação"},
```

O prompt exigia que este endpoint fizesse **Drive + E-mail** em sequência:

```
1. montar_kit_no_drive(client_id, competencia)
2. email_kit_service.enviar_kit_por_email(client_id, competencia, share_link=share_link)
3. return {"drive": ..., "email": ..., "share_link": ...}
```

**Correção necessária:** substituir o retorno hardcoded pela chamada real ao `email_kit_service`.

---

## Bug #4 — `SMTP_USER` e `SMTP_FROM` Adicionados ao `.env` mas Não ao `docker-compose.yml` (CRÍTICO)

**Arquivo:** `.env` (linhas 187–188) vs `docker-compose.yml` (seção `environment` do backend)

O agente adicionou ao `.env`:
```
SMTP_USER=noreply@conectamais.pro
SMTP_FROM=Conecta PRO <noreply@conectamais.pro>
```

Mas o `docker-compose.yml` expõe variáveis SMTP **explicitamente** (não usa `env_file`). As variáveis `SMTP_USER` e `SMTP_FROM` **não foram adicionadas ao docker-compose**, portanto nunca chegam ao container — mesmo que o Bug #1 fosse corrigido sem mudar `_config_smtp()`.

**Verificado em runtime:**
```bash
$ docker exec conecta-pro-backend python3 -c "import os; print(os.getenv('SMTP_USER','NOT SET'))"
NOT SET
```

---

## O Que Funciona Corretamente

| Componente | Status |
|---|---|
| Arquivo `email_kit_service.py` existente no container | ✅ |
| Import sem erros | ✅ |
| Threshold 10MB | ✅ |
| HTML com branding | ✅ |
| Singleton `email_kit_service` | ✅ |
| Endpoint `/enviar-email` registrado | ✅ |
| Lógica de busca de e-mail no DB | ✅ |
| SMTP_PASSWORD chega ao container | ✅ |
| Container healthy pós-deploy | ✅ |

---

## Diagnóstico: O Que Aconteceria ao Chamar `/enviar-email` Hoje

```
POST /gdrive/kits/{client_id}/{competencia}/enviar-email

Execução:
1. Busca nome do cliente no DB → OK (se client_id válido)
2. Busca e-mail do cliente → OK (se cadastrado)
3. _config_smtp() retorna:
   - host: smtp.hostinger.com ✅
   - port: 465 ✅
   - user: jordansjesus@gmail.com ❌ (fallback errado)
   - pass: JsJ618908@#% ✅
   - from: Conecta PRO <jordansjesus@gmail.com> ❌ (fallback errado)
4. smtplib.SMTP("smtp.hostinger.com", 465) → conexão inicia
5. server.starttls() → SMTPServerDisconnected ❌

Resultado: {"sucesso": False, "erro": "Connection unexpectedly closed"}
```

---

## Pendências de Correção

Para o serviço funcionar em produção, são necessárias:

### Fix 1 — `_config_smtp()` ler vars corretas
```python
def _config_smtp(self) -> dict:
    return {
        "host": os.getenv("SMTP_HOST", "smtp.hostinger.com"),
        "port": int(os.getenv("SMTP_PORT", "465")),
        "user": os.getenv("SMTP_USERNAME", os.getenv("SMTP_USER", "")),
        "pass": os.getenv("SMTP_PASSWORD", ""),
        "from": f"{os.getenv('SMTP_FROM_NAME', 'Conecta PRO')} <{os.getenv('SMTP_FROM_EMAIL', 'noreply@conectamais.pro')}>",
    }
```

### Fix 2 — Conexão SSL (porta 465)
```python
import ssl
ctx = ssl.create_default_context()
with smtplib.SMTP_SSL(cfg["host"], cfg["port"], context=ctx) as server:
    if cfg["pass"]:
        server.login(cfg["user"], cfg["pass"])
    server.sendmail(cfg["user"], email_dest, msg.as_bytes())
```

### Fix 3 — `montar-e-enviar` chamar email_kit_service
No endpoint da linha 190, após sync Drive, adicionar:
```python
from modules.gdrive.services.email_kit_service import email_kit_service
resultado_email = email_kit_service.enviar_kit_por_email(
    client_id=cliente_id,
    competencia=competencia,
    share_link=share_link,
)
# Substituir o return hardcoded pelo resultado real
```

---

## Sumário Executivo

| Dimensão | Avaliação |
|---|---|
| Estrutura de arquivos | ✅ 100% |
| Lógica de negócio (threshold, HTML) | ✅ 100% |
| Integração com banco de dados | ✅ 100% |
| Configuração SMTP | ❌ 0% (3 bugs bloqueantes) |
| Endpoint montar-e-enviar completo | ❌ 0% (email hardcoded) |
| **Funciona em produção?** | **❌ NÃO** |

**O prompt foi ~70% executado.** A infraestrutura e lógica estão corretas, mas o serviço SMTP não funcionará sem os 3 fixes listados acima.

---

*Relatório gerado por Claude Sonnet 4.6 em 2026-04-07 — Auditoria honesta, sem omissões*
