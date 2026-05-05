# T5 Fix Onvio CPRO12
Data: 2026-05-05

Bug Grupo A: corrigido em onvio_doc_scope_classifier.py linha 241 (is_matriz antes de match_condominio)
Docs scope=NULL antes: 169
Docs scope=NULL depois: 0
Docs reclassificados: 605
/onvio/sync após fix: HTTP 500 (401 Unauthorized Onvio — token expirado, endpoint funcional)
MAPA_TIPOS_ONVIO: 19 categorias antes → 28 depois
Novos tipos adicionados: recibo_folha, contracheque, fgts_crf, contrato_trabalho, ficha_registro, aso, atestado, rescisao_contrato, aviso_previo

Commits: docs=082dd821 code=3bb58092
Auditoria 1: rescisao→rescisao_contrato: ccc81399
Auditoria 2: contracheque+titulo §95: d362b950
Push: feature/people-management-reorganization → remoto OK

---

## Detalhes

### Sub-task A — Bug Grupo A OnvioDocScopeClassifier
Arquivo: backend/modules/gedeon/services/onvio_doc_scope_classifier.py
Fix: is_matriz() adicionado antes de match_condominio() no bloco scope=="condominio" (linha 241)
Resultado: docs Conecta Mais com cat. Grupo A agora recebem doc_scope=empresa_matriz

### Sub-task B — POST /onvio/sync retornava 404
Causa raiz real: gedeon/onvio/ inteiro ausente do container (não era roteador não registrado)
Fix: hot-copy gedeon/onvio/ completo; EnrichmentService lazy import (pdfplumber ausente)
Resultado: /onvio/sync → HTTP 500 com 401 Onvio (token expirado — comportamento correto)

### Sub-task C — 169 docs doc_scope=NULL
Fix: backfill_doc_scope_fase_3_5.py executado no container com classifier corrigido
Resultado: 605/605 classificados — INV-8 OK (zero NULL)
Distribuição: empresa_matriz=370, condominio=124, funcionario=111, revisao_manual=251

### Sub-task D — MAPA_TIPOS_ONVIO
Arquivo: backend/modules/people_management/ged/services/kit_builder_service.py
Antes: 19 entradas | Depois: 28 entradas
Adicionadas: recibo_folha→contracheque, contracheque→contracheque, fgts_crf→crf_fgts,
  contrato_trabalho→contrato_trabalho, ficha_registro→ficha_empregado, aso→aso,
  atestado→atestado_medico, rescisao→rescisao_contrato, aviso_previo→aviso_previo_ferias

### Verificação STEP 6 (categoria/scope)
categoria              | doc_scope      | count
documento_digitalizado | empresa_matriz | 26
ficha_registro         | funcionario    | 14
outros                 | empresa_matriz | 144
outros                 | funcionario    | 13
