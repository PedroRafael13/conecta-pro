# Conecta PRO - Backend

## Projeto
Sistema ERP completo para gestão empresarial com foco em vigilância e segurança patrimonial.

**Empresa:** JORDAN SANTOS DE JESUS LTDA
**CNPJ:** 35.710.481/0001-03
**Regime:** Simples Nacional
**Setor:** Vigilância e Segurança

## Stack Técnico
- **Backend:** Python 3.12 + FastAPI + SQLAlchemy
- **Database:** PostgreSQL 16 + Redis 7
- **Containers:** Docker + Docker Compose

## Sprint 34 - NFS-e Emissão Real (EM ANDAMENTO)

### Implementado (16/01/2026)

| Item | Arquivo | Status |
|------|---------|--------|
| Service NFS-e Manaus | `services/nfse_manaus_service.py` | ✅ OK |
| Schemas NFS-e | `schemas/nfse_manaus.py` | ✅ OK |
| Controller REST NFS-e | `controllers/nfse_manaus_controller.py` | ✅ OK |
| Testes NFS-e | `tests/test_nfse_manaus.py` | ✅ 21 passed |
| NFS-e Padrão Nacional | `core/nfse_nacional.py` | ✅ Preparação |

### Endpoints NFS-e Disponíveis

```
POST /api/v1/government/nfse-manaus/emitir      - Emite NFS-e via RPS
GET  /api/v1/government/nfse-manaus/consultar/rps/{numero}  - Consulta por RPS
GET  /api/v1/government/nfse-manaus/consultar/numero/{numero}  - Consulta por número
POST /api/v1/government/nfse-manaus/cancelar   - Cancela NFS-e
POST /api/v1/government/nfse-manaus/substituir - Substitui NFS-e
GET  /api/v1/government/nfse-manaus/lote/{numero}  - Consulta lote
GET  /api/v1/government/nfse-manaus/status     - Valida conexão WebService
GET  /api/v1/government/nfse-manaus/codigos-servico  - Lista códigos LC 116
```

### Exemplo de Emissão NFS-e

```python
from modules.government_integrations.services import get_nfse_manaus_service

service = get_nfse_manaus_service()

resultado = service.emitir_nfse(
    tomador_data={
        "cpf_cnpj": "12345678901234",
        "razao_social": "Empresa Cliente LTDA",
        "endereco": "Av. Eduardo Ribeiro",
        "numero": "1000",
        "bairro": "Centro",
        "cidade": "Manaus",
        "uf": "AM",
        "cep": "69010001",
        "email": "contato@empresa.com.br"
    },
    servico_data={
        "codigo_servico": "11.02",  # Vigilância
        "discriminacao": "Serviços de vigilância patrimonial - Janeiro/2026",
        "valor_servicos": "15000.00",
        "aliquota_iss": "0.05",
        "iss_retido": False
    },
    competencia="2026-01",
    optante_simples=True
)
```

### Códigos de Serviço (Vigilância)

| Código | Descrição | Alíquota ISS |
|--------|-----------|--------------|
| 11.02 | Vigilância, segurança ou monitoramento | 5% |
| 11.03 | Escolta, inclusive de veículos e cargas | 5% |
| 11.04 | Armazenamento, depósito, guarda de bens | 5% |
| 11.05 | Transporte de valores | 5% |

### Credenciais Configuradas

Arquivo: `/opt/conecta-pro/credentials/.env.credentials`

```env
NFSE_MANAUS_CNPJ=35710481000103
NFSE_MANAUS_USUARIO=35710481000103
NFSE_MANAUS_SENHA=jordan0612
NFSE_MANAUS_ENVIRONMENT=producao
CERTIFICATE_PATH=/opt/conecta-pro/credentials/certificates/certificado.pfx
CERTIFICATE_PASSWORD=Conecta123
```

## Sprint 33 - Integrações Governamentais (CONCLUÍDO)

### Módulos Implementados (11/11 - 100%)

| Módulo | Arquivo | Status |
|--------|---------|--------|
| NFS-e Manaus | `core/nfse_manaus.py` | OK |
| EFD-Reinf | `core/efd_reinf.py` | OK |
| DCTFWeb | `core/dctfweb.py` | OK |
| FGTS Digital | `core/fgts_digital.py` | OK |
| Simples Nacional | `core/simples_nacional.py` | OK |
| SPED Fiscal | `core/sped_fiscal.py` | OK |
| SPED Contábil | `core/sped_contabil.py` | OK |
| CT-e | `core/cte.py` | OK |
| MDF-e | `core/mdfe.py` | OK |
| Gov.br | `core/govbr.py` | OK |
| e-CAC | `core/ecac.py` | OK |

### WebService NFS-e Manaus

```
URL Produção: https://nfse-prd.manaus.am.gov.br/nfse/servlet
URL Homologação: https://nfse-hml.manaus.am.gov.br/nfse/servlet
Provider: Abaco/GIF
Namespace: http://www.e-nfs.com.br
Versão ABRASF: 2.04
```

## Migração NFS-e Padrão Nacional (Previsão: 2026)

O Padrão Nacional substituirá gradualmente o ABRASF em todos os municípios.

### Diferenças Principais

| Característica | ABRASF (Atual) | Padrão Nacional |
|----------------|----------------|-----------------|
| Protocolo | SOAP/XML | REST/JSON |
| Documento | RPS | DPS |
| Numeração | Municipal | Nacional |
| Autenticação | Certificado A1 | Certificado + Gov.br |

### Preparação

Módulo `core/nfse_nacional.py` criado com:
- `NFSeNacionalManager` - Manager preparatório
- `DPSNacional` - Estrutura do novo documento
- `MAPEAMENTO_SERVICOS_VIGILANCIA` - Mapeamento ABRASF → NBS

## Estrutura do Módulo Government Integrations

```
modules/government_integrations/
├── core/
│   ├── __init__.py
│   ├── certificate_manager.py    # Certificados A1
│   ├── xml_signer.py             # Assinatura XMLDSig
│   ├── nfse_manaus.py            # NFS-e ABRASF 2.04
│   ├── nfse_nacional.py          # Padrão Nacional (prep)
│   ├── esocial_transmitter.py
│   ├── sefaz_manager.py
│   ├── fgts_inss_manager.py
│   ├── efd_reinf.py
│   ├── dctfweb.py
│   ├── fgts_digital.py
│   ├── simples_nacional.py
│   ├── sped_fiscal.py
│   ├── sped_contabil.py
│   ├── cte.py
│   ├── mdfe.py
│   ├── govbr.py
│   └── ecac.py
├── controllers/
│   ├── __init__.py
│   ├── nfse_manaus_controller.py  # NOVO
│   ├── esocial_controller.py
│   ├── sefaz_controller.py
│   ├── fgts_inss_controller.py
│   ├── certificate_controller.py
│   └── status_controller.py
├── services/
│   ├── __init__.py
│   ├── nfse_manaus_service.py     # NOVO
│   ├── esocial_service.py
│   ├── sefaz_service.py
│   └── fgts_inss_service.py
└── schemas/
    ├── __init__.py
    ├── nfse_manaus.py             # NOVO
    ├── common.py
    ├── esocial.py
    ├── sefaz.py
    └── fgts_inss.py
```

## Comandos Úteis

```bash
# Executar testes NFS-e
cd /opt/conecta-pro/backend
source venv/bin/activate
python3 -m pytest tests/test_nfse_manaus.py -v

# Verificar imports
python3 -c "from modules.government_integrations.services import get_nfse_manaus_service; print('OK')"

# Testar conexão WebService
python3 -c "
from modules.government_integrations.services import get_nfse_manaus_service
service = get_nfse_manaus_service()
print(service.validar_conexao())
"

# Git status
git log --oneline -5
```

## Sprint 35 - Sincronização Real de Dados Governamentais (EM ANDAMENTO)

### Sistema de Sincronização Implementado

#### SyncManager (Gerenciador Central)
Coordena sincronizações de 12 serviços governamentais:

| Nível | Serviços | Status |
|-------|----------|--------|
| Federal | eSocial, Receita Federal, FGTS Digital, EFD-Reinf, DCTFWeb, SPED Contábil | ✅ |
| Estadual | NF-e (SVRS), CT-e, MDF-e, SPED Fiscal | ✅ |
| Municipal | NFS-e Manaus, NFS-e Nacional | ✅ |

#### Endpoints REST de Sincronização
```
POST /sync/{servico}              - Executar sync
POST /sync/todos                  - Sincronizar todos
POST /sync/{servico}/background   - Sync em background
GET  /sync/status/{cnpj}          - Status
GET  /sync/historico/{cnpj}       - Histórico
GET  /sync/jobs                   - Jobs ativos
POST /sync/agendamento            - Configurar agendamento
POST /sync/configuracao           - Configurar integração
GET  /sync/dados/documentos/{cnpj}      - Documentos fiscais
GET  /sync/dados/eventos-esocial/{cnpj} - Eventos eSocial
GET  /sync/dados/certidoes/{cnpj}       - Certidões
GET  /sync/dados/guias/{cnpj}           - Guias DARF/GPS/FGTS
```

### Teste de Conexão Real (16/01/2026 18:33)

**Taxa de sucesso: 75% (12/16)**

| Serviço | Status | Observação |
|---------|--------|------------|
| Certificado A1 | ✅ OK | Válido até 13/01/2027 (361 dias) |
| Receita Federal | ✅ OK | CNPJ 35.710.481/0001-03 - ATIVA |
| e-CAC | ✅ OK | Portal acessível |
| eSocial | ✅ OK | Portal acessível |
| SVRS NF-e | ✅ OK | WebService respondendo (403 = precisa certificado) |
| CT-e | ✅ OK | WebService respondendo |
| MDF-e | ✅ OK | WebService respondendo |
| FGTS Digital | ✅ OK | Portal acessível |
| Portal Receita | ✅ OK | Acessível |
| Portal eSocial | ✅ OK | Acessível |
| NFS-e Nacional | ✅ OK | Portal acessível |
| NFS-e Manaus | ✅ OK | Portal e WebService OK |
| SEFAZ AM Prod | ❌ ERRO | Requer certificado cliente SSL |
| SEFAZ AM Hom | ❌ ERRO | Requer certificado cliente SSL |
| Conectividade Social | ❌ ERRO | DNS não resolve |
| Portal SPED | ⏱️ TIMEOUT | Servidor lento |

### Script de Teste
```bash
cd /opt/conecta-pro/backend
source venv/bin/activate
python3 scripts/test_gov_connections.py
```

### Testes Automatizados
```
tests/test_nfse_manaus.py: 21 passed, 2 skipped
tests/test_sync_system.py: 43 passed
tests/test_govbr.py: testes Gov.br
```

### Próximos Passos
1. [ ] Integrar certificado A1 no cliente SOAP para SEFAZ AM
2. [ ] Criar migration para tabelas de sincronização
3. [ ] Registrar routers de sync no main.py
4. [ ] Implementar sincronização real com eSocial
5. [ ] Dashboard de monitoramento de sincronizações

---
*Última atualização: 16/01/2026 18:35*
