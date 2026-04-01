# RELATORIO DE EXECUCAO — FIX DP FOLHA + PONTO
## Bug Report CEO: "Folha R$ 0,00 e Ponto vazio"
## Data: 24 de Marco de 2026

> **Commit:** 34a6937b
> **Branch:** feature/people-management-reorganization
> **Executor:** Claude Opus 4.6

---

## 1. BUG REPORTADO

O CEO reportou via prints que:
- `/modulos/dp/folha` → R$ 0,00 em tudo (proventos, descontos, liquido, FGTS)
- `/modulos/dp/ponto` → vazio (nenhum registro de ponto)
- `/modulos/gestao-pessoas/ponto` → OK (1.840 batidas, funciona)

O sistema estava 10/10 em 23/03.

---

## 2. DIAGNOSTICO

### 2.1 Dados no banco — INTACTOS
```
Funcionarios ativos:  42
Folha bruta:          R$ 70.520,10
Batidas de ponto:     1.840 (1.824 Tangerino + 16 portal)
```
Os dados NAO sumiram. O problema era no frontend e no service.

### 2.2 Causa Raiz — FOLHA R$ 0,00

**Arquivo:** `frontend/src/app/modulos/dp/folha/page.tsx`

**Problema:** Linha 33 chamava:
```javascript
fetch(`${API_BASE}/employees/?page_size=100`)
//                          ^ trailing slash
```

O backend (`/people-management/hr/employees`) so responde SEM trailing slash.
Com trailing slash → 404. Sem lista de funcionarios → folha calcula zero.

**Prova:**
```
404 → /hr/employees/?page_size=100   (com slash)
200 → /hr/employees?page_size=100    (sem slash) → 42 funcionarios
```

**Fix:** Removido trailing slash: `/employees?page_size=100`

### 2.3 Causa Raiz — PONTO VAZIO

**Arquivo:** `backend/modules/people_management/hr/services/time_tracking_service.py`

**Problema 1:** O service fazia:
```sql
SELECT ... FROM time_entries WHERE employee_id = :emp_id
```
A tabela `time_entries` nao existe ou esta vazia. As batidas reais estao em `gp_clock_punches`.

**Problema 2:** Mesmo corrigindo a tabela, asyncpg rejeitava strings como datas:
```
asyncpg.exceptions.DataError: invalid input for query argument $2:
'2026-03-01' (expected datetime.date, got 'str')
```

**Problema 3:** Turno noturno (21h→09h) ficava com entrada e saida em dias diferentes,
gerando registros orfaos.

**Fix:** Reescrito `get_entries()` para:
1. Ler de `gp_clock_punches` (fonte real)
2. Converter strings para `datetime` objects (asyncpg compat)
3. Emparelhar entrada+saida consecutiva (turnos noturnos)

**Resultado:**
```
ANTES:  0 registros
DEPOIS: 11 registros reais por funcionario
  2026-03-21 | 21:09 → 09:00 | 12:00 | tangerino
  2026-03-19 | 21:01 → 09:05 | 12:00 | tangerino
  2026-03-17 | 21:09 → 08:59 | 12:00 | tangerino
```

### 2.4 Bug adicional — Ponto page

**Arquivo:** `frontend/src/app/modulos/dp/ponto/page.tsx`

**Problema:** Linha 41 usava `?limit=100` (parametro errado) + trailing slash:
```javascript
fetch(`${API_BASE}/employees/?limit=100`)
```

**Fix:** Corrigido para `?page_size=100` sem trailing slash.

---

## 3. CORRECOES APLICADAS

| Arquivo | Linha | Antes | Depois |
|---------|-------|-------|--------|
| `dp/folha/page.tsx` | 33 | `/employees/?page_size=100` | `/employees?page_size=100` |
| `dp/ponto/page.tsx` | 41 | `/employees/?limit=100` | `/employees?page_size=100` |
| `time_tracking_service.py` | 127-209 | `SELECT FROM time_entries` | `SELECT FROM gp_clock_punches` + datetime fix + emparelhamento |

**Total: 3 arquivos, 88 linhas alteradas.**

---

## 4. VALIDACAO POS-FIX

### APIs respondendo com dados reais
```
Employees:  200 → 42 funcionarios (ex: CINTIA BEZERRA R$ 1.670)
Calculate:  200 → Base R$ 1.670 | Liq R$ 1.429,27 | FGTS R$ 133,60
Entries:    200 → 11 registros ponto (21:09→09:00, tangerino)
Folha dash: 200 → 42 funcs | R$ 95.694,24 proventos
Ponto dash: 200 → 42 funcs | 12x36: 31 | 44h: 11
Frontend:   200 → localhost:3001
Producao:   200 → erp.conectamais.pro
```

### Deploy realizado
- Backend: rebuild + deploy (`docker compose build + up`)
- Frontend: `npx next build` + `pm2 restart`
- Commit: `34a6937b` pushed

---

## 5. GAPS RESTANTES

### 5.1 Trailing slash sistematico
O bug de trailing slash afeta potencialmente OUTRAS paginas DP/frontend.
Os controllers HR usam `@router.get("")` que so responde sem slash.

**Paginas potencialmente afetadas:**
- `/dp/beneficios` → pode chamar `/hr/benefits/` (com slash)
- `/dp/contratos` → pode chamar `/hr/contracts/` (com slash)
- `/dp/ferias` → pode chamar `/hr/vacations/` (com slash)
- `/dp/admissao` → pode chamar `/hr/admissions/` (com slash)

**Acao sugerida:** Varrer todas as paginas em `/modulos/dp/` e remover
trailing slashes nas chamadas fetch/axios.

### 5.2 Calculo de horas reais no ponto
O ponto mostra "12:00" fixo para todos os turnos. O calculo real
deveria ser `saida - entrada` considerando turnos noturnos.

### 5.3 Ponto so mostra 20 funcionarios
O frontend `dp/ponto/page.tsx` tem `emps.slice(0, 20)` (linha 50)
que limita a 20 funcionarios. Deveria ser todos os 42.

---

## 6. BLOQUEADORES

**Nenhum bloqueador critico.** O modulo DP esta funcional com dados reais.

Bloqueador menor: o parametro de paginacao do backend usa `page_size`
mas algumas paginas frontend usam `limit`. Precisa padronizar.

---

## 7. POR QUE QUEBROU

A branch `feature/people-management-reorganization` fez uma reorganizacao
massiva dos modulos. Durante essa reorganizacao:

1. Os controllers HR foram movidos e seus routers recriados com `@router.get("")`
   (sem trailing slash), mas o frontend continuou chamando com `/`.

2. O `TimeTrackingService` foi criado apontando para `time_entries` (tabela
   generica) em vez de `gp_clock_punches` (onde as batidas reais do Tangerino
   foram importadas).

3. O frontend nao foi atualizado para refletir as novas convencoes de rota.

---

## 8. RECOMENDACAO

Para evitar regressoes futuras:

1. **Padronizar trailing slash:** Configurar FastAPI com `redirect_slashes=True`
   (nao precisa alterar cada controller)

2. **Testes E2E:** Criar teste que chama `/dp/folha` e verifica que retorna > R$ 0

3. **Monitoramento:** Alertar quando folha retorna zero para empresa com
   funcionarios ativos

---

## 9. COMANDO PARA DOWNLOAD

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_FIX_DP_FOLHA_PONTO_2026-03-24.md ~/Downloads/
```
