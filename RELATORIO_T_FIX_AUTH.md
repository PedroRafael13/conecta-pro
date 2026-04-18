# RELATÓRIO T_FIX_AUTH | 2026-04-18

## 1. Contrato
Versão lida: **1.7** | Princípio: **13.4 (Escopo Sagrado)** — 1 parâmetro adicionado, nada mais.

## 2. Padrão de auth identificado (STEP 1)
Referência: `diarist_controller.py` — `_: dict = Depends(get_current_user)` com import `from core.auth.dependencies import get_current_user`. Nenhum endpoint do próprio `onvio_controller.py` usava auth (confirmado por grep vazio).

## 3. Diff (STEP 2)
```diff
+from core.auth.dependencies import get_current_user   # linha nova no import

 @router.post("/extrair-valores")
 async def extrair_valores(
     forcar: bool = False,
     limite: int | None = None,
+    _: dict = Depends(get_current_user),               # linha nova na assinatura
 ):
```
2 linhas adicionadas. Zero outras alterações.

## 4–7. Validação dupla (STEP 3) + Falsificação (STEP 4)
| Teste | Esperado | Resultado |
|-------|----------|-----------|
| STEP 3.2 — sem token | HTTP 401 | ✅ HTTP 401 |
| STEP 3.3 — token inválido | HTTP 401 | ✅ HTTP 401 |
| STEP 3.4 — GET /stats (não afetado) | HTTP 200 | ✅ HTTP 200 |
| STEP 4.2 — inspect.signature params | `_` presente | ✅ `['forcar', 'limite', '_']` |

## 8. Commits
- `56ea10b7` — docs(gedeon): CONTRATO v1.8 — §16.1 resolvido
- `3fb971c9` — fix(security): T_FIX_AUTH — autenticação obrigatória em /extrair-valores

## 9. Contrato
Versão: **1.8** ativo. §16.1 marcado **RESOLVIDO**.

## 10. Veredito
**T_FIX_AUTH OK — LIBERAR MINI-REAUDITORIA T7**
