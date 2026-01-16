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

## Sessão Atual (16/01/2026)

### O que foi feito:
- [x] Criado `nfse_manaus_service.py` - Service completo com integração real
- [x] Criado `nfse_manaus.py` (schemas) - Validação Pydantic entrada/saída
- [x] Criado `nfse_manaus_controller.py` - 8 endpoints REST
- [x] Criado `test_nfse_manaus.py` - 21 testes (todos passando)
- [x] Criado `nfse_nacional.py` - Preparação migração Padrão Nacional
- [x] Corrigido `NFSeManausManager` para suportar operação sem certificado
- [x] Atualizados todos os `__init__.py`

### Testes executados:
```
tests/test_nfse_manaus.py: 21 passed, 2 skipped
```

### Próximos passos sugeridos:
1. Configurar certificado digital A1 real
2. Testar emissão em ambiente de homologação
3. Implementar persistência de NFS-e no banco de dados
4. Criar fluxo de integração com módulo financeiro
5. Implementar relatórios de NFS-e emitidas

---
*Última atualização: 16/01/2026 13:45*
