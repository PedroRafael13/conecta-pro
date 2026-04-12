# RELATÓRIO — Diagnóstico Nginx + Webhook Inter
**Data:** 2026-04-12
**Branch:** `feature/people-management-reorganization`

---

## SUMÁRIO EXECUTIVO

| Item | Status |
|------|--------|
| Endpoint HTTPS acessível | ✅ 200 OK |
| nginx SSL (Let's Encrypt) | ✅ Válido |
| mTLS no nginx | ❌ Não configurado |
| CA cert Inter no nginx | ❌ Não referenciado |
| Validação CA na aplicação | ✅ `_validar_assinatura_inter()` |

---

## 1 — CERTIFICADO INTER CA

```
path   : /opt/conecta-pro/credentials/inter/inter_ca.crt
subject: CN=API Intermediate Certificate Authority, O=API, L=Belo Horizonte
issuer : CN=SSSS Root Certificate Authority, O=SSSS
válido : Feb 11 2019 → Feb 8 2029
```

---

## 2 — NGINX — ESTADO ATUAL

**Arquivo:** `/etc/nginx/sites-enabled/erp.conectamais.pro`

```
SSL cert : /etc/letsencrypt/live/erp.conectamais.pro/fullchain.pem  ✅
Protocolos: TLSv1.2 + TLSv1.3
mTLS     : NÃO configurado (sem ssl_client_certificate / ssl_verify_client)
/etc/nginx/ssl/ : somente selfsigned.crt (não usado)
```

**Configuração atual do bloco `/api/`:**
- Aceita qualquer requisição sem verificar certificado cliente
- Proxy para `http://127.0.0.1:8080` (FastAPI)
- Rate limit: 30r/s, burst 50

---

## 3 — TESTE ENDPOINT VIA HTTPS

```bash
curl -sf -o /dev/null -w "%{http_code}" \
  "https://erp.conectamais.pro/api/v1/webhooks/inter/pix" \
  -X POST -H "Content-Type: application/json" \
  -d '{"pix":[{"endToEndId":"TESTE","valor":"10.00"}]}'
→ 200 ✅
```

Inter consegue chamar o endpoint — URL pública funcionando.

---

## 4 — CAMADAS DE SEGURANÇA ATUAIS

| Camada | Status | Detalhe |
|--------|--------|---------|
| HTTPS (TLS servidor) | ✅ | Let's Encrypt, TLS 1.2/1.3 |
| mTLS nginx (cert cliente) | ❌ | Não configurado |
| Validação assinatura (app) | ✅ | `_validar_assinatura_inter()` — RSA-SHA256 com CA cert |
| Sem assinatura no header | ✅ | Aceita (comportamento atual do Inter) |
| Com assinatura inválida | ✅ | Rejeita HTTP 401 |

---

## 5 — RECOMENDAÇÃO: ADICIONAR mTLS NO NGINX

Para maior segurança, adicionar bloco específico para webhooks Inter:

```nginx
# Webhooks Inter — mTLS opcional (valida cert cliente se presente)
location /api/v1/webhooks/inter/ {
    ssl_client_certificate /opt/conecta-pro/credentials/inter/inter_ca.crt;
    ssl_verify_client optional;
    proxy_set_header X-SSL-Client-Verify $ssl_client_verify;
    proxy_set_header X-SSL-Client-DN     $ssl_client_s_dn;

    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Host              $host;
    proxy_set_header X-Real-IP         $remote_addr;
    proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_connect_timeout 5s;
    proxy_send_timeout 30s;
    proxy_read_timeout 30s;
}
```

> `ssl_verify_client optional` → aceita chamadas com e sem cert cliente.
> `ssl_verify_client on` → exige cert cliente Inter em todas as chamadas.

**Importante:** requer que o Inter apresente seu certificado cliente ao chamar o webhook — confirmar com Inter se usam mTLS nos webhooks antes de ativar `on`.

---

## 6 — PENDÊNCIAS

| Item | Ação |
|------|------|
| mTLS nginx | Aguardar confirmação Inter sobre uso de cert cliente em webhooks |
| Portal Inter | Habilitar escopos webhook em `developers.inter.co` (login: `contato@conectamaistech.com.br`) |
| Certificado folha | Solicitar ao Inter o cert folha de assinatura para validação RSA funcionar em produção |

---

**Relatório gerado:** 2026-04-12
