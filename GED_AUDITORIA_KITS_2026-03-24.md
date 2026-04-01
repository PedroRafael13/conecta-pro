# AUDITORIA GED — MONTAGEM AUTOMATICA DE KITS DOCUMENTAIS
# Data: 2026-03-24 | Auditor: Claude Opus 4.6

## 1. INVENTARIO COMPLETO

### Endpoints Funcionando (8/12)
| Status | Endpoint | Funcao |
|--------|----------|--------|
| 200 | GET /ged/documents | Lista documentos GED |
| 200 | GET /ged/folders | Lista pastas |
| 200 | GET /ged/dashboard | Metricas GED consolidadas |
| 200 | GET /ged/kits | Lista kits com filtros |
| 200 | POST /ged/auto-assemble | Monta kits automaticamente |
| 200 | GET /document-kits | Lista kits template |
| 200 | GET /document-kits/templates | Templates disponiveis |
| 200 | GET /document-kits-operational/condominiums | Condominios com funcionarios |
| 200 | GET /financial/nfse | 27 NFS-e reais |
| 200 | GET /financial/nfse/dashboard | Dashboard faturamento |
| 200 | GET /financial/headcount | Headcount por cliente |
| 200 | GET /financial/bi/dashboard | KPIs + fiscal |

### Endpoints Ausentes (nao registrados no router)
| Status | Endpoint | Motivo |
|--------|----------|--------|
| 404 | GET /ged/tags | Router nao registrado (import circular) |
| 404 | GET /ged/shares | Router nao registrado |
| 404 | GET /ged/signatures | Router nao registrado |
| 404 | GET /ged/versions | Router nao registrado |

### Banco de Dados — Tabelas com Dados
| Tabela | Registros | Descricao |
|--------|-----------|-----------|
| ged_kit_documents | 351 | Documentos dentro dos kits |
| ged_document_kits | 14 | Kits mensais (14 clientes x mar/2026) |
| ged_clients | 14 | Clientes GED cadastrados |
| ged_folders | 16 | Pastas organizacionais |
| ged_document_tags | 15 | Tags do sistema |
| ged_documents | 3 | Documentos avulsos |
| ged_document_versions | 3 | Versoes de documentos |
| document_kits | 4 | Templates de kit (Admissao, Demissao, Afastamento, Mensal) |
| document_kit_items | 29 | Itens dos templates |
| nfses | 27 | NFS-e reais jan+fev 2026 |
| ged_contracheques | 1 | Contracheque teste |

## 2. ESTADO ATUAL DOS KITS

### 14 kits criados para marco/2026
| Cliente | Funcionarios | Documentos | Completude | Status |
|---------|-------------|-----------|------------|--------|
| Bellavile (d387d8aa) | 12 | 77 | 6.49% | em_montagem |
| River Park (9459bb4f) | 31 | 191 | 2.62% | em_montagem |
| Conecta Mais (283b366c) | 3 | 83 | 6.02% | enviado |
| Ideal Flores (4db583b6) | 0 | 0 | 0% | em_montagem |
| Mirante (130186bf) | 0 | 0 | 0% | em_montagem |
| Laranjeiras (e55f6f4c) | 0 | 0 | 0% | em_montagem |
| Prime Arena (52958919) | 0 | 0 | 0% | em_montagem |
| Villa Fiori (14809ac8) | 0 | 0 | 0% | em_montagem |
| Villa Passaros (4909237d) | 0 | 0 | 0% | em_montagem |
| Michelangelo (02d784d5) | 0 | 0 | 0% | em_montagem |
| Gelain (8199960d) | 0 | 0 | 0% | em_montagem |
| Parise (d4dd6c53) | 0 | 0 | 0% | em_montagem |
| Life Centro (4a9aa6a6) | 0 | 0 | 0% | em_montagem |
| Green Hills (b4a13504) | 0 | 0 | 0% | em_montagem |

PROBLEMA: 11 de 14 kits tem 0 documentos — o auto-assemble so populou
3 kits (Bellavile, River Park, Conecta Mais) porque posts.client_id
foi relinkado mas o backend no container ainda usa os IDs antigos.

### Composicao dos 351 documentos coletados
| Tipo | Quantidade | Assinados | Funcionarios |
|------|-----------|-----------|--------------|
| contracheque | 56 | 0 | 40 |
| folha_ponto | 56 | 0 | 40 |
| comprovante_vt | 56 | 0 | 40 |
| comprovante_va | 56 | 0 | 40 |
| comprovante_vr | 56 | 0 | 40 |
| escala_mes | 56 | 0 | 40 |
| cnd_federal | 3 | 3 | — |
| cnd_estadual | 3 | 3 | — |
| cnd_municipal | 3 | 3 | — |
| crf_fgts | 3 | 3 | — |
| cndt_trabalhista | 3 | 3 | — |

## 3. FLUXO DE MONTAGEM ATUAL

### O que o auto-assemble faz HOJE:
```
POST /ged/auto-assemble?reference_month=2026-03-01
  |
  v
KitBuilderService.auto_build_all_kits(2026-03-01)
  |
  v  Para cada GED Client:
  |    1. get_employees_for_client(client_id)
  |       → Posts com client_id → Allocations ativas → employee_ids
  |    2. build_kit_for_client(client_id, 2026-03-01)
  |       → Cria GedDocumentKit (status: em_montagem)
  |       → Para cada funcionario:
  |          - Contracheque (PLACEHOLDER path)
  |          - Folha de Ponto (PLACEHOLDER path)
  |          - Comprovante VT (PLACEHOLDER path)
  |          - Comprovante VA (PLACEHOLDER path)
  |          - Comprovante VR (PLACEHOLDER path)
  |          - Escala do Mes (PLACEHOLDER path)
  |       → Para a empresa (1x):
  |          - CND Federal (PLACEHOLDER)
  |          - CND Estadual (PLACEHOLDER)
  |          - CND Municipal (PLACEHOLDER)
  |          - CRF FGTS (PLACEHOLDER)
  |          - CNDT Trabalhista (PLACEHOLDER)
  |    3. Recalcula completion_percentage
  v
  Retorna: { kits_created: 3, total_documents: 351 }
```

### CRITICO: Todos sao PLACEHOLDERS
- file_path = "documents/dp/contracheques/2026-03/UUID.pdf"
- O arquivo PDF NAO EXISTE no storage
- completion_percentage conta registros, nao arquivos reais
- is_signed = false para todos exceto CNDs

## 4. O QUE FALTA NO KIT

### Documentos que DEVERIAM estar no kit mas NAO estao:
| Documento | Prioridade | Fonte | Status |
|-----------|-----------|-------|--------|
| NFS-e do mes | CRITICA | Tabela nfses | Nao coletada |
| GFIP/SEFIP paga | ALTA | Fiscal | Nao coletada |
| GRF FGTS paga | ALTA | Fiscal | Nao coletada |
| GPS INSS paga | ALTA | Fiscal | Nao coletada |
| ASO periodico | MEDIA | Saude ocupacional | Nao integrado |
| Advertencias/Suspensoes | MEDIA | Operacional | Nao integrado |
| Atestados medicos | MEDIA | RH | Nao integrado |
| Comprovante ferias | MEDIA | RH | Nao integrado |
| Documentos rescisao | MEDIA | RH | Nao integrado |
| Relatorio de ocorrencias | BAIXA | Operacional | Nao integrado |
| Certificados treinamento | BAIXA | Treinamento | Nao integrado |
| Comprovante equipamento | BAIXA | Patrimonio | Nao integrado |

### Funcionalidades de entrega ausentes:
| Feature | Status |
|---------|--------|
| Gerar ZIP do kit | Campo existe, nao implementado |
| Upload Google Drive | Campo existe, nao implementado |
| Envio WhatsApp | Pagina existe, Evolution API nao conecta |
| Envio email com anexo | Endpoint existe mas nao testado |
| Portal do cliente visualizar | Portal existe, kit nao linkado |
| Assinatura digital | Modelo existe, fluxo nao implementado |

## 5. AUTOMACOES ATIVAS

| Automacao | Schedule | Status |
|-----------|----------|--------|
| Celery Beat: ged.sync_cnds | Diario | ATIVO (worker operacional) |
| Celery Beat: ged.auto_collect_documents | Dia 1 as 02:00 | ATIVO |
| Cron: gerar_kits_mensais.sh | Dia 1 as 02:00 | ATIVO |
| APScheduler: kit monthly generator | Dia 1 as 02:00 | BUG (event loop) |
| Event: on_payroll_closed | Apos folha | CODIGO OK, sem trigger |
| Event: on_cnd_renewed | Apos CND renovar | CODIGO OK, sem trigger |

## 6. STORAGE

| Local | Arquivos | Descricao |
|-------|----------|-----------|
| /opt/conecta-pro/storage/ged/ | 0 | Vazio (storage planejado) |
| /opt/conecta-pro/uploads/ged/ | 4 | PDFs de teste |
| Container /app/uploads/ged/ | 4 | PDFs de teste no container |

CRITICO: Storage vazio — kits tem placeholders mas 0 PDFs reais

## 7. GAPS PARA MONTAGEM 100% AUTOMATICA

### Nivel 1 — Critico (sem isso o kit nao serve)
1. Gerar PDFs reais de contracheque a partir dos dados de folha
2. Gerar PDFs de folha de ponto a partir dos turnos/shifts
3. Incluir NFS-e do mes no kit (ja existe na tabela nfses)
4. Incluir guias FGTS/INSS pagas
5. Popular todos os 14 kits (11 estao com 0 documentos — relinkar posts)

### Nivel 2 — Importante (kit incompleto sem isso)
6. Gerar PDF da escala mensal a partir dos dados de scale
7. Incluir certidoes reais (download automatico dos portais gov)
8. Assinatura digital dos documentos
9. ZIP do kit para download/envio

### Nivel 3 — Desejavel (valor agregado)
10. Upload automatico Google Drive
11. Envio WhatsApp via Evolution API
12. Notificacao push ao cliente
13. Aprovacao no Portal do Cliente
14. Historico de versoes

## 8. SCORE ATUAL E ROADMAP

### Score: 5/10

| Aspecto | Score | Justificativa |
|---------|-------|---------------|
| Estrutura de codigo | 9/10 | 73 arquivos, bem organizado |
| Endpoints API | 7/10 | 8/12 funcionam, 4 import circular |
| Dados no banco | 6/10 | 351 placeholders, 0 PDFs reais |
| Montagem automatica | 4/10 | Funciona mas cria placeholders |
| Storage | 1/10 | 0 arquivos reais |
| Entrega ao cliente | 2/10 | ZIP/Drive/WhatsApp nao implementados |
| Automacao | 7/10 | Cron + Celery Beat ativos |
| Frontend | 6/10 | Paginas existem, parcialmente funcionais |

### Roadmap para 10/10
| Fase | Esforco | Impacto |
|------|---------|---------|
| 1. Relinkar posts + re-executar auto-assemble | 1h | Popula 14 kits |
| 2. Integrar NFS-e nos kits | 2h | Documento critico |
| 3. Gerar PDFs reais (contracheque, ponto, escala) | 8h | Transforma placeholder em real |
| 4. Download automatico CNDs dos portais | 4h | Certidoes reais |
| 5. ZIP export do kit | 2h | Entrega funcional |
| 6. Envio email com kit | 2h | Notificacao ao cliente |
| 7. Portal do cliente visualizar kit | 4h | Self-service |
| 8. WhatsApp notificacao | 2h | Apos DNS resolver |

## 9. FLUXO IDEAL (dia 1 do mes)

```
02:00 — Celery Beat dispara ged.auto_collect_documents
  |
  v
  1. Para cada GED Client com funcionarios:
     a. Gerar contracheques PDF (dados da folha)
     b. Gerar folhas de ponto PDF (dados dos turnos)
     c. Gerar escala PDF (dados do scale)
     d. Copiar NFS-e do mes anterior
     e. Copiar certidoes validas
     f. Copiar guias FGTS/INSS pagas
  |
  v
  2. Montar kit:
     a. Criar GedDocumentKit (status: em_montagem)
     b. Associar todos documentos (file_path real)
     c. Calcular completion_percentage
     d. Se 100%: status → completo
  |
  v
  3. Empacotar:
     a. Gerar ZIP do kit
     b. Upload para Google Drive (opcional)
  |
  v
  4. Entregar:
     a. Enviar email com link/ZIP ao cliente
     b. Enviar WhatsApp notificacao
     c. Disponibilizar no Portal do Cliente
     d. Status: enviado
  |
  v
  5. Cliente confere:
     a. Login no portal
     b. Visualizar documentos
     c. Aprovar kit → status: aprovado
     d. Solicitar correcao → status: em_montagem
  |
  v
  6. Finalizar:
     a. Kit aprovado = liberacao pagamento
     b. Log de auditoria
     c. Arquivo morto apos 12 meses
```
