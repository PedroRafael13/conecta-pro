# ✅ CHECKLIST DE PROGRESSO - GOVERNMENT INTEGRATIONS

**Objetivo:** Completar cobertura de 26% para 100% (153 endpoints)
**Tempo Estimado:** 40 horas (~1 semana)
**Status:** 🔄 EM PROGRESSO

---

## 📊 PROGRESSO GERAL

```
╔════════════════════════════════════════════════════════════════╗
║  PROGRESSO GERAL                                               ║
╠════════════════════════════════════════════════════════════════╣
║  Fases Concluídas:        0 / 7                                ║
║  Endpoints Implementados: 56 / 209 (26%)                       ║
║  Tempo Investido:         0h / 40h                             ║
║  Status:                  🔄 INICIANDO                          ║
╚════════════════════════════════════════════════════════════════╝
```

**Atualizar após cada fase!**

---

## 🚀 FASE 1: ANÁLISE E SETUP (4h)

**Objetivo:** Configurar ambiente e gerar tipos TypeScript
**Tempo:** 4 horas
**Status:** ⏳ PENDENTE

### 1.1 Baixar OpenAPI Spec (30min)
- [ ] Backend está rodando (`curl http://localhost:8080/health`)
- [ ] OpenAPI completo baixado (2.28 MB)
  ```bash
  curl -s http://localhost:8080/openapi.json -o /opt/conecta-pro/docs/expansao-orval-28-01-2026/openapi-conecta-pro.json
  ```
- [ ] Arquivo validado (`jq '.paths | keys | length' openapi-conecta-pro.json`)
- [ ] Deve ter >1000 endpoints

**Checkpoint:** Arquivo `openapi-conecta-pro.json` criado com ~2.28MB

---

### 1.2 Criar Script de Extração (1h)
- [ ] Script criado: `extract-government-spec.py`
- [ ] Permissões de execução (`chmod +x`)
- [ ] Testado com sucesso
- [ ] OpenAPI filtrado gerado: `openapi-government.json`
- [ ] Tamanho reduzido: ~420KB (81.6% redução)
- [ ] 209 endpoints extraídos
- [ ] 158 schemas copiados

**Comando:**
```bash
cd /opt/conecta-pro/docs/expansao-orval-28-01-2026
python3 extract-government-spec.py
```

**Checkpoint:** Arquivo `openapi-government.json` criado

---

### 1.3 Configurar Orval (1h)
- [ ] Arquivos copiados para frontend:
  - [ ] `openapi-government.json`
  - [ ] `orval.config.government.ts`
- [ ] Orval instalado (`npm install -D orval`)
- [ ] Script adicionado ao `package.json`:
  ```json
  "orval:government": "orval --config orval.config.government.ts"
  ```
- [ ] Versão verificada (`npx orval --version`)

**Comandos:**
```bash
cd /opt/conecta-pro/frontend
cp /opt/conecta-pro/docs/expansao-orval-28-01-2026/openapi-government.json ./
cp /opt/conecta-pro/docs/expansao-orval-28-01-2026/orval.config.government.ts ./
npm install -D orval
```

**Checkpoint:** Orval configurado e pronto

---

### 1.4 Gerar Tipos (30min)
- [ ] Tipos gerados com sucesso (`npm run orval:government`)
- [ ] 24 arquivos de modelo criados em `src/types/generated/government/models/`
- [ ] 158 interfaces/types gerados
- [ ] Arquivo index.ts com exports

**Comando:**
```bash
npm run orval:government
```

**Arquivos esperados:**
- [ ] `nfse-manaus.ts`
- [ ] `nfse-nacional.ts`
- [ ] `esocial.ts`
- [ ] `sefaz.ts`
- [ ] `sped-fiscal.ts`
- [ ] `sped-contabil.ts`
- [ ] `fgts-digital.ts`
- [ ] `fgts-inss.ts`
- [ ] `efd-reinf.ts`
- [ ] `dctfweb.ts`
- [ ] `simples-nacional.ts`
- [ ] `ecac.ts`
- [ ] `cte.ts`
- [ ] `mdfe.ts`
- [ ] `nfce.ts`
- [ ] `govbr.ts`
- [ ] `certificate.ts`
- [ ] `sync.ts`
- [ ] `jobs.ts`
- [ ] `dashboard.ts`
- [ ] `extraction.ts`
- [ ] `receita-federal.ts`
- [ ] `status.ts`
- [ ] `common.ts`

**Checkpoint:** 158 tipos gerados

---

### 1.5 Validar Build (2h)
- [ ] Type check sem erros (`npm run types:check`)
- [ ] Build sem erros (`npm run build`)
- [ ] Imports funcionando
- [ ] Mutator configurado em `src/lib/api.ts`

**Checkpoint:** Build limpo

---

**✅ FASE 1 CONCLUÍDA:** ___/___/___ às ___:___
**Tempo gasto:** ___h
**Bloqueadores:** _________________________________

---

## 🔧 FASE 2: SERVICE LAYER (12h)

**Objetivo:** Implementar service completo com 209 métodos
**Tempo:** 12 horas
**Status:** ⏳ PENDENTE

### 2.1 Criar Estrutura Base (1h)
- [ ] Diretório criado: `src/lib/services/government/`
- [ ] Arquivo base: `government.ts`
- [ ] Imports dos tipos gerados
- [ ] Constante `BASE_URL = '/api/v1/government'`

**Checkpoint:** Estrutura criada

---

### 2.2 Implementar Sub-Services (10h)

#### 2.2.1 NFS-e Manaus (8 métodos) - 30min
- [ ] `emitir()`
- [ ] `consultar()`
- [ ] `cancelar()`
- [ ] `substituir()`
- [ ] `validarConexao()`
- [ ] `enviarLote()`
- [ ] `consultarLote()`
- [ ] `listarPrefeituras()`

#### 2.2.2 NFS-e Nacional (12 métodos) - 45min
- [ ] `emitir()`
- [ ] `consultar()`
- [ ] `cancelar()`
- [ ] `validarConexao()`
- [ ] `enviarLote()`
- [ ] `consultarLote()`
- [ ] `consultarPendencias()`
- [ ] `consultarConfiguracao()`
- [ ] `listarMunicipios()`
- [ ] `consultarEspecifico()`
- [ ] `validarXML()`
- [ ] `baixarPDF()`

#### 2.2.3 eSocial (3 métodos) - 15min
- [ ] `enviarEvento()`
- [ ] `consultarStatus()`
- [ ] `listarEventosSuportados()`

#### 2.2.4 SEFAZ (2 métodos) - 10min
- [ ] `emitirNFe()`
- [ ] `consultarNFe()`

#### 2.2.5 SEFAZ-AM (8 métodos) - 30min
- [ ] `emitirNFe()`
- [ ] `consultarNFe()`
- [ ] `cancelarNFe()`
- [ ] `inutilizarNumeracao()`
- [ ] `downloadXML()`
- [ ] `consultarCadastro()`
- [ ] `consultarStatusServico()`
- [ ] `validarConexao()`

#### 2.2.6 SPED Fiscal (13 métodos) - 45min
- [ ] `gerarArquivo()`
- [ ] `validarArquivo()`
- [ ] `consultarArquivos()`
- [ ] `downloadArquivo()`
- [ ] `importarArquivo()`
- [ ] `gerarEFD()`
- [ ] `validarEFD()`
- [ ] `consultarApuracao()`
- [ ] `gerarRegistrosC()`
- [ ] `gerarRegistrosD()`
- [ ] `gerarRegistrosE()`
- [ ] `consultarSaldos()`
- [ ] `exportarParaContabilidade()`

#### 2.2.7 SPED Contábil (13 métodos) - 45min
- [ ] `gerarECD()`
- [ ] `validarECD()`
- [ ] `consultarArquivos()`
- [ ] `downloadArquivo()`
- [ ] `importarLancamentos()`
- [ ] `consultarLancamentos()`
- [ ] `gerarBalancete()`
- [ ] `gerarDRE()`
- [ ] `gerarBalancoPatrimonial()`
- [ ] `consultarPlanoContas()`
- [ ] `validarPlanoContas()`
- [ ] `sincronizarContabilidade()`
- [ ] `exportarDemonstrativo()`

#### 2.2.8 FGTS Digital (11 métodos) - 40min
- [ ] `gerarGuia()`
- [ ] `consultarGuia()`
- [ ] `pagarGuiaPix()`
- [ ] `consultarPagamento()`
- [ ] `gerarRelatorioRescisao()`
- [ ] `consultarRescisoes()`
- [ ] `validarConectividade()`
- [ ] `sincronizarDados()`
- [ ] `consultarSaldos()`
- [ ] `gerarRelatorioMensal()`
- [ ] `exportarArquivos()`

#### 2.2.9 FGTS/INSS (3 métodos) - 15min
- [ ] `calcularFGTS()`
- [ ] `calcularINSS()`
- [ ] `consultarTabelas()`

#### 2.2.10 EFD-Reinf (9 métodos) - 35min
- [ ] `enviarEvento()`
- [ ] `consultarEvento()`
- [ ] `fecharCompetencia()`
- [ ] `reabrirCompetencia()`
- [ ] `consultarCompetencia()`
- [ ] `validarXML()`
- [ ] `consultarTotalizadores()`
- [ ] `gerarRelatorio()`
- [ ] `sincronizarEventos()`

#### 2.2.11 DCTFWeb (11 métodos) - 40min
- [ ] `gerarDeclaracao()`
- [ ] `consultarDeclaracao()`
- [ ] `retificarDeclaracao()`
- [ ] `consultarDebitos()`
- [ ] `gerarDARF()`
- [ ] `consultarDARF()`
- [ ] `transmitirDeclaracao()`
- [ ] `consultarRecibo()`
- [ ] `validarConexao()`
- [ ] `sincronizarDados()`
- [ ] `exportarRelatorio()`

#### 2.2.12 Simples Nacional (10 métodos) - 40min
- [ ] `consultarEnquadramento()`
- [ ] `calcularDAS()`
- [ ] `gerarDAS()`
- [ ] `consultarDAS()`
- [ ] `pagarDAS()`
- [ ] `calcularFatorR()`
- [ ] `transmitirPGDAS()`
- [ ] `consultarPGDAS()`
- [ ] `retificarPGDAS()`
- [ ] `consultarOpcao()`

#### 2.2.13 e-CAC (9 métodos) - 35min
- [ ] `consultarSituacaoFiscal()`
- [ ] `listarCertidoes()`
- [ ] `solicitarCertidao()`
- [ ] `downloadCertidao()`
- [ ] `consultarDebitos()`
- [ ] `consultarParcelamentos()`
- [ ] `validarCertidao()`
- [ ] `consultarRestituicoes()`
- [ ] `validarConexao()`

#### 2.2.14 CT-e (10 métodos) - 40min
- [ ] `emitir()`
- [ ] `consultar()`
- [ ] `cancelar()`
- [ ] `corrigir()`
- [ ] `inutilizar()`
- [ ] `downloadXML()`
- [ ] `downloadPDF()`
- [ ] `consultarStatus()`
- [ ] `validarXML()`
- [ ] `consultarEvento()`

#### 2.2.15 MDF-e (14 métodos) - 50min
- [ ] `emitir()`
- [ ] `consultar()`
- [ ] `encerrar()`
- [ ] `cancelar()`
- [ ] `incluirCondutor()`
- [ ] `incluirDFe()`
- [ ] `consultarNaoEncerrados()`
- [ ] `downloadXML()`
- [ ] `downloadPDF()`
- [ ] `consultarStatus()`
- [ ] `validarXML()`
- [ ] `consultarEvento()`
- [ ] `registrarPassagem()`
- [ ] `consultarViagem()`

#### 2.2.16 NFC-e (9 métodos) - 35min
- [ ] `emitir()`
- [ ] `consultar()`
- [ ] `cancelar()`
- [ ] `inutilizar()`
- [ ] `downloadXML()`
- [ ] `downloadDANFE()`
- [ ] `consultarStatus()`
- [ ] `validarConexao()`
- [ ] `sincronizarContingencia()`

#### 2.2.17 GOV.BR (12 métodos) - 45min
- [ ] `autenticar()`
- [ ] `renovarToken()`
- [ ] `consultarUsuario()`
- [ ] `consultarPermissoes()`
- [ ] `consultarEmpresasVinculadas()`
- [ ] `consultarProcuracoes()`
- [ ] `validarProcuracao()`
- [ ] `consultarServicosDisponiveis()`
- [ ] `consultarNotificacoes()`
- [ ] `marcarNotificacaoLida()`
- [ ] `consultarHistoricoAcessos()`
- [ ] `logout()`

#### 2.2.18 Certificado Digital (7 métodos) - 25min
- [ ] `upload()`
- [ ] `listar()`
- [ ] `consultar()`
- [ ] `validar()`
- [ ] `excluir()`
- [ ] `consultarExpiracao()`
- [ ] `renovar()`

#### 2.2.19 Sincronização (16 métodos) - 1h
- [ ] `executar()`
- [ ] `executarTodos()`
- [ ] `consultarStatus()`
- [ ] `consultarHistorico()`
- [ ] `pausar()`
- [ ] `retomar()`
- [ ] `cancelar()`
- [ ] `configurarAgendamento()`
- [ ] `listarAgendamentos()`
- [ ] `atualizarAgendamento()`
- [ ] `excluirAgendamento()`
- [ ] `consultarJobAtivo()`
- [ ] `listarJobsAtivos()`
- [ ] `consultarEstatisticas()`
- [ ] `configurarEmpresa()`
- [ ] `consultarConfiguracaoEmpresa()`

#### 2.2.20 Jobs (8 métodos) - 30min
- [ ] `listar()`
- [ ] `consultar()`
- [ ] `criar()`
- [ ] `atualizar()`
- [ ] `executar()`
- [ ] `pausar()`
- [ ] `cancelar()`
- [ ] `excluir()`

#### 2.2.21 Dashboard (6 métodos) - 25min
- [ ] `consultarResumo()`
- [ ] `consultarMetricas()`
- [ ] `consultarExtracoesRecentes()`
- [ ] `consultarErros()`
- [ ] `consultarDesempenho()`
- [ ] `consultarStatusServicos()`

#### 2.2.22 Extração (10 métodos) - 40min
- [ ] `iniciarExtracao()`
- [ ] `consultarExtracao()`
- [ ] `listarExtracoes()`
- [ ] `pausarExtracao()`
- [ ] `retomarExtracao()`
- [ ] `cancelarExtracao()`
- [ ] `consultarProgresso()`
- [ ] `downloadResultado()`
- [ ] `consultarLogs()`
- [ ] `consultarEstatisticas()`

#### 2.2.23 Receita Federal (3 métodos) - 15min
- [ ] `validarCPF()`
- [ ] `validarCNPJ()`
- [ ] `consultarCNPJ()`

#### 2.2.24 Status (2 métodos) - 10min
- [ ] `geral()`
- [ ] `porServico()`

**Checkpoint:** 209 métodos implementados

---

### 2.3 Service Agregado (30min)
- [ ] Objeto `governmentService` criado
- [ ] 24 sub-services agregados
- [ ] Exports configurados
- [ ] Documentação inline

**Checkpoint:** Service completo exportado

---

### 2.4 Validar Build (30min)
- [ ] Type check sem erros
- [ ] Build sem erros
- [ ] Imports testados

**Checkpoint:** Service validado

---

**✅ FASE 2 CONCLUÍDA:** ___/___/___ às ___:___
**Tempo gasto:** ___h
**Bloqueadores:** _________________________________

---

## 🎣 FASE 3: HOOKS REACT QUERY (8h)

**Objetivo:** Criar hooks para todas as 24 integrações
**Tempo:** 8 horas
**Status:** ⏳ PENDENTE

### 3.1 Configurar React Query Provider (30min)
- [ ] `QueryClient` configurado em `app/providers.tsx`
- [ ] `staleTime` e `cacheTime` configurados
- [ ] `ReactQueryDevtools` adicionado (dev only)

---

### 3.2 Criar Hooks por Integração (6h)

#### Arquivo: `src/hooks/useGovernment.ts`

- [ ] `useNFSeManaus()` - Hooks para NFS-e Manaus
- [ ] `useNFSeNacional()` - Hooks para NFS-e Nacional
- [ ] `useESocial()` - Hooks para eSocial (com polling)
- [ ] `useSEFAZ()` - Hooks para SEFAZ
- [ ] `useSEFAZAM()` - Hooks para SEFAZ-AM
- [ ] `useSPEDFiscal()` - Hooks para SPED Fiscal
- [ ] `useSPEDContabil()` - Hooks para SPED Contábil
- [ ] `useFGTSDigital()` - Hooks para FGTS Digital
- [ ] `useFGTSINSS()` - Hooks para FGTS/INSS
- [ ] `useEFDReinf()` - Hooks para EFD-Reinf
- [ ] `useDCTFWeb()` - Hooks para DCTFWeb
- [ ] `useSimplesNacional()` - Hooks para Simples Nacional
- [ ] `useECAC()` - Hooks para e-CAC
- [ ] `useCTe()` - Hooks para CT-e
- [ ] `useMDFe()` - Hooks para MDF-e
- [ ] `useNFCe()` - Hooks para NFC-e
- [ ] `useGovBR()` - Hooks para GOV.BR
- [ ] `useCertificate()` - Hooks para Certificado
- [ ] `useSync()` - Hooks para Sincronização (com polling)
- [ ] `useJobs()` - Hooks para Jobs
- [ ] `useDashboard()` - Hooks para Dashboard
- [ ] `useExtraction()` - Hooks para Extração
- [ ] `useReceitaFederal()` - Hooks para Receita Federal
- [ ] `useStatus()` - Hooks para Status

---

### 3.3 Hook Consolidado de Dashboard (1h)
- [ ] `useGovernmentDashboard()` criado
- [ ] Agrega status de todas integrações
- [ ] Polling configurado
- [ ] Métricas consolidadas

---

### 3.4 Configurar Cache (30min)
- [ ] Query keys bem definidas
- [ ] Invalidation strategies
- [ ] Stale time por tipo de dado
- [ ] Cache time otimizado

---

**✅ FASE 3 CONCLUÍDA:** ___/___/___ às ___:___
**Tempo gasto:** ___h
**Bloqueadores:** _________________________________

---

## 🎨 FASE 4: COMPONENTES UI (8h)

**Objetivo:** Criar interface completa para integrações
**Tempo:** 8 horas
**Status:** ⏳ PENDENTE

### 4.1 Dashboard Principal (2h)
- [ ] Arquivo: `GovIntegrationsDashboard.tsx`
- [ ] Status cards por integração
- [ ] Gráfico de disponibilidade
- [ ] Métricas consolidadas
- [ ] Últimas sincronizações

---

### 4.2 Componentes de Status (1h)
- [ ] `IntegrationStatusCard.tsx` - Card de status
- [ ] `ConnectivityIndicator.tsx` - Indicador de conectividade
- [ ] `CertificateStatus.tsx` - Status do certificado
- [ ] `TokenStatus.tsx` - Status do token GOV.BR

---

### 4.3 Monitorde Jobs (2h)
- [ ] `JobMonitor.tsx` - Monitor de jobs ativos
- [ ] `JobProgress.tsx` - Barra de progresso
- [ ] `JobLogs.tsx` - Logs em tempo real
- [ ] `JobActions.tsx` - Ações (pausar, cancelar)

---

### 4.4 Formulários de Integração (2h)
- [ ] `NFSeForm.tsx` - Emissão de NFS-e
- [ ] `ESocialEventForm.tsx` - Eventos eSocial
- [ ] `NFEForm.tsx` - Emissão de NF-e
- [ ] `SyncScheduler.tsx` - Agendamento de sync

---

### 4.5 Logs Viewer (1h)
- [ ] `IntegrationLogs.tsx` - Visualizador de logs
- [ ] Filtros por integração
- [ ] Filtros por severidade
- [ ] Download de logs

---

**✅ FASE 4 CONCLUÍDA:** ___/___/___ às ___:___
**Tempo gasto:** ___h
**Bloqueadores:** _________________________________

---

## 📄 FASE 5: PÁGINA (3h)

**Objetivo:** Refatorar página fiscal para exibir integrações
**Tempo:** 3 horas
**Status:** ⏳ PENDENTE

### 5.1 Estrutura Base (1h)
- [ ] Remover `ComingSoon`
- [ ] Adicionar `Tabs` de navegação
- [ ] Configurar rotas internas

---

### 5.2 Tabs de Conteúdo (1h30)
- [ ] Tab "Dashboard" - Dashboard geral
- [ ] Tab "NFS-e" - Gestão de NFS-e
- [ ] Tab "eSocial" - Eventos eSocial
- [ ] Tab "SEFAZ" - Notas fiscais
- [ ] Tab "SPED" - Escrituração
- [ ] Tab "Sincronização" - Sincronização e jobs

---

### 5.3 Navegação e UX (30min)
- [ ] Breadcrumbs
- [ ] Loading states
- [ ] Error boundaries
- [ ] Empty states

---

**✅ FASE 5 CONCLUÍDA:** ___/___/___ às ___:___
**Tempo gasto:** ___h
**Bloqueadores:** _________________________________

---

## 🧪 FASE 6: TESTES (4h)

**Objetivo:** Garantir qualidade com testes
**Tempo:** 4 horas
**Status:** ⏳ PENDENTE

### 6.1 Testes de Service (2h)
- [ ] Setup de testes (`vitest`)
- [ ] Mocks de API
- [ ] Testes por sub-service (24)
- [ ] Testes de erro

---

### 6.2 Testes de Hooks (1h)
- [ ] Setup de `@testing-library/react-hooks`
- [ ] Testes de queries
- [ ] Testes de mutations
- [ ] Testes de polling

---

### 6.3 Testes de Integração (1h)
- [ ] Fluxos completos
- [ ] Interação entre componentes
- [ ] Validação de dados

---

### 6.4 Cobertura (30min)
- [ ] Cobertura >80%
- [ ] Report gerado
- [ ] CI configurado

---

**✅ FASE 6 CONCLUÍDA:** ___/___/___ às ___:___
**Tempo gasto:** ___h
**Bloqueadores:** _________________________________

---

## 📚 FASE 7: DOCUMENTAÇÃO (2h)

**Objetivo:** Documentar tudo para manutenção futura
**Tempo:** 2 horas
**Status:** ⏳ PENDENTE

### 7.1 README do Service (1h)
- [ ] Arquivo criado: `src/lib/services/government/README.md`
- [ ] Documentação de cada sub-service
- [ ] Exemplos de uso
- [ ] Tipos importados

---

### 7.2 Guia de Configuração (30min)
- [ ] Arquivo criado: `CONFIGURACAO-INTEGRACAO.md`
- [ ] Guia por órgão governamental
- [ ] Requisitos de certificado
- [ ] Credenciais GOV.BR
- [ ] URLs de ambiente

---

### 7.3 Troubleshooting (30min)
- [ ] Problemas comuns
- [ ] Soluções documentadas
- [ ] Logs de debug
- [ ] Contatos de suporte

---

**✅ FASE 7 CONCLUÍDA:** ___/___/___ às ___:___
**Tempo gasto:** ___h
**Bloqueadores:** _________________________________

---

## 🎉 CONCLUSÃO

**Data de Conclusão:** ___/___/___ às ___:___
**Tempo Total:** ___h / 40h

### Métricas Finais

```
╔═══════════════════════════════════════════════════════════╗
║  MÓDULO GOVERNMENT - RESULTADO FINAL                      ║
╠═══════════════════════════════════════════════════════════╣
║  Cobertura Inicial:        56/209 (26%)                   ║
║  Cobertura Final:          ___/209 (___%)                 ║
║  Endpoints Implementados:  ___                            ║
║  Service Layer:            [ ] COMPLETO                   ║
║  Hooks React Query:        [ ] COMPLETO                   ║
║  Componentes UI:           [ ] COMPLETO                   ║
║  Página:                   [ ] COMPLETO                   ║
║  Testes:                   ___% cobertura                 ║
║  Documentação:             [ ] COMPLETA                   ║
╚═══════════════════════════════════════════════════════════╝
```

### Próximos Passos

- [ ] Deploy em staging
- [ ] Testes com usuários
- [ ] Ajustes de UX
- [ ] Deploy em produção
- [ ] Monitoramento contínuo

---

**🚀 PARABÉNS! COMPLIANCE GOVERNAMENTAL GARANTIDO! 🎉**

---

**Criado por:** Claude Sonnet 4.5
**Data:** 28 de Janeiro de 2026
**Última atualização:** ___/___/___ às ___:___
