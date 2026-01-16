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

### WebService NFS-e Manaus (Testado)

```
URL Base: https://nfse-prd.manaus.am.gov.br/nfse/servlet
Provider: Abaco/GIF
Namespace: http://www.e-nfs.com.br
Versão ABRASF: 2.04
```

**Endpoints funcionais:**
- `/arecepcionarloterps` - Envio de lote RPS
- `/aconsultarsituacaoloterps` - Consulta situação
- `/aconsultarnfseporrps` - Consulta por RPS
- `/aconsultarloterps` - Consulta lote

### Credenciais Configuradas

Arquivo: `/opt/conecta-pro/credentials/.env.credentials`

```env
# Prefeitura de Manaus (NFS-e)
NFSE_MANAUS_CNPJ=35710481000103
NFSE_MANAUS_USUARIO=35710481000103
NFSE_MANAUS_SENHA=jordan0612
NFSE_MANAUS_ENVIRONMENT=producao
```

### Último Commit

```
fcfef44 feat(sprint33): implementa 11 módulos de integração governamental
```

## Estrutura do Módulo Government Integrations

```
modules/government_integrations/
├── core/
│   ├── __init__.py          # Exports (v1.1.0)
│   ├── certificate_manager.py
│   ├── xml_signer.py
│   ├── esocial_transmitter.py
│   ├── sefaz_manager.py
│   ├── fgts_inss_manager.py
│   ├── nfse_manaus.py        # NFS-e Manaus (Abaco)
│   ├── efd_reinf.py          # EFD-Reinf
│   ├── dctfweb.py            # DCTFWeb
│   ├── fgts_digital.py       # FGTS Digital
│   ├── simples_nacional.py   # Simples Nacional
│   ├── sped_fiscal.py        # SPED Fiscal
│   ├── sped_contabil.py      # SPED Contábil
│   ├── cte.py                # CT-e
│   ├── mdfe.py               # MDF-e
│   ├── govbr.py              # Gov.br OAuth2
│   └── ecac.py               # e-CAC
├── controllers/
├── services/
└── schemas/
```

## Próximos Passos Sugeridos

1. **Implementar emissão real de NFS-e** - Testar com RPS de homologação
2. **Integrar certificado digital A1** - Usar certificado real para assinatura
3. **Criar controllers REST** - Expor APIs para frontend
4. **Testes de integração** - Validar fluxos completos
5. **Migração NFS-e Padrão Nacional** - Manaus migrará em 2026

## Sessão Anterior (16/01/2026)

### O que foi feito:
- Implementados 11 módulos de integração governamental
- Testada conexão real com WebService NFS-e Manaus
- Atualizado NFSeManausManager com URLs corretas do Abaco
- Configuradas credenciais de produção
- Commit realizado: `fcfef44`

### Testes realizados:
- Todos os 11 módulos carregando corretamente
- WebService Manaus respondendo (HTTP 200)
- Estrutura SOAP validada via WSDL
- Classes e dataclasses funcionando

### Observações:
- WebService portal login retornando 500 (problema do lado da prefeitura)
- Endpoints SOAP funcionando normalmente
- Zeep instalado para cliente SOAP

## Comandos Úteis

```bash
# Testar módulos
python3 /tmp/test_final_correto.py

# Verificar imports
python3 -c "from modules.government_integrations.core import *; print('OK')"

# Git status
git log --oneline -5
```

---
*Última atualização: 16/01/2026 03:55*
