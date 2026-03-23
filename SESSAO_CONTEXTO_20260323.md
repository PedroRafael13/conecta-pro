# CONTEXTO DA SESSÃO — CONECTA PRO
# Data: 2026-03-24 | Branch: feature/people-management-reorganization

## ESTADO ATUAL DO SISTEMA

### SCORES DOS MÓDULOS
- Gestão de Pessoas / DP: 9.5/10
- Financeiro: 10/10
- GED / Kit Mensal: 10/10
- Integrações Gov: 9/10
- Banking: 10/10
- BI/Analytics: 10/10
- Contratos: 9/10
- Operacional: 8/10
- CRM: 7/10
- WhatsApp: 6/10

### INFRA
- VPS: srv1134814.hstgr.cloud (82.25.75.74) Hostinger KV4
- Backend: FastAPI porta 8080 | docker ancestor=conecta-pro-backend
- Frontend: Next.js porta 3001 via PM2
- Branch: feature/people-management-reorganization
- REGRA: sempre 127.0.0.1, NUNCA localhost
- TMUX: t1-t5 sempre via tmux attach -t tN

### ZONAS PROIBIDAS
alembic/versions/, main_production.py, docker-compose*.yml, .env*, credentials/

### TOKEN
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend --format '{{.Names}}' | head -1)

### CONQUISTAS DESTA SESSÃO (2026-03-24)

#### T1 — DP/Gestão de Pessoas
- Folha R$ 70.520 funcionando (era R$ 0,00)
- Ponto 1.840 batidas reais Tangerino
- Trailing slash corrigido em 10 arquivos
- Slice(0,20) removido — todos 42 aparecem
- Horas reais calculadas (11h51m, 12h04m, etc.)
- Commits: 34a6937b, 1d3ed738

#### T2 — Financeiro
- 31 endpoints retornando 200
- DRE Lucro Real: R$ 87.779 lucro líquido
- Conciliação bancária: 81,8% (9/11 receivables)
- NFS-e entrada criada (compliance Lucro Real)
- Saldo bancário no dashboard: R$ 32.070,26
- Commits: c34d0166, 7e37feba, 9746238d, 090d2b58, 14dfc7fa

#### T3 — GED / Kit Mensal
- Kit 19/19 (100%) — 375 PDFs reais
- 7 fontes internas conectadas
- Montagem guiada: 4 endpoints
- ZIP download funcionando
- Commits: d99b3e5e, b83986c4, 82e04211, 810a5c4e, 555243c9

#### T5 — Integrações Governamentais
- eSocial S-1000 ACEITO: recibo 1.2.0000000000305333794
- NFS-e Nacional: pipeline 100% funcional, schema validado
- 13 erros resolvidos (E6155→RNG6110×6→E0237→E0006→E0008)
- Dados falsos eliminados (FGTS/INSS/SN/eCAC/RF)
- Commits: fix(gov), feat(nfse)

### PENDÊNCIAS PARA PRÓXIMA SESSÃO

#### DEV (terminais)
- T5: EFD-Reinf R-1000 (SOAP = mesmo padrão eSocial, 2-4h)
- T5: eSocial S-1005/S-1010/S-1020 (tabelas)
- T1: S-2200 (aguarda dados Jordan)
- T3: Página frontend do kit (síndico visualizar/baixar)
- T3: Envio email ZIP do kit
- T2: 5 páginas estáticas (cobranças, custos, orçamentos, custeio, fiscal)
- T2: Conciliação Laranjeiras + Gelain (boleto, não PIX)
- Frontend: corrigir tela em branco (/_next/static 404)

#### JORDAN (ações externas)
- NFS-e E0310: contatar SEMEF nota.monitoramento@manaus.am.gov.br
  → Quais cTribNac estão cadastrados para 35.710.481/0001-03?
  → Verificar portal: www.nfse.gov.br/EmissorNacional
- S-2200: pegar data_nascimento + sexo + estado_civil dos 52 func
  no Domínio Sistemas com o contador
- Gov.br OAuth2: registrar app em
  manual-roteiro-integracao-login-unico.servicos.gov.br
- CRF FGTS: vence 31/03 — renovar no portal Caixa
- Laranjeiras + Gelain: verificar se pagam via boleto e conciliar manual

### CLIENTES ATIVOS COM KIT MENSAL (mão de obra)
Ideal Flores (23.147.782/0001-91) — R$ 65.842 — ISS+INSS+CSLL retidos
Laranjeiras Village (24.632.786/0001-28) — R$ 42.544 — ISS+INSS+CSLL
Mirante das Flores (52.605.708/0001-70) — R$ 42.255 — sem retenção
Prime Arena (47.405.340/0001-66) — R$ 40.466 — INSS 11%
Villa dos Pássaros (13.221.953/0001-21) — R$ 37.338 — sem retenção
Villa Dei Fiori (02.153.384/0001-08) — R$ 25.592 — sem retenção
Michelangelo (04.911.208/0001-13) — R$ 8.346 — sem retenção
Gelain (00.736.037/0001-82) — R$ 6.000 — portaria remota

SEM KIT: Parise Village, Green Hills, Life Centro (manutenção CFTV)

### DADOS FINANCEIROS REAIS
MRR: R$ 272.086,96 | Folha: R$ 70.520,10 | FGTS: R$ 7.676,02
INSS Patronal: R$ 19.190,04 | ISS: R$ 13.604,35
Saldo Inter: R$ 32.041,91 | Saldo Cora: R$ 28,35
NFS-e emitidas: 27 (R$ 542.673,92) | Transações Inter: 649
Lucro Líquido: R$ 87.779,00 (32,3%) — PARCIAL, faltam despesas reais

### REGRAS IMUTÁVEIS
- Pylint 99/100+, TypeScript zero any
- useQuery+staleTime NUNCA useState([])
- Endpoints sempre 200 com dados reais, NUNCA mock
- Hot copy backend: docker cp + restart (sem rebuild)
- Build frontend: NODE_OPTIONS=--max-old-space-size=4096, SERIALIZADO
- CNPJ raiz eSocial: 35710481000000 (padded zeros 14 chars)
- NFS-e URL: sefin.nfse.gov.br/sefinnacional/
- eSocial URL: webservices.producaorestrita.esocial.gov.br

### GITHUB
https://github.com/jjesus1982/conecta-pro
Branch: feature/people-management-reorganization
