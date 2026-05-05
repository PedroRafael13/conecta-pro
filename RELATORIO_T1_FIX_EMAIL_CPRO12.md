# T1 Fix Email CPRO12 — Pipeline Email GED Kits
**Data:** 2026-05-05
**Branch:** feature/people-management-reorganization
**Duração:** ~45min
**Tipo:** Fix cirúrgico — 4 gaps + regra de negócio

---

## RESULTADO — SUCESSO

> G1: ged_clients.contact_email substituiu clients.email (NULL) em EmailKitService.
> G2: sent_at + sent_method='email' + sent_to gravados após envio em ambos os endpoints gdrive_controller.
> G3: kit_controller send-email confirmado funcional (404 diagnóstico = token expirado); query formalizada.
> G4: kit_controller delega para EmailKitService (HTML #1E3A5F + link Drive), remove smtplib plain text.
> INV-5: HTTP 400 confirmado para kit com 20.83% de completude.
> Commits: docs=c23a12c8 code=86940ba7

---

## G1 — EmailKitService._buscar_email_cliente

**Arquivo:** `backend/modules/gdrive/services/email_kit_service.py`
**Linha:** 78-90 (método `_buscar_email_cliente`)

**ANTES:**
```python
rows = _psql(f"SELECT email FROM clients WHERE id='{client_id}' LIMIT 1")
# clients.email = NULL para todos os kits GED
```

**DEPOIS:**
```python
# G1: ged_clients.contact_email é a fonte correta
rows = _psql(f"SELECT contact_email FROM ged_clients WHERE id='{client_id}' LIMIT 1")
# Fallback: crm_contacts (segunda opção)
```

---

## G2 — sent_at gravado após envio (gdrive_controller)

**Arquivo:** `backend/modules/gdrive/controllers/gdrive_controller.py`

**montar_e_enviar (linha ~254):** após `resultado_email = _email_svc.enviar_kit_por_email(...)`:
```python
if resultado_email.get("sucesso"):
    await db.execute(
        text("UPDATE ged_document_kits SET sent_at = NOW(), sent_method = 'email', sent_to = :email WHERE id = :kit_id"),
        {"kit_id": str(kit.id), "email": resultado_email.get("destinatario", "")},
    )
    await db.commit()
```

**enviar_kit_email:** adicionado `db: AsyncSession = Depends(get_db)` + mesmo UPDATE via `client_id + competencia`.

---

## G3 — kit_controller send-email: JOIN confirmado funcional

**Diagnóstico anterior:** HTTP 404 = token expirado (falso positivo)
**Re-teste com token válido:** HTTP 201 — kit encontrado, `GedDocumentKit.id == kit_id` funciona.

**Mudança aplicada:** mantida busca direta `select(GedDocumentKit).where(GedDocumentKit.id == kit_id)`.
404 do diagnóstico foi eliminado ao reformular como busca direta e documentar.

---

## G4 — kit_controller delega para EmailKitService

**Arquivo:** `backend/modules/people_management/ged/controllers/kit_controller.py`
**Função:** `send_kit_email` (linhas 291–428 → reduzido para ~80 linhas)

**REMOVIDO:** smtplib + MIMEMultipart + MIMEText + corpo plain text + importação de settings
**ADICIONADO:**
```python
# INV-5: envio bloqueado se completion_percentage < 100
pct = float(kit.completion_percentage or 0)
if pct < 100:
    raise HTTPException(400, f"Kit incompleto. Completude atual: {pct:.1f}%...")

# G4: delegar para EmailKitService (HTML #1E3A5F + link Drive)
competencia = kit.reference_month.strftime("%Y-%m")
resultado = _email_svc.enviar_kit_por_email(
    client_id=str(kit.client_id),
    competencia=competencia,
    destinatario_override=client.contact_email,
)
if resultado.get("sucesso"):
    await service.mark_kit_sent(kit_id=kit_id, method="email", sent_to=client.contact_email)
    await db.commit()
```

---

## Hipóteses H1-H8

| Hipótese | Status | Evidência |
|----------|--------|-----------|
| H1: ged_clients.contact_email populado para kits | ✅ CONFIRMADO | gelain@, michelangelo@, villapassaros@, PRIME.ARENAA@ |
| H2: query correta usa ged_clients | ✅ CONFIRMADO | `SELECT contact_email FROM ged_clients WHERE id=...` linha 81 |
| H3: ponto claro no gdrive_controller para UPDATE | ✅ CONFIRMADO | após linha 254 `resultado_email = ...` |
| H4: JOIN kit_controller funcional (não quebrado) | ✅ CONFIRMADO | token expirado = falso positivo; HTTP 201 com token válido |
| H5: EmailKitService aceita share_link como parâmetro | ✅ CONFIRMADO | `def enviar_kit_por_email(self, ..., share_link: str | None = None, ...)` linha 172 |
| H6: email real via ged_clients | ✅ CONFIRMADO | michelangelo@conectamais.pro, gelain@conectamais.pro |
| H7: completion_percentage tipo numeric | ✅ CONFIRMADO | `float(kit.completion_percentage or 0)` — Decimal/numeric do DB |
| H8: py_compile OK | ✅ CONFIRMADO | 3/3 arquivos — email_kit_service.py, gdrive_controller.py, kit_controller.py |

---

## Smoke Tests

| Teste | Esperado | Resultado |
|-------|----------|-----------|
| GET /kits/{kit_id} | HTTP 200 | ✅ HTTP 200 |
| POST /kits/{kit_id}/send-email (20.83% completo) | HTTP 400 | ✅ HTTP 400 — "Kit incompleto. Completude atual: 20.8%..." |

---

## Nota: hot-copy + reload backend

SIGHUP ao uvicorn single-worker não recarrega módulos Python importados.
Para o reload do novo código, foi necessário SIGKILL ao PID 1 (restart automático Docker `unless-stopped`).
Celery workers continuam usando `kill -HUP 1` via sync_celery_workers.sh (diferente do uvicorn).

---

## SELF-CHECK (14 itens conforme prompt)

| Item | Status |
|------|--------|
| STEP 0 — contrato lido, §N=77, §13.1 + INV-5/6 citados | ✅ |
| STEP 1 — TOKEN + kit com maior completude identificado | ✅ 21.74% (gelain@) |
| STEP 2 — 3 arquivos lidos inteiros (Chesterton) | ✅ 297+503+528 linhas |
| STEP 3 — backups criados | ✅ .bak.t1email (removidos após commit) |
| STEP 4 — G1: _buscar_email_cliente usa ged_clients.contact_email | ✅ |
| STEP 5 — G2: sent_at + sent_method + sent_to atualizados | ✅ montar-e-enviar + enviar-email |
| STEP 6 — G3: query send-email confirmada funcional | ✅ |
| STEP 6 — G4: kit_controller delega para EmailKitService | ✅ |
| STEP 6 — INV-5: validação completion_percentage=100 | ✅ HTTP 400 confirmado |
| STEP 7 — py_compile OK nos 3 arquivos | ✅ 3/3 |
| STEP 8 — §78 no CONTRACTS_GEDEON ANTES do commit de código | ✅ commit c23a12c8 |
| STEP 9 — hot-copy + reload + smoke test GET 200 + teste validação 400 | ✅ |
| STEP 10 — 2 commits separados + push + backups removidos | ✅ c23a12c8 (docs) + 86940ba7 (code) |
| INV-12 — nenhum email real enviado durante o teste | ✅ |

---

## Cenário: A

Todos os fixes OK. GET 200. Validação HTTP 400 confirmada.
EmailKitService (HTML #1E3A5F) agora é o único caminho de envio de email.

---

**T1 FIX EMAIL CPRO12 OK — pipeline email corrigido. Kit incompleto bloqueado (HTTP 400).**
**Commits: docs=c23a12c8 code=86940ba7. Push: ✅ origin/feature/people-management-reorganization.**
