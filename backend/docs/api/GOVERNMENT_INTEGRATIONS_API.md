# API de Integracoes Governamentais

Base URL: `/api/v1/government`

## Sumario de Endpoints

| Modulo | Qtd Endpoints | Prefixo |
|--------|---------------|---------|
| NF-e (SEFAZ) | 2 | `/sefaz` |
| NFC-e | 11 | `/nfce` |
| CT-e | 12 | `/cte` |
| MDF-e | 14 | `/mdfe` |
| NFS-e Manaus | 6 | `/nfse-manaus` |
| NFS-e Nacional | 10 | `/nfse-nacional` |
| EFD-REINF | 8 | `/reinf` |
| eSocial | 8 | `/esocial` |
| DCTFWeb | 6 | `/dctfweb` |
| SPED Fiscal | 8 | `/sped-fiscal` |
| SPED Contabil | 10 | `/sped-contabil` |
| FGTS/INSS | 4 | `/fgts-inss` |
| FGTS Digital | 6 | `/fgts-digital` |
| Simples Nacional | 6 | `/simples-nacional` |
| e-CAC | 8 | `/ecac` |
| Receita Federal | 4 | `/receita-federal` |
| Gov.br | 6 | `/govbr` |
| Certificados | 4 | `/certificates` |
| Status | 2 | `/status` |
| Sync | 4 | `/sync` |
| Jobs | 4 | `/jobs` |
| Dashboard | 4 | `/dashboard` |
| Extraction | 4 | `/extraction` |

**Total: 147 endpoints**

---

## NFC-e - Nota Fiscal Consumidor Eletronica

### POST /nfce/emitir
Emite NFC-e para venda ao consumidor final.

**Request Body:**
```json
{
  "consumidor": {
    "cpf": "12345678900",
    "nome": "Nome do Consumidor",
    "email": "email@exemplo.com"
  },
  "itens": [
    {
      "codigo": "001",
      "ean": "7891234567890",
      "descricao": "Produto Exemplo",
      "ncm": "12345678",
      "cfop": "5102",
      "unidade": "UN",
      "quantidade": 1.0,
      "valor_unitario": 10.00,
      "cst_icms": "102"
    }
  ],
  "pagamentos": [
    {
      "tipo": "01",
      "valor": 10.00
    }
  ],
  "serie": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "NFC-e autorizada com sucesso",
  "data": {
    "chave_acesso": "13260135710481000103650010000000011234567890",
    "numero": 1,
    "serie": 1,
    "protocolo": "313260000123456",
    "qrcode_url": "https://...",
    "url_consulta": "https://..."
  }
}
```

### GET /nfce/consultar/{chave_acesso}
Consulta situacao da NFC-e pela chave de acesso.

### POST /nfce/cancelar
Cancela NFC-e autorizada (prazo: 30 min).

### POST /nfce/inutilizar
Inutiliza faixa de numeracao.

### GET /nfce/status
Status do servico NFC-e na SEFAZ.

### POST /nfce/contingencia/transmitir
Transmite NFC-e emitida em contingencia offline.

### GET /nfce/danfe/{chave_acesso}
Gera DANFE (PDF, HTML ou ESC/POS).

### GET /nfce/xml/{chave_acesso}
Download do XML autorizado.

### GET /nfce/listar
Lista NFC-e emitidas com filtros.

---

## CT-e - Conhecimento de Transporte Eletronico

### GET /cte/status
Retorna status da configuracao.

### POST /cte/criar
Cria novo CT-e.

**Request Body:**
```json
{
  "numero": 1,
  "serie": 1,
  "modal": "rodoviario",
  "tipo_servico": "normal",
  "cfop": "6353",
  "natureza_operacao": "PRESTACAO DE SERVICO DE TRANSPORTE",
  "tomador": "remetente",
  "valor_total": 500.00,
  "remetente": {
    "cnpj_cpf": "12345678000100",
    "razao_social": "Empresa Remetente",
    "endereco": {...}
  },
  "destinatario": {...},
  "carga": {
    "produto_predominante": "MERCADORIAS",
    "valor_carga": 10000.00,
    "peso_bruto": 1000.0
  }
}
```

### POST /cte/gerar-xml
Gera XML do CT-e.

### POST /cte/gerar-xml/download
Download do XML gerado.

### GET /cte/consultar-status-servico
Consulta status do servico na SEFAZ.

### GET /cte/modais
Lista modais de transporte (rodoviario, aereo, aquaviario, ferroviario, dutoviario).

### GET /cte/tipos-servico
Lista tipos de servico (normal, subcontratacao, redespacho, etc).

### GET /cte/listar
Lista CT-e em cache.

### GET /cte/obter/{numero}
Obtem CT-e especifico.

### DELETE /cte/limpar
Limpa cache de CT-e.

---

## MDF-e - Manifesto Eletronico de Documentos Fiscais

### GET /mdfe/status
Retorna status da configuracao.

### POST /mdfe/criar
Cria novo MDF-e.

**Request Body:**
```json
{
  "numero": 1,
  "serie": 1,
  "modal": "rodoviario",
  "tipo_emitente": "prestador_servico",
  "uf_carregamento": "AM",
  "uf_descarregamento": "SP",
  "veiculo_tracao": {
    "placa": "ABC1234",
    "renavam": "123456789",
    "tara": 5000,
    "capacidade_kg": 10000,
    "tipo_rodado": "truck",
    "tipo_carroceria": "fechada",
    "uf": "AM"
  },
  "condutores": [
    {"cpf": "12345678900", "nome": "Motorista"}
  ],
  "percurso": ["PA", "TO", "GO", "MG"],
  "documentos": [
    {
      "tipo": "cte",
      "chave": "13260135710481000103570010000000011234567890"
    }
  ]
}
```

### POST /mdfe/gerar-xml
Gera XML do MDF-e.

### POST /mdfe/gerar-xml/download
Download do XML gerado.

### POST /mdfe/encerrar
Gera evento de encerramento (obrigatorio ao fim da viagem).

### POST /mdfe/incluir-condutor
Inclui condutor em transito.

### GET /mdfe/consultar-status-servico
Consulta status do servico na SEFAZ.

### GET /mdfe/nao-encerrados
Lista MDF-e autorizados nao encerrados.

### GET /mdfe/modais
Lista modais de transporte.

### GET /mdfe/tipos-emitente
Lista tipos de emitente.

### GET /mdfe/tipos-carroceria
Lista tipos de carroceria.

### GET /mdfe/listar
Lista MDF-e.

### GET /mdfe/{mdfe_id}
Busca MDF-e pelo ID.

### DELETE /mdfe/limpar
Limpa dados em memoria.

---

## EFD-REINF

### POST /reinf/r1000
Gera evento R-1000 (Informacoes do Contribuinte).

### POST /reinf/r2010
Gera evento R-2010 (Retencoes Servicos Tomados).

### POST /reinf/r4010
Gera evento R-4010 (Pagamentos a Beneficiarios PF).

### POST /reinf/r4020
Gera evento R-4020 (Pagamentos a Beneficiarios PJ).

### POST /reinf/r2099
Gera evento R-2099 (Fechamento Periodo).

### POST /reinf/enviar-lote
Envia lote de eventos.

### GET /reinf/consultar-lote/{protocolo}
Consulta situacao do lote.

### GET /reinf/status
Status da configuracao REINF.

---

## eSocial

### POST /esocial/s1000
Gera evento S-1000 (Informacoes do Empregador).

### POST /esocial/s2200
Gera evento S-2200 (Cadastramento Inicial).

### POST /esocial/s1200
Gera evento S-1200 (Remuneracao).

### POST /esocial/enviar-lote
Envia lote de eventos.

### GET /esocial/consultar-lote/{protocolo}
Consulta situacao do lote.

### GET /esocial/status
Status da configuracao eSocial.

### GET /esocial/eventos-pendentes
Lista eventos pendentes de envio.

### GET /esocial/tabela/{codigo}
Consulta tabela do eSocial.

---

## SPED Fiscal (EFD-ICMS/IPI)

### POST /sped-fiscal/iniciar
Inicia escrituracao do periodo.

### POST /sped-fiscal/registro
Adiciona registro ao arquivo.

### POST /sped-fiscal/apuracao
Calcula apuracao de impostos.

### POST /sped-fiscal/inventario
Adiciona inventario (Bloco H).

### POST /sped-fiscal/gerar
Gera arquivo SPED Fiscal.

### POST /sped-fiscal/validar
Valida arquivo com PVA.

### GET /sped-fiscal/status
Status da escrituracao.

### DELETE /sped-fiscal/limpar
Limpa dados da escrituracao.

---

## SPED Contabil (ECD)

### POST /sped-contabil/iniciar
Inicia escrituracao contabil.

### POST /sped-contabil/conta
Adiciona conta ao plano de contas.

### POST /sped-contabil/lancamento
Adiciona lancamento contabil.

### POST /sped-contabil/balanco
Define balanco patrimonial.

### POST /sped-contabil/dre
Define DRE.

### POST /sped-contabil/gerar
Gera arquivo ECD.

### POST /sped-contabil/assinar
Assina arquivo digitalmente.

### GET /sped-contabil/plano-contas
Lista plano de contas.

### GET /sped-contabil/status
Status da escrituracao.

### DELETE /sped-contabil/limpar
Limpa dados da escrituracao.

---

## Tipos de Pagamento NFC-e

| Codigo | Descricao |
|--------|-----------|
| 01 | Dinheiro |
| 02 | Cheque |
| 03 | Cartao de Credito |
| 04 | Cartao de Debito |
| 05 | Credito Loja |
| 10 | Vale Alimentacao |
| 11 | Vale Refeicao |
| 12 | Vale Presente |
| 13 | Vale Combustivel |
| 17 | PIX |
| 18 | Transferencia |
| 19 | Cashback |
| 90 | Sem Pagamento |
| 99 | Outros |

---

## Modais de Transporte (CT-e/MDF-e)

| Codigo | Modal |
|--------|-------|
| 01 | Rodoviario |
| 02 | Aereo |
| 03 | Aquaviario |
| 04 | Ferroviario |
| 05 | Dutoviario |

---

## Codigos de Retorno SEFAZ

| Codigo | Significado |
|--------|-------------|
| 100 | Autorizado o uso da NF-e/NFC-e/CT-e/MDF-e |
| 101 | Cancelamento homologado |
| 102 | Inutilizacao homologada |
| 107 | Servico em operacao |
| 108 | Servico paralisado momentaneamente |
| 109 | Servico paralisado sem previsao |
| 135 | Evento registrado e vinculado |
| 215 | Rejeicao: Chave invalida |
| 217 | Rejeicao: CNPJ invalido |
| 225 | Rejeicao: Falha no Schema XML |
| 539 | Rejeicao: Duplicidade de NF-e |

---

## Autenticacao

Todos os endpoints requerem autenticacao via Bearer Token:

```
Authorization: Bearer {token}
```

## Rate Limiting

- 200 requests/minuto por IP
- 50 requests/minuto para endpoints de emissao

## Ambientes

- **Producao:** `https://api.conectapro.com.br/api/v1`
- **Homologacao:** `https://hom.conectapro.com.br/api/v1`

---

*Documentacao gerada em: 2026-01-17*
*Versao API: 1.0.0*
