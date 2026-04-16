---
name: nfse-nacional-manaus-limitacao
description: Documentação técnica da integração NFS-e Portal Nacional (nfse.gov.br) para Manaus/AM — limitações conhecidas do protocolo ABRASF, status atual e alternativas.
---

# NFS-e Portal Nacional — Documentação Técnica Manaus/AM

## Status atual (16/04/2026)
- Portal: https://www.nfse.gov.br (nacional, desde 01/01/2026)
- CNPJ emissor: 35.710.481/0001-03
- Certificado A1: válido até jan/2027
- NFS-e emitidas: 27 (jan-abr/2026) | Total faturado: R$542.673,92
- Método: manual via portal (automação bloqueada)

## Por que a automação está bloqueada

### Limitação ABRASF para Manaus/AM
O Portal Nacional de NFS-e usa o padrão ABRASF v2.04.
Manaus/AM tem uma particularidade:

1. **SEMEF (prefeitura antiga)** — usava sistema próprio em nfse-prd.manaus.am.gov.br
   → Descontinuado em 01/01/2026, migrado para portal nacional

2. **Portal Nacional** — aceita emissão via webservice SOAP, MAS:
   → Requer credencial de acesso à API aprovada pela prefeitura local
   → Manaus/AM ainda não liberou automaticamente as credenciais API para novos emissores
   → Processo de habilitação: protocolar na SEMEF + aguardar aprovação (prazo indefinido)

3. **Alternativa atual** — emissão manual no portal web:
   → Login: erp.conectamais.pro → Fiscal → NFS-e
   → Preencher dados → Emitir → Salvar XML + PDF

## Fluxo atual (manual, funcional)
```
1. CRM gera fatura do cliente (billing_rules trigger)
2. Operador acessa /modulos/fiscal/nfse
3. Clica "Emitir NFS-e" → formulário pré-preenchido do contrato
4. Confirma → POST manual no portal nfse.gov.br
5. XML + PDF salvos no GED do cliente automaticamente
6. NFS-e registrada em nfses table com chave de acesso
```

## Próximos passos para automação
- [ ] Protocolar habilitação API na SEMEF Manaus (rua Maceió, s/n — Centro)
- [ ] Documentos: procuração + certidão negativa + CNPJ + contrato social
- [ ] Prazo estimado: 30-90 dias após protocolo
- [ ] Quando aprovado: endpoint `/nfse/emitir` já implementado — só precisa da credencial

## Impacto atual
- Sem automação: ~5 min por nota × 27 notas/mês = ~2,25h/mês operacionais
- Com automação: 0 tempo (disparado por billing_rules trigger)
- Prioridade: MÉDIA — não bloqueia operação, mas escala mal a partir de 50+ notas/mês

## O que o Conecta PRO já tem pronto (aguardando habilitação)
```python
# backend/modules/fiscal/services/nfse_service.py
class NfseNacionalService:
    async def emitir_automatico(self, billing_rule_id: UUID) -> NfseResult:
        """
        Emissão automática via WebService SOAP Portal Nacional
        Status: AGUARDANDO habilitação API na SEMEF Manaus
        Implementado: sim | Habilitado: não
        Ativar: definir NFSE_API_TOKEN no .env após aprovação SEMEF
        """
        ...
```

## Dados reais das 27 NFS-e emitidas
- Total faturado: R$542.673,92
- Período: jan/2026 — abr/2026
- Todas com status 'autorizada'
- Serviço: código 11.02 (vigilância/portaria) | ISS 5%
- Última emissão: 12/02/2026
