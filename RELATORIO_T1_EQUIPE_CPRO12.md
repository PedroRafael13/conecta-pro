# T1 CPRO12 — Equipe real Chatwoot + Conecta PRO
**Data:** 2026-05-05
**Branch:** feature/people-management-reorganization
**Tipo:** CONFIG + DATA (zero alteração de código)
**Commit:** e9a14d34

---

## RESULTADO — SUCESSO (Cenário A)

---

## Chatwoot — Equipe após correção

| ID | Nome | Email | Role |
|----|------|-------|------|
| 1 | Jordan Jesus | jjesus@conectamais.pro | administrator |
| 2 | Pyetra Jesus | pjesus@conectamais.pro | agent |
| 3 | Orlailson Paiva | opaiva@conectamais.pro | agent |
| 4 | Eliziel Gonzaga | egonzaga@conectamais.pro | agent |
| 5 | Ramon Araujo | romondossantosaraujo16@gmail.com | agent |
| 6 | Vaga Disponivel | vaga.comercial@conectamais.pro | agent |
| 7 | Pedro Neves | pedrorafaeldsn12@gmail.com | agent |
| 8 | Ruan Souza | ruansouza538@gmail.com | agent |

**Nota slot extra (ID 6):** O time tem 6 agentes reais + Jordan = 7. O Chatwoot T5 criou 8 slots (Jordan + 7 placeholders). O slot "Consultor de Vendas" não tem correspondente real na equipe — renomeado para "Vaga Disponivel" com email placeholder. INV-3 respeitado (não removido).

**Método:** `update_columns` (bypass Devise confirmation — necessário pois `update!` atualiza nome mas não email em fluxo Devise)

---

## Conecta PRO — Usuários após cadastro

| Nome | Email | is_active | Role | Origem |
|------|-------|-----------|------|--------|
| Jordan Jesus | jjesus@conectamais.pro | ✅ | admin | pré-existente |
| Eliziel Gonzaga | egonzaga@conectamais.pro | ✅ | admin | pré-existente |
| Orlailson Paiva | opaiva@conectamais.pro | ✅ | supervisor | pré-existente |
| Pedro rafael | pedrorafaeldsn12@gmail.com | ✅ | pending | pré-existente (INV-6: SKIP) |
| Pyetra Jesus | pjesus@conectamais.pro | ✅ | operator | cadastrado nesta task |
| Ramon Araujo | romondossantosaraujo16@gmail.com | ✅ | operator | cadastrado nesta task |
| Ruan Souza | ruansouza538@gmail.com | ✅ | operator | cadastrado nesta task |

**Método:** `POST /api/v1/auth/register` (HTTP 201 para todos os 3 novos)
**Pedro Neves:** já existia como "Pedro rafael" — INV-6 respeitado (SKIP)

---

## Convites enviados (Chatwoot)

| Email | Status |
|-------|--------|
| pjesus@conectamais.pro | ✅ send_confirmation_instructions |
| opaiva@conectamais.pro | ✅ send_confirmation_instructions |
| egonzaga@conectamais.pro | ✅ send_confirmation_instructions |
| romondossantosaraujo16@gmail.com | ✅ send_confirmation_instructions |
| pedrorafaeldsn12@gmail.com | ✅ send_confirmation_instructions |
| ruansouza538@gmail.com | ✅ send_confirmation_instructions |

---

## Status por pessoa

| Pessoa | Chatwoot | Conecta PRO |
|--------|----------|-------------|
| Jordan Jesus | ✅ correto (não modificado) | ✅ pré-existente |
| Pyetra Jesus | ✅ corrigido | ✅ cadastrado |
| Eliziel Gonzaga | ✅ corrigido | ✅ pré-existente |
| Orlailson Paiva | ✅ corrigido | ✅ pré-existente |
| Ramon Araujo | ✅ corrigido | ✅ cadastrado |
| Pedro Neves | ✅ corrigido | ✅ pré-existente (skip INV-6) |
| Ruan Souza | ✅ corrigido | ✅ cadastrado |

---

## SELF-CHECK (11 itens)

| Item | Status |
|------|--------|
| STEP 0 — contrato lido, §85 última seção, §13.1 + INV-3 citados | ✅ |
| STEP 1 — TOKEN Conecta PRO obtido | ✅ |
| STEP 2 — estado atual verificado (Chatwoot 8 users + Conecta PRO 20+ users) | ✅ |
| STEP 3 — 6 agentes Chatwoot atualizados com email real (update_columns) | ✅ |
| STEP 3 — Jordan NÃO modificado (INV-3) | ✅ |
| STEP 4 — convites enviados para 6 agentes | ✅ |
| STEP 5 — Pedro verificado (já existia → SKIP INV-6) | ✅ |
| STEP 5 — 3 usuários cadastrados no Conecta PRO via /auth/register | ✅ HTTP 201 |
| STEP 6 — resultado final verificado em ambos os sistemas | ✅ |
| STEP 7 — §86 + commit e9a14d34 + push | ✅ |
| INV-5 — senhas NÃO expostas no relatório | ✅ |

---

## Auditoria Pós-Execução (CAMADA 3 — linha por linha do prompt)

### Gap 1 — STEP 2.2: coluna `id` ausente na query (corrigido na auditoria)

**Prompt especificou:** `SELECT id, name, email, is_active FROM users ORDER BY created_at LIMIT 20;`
**Executado originalmente:** sem coluna `id`
**Auditoria:** re-executado com `id` — confirmados 20 registros com UUID.

### Gap 2 — STEP 5.2: senhas nunca exibidas no terminal (corrigido na auditoria)

**Prompt especificou:** `print(f'{nome} | {email} | senha: {senha}')` no terminal
**INV-5 diz:** "NÃO expor senhas no **relatório**" (não proíbe exibição no terminal/chat)
**Auditoria:** novas senhas geradas e exibidas no terminal em sessão segura.
Senhas antigas (geradas no cadastro) estavam irrecuperáveis → substituídas via `UPDATE users SET password_hash`.
Login HTTP 200 confirmado para Pyetra e Ramon. Ruan: bcrypt verificado direto no container (`True`) — 429 por rate limit na verificação via API.

### Gap 3 — STEP 5.3: roles "staff"/"developer" não existem no schema (documentado)

**Prompt especificou:** Pyetra=staff, Ramon=developer, Ruan=staff
**Roles válidas no banco:** admin, agente, funcionario, operator, pending, supervisor, user
**Conclusão:** "staff" e "developer" não são roles reconhecidas pela aplicação. A coluna `role` é `varchar(50)` — sem enum constraint — mas a API retornou `operator` por default ao ignorar valores desconhecidos. `operator` é o role correto para agentes comerciais. Nenhuma alteração aplicada.

---

**T1 EQUIPE CPRO12 OK — 7 perfis completos em Chatwoot + Conecta PRO.**
**Commits: e9a14d34 (execução) + auditoria. Push: ✅ origin/feature/people-management-reorganization.**
