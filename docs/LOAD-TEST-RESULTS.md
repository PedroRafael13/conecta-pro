# Resultados de Load Testing - ERP Conecta Mais

## Template de Registro

### Data: YYYY-MM-DD

#### Configuração
| Parâmetro | Valor |
|-----------|-------|
| Ambiente | staging / production |
| URL Base | http://localhost:8080 / https://erp.conectamais.pro |
| k6 Version | v0.49.0 |
| Executado por | [Nome] |

#### Cenários Executados

| Cenário | Duração | VUs Máx | Taxa Req/s |
|---------|---------|---------|------------|
| health | 2m | 10 | ~10 |
| login | 3m | 50 | ~50 |
| api_reads | 3m | 100 | 30 |
| smoke | 30s | 5 | ~10 |

#### Resultados

| Métrica | Valor | Threshold | Status |
|---------|-------|-----------|--------|
| P95 Latency | X ms | < 500ms | ✅/❌ |
| P99 Latency | X ms | < 1000ms | ✅/❌ |
| Error Rate | X% | < 1% | ✅/❌ |
| Throughput | X req/s | - | - |
| Checks Passed | X% | > 95% | ✅/❌ |

#### Observações
- [Observações sobre comportamento do sistema]
- [Gargalos identificados]
- [Recomendações]

#### Artefatos
- Resultado JSON: `/opt/conecta-pro/logs/load-test-YYYYMMDD-HHMMSS.json`
- Log: `/opt/conecta-pro/logs/load-test-YYYYMMDD-HHMMSS.log`

---

## Histórico de Execuções

### 2026-02-XX - Staging
*Aguardando execução na Fase 8*

### 2026-02-XX - Pré-Deploy
*Aguardando execução*

---

## Notas

### Comandos Úteis

```bash
# Smoke test rápido (executar localmente)
k6 run --env BASE_URL=http://localhost:8080 tests/load/k6-scenarios.js

# Teste completo com dashboard web
k6 run --env BASE_URL=http://localhost:8080 --env K6_WEB_DASHBOARD=true tests/load/k6-scenarios.js

# Usando o script helper
cd tests/load && ./run-load-test.sh smoke staging
```

### Thresholds Definidos

- **P95 Latency**: < 500ms
- **P99 Latency**: < 1000ms
- **Error Rate**: < 1%
- **HTTP 5xx**: 0%

### Escalabilidade Esperada

| Métrica | Staging | Produção (estimado) |
|---------|---------|---------------------|
| Usuários simultâneos | 100 | 500+ |
| Req/s sustentado | 50 | 200+ |
| Latência P95 | < 500ms | < 300ms |
