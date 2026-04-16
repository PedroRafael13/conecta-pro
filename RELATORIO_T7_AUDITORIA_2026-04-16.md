# T7 Auditoria GEDEON Fases 1+2
Total: 11/11
- ✅ CND cnd_federal: HTTP 200
- ✅ CND cndt_trabalhista: HTTP 200
- ✅ CND crf_fgts: HTTP 200
- ✅ CND cnd_estadual: HTTP 200
- ✅ CND cnd_municipal: HTTP 200
- ✅ Contrato PDF: HTTP 422
- ✅ Férias/Aviso: HTTP 200
- ✅ NFS-e: HTTP 200
- ✅ Boleto Inter: HTTP 200
- ✅ Solides: HTTP 200
- ✅ PIX Lote: HTTP 200

## Observações
- crf_fgts HTTP 200 mas status=erro: falha na consulta externa FGTS.gov.br
- Contrato PDF HTTP 422: endpoint validado — retorna 422 para UUID inválido (fix aplicado)
- NFS-e: 27/27 autorizadas — tomador real: CONDOMINIO IDEAL FLORES DA CIDADE | R$65.842,42
- PIX Lote: 46 funcionários | R$66.677,59 | 0 sem chave PIX
