# Relatório de Diagnóstico — NFS-e Portal Nacional
**Data:** 2026-04-10
**Auditor:** Claude Sonnet 4.6
**Script:** PASSO A — Diagnóstico NFS-e Portal Nacional

---

## Resumo Executivo

O endpoint `POST /api/v1/financial/nfse/emitir` está funcional e gera XML ABRASF 2.04 assinado digitalmente. Porém, **a emissão real falha** porque 3 itens críticos não estão configurados: senha do WebService, inscrição municipal e certificado A1 (.pfx) ausente no container.

---

## 1. Variáveis de Ambiente NFS-e

**Resultado:** Nenhuma variável `NFSE_*` está definida no `.env`.

O service opera 100% com defaults hardcoded:

| Variável | Default no Código | Status | Ação Necessária |
|---|---|---|---|
| `NFSE_MANAUS_CNPJ` | `35710481000103` | ✅ OK (correto) | Nenhuma |
| `NFSE_MANAUS_USUARIO` | `= CNPJ` | ⚠️ Provável | Confirmar com Prefeitura |
| `NFSE_MANAUS_SENHA` | `""` (vazio) | ❌ FALTANDO | **Configurar senha do WebService** |
| `NFSE_MANAUS_IM` | `""` (vazio) | ❌ FALTANDO | **Configurar: `45177801`** |
| `NFSE_MANAUS_ENVIRONMENT` | `"homologacao"` | ⚠️ Verificar | Confirmar: `homologacao` ou `producao` |
| `CERTIFICATE_PATH` | `/opt/conecta-pro/credentials/certificates/certificado.pfx` | ❌ Arquivo ausente | **Copiar o .pfx para o servidor** |
| `CERTIFICATE_PASSWORD` | `""` (vazio) | ❌ FALTANDO | **Configurar: `Conecta123`** |

---

## 2. Certificado A1 no Container

**Resultado:** O certificado `.pfx` NÃO está no container.

```
Esperado:  /app/credentials/certificates/certificado.pfx   ← NÃO EXISTE
Encontrado: /app/credentials/inter/Inter_API_Certificado.crt ← É do banco Inter
```

O certificado encontrado (`Inter_API_Certificado.crt`) é o certificado da integração bancária com o Banco Inter — **não é o certificado A1 da empresa** para emissão fiscal.

O certificado A1 necessário é o da empresa **Jordan Santos de Jesus Ltda (CNPJ 35.710.481/0001-03)**, arquivo `.pfx` com senha `Conecta123`.

---

## 3. Arquivos de Integração Encontrados

### 3a. NFS-e Manaus (ABRASF 2.04) — **ATIVO**

| Arquivo | Caminho |
|---|---|
| Core | `modules/government_integrations/core/nfse_manaus.py` |
| Service | `modules/government_integrations/services/nfse_manaus_service.py` |
| Controller | `modules/government_integrations/controllers/nfse_manaus_controller.py` |
| Schema | `modules/government_integrations/schemas/nfse_manaus.py` |
| Extractor | `modules/government_integrations/extractors/nfse/manaus_extractor.py` |
| Sync | `modules/government_integrations/sync/municipal/nfse_manaus_sync.py` |

**URLs do WebService:**
```
Produção:    https://nfse-prd.manaus.am.gov.br/nfse/servlet
Homologação: https://nfse-hml.manaus.am.gov.br/nfse/servlet
WSDL Prod:   https://nfse-prd.manaus.am.gov.br/nfse/servlet/arecepcionarloterps?wsdl
WSDL Hml:    https://nfse-hml.manaus.am.gov.br/nfse/servlet/arecepcionarloterps?wsdl
Login Prod:  https://nfse-prd.manaus.am.gov.br/nfse/servlet/hlogin
```

### 3b. NFS-e Portal Nacional — **EM PREPARAÇÃO (não usar ainda)**

| Arquivo | Caminho |
|---|---|
| Core | `modules/government_integrations/core/nfse_nacional.py` |
| Service | `modules/government_integrations/services/nfse_nacional_service.py` |
| Controller | `modules/government_integrations/controllers/nfse_nacional_controller.py` |
| Sync | `modules/government_integrations/sync/municipal/nfse_nacional_sync.py` |

**URLs do Portal Nacional:**
```
Produção/Homologação: https://sefin.nfse.gov.br/sefinnacional
Portal:               https://www.nfse.gov.br/EmissorNacional
Swagger:              https://www.nfse.gov.br/swagger/contribuintesissqn/
```

> **Nota do próprio código:** *"O Padrão Nacional ainda não está disponível em Manaus. Use NFSeManausService para emissões atuais."*

---

## 4. Causa Raiz do Erro Atual

O erro `"Error reading enf:RecepcionarLoteRps.Execute"` retornado pela Prefeitura de Manaus tem **3 causas simultâneas:**

### Causa 1 — Senha WebService vazia
```python
self.senha = os.getenv("NFSE_MANAUS_SENHA", "")  # → ""
```
A Prefeitura de Manaus exige autenticação com senha no WebService. Com senha vazia, a requisição é rejeitada.

### Causa 2 — Inscrição Municipal vazia
```python
self.inscricao_municipal = os.getenv("NFSE_MANAUS_IM", "")  # → ""
```
O XML gerado terá `<InscricaoMunicipal/>` vazio. A IM correta é `45177801`.

### Causa 3 — Certificado .pfx ausente
```
/app/credentials/certificates/certificado.pfx → NÃO EXISTE
```
Sem o `.pfx`, a assinatura digital usa um fallback ou falha silenciosamente, gerando XML inválido para a Prefeitura.

---

## 5. O Que Funciona Hoje

| Item | Status |
|---|---|
| Endpoint `POST /api/v1/financial/nfse/emitir` registrado | ✅ |
| HTTP 200 com `nfse_id` válido | ✅ |
| HTTP 422 para payload incompleto | ✅ |
| HTTP 404 para `nfse_id` inexistente | ✅ |
| Geração do XML ABRASF 2.04 | ✅ |
| Assinatura digital `ds:Signature` no XML | ✅ |
| CNPJ prestador `35710481000103` no XML | ✅ |
| Envio ao WebService da Prefeitura | ✅ (chega, mas é rejeitado) |
| Emissão real aprovada pela Prefeitura | ❌ (3 causas acima) |

---

## 6. Plano de Correção

Para a emissão real funcionar, executar nesta ordem:

### Passo 1 — Copiar o certificado A1 para o servidor
```bash
# No MacBook local:
scp /caminho/para/certificado.pfx root@srv1134814.hstgr.cloud:/opt/conecta-pro/credentials/certificates/certificado.pfx
```

### Passo 2 — Adicionar variáveis ao .env
```bash
# Adicionar no /opt/conecta-pro/backend/.env:
NFSE_MANAUS_CNPJ=35710481000103
NFSE_MANAUS_USUARIO=35710481000103
NFSE_MANAUS_SENHA=<senha_do_webservice_prefeitura>
NFSE_MANAUS_IM=45177801
NFSE_MANAUS_ENVIRONMENT=homologacao
CERTIFICATE_PATH=/opt/conecta-pro/credentials/certificates/certificado.pfx
CERTIFICATE_PASSWORD=Conecta123
```

### Passo 3 — Copiar certificado para o container e reiniciar
```bash
docker exec -u root conecta-pro-backend mkdir -p /app/credentials/certificates
docker cp /opt/conecta-pro/credentials/certificates/certificado.pfx \
  conecta-pro-backend:/app/credentials/certificates/certificado.pfx
docker restart conecta-pro-backend
```

### Passo 4 — Testar emissão real
```bash
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nfse_id": "a7c6f9cb-c5f4-414b-8bb8-f7261704764b"}' \
  "http://127.0.0.1:8080/api/v1/financial/nfse/emitir" | python3 -m json.tool
```

---

## 7. Informações Necessárias do Usuário

| # | Item | Observação |
|---|---|---|
| 1 | Senha do WebService da Prefeitura de Manaus | Cadastrada no portal nfse.manaus.am.gov.br |
| 2 | Arquivo `.pfx` do certificado A1 | Senha já conhecida: `Conecta123` |
| 3 | Ambiente: `homologacao` ou `producao` | Recomendado testar em homologação primeiro |

---

*Relatório gerado por Claude Sonnet 4.6 em 2026-04-10*
