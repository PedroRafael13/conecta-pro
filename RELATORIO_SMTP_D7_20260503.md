# RELATÓRIO — INVESTIGAÇÃO SMTP D7
## Destino OTP financeiro corrigido: Gmail → jjesus@conectamais.pro

**Data:** 2026-05-03
**Branch:** feature/people-management-reorganization
**Commit de correção:** `1e433a32`
**Solicitante:** Jordan Jesus

---

## 1. CONTEXTO

Investigação solicitada por Jordan para garantir que o sistema D7 (Pagamentos Inter)
envie o OTP de 2FA **exclusivamente** para `jjesus@conectamais.pro` e **nunca** para
`jordansjesus@gmail.com` (conta usada apenas para OAuth Google/GDrive).

---

## 2. RESULTADO DA VARREDURA

### 2.1 Ocorrências de `jordansjesus` no código

| Arquivo | Linha | Ocorrência | Criticidade |
|---------|-------|-----------|-------------|
| `backend/modules/integrations/inter/services/payment_service.py` | 239 | `os.getenv("JORDAN_EMAIL", "jordansjesus@gmail.com")` | 🔴 CRÍTICO — fallback errado |
| `frontend/src/app/modulos/financeiro/inter/pagamentos/page.tsx` | 432 | Texto fixo "Código enviado para jordansjesus@gmail.com" | 🟡 MÉDIO — exibição enganosa |
| `frontend/src/app/modulos/financeiro/inter/pagamentos/page.tsx` | 485 | `email === "jordansjesus@gmail.com"` em `isJordan` | 🟢 OK — verificação de identidade UI |
| `backend/modules/gdrive/controllers/gdrive_controller.py` | 453 | `GDRIVE_OWNER_EMAIL` fallback gmail | 🟢 OK — GDrive OAuth, não financeiro |

### 2.2 Variável `JORDAN_EMAIL` no container

**Antes da correção:**
```
# Variável NÃO existia no .env nem no container
# → os.getenv("JORDAN_EMAIL", "jordansjesus@gmail.com") retornava o fallback
# → OTP seria enviado para conta Gmail em produção
```

**Depois da correção:**
```
JORDAN_EMAIL=jjesus@conectamais.pro   ← adicionado ao .env
```

### 2.3 Configuração SMTP (estava correta antes)

```
SMTP_HOST=smtp.hostinger.com
SMTP_PORT=465
SMTP_FROM_EMAIL=noreply@conectamais.pro   ✅ sender correto
SMTP_USERNAME=noreply@conectamais.pro     ✅ sender correto
SMTP_USE_TLS=false (SSL implícito na porta 465)
```

### 2.4 Tabela `users` — dois registros Jordan

| id (início) | email | is_active | Criado |
|-------------|-------|-----------|--------|
| `ad9abb59` | `jjesus@conectamais.pro` | ✅ | 2026-01-16 |
| `266007cb` | `jordansjesus@gmail.com` | ✅ | 2026-01-17 |

**Conclusão:** dois registros distintos e ativos. A conta Gmail é usada para OAuth Google
(GDrive, Calendar). A conta `@conectamais.pro` é a identidade corporativa principal.

### 2.5 OTPs enviados em produção

```
total_otps = 0   ← nenhum OTP foi enviado antes da correção
```

**Impacto real: ZERO.** A variável incorreta nunca chegou a disparar um envio real.

---

## 3. CORREÇÕES APLICADAS

### 3.1 `backend/modules/integrations/inter/services/payment_service.py`

```python
# ANTES (linha 239):
email_destino = os.getenv("JORDAN_EMAIL", "jordansjesus@gmail.com")

# DEPOIS:
email_destino = os.getenv("JORDAN_EMAIL", "jjesus@conectamais.pro")
```

### 3.2 `backend/.env`

```bash
# ADICIONADO:
JORDAN_EMAIL=jjesus@conectamais.pro
```

### 3.3 `frontend/src/app/modulos/financeiro/inter/pagamentos/page.tsx`

```tsx
// ANTES (linha 432):
<p>✅ Código enviado para jordansjesus@gmail.com. Digite o código:</p>

// DEPOIS:
<p>✅ Código enviado para jjesus@conectamais.pro. Digite o código:</p>
```

### 3.4 Não alterado — `gdrive_controller.py:453`

```python
# GDRIVE_OWNER_EMAIL usa gmail como fallback — CORRETO e INTENCIONAL
# GDrive OAuth é vinculado à conta Google pessoal de Jordan
# Fora do escopo D7 (financeiro)
```

---

## 4. FLUXO OTP CORRETO PÓS-CORREÇÃO

```
Jordan (qualquer conta) → POST /payments/{id}/gerar-otp
         ↓
payment_service.gerar_otp()
         ↓
os.getenv("JORDAN_EMAIL", "jjesus@conectamais.pro")
         ↓
SMTP: noreply@conectamais.pro → jjesus@conectamais.pro
         ↓
Jordan recebe código em caixa corporativa (Hostinger/Gmail Workspace)
         ↓
Jordan digita código na UI → POST /payments/{id}/aprovar
         ↓
Pagamento aprovado → POST /payments/{id}/executar
         ↓
Inter API chamada (dinheiro move)
```

---

## 5. VERIFICAÇÃO DE IDENTIDADE "APENAS JORDAN" (UI)

O frontend verifica se o usuário logado é Jordan para exibir:
- Botão "Aprovar" (pagamentos status='preparado')
- Aba "Audit Log"

```typescript
// Aceita AMBAS as contas Jordan (corporativa + Gmail)
const email: string = payload.email || payload.sub || "";
setIsJordan(
  email === "jjesus@conectamais.pro" ||
  email === "jordansjesus@gmail.com"   // ← mantido: Jordan pode logar via Google OAuth
);
```

**Decisão:** ambas as contas são reconhecidas como Jordan na UI (quem pode aprovar).
O OTP, porém, é **sempre enviado para `jjesus@conectamais.pro`** independente de qual
conta Jordan usou para logar.

---

## 6. ESTADO FINAL

| Item | Status |
|------|--------|
| Sender SMTP | ✅ `noreply@conectamais.pro` |
| Destinatário OTP | ✅ `jjesus@conectamais.pro` (via `JORDAN_EMAIL`) |
| Fallback seguro | ✅ fallback também aponta para `@conectamais.pro` |
| OTPs enviados para Gmail | ✅ ZERO (tabela vazia antes da correção) |
| GDrive (gmail) | ✅ Inalterado — escopo diferente |
| Testes D7 | ✅ 22/22 passando |
| Build frontend | ✅ `conecta-pro-1777839027654` |

---

## 7. COMMITS DESTA SESSÃO (D7 COMPLETO)

| Hash | Descrição |
|------|-----------|
| `91cd2b11` | feat(inter-d7): implementação completa — 2FA OTP + limite diário + audit log |
| `f796433d` | fix(inter-d7): auditoria 1 — 7 testes faltantes + ENV vars + validação destinatário |
| `baeef1ec` | fix(inter-d7): auditoria 2 — audit table completa + restrições Jordan + validação saldo |
| `b5abaf90` | docs(inter-d7): relatório de auditoria final — 100% completo |
| `1e433a32` | fix(inter-d7): OTP email destino corrigido — jjesus@conectamais.pro (não gmail) |

---

## 8. PRÓXIMOS PASSOS (AGUARDANDO JORDAN)

1. **Testar SMTP ao vivo:** acesse `/modulos/financeiro/inter/pagamentos`, crie um
   pagamento PIX R$0,01, clique "Enviar código OTP" e confirme recebimento em
   `jjesus@conectamais.pro`.

2. **Após confirmação SMTP:** prosseguir com D7.2 (boleto R$0,50 real) e D7.3 (PIX R$0,01).

3. **Fornecer para D7.2:** linha digitável de 1 boleto real de valor baixo.

4. **Fornecer para D7.3:** confirmar que a chave PIX `jjesus@conectamais.pro` (ou CPF)
   está ativa na conta Inter para receber o PIX de teste.
