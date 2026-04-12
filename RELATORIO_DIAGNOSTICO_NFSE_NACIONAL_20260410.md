# Relatório de Diagnóstico — NFS-e Padrão Nacional
**Data:** 2026-04-10
**Auditor:** Claude Sonnet 4.6
**Script:** PASSO B — Diagnóstico NFS-e Nacional (core + service + controller + swagger)

---

## Resumo Executivo

A integração NFS-e Padrão Nacional está **parcialmente implementada** — endpoints registrados e acessíveis, geração de XML DPS funcional em modo `dry_run`, mas com **4 bugs** que impedem a transmissão real. Como Manaus ainda não migrou para o Padrão Nacional, os bugs são não-críticos agora, mas devem ser corrigidos antes da migração.

---

## 1. Arquivos Inspecionados

| Arquivo | Caminho |
|---|---|
| Core | `modules/government_integrations/core/nfse_nacional.py` |
| Service | `modules/government_integrations/services/nfse_nacional_service.py` |
| Controller | `modules/government_integrations/controllers/nfse_nacional_controller.py` |
| Swagger Portal Nacional | `https://sefin.nfse.gov.br/sefinnacional/swagger-ui/index.html` (inacessível do VPS) |

---

## 2. Estrutura e Registro

| Item | Status | Detalhe |
|---|---|---|
| `nfse_nacional.py` (core) | ✅ Existe | 2 classes: `NFSeNacionalManager` (sync) + `NFSeNacionalClient` (async/httpx) |
| `nfse_nacional_service.py` | ✅ Existe | Usa `NFSeNacionalManager` (sync) |
| `nfse_nacional_controller.py` | ✅ Existe | 10 endpoints REST implementados |
| Registro no agregador | ✅ | `government_integrations/controllers/__init__.py` linha 71 |
| Registro no main | ✅ | Via `government_integrations_router` → `fiscal_contabil/__init__.py` linha 25 |
| URL base da API | ✅ | `https://sefin.nfse.gov.br/sefinnacional` |
| Swagger `sefin.nfse.gov.br` | ❌ | Não retornou conteúdo (inacessível do VPS) |

### Endpoints disponíveis

| Método | URL | Status |
|---|---|---|
| `POST` | `/api/v1/nfse-nacional/emitir` | ✅ (dry_run OK, transmissão real falha — Bug 1) |
| `GET` | `/api/v1/nfse-nacional/consultar/dps/{id}` | ✅ (retorna "preparacao") |
| `GET` | `/api/v1/nfse-nacional/consultar/nfse/{numero}` | ✅ (retorna "preparacao") |
| `POST` | `/api/v1/nfse-nacional/cancelar` | ✅ (retorna "preparacao") |
| `POST` | `/api/v1/nfse-nacional/substituir` | ✅ (retorna "preparacao") |
| `GET` | `/api/v1/nfse-nacional/eventos/{numero}` | ✅ (retorna "preparacao") |
| `GET` | `/api/v1/nfse-nacional/status` | ✅ |
| `GET` | `/api/v1/nfse-nacional/migracao/status` | ✅ |
| `GET` | `/api/v1/nfse-nacional/migracao/comparar-padroes` | ✅ |
| `GET` | `/api/v1/nfse-nacional/migracao/mapeamento-servicos` | ✅ |
| `GET` | `/api/v1/nfse-nacional/codigos-servico` | ✅ |
| `GET` | `/api/v1/nfse-nacional/info` | ✅ |

---

## 3. Fluxo de Emissão (DPS)

```
POST /nfse-nacional/emitir
    ↓
NFSeNacionalService.emitir_dps()
    ↓
NFSeNacionalManager._build_dps_xml()  → XML DPS conforme XSD Nacional
    ↓
NFSeNacionalXMLSigner.sign_nfse()     → XMLDSig sem prefixo ds: (resolve E6155)
    ↓
gzip.compress() → base64.b64encode()  → dpsXmlGZipB64
    ↓
requests.post(url, json={"dpsXmlGZipB64": ...}, cert=(cert_pem, key_pem))
    ↓
https://sefin.nfse.gov.br/sefinnacional/nfse
```

Protocolo: **REST/JSON** (não SOAP — diferente do ABRASF 2.04)
Autenticação: **mTLS** com certificado A1 ICP-Brasil

---

## 4. Bugs Identificados

### Bug 1 — CRÍTICO: PEM inexistente em `NFSeNacionalManager.emitir_dps()`

**Arquivo:** `nfse_nacional.py` ~linha 375

```python
# ATUAL (BUGADO):
cert_pem = self.certificado_path.replace(".pfx", "").replace("certificado", "a1_cert") + ".pem"
key_pem = cert_pem.replace("a1_cert", "a1_key")
# Resulta em: /app/credentials/certificates/a1_cert.pem  ← NÃO EXISTE

# CORRETO (como NFSeNacionalClient já faz):
# Usar CertificateManager para exportar cert e key para arquivos temporários .pem
```

**Impacto:** 100% das transmissões reais falham com `FileNotFoundError` ao tentar usar o certificado mTLS.

**Nota:** `NFSeNacionalClient` (classe async no mesmo arquivo) faz corretamente via `CertificateManager` + `tempfile`. O `NFSeNacionalManager` (sync) tem a implementação quebrada.

---

### Bug 2 — MÉDIO: `tpAmb` hardcoded como `"1"` (produção)

**Arquivo:** `nfse_nacional.py` ~linha 241

```python
# ATUAL (BUGADO):
tp_amb = "1"  # hardcoded — sempre produção

# CORRETO:
tp_amb = "1" if self.ambiente == AmbienteNacional.PRODUCAO else "2"
```

**Impacto:** Em homologação, o XML envia `tpAmb=1` (produção), o que pode causar rejeição ou emissão acidental em produção durante testes.

---

### Bug 3 — BAIXO: `razao_social` default errado no service

**Arquivo:** `nfse_nacional_service.py` linha 871

```python
# ATUAL (BUGADO):
self.razao_social = os.getenv("NFSE_NACIONAL_RAZAO_SOCIAL", "Conecta Plus Servicos LTDA")

# CORRETO:
self.razao_social = os.getenv("NFSE_NACIONAL_RAZAO_SOCIAL", "JORDAN SANTOS DE JESUS LTDA")
```

**Impacto:** Baixo — a env var `NFSE_NACIONAL_RAZAO_SOCIAL=JORDAN SANTOS DE JESUS LTDA` já está configurada no `.env`, então o default nunca é usado em produção.

---

### Bug 4 — FUTURO: `opSimpNac` hardcoded no XML DPS

**Arquivo:** `nfse_nacional.py` ~linha 279

```xml
<opSimpNac>2</opSimpNac>  <!-- 1=Optante, 2=Não optante -->
```

**Impacto:** A empresa está em Lucro Real em 2026, então `opSimpNac=2` (não optante) é **correto no momento**. Porém, quando migrar de volta para Simples Nacional, o valor precisará ser atualizado dinamicamente baseado em `NFSE_NACIONAL_ENVIRONMENT` ou regime tributário.

---

## 5. Comparação: NFSeManausManager × NFSeNacionalManager

| Característica | NFSeManausManager (ABRASF 2.04) | NFSeNacionalManager (Padrão Nacional) |
|---|---|---|
| Protocolo | SOAP/XML | REST/JSON |
| Documento | RPS | DPS |
| Assinatura | XMLDSig com prefixo `ds:` | XMLDSig sem prefixo (resolve E6155) |
| Compressão | Nenhuma | GZip + Base64 |
| Auth | Certificado no SOAP header | mTLS (cert_pem + key_pem) |
| URL | `nfse-prd.manaus.am.gov.br` | `sefin.nfse.gov.br/sefinnacional` |
| Status Manaus | ✅ Em uso (mas bloqueado por `detail: 2`) | ❌ Manaus não migrou ainda |

---

## 6. Variáveis de Ambiente — Status

| Variável | Valor no Container | Status |
|---|---|---|
| `NFSE_NACIONAL_CNPJ` | `35710481000103` | ✅ |
| `NFSE_NACIONAL_COD_MUNICIPIO` | `1302603` | ✅ |
| `NFSE_NACIONAL_ENVIRONMENT` | `homologacao` | ✅ |
| `NFSE_NACIONAL_RAZAO_SOCIAL` | `JORDAN SANTOS DE JESUS LTDA` | ✅ |
| `NFSE_NACIONAL_IM` | *(vazio)* | ⚠️ Fallback para `NFSE_MANAUS_IM=45177801` |
| `CERTIFICATE_PATH` | `/app/credentials/certificates/certificado.pfx` | ✅ |
| `CERTIFICATE_PASSWORD` | `Conecta123` | ✅ |

---

## 7. Status Final

```
✅ Controller registrado e endpoints acessíveis
✅ XML DPS gerado corretamente (dry_run)
✅ Assinatura XMLDSig implementada (sem prefixo ds:)
✅ Fluxo GZip + Base64 implementado
✅ Variáveis de ambiente configuradas
⚠️  Bug 1: PEM inexistente bloqueia transmissão real (mas Manaus não migrou ainda)
⚠️  Bug 2: tpAmb hardcoded como "1" (produção)
⚠️  Bug 3: razao_social default errado (irrelevante em produção com env var)
⚠️  Bug 4: opSimpNac hardcoded (correto hoje, precisará de ajuste no futuro)
⛔ Manaus ainda usa ABRASF 2.04 — Padrão Nacional não disponível
```

---

## 8. Próximos Passos

1. **Agora (opcional):** Corrigir Bug 1 (`tpAmb` + PEM path) para quando Manaus migrar
2. **Quando SEMEF anunciar migração:** Ativar `NFSE_NACIONAL_ENVIRONMENT=producao` e testar com `dry_run=true`
3. **Após habilitação SEMEF:** Transmitir DPS real para `sefin.nfse.gov.br/sefinnacional/nfse`

---

*Relatório gerado por Claude Sonnet 4.6 em 2026-04-10*
