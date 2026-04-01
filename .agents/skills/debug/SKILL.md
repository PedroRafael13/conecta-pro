---
title: Debugging Sistemático
description: Técnicas de debug para Conecta PRO
levels: [application, database, network, infrastructure]
---

# Debugging Sistemático

Metodologia de investigação de problemas no ERP Conecta PRO.

## Framework de Debug

```
1. REPRODUZIR → Consistência do erro
2. ISOLAR     → Componente responsável
3. INSPEÇÃO   → Logs, métricas, traces
4. HIPÓTESE   → Causa provável
5. TESTAR     → Validar correção
6. PREVENIR   → Evitar recorrência
```

## Ferramentas

```bash
# Backend Python
python -m pdb app.py          # Debugger
import pdb; pdb.set_trace()   # Breakpoint
pytest --pdb                  # Debug em testes

# Frontend
debugger;                      # Chrome DevTools
console.table(data);          # Visualização
React DevTools                # Componentes

# Database
EXPLAIN ANALYZE query;        # Performance
pg_stat_activity              # Queries ativas

# Infra (Docker na VPS, sem Kubernetes)
docker logs -f conecta-pro-backend   # Logs em tempo real
docker ps --filter "name=conecta"    # Status containers
```

## Logs Estruturados

```python
# Padrão Conecta PRO
logger.error(
    "falha_processamento_nfe",
    extra={
        "nfe_id": nfe.id,
        "empresa_id": empresa.id,
        "error_code": "NFE-001",
        "trace_id": request.trace_id
    }
)
```

## Comandos Diagnóstico

```bash
# Health completo
./scripts/health-check.sh

# Performance API
curl -w "@curl-format.txt" -o /dev/null -s http://api/endpoint

# Conexões ativas
ss -tuln | grep :8000
netstat -an | grep ESTABLISHED | wc -l

# Recursos
htop
df -h
free -m
```

## Checklist de Investigação

- [ ] Logs revisados (últimas 24h)
- [ ] Métricas de performance analisadas
- [ ] Alterações recentes identificadas (git log)
- [ ] Ambiente reproduzido localmente
- [ ] Dados de entrada validados
- [ ] Dependências externas verificadas
- [ ] Rollback testado (se aplicável)
