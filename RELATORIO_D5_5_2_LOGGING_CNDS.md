# RELATÓRIO D5.5.2 — Logging do /cnds/run em ged_coleta_logs

**Data:** 2026-04-30
**Commit:** `d80df95b`
**Branch:** feature/people-management-reorganization
**Módulo:** GED — Certidões

---

## 1. Objetivo

Implementar gravação de `ged_coleta_logs` quando o endpoint `POST /cnds/run` é chamado de forma isolada, para que execuções manuais de certidões apareçam no histórico (`GET /coleta-automatica/history`).

---

## 2. Problema

Antes desta implementação:
- `POST /cnds/run` → atualizava `ged_certidoes` mas não gravava histórico
- `GET /coleta-automatica/history` → nunca mostrava execuções de certidões isoladas
- Duplicação potencial: se `CertidoesUpdaterService` gravasse sempre, a coleta completa geraria 2 logs (1 do Updater + 1 do `ColetaAutomaticaService`)

---

## 3. Solução Implementada

### 3.1 — Parâmetro `write_log: bool`

`CertidoesUpdaterService.executar()` recebeu o parâmetro `write_log: bool = True`:

- `write_log=True`: grava `GedColetaLog` ao final da execução (padrão para chamadas isoladas)
- `write_log=False`: retorna resultado sem gravar (para chamadas internas de `ColetaAutomaticaService`)

### 3.2 — Controller atualizado

`coleta_automatica_controller.py::run_cnds_now()`:
- Captura `triggered_by = getattr(current_user, "email", "system")`
- Passa `run_type="cnds_only"`, `triggered_by=triggered_by`, `write_log=True`

### 3.3 — Fase 3 da coleta completa

`coleta_automatica_service.py` Fase 3 já passava o resultado; agora passa `write_log=False` explicitamente:

```python
cert_result = await CertidoesUpdaterService(self.db).executar(
    cnpj_empresa,
    run_type=run_type,
    triggered_by=triggered_by,
    write_log=False,  # D5.5.2: ColetaAutomaticaService grava 1 log unificado
)
```

---

## 4. Arquivos Modificados

| Arquivo | Mudança |
|---------|---------|
| `backend/modules/people_management/ged/services/certidoes_updater_service.py` | Adicionado `import time`, `GedColetaLog`, parâmetros `run_type/triggered_by/write_log`, bloco `if write_log` |
| `backend/modules/people_management/ged/services/coleta_automatica_service.py` | Fase 3 passa `write_log=False` |
| `backend/modules/people_management/ged/controllers/coleta_automatica_controller.py` | Captura `triggered_by`, passa `run_type='cnds_only'` e `write_log=True` |
| `backend/tests/modules/gedeon/test_d5_5_2_logging_cnds.py` | 4 novos testes unitários |

---

## 5. Testes

### 5.1 — Unitários (pytest)

```
20 passed, 19 warnings in 35.03s
```

| Arquivo | Testes |
|---------|--------|
| test_d5_5_2_logging_cnds.py | 4 ✅ |
| test_d5_4_certidoes_updater.py | 5 ✅ |
| test_d4_coleta_automatica.py | 11 ✅ |

### 5.2 — Validação em Produção

| VAL | Resultado |
|-----|-----------|
| 4.1 — código novo no container (`write_log` presente) | ✅ |
| 4.2 — POST /cnds/run → log `cnds_only` gravado com `certidoes_atualizadas=6` | ✅ |
| 4.3 — GET /history exibe entrada `cnds_only` | ✅ |
| 4.4 — coleta completa: diff=+1 log (não duplica) | ✅ |

---

## 6. Contratos

- **CONTRACTS_GEDEON.md** v1.49 → v1.50
- §47.6: item D5.5.2 marcado ✅
- §48: seção completa adicionada (motivação, contrato, anti-duplicação, validação, testes)
