# T1 — Inter Banking Bugs Corrigidos
**Data:** 2026-04-11
**Engenheiro:** Claude Sonnet 4.6
**Branch:** feature/people-management-reorganization

---

## Bug-01: Boleto endereço pagador

ANTES: pagador sem endereço → HTTP 400 Inter (violação `tipoPessoa`, campos de endereço nulos)

DEPOIS: campos `tipoPessoa`, `endereco`, `numero`, `bairro`, `cidade`, `uf`, `cep` adicionados.
Também corrigido `seuNumero` (era 17 chars, limite Inter é 15).

## Bug-02: PIX scope

ANTES: `SCOPES["saldo"] = "cob.read"` (não registrado) → token combinado rejeitado → PIX falha

DEPOIS:
- `"saldo": "extrato.read"` (corrigido)
- `"cob": "cob.write cob.read"` adicionado ao SCOPES
- `authenticate()` inclui `self.SCOPES.get("cob", "cob.write cob.read")`
- txid PIX corrigido para 27 chars (BACEN exige 26-35)

---

## Testes

**Boleto:**
```json
{
  "success": true,
  "boleto_id": "770c98a1-dde0-4698-a425-6128123e8af5",
  "amount": 6000.0,
  "due_date": "2026-04-30",
  "payer_name": "CONDOMINIO PARQUE RESIDENCIAL GELAIN",
  "payer_document": "00736037000182"
}
```
✅ Boleto R$ 6.000 emitido com sucesso — CONDOMINIO PARQUE RESIDENCIAL GELAIN

**PIX:**
```json
{
  "success": true,
  "charge_id": "CON20260411213732JHH7FY3GDX",
  "pix_copy_paste": "00020101021226930014BR.GOV.BCB.PIX...",
  "pix_qrcode": "https://spi-qrcode.bancointer.com.br/...",
  "amount": 150.0,
  "description": "Servico manutencao - Denilson Silva",
  "payer_name": "DENILSON SILVA CARDOSO",
  "expires_at": "2026-04-12T21:37:32"
}
```
✅ PIX Cobrança R$ 150 gerado — copia-e-cola e QR Code funcionais

---

*Relatório gerado em 2026-04-11 por Claude Sonnet 4.6*
