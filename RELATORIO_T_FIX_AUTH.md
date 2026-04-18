# T_FIX_AUTH | 2026-04-18
**1. Contrato:** v1.7 lido | Princípio **13.4 (Escopo Sagrado)** — só assinatura, nada mais.
**2. Padrão (STEP 1):** `_: dict = Depends(get_current_user)` (ref: diaristas controller). Import não existia no onvio_controller — adicionado.
**3. Diff (STEP 2):** +2 linhas: `from core.auth.dependencies import get_current_user` + `_: dict = Depends(get_current_user)` na assinatura. Zero outras alterações.
**4. STEP 3.2** sem token → **HTTP 401** ✅
**5. STEP 3.3** token inválido → **HTTP 401** ✅
**6. STEP 3.4** GET /stats sem token → **HTTP 200** ✅ (inalterado)
**7. STEP 4** `inspect.signature` → params: `['forcar', 'limite', '_']` ✅
**8. Commits:** `56ea10b7` CONTRATO v1.8 | `3fb971c9` fix(security) auth
**9. Contrato:** v1.8 ativo, §16.1 marcado **RESOLVIDO**.
**T_FIX_AUTH OK — LIBERAR MINI-REAUDITORIA T7**
