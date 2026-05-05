# T1-CHATWOOT-ONBOARDING CPRO12 — Fix Redirect Loop /installation/onboarding
**Data:** 2026-05-05
**Branch:** feature/people-management-reorganization
**Tipo:** DIAGNÓSTICO READ-ONLY + FIX CIRÚRGICO (zero alteração de código)

---

## RESULTADO — SUCESSO

> `/app/login` retorna HTTP 200.
> Redirect loop para `/installation/onboarding` eliminado.
> Causa raiz: chave Redis `CHATWOOT_INSTALLATION_ONBOARDING = "true"` — deletada.

---

## STEP 1 — Estado completo do banco Chatwoot

| Entidade | Estado |
|----------|--------|
| SuperAdmin | jjesus@conectamais.pro \| id=1 |
| User | Jordan Jesus \| confirmed=true \| sign_in_count=1 |
| Account | Conecta Mais \| id=1 |
| AccountUser | role=administrator \| account_id=1 |
| INSTALLATION_ONBOARDING_DONE | true (InstallationConfig no banco) |

---

## STEP 2 — Variáveis de ambiente relevantes

| Variável | Valor |
|----------|-------|
| FRONTEND_URL | https://chat.conectamais.pro |
| RAILS_ENV | production |
| INSTALLATION_ENV | docker |
| FORCE_SSL | false |
| DEFAULT_LOCALE | pt_BR |

---

## STEP 3 — Lógica do redirect (causa raiz)

O redirect está em `DashboardController#ensure_installation_onboarding`:

```ruby
# /app/app/controllers/dashboard_controller.rb
def ensure_installation_onboarding
  redirect_to '/installation/onboarding' if ::Redis::Alfred.get(::Redis::Alfred::CHATWOOT_INSTALLATION_ONBOARDING)
end
```

**Gate real = chave Redis**, não o `InstallationConfig` do banco.
- Chave **existe** → redireciona para onboarding
- Chave **ausente (nil)** → não redireciona

O `InstallationConfig.INSTALLATION_ONBOARDING_DONE` é apenas para exibição no painel — irrelevante para o redirect.

---

## STEP 4 — FRONTEND_URL

`https://chat.conectamais.pro` — correto. Não era o problema.

---

## STEP 5 — Login via API

```
POST /auth/sign_in → HTTP 200
{
  "access_token": "NjEyLiq5e1UmaveZhW1EzvXL",
  "type": "SuperAdmin",
  "role": "administrator",
  "confirmed": true
}
```
API funcionando perfeitamente. O problema era exclusivamente o redirect do DashboardController.

---

## STEP 6 — Logs e headers

| Request | Antes do fix | Após o fix |
|---------|-------------|-----------|
| GET /app/login | HTTP 302 → /installation/onboarding | HTTP 200 ✅ |
| GET / | HTTP 302 → /installation/onboarding | HTTP 200 ✅ |

---

## STEP 7 — Fix aplicado (Cenário D + limpeza de cache)

### Fix principal — deletar chave Redis

```ruby
Redis::Alfred.delete(Redis::Alfred::CHATWOOT_INSTALLATION_ONBOARDING)
# Antes: "true"
# Depois: nil
```

### Cache Rails limpo

```ruby
Rails.cache.clear
# → Cache limpo
```

### Verificação pós-cache clear

```
InstallationConfig.find_by(name: 'INSTALLATION_ONBOARDING_DONE').value → true ✅
Redis::Alfred.get(CHATWOOT_INSTALLATION_ONBOARDING) → nil ✅
```

---

## Auditoria pós-execução

### Gap encontrado: STEP 7 — `Rails.cache.clear` e verificação pós-clear não executados

**Prompt especificou:**
```bash
docker exec chatwoot bundle exec rails runner "Rails.cache.clear; puts 'Cache limpo'"
docker exec chatwoot bundle exec rails runner "puts InstallationConfig.find_by(name: 'INSTALLATION_ONBOARDING_DONE')&.value.inspect"
```
**Executados na auditoria:** Cache limpo ✅ | `INSTALLATION_ONBOARDING_DONE = true` persiste ✅

---

## SELF-CHECK (7 itens)

| Item | Status |
|------|--------|
| STEP 1 — estado completo do banco (6 queries) | ✅ |
| STEP 2 — env vars (FRONTEND_URL, RAILS_ENV, etc.) | ✅ |
| STEP 3 — lógica redirect no código identificada | ✅ DashboardController |
| STEP 4 — FRONTEND_URL verificado | ✅ correto, não era o problema |
| STEP 5 — login via API testado | ✅ HTTP 200, token retornado |
| STEP 6 — logs + curl -I executados | ✅ |
| STEP 7 — fix Redis + cache clear + verificação | ✅ (cache clear executado na auditoria) |

---

**T1-CHATWOOT-ONBOARDING CPRO12 OK — redirect loop eliminado. `/app/login` → HTTP 200.**
