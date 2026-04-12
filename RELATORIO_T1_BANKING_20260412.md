# T1 — Inter Banking: Consulta Boleto + TED
**Data:** 2026-04-12
**Engenheiro:** Claude Sonnet 4.6
**Commit:** 602f16f9
**Branch:** feature/people-management-reorganization

---

## NOVOS MÉTODOS — Adapter Inter

| Método | Endpoint Inter | Status |
|--------|---------------|--------|
| `get_boleto(boleto_id)` | GET /cobranca/v3/cobrancas/{id} | ✅ |
| `cancel_boleto(boleto_id, motivo)` | DELETE /cobranca/v3/cobrancas/{id}/cancelar | ✅ |
| `initiate_ted(valor, banco, ...)` | POST /banking/v2/transferencia | ✅ |
| `get_pix_received(inicio, fim)` | GET /pix/v2/pix | ✅ |
| `request_pix_refund(e2e_id, ...)` | PUT /pix/v2/pix/{e2eId}/devolucao/{id} | ✅ |

Scope TED adicionado: `"ted": "pagamento-ted.write pagamento-ted.read"`

---

## NOVOS ENDPOINTS — Controller

| Endpoint | Descrição |
|----------|-----------|
| `GET /banking/boleto/{boleto_id}` | Consulta boleto — barcode + PDF |
| `DELETE /banking/boleto/{boleto_id}` | Cancela boleto |
| `POST /banking/ted/transfer` | Transferência TED |
| `GET /banking/pix/received` | PIX recebidos por período |
| `POST /banking/pix/refund` | Devolução de PIX |

---

## TESTES PASSO 4

### Consulta Boleto (a24f3f5e — T7)
```json
{
  "success": true,
  "boleto_id": "a24f3f5e-fcb6-4151-8c94-17450214a9d6",
  "barcode": "07791143200000002500001112104916290675270691",
  "linha_digitavel": "07790001161210491629606752706918114320000000250",
  "nosso_numero": "90675270691",
  "status": "A_RECEBER",
  "valor": 2.5,
  "vencimento": "2026-04-30",
  "payer": {"nome": "TESTE AUDITORIA T7", "cpfCnpj": "35710481000103"}
}
```
✅ Barcode disponível após emissão de boleto

### PIX Recebidos (últimos 30 dias)
```json
{"success": true, "total": 0, "pix": [], "parametros": {"inicio": "2026-03-13", "fim": "2026-04-12"}}
```
✅ Endpoint funcional (0 PIX recebidos no período)

---

## COMMIT
```
602f16f9  feat(banking): consulta boleto+barcode, TED, PIX recebidos, devolução PIX
push: ✅ origin/feature/people-management-reorganization
```
