# CONTEXTO E2E — MODULO OPERACIONAL
# Data: 2026-03-29 | Gerado automaticamente

## ENDPOINTS OPERACIONAIS

Total testados: 14

  200 /api/v1/operacional/posts/ → 12 items
  200 /api/v1/operacional/scales/ → 26 items
  200 /api/v1/operacional/shifts/ → 1286 items
  200 /api/v1/operacional/allocations/ → 103 items
  200 /api/v1/operacional/employees/ → 52 items
  200 /api/v1/operacional/occurrences/ → 16 items
  200 /api/v1/operacional/substitutions/ → 10 items
  200 /api/v1/operacional/time-bank/ → 18 items
  200 /api/v1/operacional/reports/coverage → ? items
  404 /api/v1/operacional/kpi-trends/
  404 /api/v1/operacional/inspection-rounds/
  405 /api/v1/operacional/diaristas/
  404 /api/v1/operacional/disciplinary/
  200 /api/v1/operacional/scale-templates/ → 4 items

## TABELAS COM DADOS

  employees         |         52
  posts             |         32
  allocations       |         20
  occurrences       |         15
  substitutions     |         10
  inspection_rounds |          7
  scale_templates   |          4

## PAGINAS FRONTEND (30)

  /modulos/operacional/agentes/page.tsx
  /modulos/operacional/ai-command-center/page.tsx
  /modulos/operacional/alocacoes/page.tsx
  /modulos/operacional/banco-horas/page.tsx
  /modulos/operacional/campo/page.tsx
  /modulos/operacional/cobertura/page.tsx
  /modulos/operacional/colaboradores/[id]/page.tsx
  /modulos/operacional/colaboradores/page.tsx
  /modulos/operacional/comunicados/page.tsx
  /modulos/operacional/diaristas/escala/page.tsx
  /modulos/operacional/diaristas/fechamento/page.tsx
  /modulos/operacional/diaristas/page.tsx
  /modulos/operacional/disciplinar/page.tsx
  /modulos/operacional/escalas/[id]/page.tsx
  /modulos/operacional/escalas/page.tsx
  /modulos/operacional/escalas/templates/page.tsx
  /modulos/operacional/escalas/visual/page.tsx
  /modulos/operacional/ferias/page.tsx
  /modulos/operacional/kpi/page.tsx
  /modulos/operacional/mapa/page.tsx
  /modulos/operacional/medidas-administrativas/page.tsx
  /modulos/operacional/notificacoes/page.tsx
  /modulos/operacional/ocorrencias/page.tsx
  /modulos/operacional/page.tsx
  /modulos/operacional/postos/page.tsx
  /modulos/operacional/reembolsos/page.tsx
  /modulos/operacional/relatorios/page.tsx
  /modulos/operacional/rondas/page.tsx
  /modulos/operacional/substituicoes/page.tsx
  /modulos/operacional/turnos/page.tsx

## SUBMÓDULOS A TESTAR

### 1. Postos de Servico
- [ ] Listar postos por cliente
- [ ] Criar novo posto
- [ ] Editar dados do posto
- [ ] Status do posto (ativo/inativo)

### 2. Escalas
- [ ] Listar escalas (filtro por cliente/data)
- [ ] Criar nova escala
- [ ] Visualizar escala do dia / semana / mes
- [ ] Substituicoes de vigilante

### 3. Turnos / Shifts
- [ ] Listar turnos ativos
- [ ] Check-in / check-out
- [ ] Calendario de turnos

### 4. Alocacoes
- [ ] Listar alocacoes ativas
- [ ] Alocar funcionario em posto
- [ ] Transferir entre postos
- [ ] Historico de alocacoes

### 5. Rondas de Inspecao
- [ ] Listar rondas programadas
- [ ] Registrar execucao de ronda
- [ ] Pontos de verificacao
- [ ] Relatorio de rondas

### 6. Ocorrencias
- [ ] Listar ocorrencias (abertas/fechadas)
- [ ] Registrar nova ocorrencia
- [ ] Anexar fotos/evidencias
- [ ] Fechar ocorrencia com resolucao

### 7. Banco de Horas
- [ ] Saldo por funcionario
- [ ] Aprovar/rejeitar creditos
- [ ] Historico

### 8. Diaristas
- [ ] Cadastro e pagamento
- [ ] Escala diaria
- [ ] Fechamento mensal

### 9. Relatorios
- [ ] Cobertura operacional
- [ ] KPI trends
- [ ] Por cliente

### 10. Medidas Disciplinares
- [ ] Listar medidas
- [ ] Registrar advertencia/suspensao

## SCORECARD (preencher apos testes)

| Submodulo | Score |
|---|---|
| Postos | ? /10 |
| Escalas | ? /10 |
| Turnos | ? /10 |
| Alocacoes | ? /10 |
| Rondas | ? /10 |
| Ocorrencias | ? /10 |
| Banco Horas | ? /10 |
| Diaristas | ? /10 |
| Relatorios | ? /10 |
| Disciplinar | ? /10 |
| **GERAL** | **? /10** |

## COMANDOS UTEIS

```bash
# Token
python3 << 'PY'
import urllib.request, json
data = b"username=jjesus@conectamais.pro&password=Jordan0612"
req = urllib.request.Request("http://127.0.0.1:8080/api/v1/auth/login",
    data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
token = json.loads(urllib.request.urlopen(req).read())["access_token"]
open("/tmp/tk", "w").write(token)
print(f"Token OK")
PY
TK=$(cat /tmp/tk)

# Postos
curl -sf "http://127.0.0.1:8080/api/v1/operacional/posts/" -H "Authorization: Bearer $TK" | python3 -m json.tool | head -20

# Escalas
curl -sf "http://127.0.0.1:8080/api/v1/operacional/scales/" -H "Authorization: Bearer $TK" | python3 -m json.tool | head -20
```
