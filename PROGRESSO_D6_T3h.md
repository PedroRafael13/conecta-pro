# PROGRESSO D6 — T+3h

**Fase:** D6.3 concluída
**Timestamp:** 2026-04-30 T+3h

## ✅ Concluído nesta hora

### D6.3 — Boletos e Cobranças
- `CobrancaService.emitir(cliente_crm_id, valor, vencimento, descricao)`:
  1. Grava em `inter_cobrancas` com status `PENDENTE`
  2. Chama Inter API `adapter.generate_boleto()`
  3. Atualiza registro com `cobranca_id_inter`, `url_boleto`, `pix_copia_cola`, `barcode`, `linha_digitavel`, status `A_RECEBER`
- `CobrancaService.sincronizar_status()` — batch de 50 cobranças A_RECEBER, consulta Inter e atualiza
- `CobrancaService.listar(status, vencimento_inicio, vencimento_fim, limit)`
- `CobrancaService.estatisticas()` — GROUP BY status
- Endpoints: `POST /cobrancas`, `GET /cobrancas`, `GET /cobrancas/{id}`, `GET /cobrancas/{id}/pdf`, `DELETE /cobrancas/{id}`, `POST /cobrancas/sincronizar-status`, `GET /cobrancas/estatisticas`
- Testes D6.3 (4/4): sincronizar_status_sem_cobrancas, listar_retorna_lista, estatisticas, cobranca_emitir

## 📊 Status
- Testes: 15/16 passando
