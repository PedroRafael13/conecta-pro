---
title: Integrações Governamentais
description: eSocial, SEFAZ, NFS-e para Conecta PRO
integrations: [esocial, sefaz, nfse, sep, cte]
---

# Integrações Governamentais

Integrações obrigatórias com órgãos governamentais para compliance fiscal e trabalhista.

## Integrações Suportadas

| Sistema | Órgão | Função | Status |
|---------|-------|--------|--------|
| eSocial | CAIXA/Gov | Folha e eventos trabalhistas | ✅ |
| SEFAZ | Fazenda estadual | NF-e, NFC-e | ✅ |
| NFS-e | Prefeituras | Nota serviço municipal | ✅ |
| SEP | Polícia Federal | Porte de armas | ✅ |
| CT-e | Fazenda | Conhecimento transporte | 🚧 |

## eSocial

```bash
# Envio de eventos
python -m gov.esocial enviar S-1000
docker-compose run gov-integrator esocial send --event S-2200

# Consulta retorno
python -m gov.esocial consultar 123456789

# Eventos periódicos
S-1200  # Remuneração trabalhadores
S-1210  # Pagamentos diversos
S-1299  # Fechamento folha
```

## SEFAZ

```python
# Estados suportados
UF_SP = "35"  # São Paulo
UF_RJ = "33"  # Rio de Janeiro
UF_MG = "31"  # Minas Gerais
# ... demais estados

# Operações
emitir_nfe(dados_nfe, uf="35")
consultar_cadastro(ie, cnpj, uf)
cancelar_nfe(chave, justificativa)
inutilizar_numeracao(serie, inicio, fim)
```

## NFS-e

```python
# Prefeituras homologadas
prefeituras = [
    "saopaulo", "riodejaneiro", "belohorizonte",
    "curitiba", "portoalegre", "salvador"
]

# Emissão
emitir_nfse(
    prestador=cnpj,
    tomador=dados_tomador,
    servico=codigo_tributacao,
    valor=valor_servico
)
```

## Monitoramento

```bash
# Status das filas
python -m gov.monitor status

# Reprocessar falhas
python -m gov.integrator reprocessar --data 2024-01-15

# Relatório de pendências
python -m gov.relatorio pendencias --output pdf
```

## Checklist de Compliance

- [ ] Certificados digitais válidos (A1/A3)
- [ ] Cronjob de envios automáticos
- [ ] Tratamento de rejeições
- [ ] Backup de XMLs autorizados
- [ ] Monitoramento de filas
- [ ] Alertas de certificado próximo ao vencimento
