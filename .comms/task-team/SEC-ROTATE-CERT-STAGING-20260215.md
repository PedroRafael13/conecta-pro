# SEC-ROTATE-CERT-STAGING — 2026-02-15

## Motivo
Rotação de certificados staging (Inter, Cora, A1) como parte do plano de segurança P0.

---

## 0. Preparação — CONCLUÍDO

### Diretório seguro
```bash
$ chmod 700 /opt/conecta-secrets/certificates
$ mkdir -p /opt/conecta-secrets/certificates/{inter,cora,a1}
$ chmod 700 /opt/conecta-secrets/certificates/{inter,cora,a1}
```

### Estrutura resultante
```
/opt/conecta-secrets/certificates/   (700 root)
├── inter/                           (700 root) — VAZIO, aguardando Jordan
├── cora/                            (700 root) — VAZIO, aguardando Jordan
├── a1/                              (700 root) — VAZIO, aguardando Jordan
├── a1_key.pem                       (600) — existente (produção)
├── certificado.pfx                  (600) — existente (produção)
├── cora_api.key                     (600) — existente (produção)
├── inter_api.key                    (600) — existente (produção)
└── inter_key.pem                    (600) — existente (produção)
```

### .env atualizado
```
CERTIFICATE_PATH_STAGING=/opt/conecta-secrets/certificates/a1/certificado.pfx
CERTIFICATE_PASSWORD_STAGING=PENDENTE_JORDAN_DEFINIR
```

---

## 1. Rotação Inter (staging) — PENDENTE JORDAN

**Ação necessária:**
1. Acessar painel Inter → gerar/baixar novo certificado e chave para staging
2. Salvar no servidor:
   - `/opt/conecta-secrets/certificates/inter/inter_key.pem`
   - `/opt/conecta-secrets/certificates/inter/inter_api.key`
   - `/opt/conecta-secrets/certificates/inter/inter_cert.pem`
   - `/opt/conecta-secrets/certificates/inter/inter_api.crt`
3. Executar: `chmod 600 /opt/conecta-secrets/certificates/inter/*`

---

## 2. Rotação Cora (staging) — PENDENTE JORDAN

**Ação necessária:**
1. Acessar painel Cora → gerar nova chave/cert
2. Salvar no servidor:
   - `/opt/conecta-secrets/certificates/cora/cora_api.key`
   - `/opt/conecta-secrets/certificates/cora/cora_api.crt`
3. Executar: `chmod 600 /opt/conecta-secrets/certificates/cora/*`

---

## 3. Rotação A1 (staging) — PENDENTE JORDAN

**Ação necessária:**
1. Emitir novo certificado A1 (.pfx) com nova senha
2. Salvar no servidor:
   - `/opt/conecta-secrets/certificates/a1/certificado.pfx`
3. Atualizar `/opt/conecta-pro/.env`:
   - `CERTIFICATE_PASSWORD_STAGING=<NOVA_SENHA_DO_PFX>`
4. Executar: `chmod 600 /opt/conecta-secrets/certificates/a1/*`

---

## 4. Pós-upload (executar após Jordan colocar os arquivos)

```bash
# Verificar permissões
chmod 600 /opt/conecta-secrets/certificates/inter/*
chmod 600 /opt/conecta-secrets/certificates/cora/*
chmod 600 /opt/conecta-secrets/certificates/a1/*

# Reiniciar backend staging
cd /opt/conecta-pro
docker compose -f docker-compose.staging.yml --env-file .env up -d --force-recreate backend-staging

# Validar health
docker exec conecta-pro-backend-staging curl -sf http://localhost:8080/health
```

---

## 5. Validação atual

### Health check backend staging
```bash
$ docker exec conecta-pro-backend-staging curl -sf http://localhost:8080/health
{"status":"healthy","app":"Conecta PRO","version":"2.0.0","environment":"staging"}
```

Backend saudável. Módulos de integração (Inter/Cora/NFS-e) não testáveis sem os certificados novos.

---

## 6. Status Geral

| Componente | Status | Bloqueio |
|-----------|--------|----------|
| Diretório seguro | OK (700) | — |
| Subdiretórios | OK (inter/cora/a1, 700) | — |
| .env staging vars | OK (paths + password placeholder) | — |
| Certificados Inter | PENDENTE | Jordan: gerar no painel Inter |
| Certificados Cora | PENDENTE | Jordan: gerar no painel Cora |
| Certificado A1 | PENDENTE | Jordan: emitir novo .pfx |
| Backend staging | HEALTHY | — |
| Validação integração | BLOQUEADA | Depende dos certificados |

---

## Metadados
- **Executor:** Claude Opus 4.6
- **Timestamp:** 2026-02-15T16:18Z
- **Auditado por:** Codex 5.3
- **Status:** PARCIAL — infraestrutura pronta, aguardando certificados do Jordan
