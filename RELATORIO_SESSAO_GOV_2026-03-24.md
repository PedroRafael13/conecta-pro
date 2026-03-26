# RELATÓRIO — SESSÃO INTEGRAÇÕES GOVERNAMENTAIS
**Data:** 2026-03-24 (madrugada)
**Branch:** feature/people-management-reorganization
**Commits:** b9a6b229, 9019d6a6

---

## 1. CONQUISTA PRINCIPAL: eSocial S-1000 ACEITO PELO GOVERNO

```
Evento:     S-1000 (Informações do Empregador)
Empresa:    JORDAN SANTOS DE JESUS LTDA — CNPJ 35.710.481/0001-03
Protocolo:  1.2.202603.0000000000203878541
Recibo:     1.2.0000000000305333794
Resposta:   202 — Sucesso com advertência
Ambiente:   Produção Restrita (homologação)
Assinatura: Certificado A1 — XMLDSig SHA256 — Válida
```

Este é o **primeiro evento real** transmitido do Conecta PRO para o governo federal. Comunicação bidirecional SOAP+mTLS confirmada e funcionando.

---

## 2. CAMINHO ATÉ O SUCESSO — 18 TENTATIVAS

Cada tentativa corrigiu um erro real retornado pelo webservice do eSocial. Documentar isso é crítico porque os mesmos padrões se aplicam a qualquer transmissão futura (S-2200, S-1200, EFD-Reinf).

### Erros de envelope SOAP (tentativas 1-9)

| # | Erro governo | Causa | Correção |
|---|---|---|---|
| 1 | Namespace `v1_1_0` rejeitado | Envelope SOAP com namespace antigo | `v1_1_1` no `<eSocial>` do lote |
| 2 | SOAPAction inválida | SOAPAction também com `v1_1_1` | SOAPAction mantém `v1_1_0` |
| 3 | nrInsc transmissor ≠ certificado | Transmissor com 8 dígitos | CNPJ completo 14 dígitos no transmissor |
| 4 | Id começa com número (`1A91...`) | UUID hex como Id do `<evento>` | Formato `ID` + prefixo |
| 5-9 | Código 609 — Id inválido | CNPJ completo no Id do lote | **Raiz CNPJ (8 dig) padded com zeros até 14** |

**Regra descoberta:** O `nrInsc` dentro do `Id` do `<evento>` no lote deve usar a **raiz do CNPJ** (8 primeiros dígitos) preenchida com zeros até 14 caracteres. Ex: `35710481` → `35710481000000`. Formato final do Id: `ID1` + `35710481000000` + `AAAAMMDDHHMMSS` + `NNNNN` = 36 chars exatos.

**Regra do double-wrapping:** O XSD do lote (`EnvioLoteEventos-v1_1_1.xsd`) usa `<xs:any processContents="skip">` dentro de `<evento>`. Isso significa que o XML completo do evento (com `<eSocial>` wrapper) vai DENTRO de `<evento>`. O double-wrapping `<eSocial lote>...<evento><eSocial evt>...</eSocial evt></evento>...</eSocial lote>` é o formato CORRETO.

### Erros de schema XML (tentativas 10-12)

| # | Erro governo | Causa | Correção |
|---|---|---|---|
| 10 | `indRetif` inválido no `ideEvento` | Campo não existe no S-1000 do leiaute S-1.3 | Removido |
| 11 | `nmRazao` fora de posição | Campo não existe no leiaute simplificado | Removido |
| 12 | Schema genérico inválido | `nmRazao`, `natJurid`, `contato` removidos do S-1000 no eSocial Simplificado | Todos removidos |

**Regra descoberta:** No eSocial Simplificado (versão S-1.x), o S-1000 é **minimalista**. Razão social, natureza jurídica e contato são obtidos automaticamente da base da Receita Federal pelo CNPJ. O evento só tem: `classTrib`, `indCoop`, `indConstr`, `indDesFolha`, `indOptRegEletron`.

### Erros de assinatura digital (tentativas 13-15)

| # | Erro governo | Causa | Correção |
|---|---|---|---|
| 13 | `CanonicalizationMethod` inválido | C14N exclusiva (`xml-exc-c14n#`) | C14N normal (`REC-xml-c14n-20010315`) |
| 14 | URI deve ser vazia | `URI="#ID..."` referenciando elemento | `URI=""` (assina documento inteiro) |
| 15 | Signature como child do `evtInfoEmpregador` | xml_signer colocava dentro do evt | Movida para **sibling** (child do `<eSocial>`) |

**Regras de assinatura eSocial (S-1.3):**
- CanonicalizationMethod: `http://www.w3.org/TR/2001/REC-xml-c14n-20010315` (NÃO exclusiva)
- SignatureMethod: `rsa-sha256`
- DigestMethod: `sha256`
- Reference URI: **vazia** (assinatura sobre documento inteiro)
- Transforms: enveloped-signature + c14n
- Posição: `<eSocial><evtXXX>...</evtXXX><Signature>...</Signature></eSocial>`

### Erro de versão do leiaute (tentativa 16)

| # | Erro governo | Causa | Correção |
|---|---|---|---|
| 16 | Código 403 — Leiaute inválido | Namespace `v_S_01_02_00` (versão S-1.2) | `v_S_01_03_00` (versão S-1.3, vigente) |

**Regra:** A versão vigente do eSocial em março/2026 é **S-1.3**. O namespace correto é `v_S_01_03_00`.

### Erro de campos obrigatórios (tentativa 17)

| # | Erro governo | Causa | Correção |
|---|---|---|---|
| 17 | `indCoop` obrigatório | Removido junto com campos opcionais | Adicionado de volta |

### Sucesso (tentativa 18)

Recibo `1.2.0000000000305333794` — advertência informativa sobre classificação tributária.

---

## 3. NFS-e NACIONAL — API DESCOBERTA E VALIDADA

### Descoberta

A API do portal NFS-e Nacional está em:
```
Produção:    https://sefin.nfse.gov.br/sefinnacional/
Versão:      SefinNacional_1.6.0
Autenticação: mTLS com certificado A1 ICP-Brasil
```

**NÃO está em** `www.nfse.gov.br/api/` nem em `www.producaorestrita.nfse.gov.br/api/` (que retornam 404 do IIS). O código atual do Conecta PRO aponta para URLs erradas.

### Endpoints confirmados

| Método | Endpoint | Testado | Resultado |
|---|---|---|---|
| POST | `/nfse` | Sim | 400 — E1226: XML mal formado (esperado, não enviamos DPS válido) |
| GET | `/nfse/{chaveAcesso}` | Sim | 404 — E2401: Chave não encontrada (API funcional) |
| GET | `/nfse/DPS/{chave}` | Sim | 400 — Espera chave 50 dígitos |
| GET | `/nfse/DANFSe/{chave}` | Sim | 400 — Espera chave 50 dígitos |
| POST | `/nfse/{chave}/eventos` | Não testado | Cancelamento/substituição |
| GET | `/nfse/contribuinte` | Sim | 404 — Espera chaveAcesso param |

### Formato de envio da DPS

O POST `/nfse` espera:
1. XML da DPS (Declaração de Prestação de Serviços) conforme schema nacional
2. Assinado com XMLDSig (certificado A1)
3. Comprimido com GZip
4. Codificado em Base64
5. Enviado como corpo da requisição HTTP POST

### O que falta para emitir NFS-e

1. Corrigir URLs no `NFSeNacionalClient` → `sefin.nfse.gov.br/sefinnacional/`
2. Implementar geração do XML DPS conforme schema nacional
3. Assinar XML com o mesmo XMLSigner (já funciona)
4. Comprimir + Base64
5. POST ao endpoint com mTLS
6. Parsear resposta (chave acesso 50 dígitos)

### Dados reais para DPS (extraídos da NFS-e nº 16)

```
prestador_cnpj:         35710481000103
prestador_im:           45177801
codigo_tributacao_nac:   14.06.01
codigo_tributacao_mun:   100
aliquota_iss:            5.00% (0.05)
iss_retido:              false
nbs:                     120032900
serie_dps:               900
municipio_prestacao:     1302603 (Manaus)
simples_nacional:        false (Lucro Real)
```

---

## 4. GAPS NOS DADOS DOS FUNCIONÁRIOS

Para transmitir S-2200 (Admissão), estes campos são obrigatórios e estão faltando:

| Campo | Preenchido | Total | Status |
|---|---|---|---|
| CPF | 52/52 | 100% | OK |
| Matrícula | 52/52 | 100% | OK |
| Data admissão | 52/52 | 100% | OK |
| Salário base | 52/52 | 100% | OK |
| **Data nascimento** | **0/52** | **0%** | **BLOQUEADOR** |
| **Sexo** | **0/52** | **0%** | **BLOQUEADOR** |
| **Estado civil** | **0/52** | **0%** | **BLOQUEADOR** |
| PIS/PASEP | 37/52 | 71% | 15 faltando |
| RG | 0/52 | 0% | Não obrigatório |

**Ação:** Jordan precisa fornecer data de nascimento, sexo e estado civil dos 52 funcionários. Provavelmente existem no Domínio Sistemas (TOTVS) do contador.

---

## 5. BLOQUEADORES POR INTEGRAÇÃO

### eSocial — Próximos eventos

| Evento | Bloqueador | Ação |
|---|---|---|
| S-1000 | **NENHUM — ACEITO** | ✅ Concluído |
| S-1005 (Estabelecimentos) | Implementar XML conforme XSD S-1.3 | Dev |
| S-1010 (Rubricas) | Tabela de rubricas da folha | DP + Dev |
| S-1020 (Lotações) | Dados de lotação tributária | DP |
| S-2200 (Admissões) | data_nascimento, sexo, estado_civil | **Jordan/DP** |
| S-1200 (Folha) | S-2200 aceitos primeiro | Sequencial |
| S-1299 (Fechamento) | S-1200 aceitos primeiro | Sequencial |

### NFS-e Nacional

| Item | Bloqueador | Ação |
|---|---|---|
| URLs da API | Código aponta para `www.nfse.gov.br/api` (errado) | Dev |
| XML DPS | Schema nacional não implementado | Dev |
| Assinatura DPS | XMLSigner funciona, precisa adaptar | Dev |
| GZip + Base64 | Código existe mas nunca chamado | Dev |
| Ambiente homologação | `adn-homologacao.nfse.gov.br` não resolve DNS | Pode não existir |

### EFD-Reinf

| Item | Bloqueador | Ação |
|---|---|---|
| Transmissão SOAP | Mesmo padrão do eSocial (já provado) | Dev |
| XML R-1000 | Implementar conforme XSD | Dev |
| Webservice URL | `reinf.receita.economia.gov.br` (não testado) | Dev |

### Gov.br

| Item | Bloqueador | Ação |
|---|---|---|
| CLIENT_ID / SECRET | Não registrado | **Jordan** (burocracia) |
| OAuth2 PKCE | Código existe, precisa de credenciais | Dev após Jordan |

### Dados hardcoded falsos

| Endpoint | Dado falso | Correção necessária |
|---|---|---|
| Simples Nacional | Retorna "optante Anexo III" | Empresa está no Lucro Real |
| e-CAC | Retorna "situação regular" | Deveria retornar "não sincronizado" |
| FGTS/INSS | Não marca como "cálculo local" | Adicionar `fonte: "calculo_local"` |
| Receita Federal | Retorna 500 | Tratar erro gracefully |

---

## 6. ARQUITETURA SOAP VALIDADA

Os parâmetros abaixo foram validados contra o webservice real do governo e devem ser reutilizados em qualquer transmissão futura:

```python
# ENVELOPE SOAP — eSocial
NAMESPACE_ENVIO_LOTE = "http://www.esocial.gov.br/schema/lote/eventos/envio/v1_1_1"
NAMESPACE_SERVICO = "http://www.esocial.gov.br/servicos/empregador/lote/eventos/envio/v1_1_1"
SOAP_ACTION_ENVIAR = "http://www.esocial.gov.br/servicos/empregador/lote/eventos/envio/v1_1_0/ServicoEnviarLoteEventos/EnviarLoteEventos"
URL_PRODUCAO_RESTRITA = "https://webservices.producaorestrita.esocial.gov.br/servicos/empregador/enviarloteeventos/WsEnviarLoteEventos.svc"

# CONSULTA STATUS
NAMESPACE_CONSULTA = "http://www.esocial.gov.br/schema/lote/eventos/envio/consulta/retornoProcessamento/v1_0_0"
SOAP_ACTION_CONSULTAR = "http://www.esocial.gov.br/servicos/empregador/lote/eventos/envio/consulta/retornoProcessamento/v1_1_0/ServicoConsultarLoteEventos/ConsultarLoteEventos"
URL_CONSULTA = "https://webservices.producaorestrita.esocial.gov.br/servicos/empregador/consultarloteeventos/WsConsultarLoteEventos.svc"

# EVENTO S-1000
NAMESPACE_EVT = "http://www.esocial.gov.br/schema/evt/evtInfoEmpregador/v_S_01_03_00"
LEIAUTE_VERSAO = "S-1.3"  # v_S_01_03_00

# ASSINATURA
CANONICALIZATION = "http://www.w3.org/TR/2001/REC-xml-c14n-20010315"  # NÃO exclusiva
SIGNATURE_METHOD = "rsa-sha256"
DIGEST_METHOD = "sha256"
REFERENCE_URI = ""  # Vazia — documento inteiro
SIGNATURE_POSITION = "sibling do evtXXX, child do <eSocial>"

# IDENTIFICAÇÃO
nrInsc_EMPREGADOR = "35710481"  # 8 dígitos (raiz CNPJ)
nrInsc_TRANSMISSOR = "35710481000103"  # 14 dígitos (CNPJ completo)
nrInsc_NO_ID = "35710481000000"  # Raiz padded zeros até 14

# NFS-e NACIONAL
NFSE_API_URL = "https://sefin.nfse.gov.br/sefinnacional/"
NFSE_AUTH = "mTLS com certificado A1 ICP-Brasil"
NFSE_FORMATO = "XML DPS assinado → GZip → Base64 → POST"
```

---

## 7. PRÓXIMO PROMPT SUGERIDO

### Opção A — Completar eSocial (S-2200 dos funcionários)
```
Missão: Popular dados faltantes dos 52 funcionários e transmitir S-2200.
Pré-requisito: Jordan fornecer data_nascimento, sexo, estado_civil.
Resultado: 52 admissões cadastradas no eSocial.
```

### Opção B — NFS-e Nacional real
```
Missão: Corrigir URLs, implementar XML DPS, emitir NFS-e real.
Pré-requisito: Nenhum (certificado A1 + API já validados).
Resultado: Emissão automatizada de NFS-e pelo portal nacional.
```

### Opção C — EFD-Reinf R-1000
```
Missão: Implementar transmissão SOAP para Reinf usando padrão do eSocial.
Pré-requisito: Nenhum (mesmo padrão SOAP+mTLS já funciona).
Resultado: R-1000 transmitido, base para R-2010 (serviços tomados).
```

### Opção D — Corrigir dados falsos
```
Missão: Eliminar hardcodes falsos nos endpoints gov.
Pré-requisito: Nenhum.
Resultado: Endpoints honestos — "não sincronizado" em vez de "regular".
```

---

## 8. ARQUIVOS MODIFICADOS

```
backend/modules/government_integrations/core/esocial_transmitter.py
  - build_event_id(): CNPJ raiz padded zeros
  - build_s1000_empregador(): Schema S-1.3 (sem nmRazao, natJurid, contato)
  - _build_soap_envelope(): Double-wrap correto
  - transmit(): SOAP+mTLS real com requests
  - check_status(): Consulta real ao webservice
  - _extract_protocol(), _extract_error(): Parsing de resposta gov

backend/modules/government_integrations/core/xml_signer.py
  - DEFAULT_CONFIGS[ESOCIAL]: C14N normal (não exclusiva)
  - _insert_signature(): Signature como sibling no <eSocial>
  - sign_event(): URI vazia (documento inteiro)

backend/modules/government_integrations/controllers/esocial_controller.py
  - POST /esocial/transmitir-s1000: Endpoint de transmissão real
  - GET /esocial/gaps-funcionarios: Verificação de dados para S-2200
```

---

*Gerado em 2026-03-24 — Conecta PRO v2.0.0*
