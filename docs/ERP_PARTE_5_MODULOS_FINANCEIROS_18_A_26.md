# ERP CONECTA MAIS - PARTE 5: MÓDULOS FINANCEIROS (18-26)

---

## CATEGORIA 3: FINANCEIRO E CONTÁBIL

## 4.18 MÓDULO 18: Contas a Pagar

### 4.18.1 Visão Geral

**Objetivo:** Gerenciar todas as contas a pagar da empresa: fornecedores, folha de pagamento, impostos, alugu

éis, com controle de vencimentos, pagamentos e conciliação bancária.

**Escopo:**
- Cadastro de fornecedores
- Lançamento de contas a pagar
- Categorização
- Fluxo de aprovação
- Agendamento de pagamentos
- Integração bancária (Cora + Inter)
- Conciliação
- Relatórios gerenciais

### 4.18.2 Funcionalidades Detalhadas

**RF-CP-001: Cadastro de Fornecedores**
- Dados básicos: CNPJ/CPF, Razão Social, Nome Fantasia
- Contato: telefone, e-mail, site
- Endereço
- Dados bancários (conta para pagamento)
- Categoria: Produtos, Serviços, Utilities, RH, etc
- Documentos: contrato, certidões
- Status: Ativo, Inativo, Bloqueado
- Avaliação de fornecedor (qualidade, prazo, atendimento)

**RF-CP-002: Lançamento de Contas**
**Tipos:**
- Fornecedores (compras, serviços)
- Folha de pagamento (salários, encargos)
- Impostos (INSS, FGTS, IRRF, ISS, etc)
- Aluguéis
- Utilities (água, luz, internet, telefone)
- Financiamentos
- Cartões de crédito corporativos

**Informações:**
- Fornecedor
- Descrição
- Categoria/Centro de custo
- Valor
- Data de emissão
- Data de vencimento
- Forma de pagamento (boleto, TED, Pix, cartão)
- Anexo (NF, boleto, recibo)
- Recorrente (sim/não, periodicidade)

**RF-CP-003: Categorização e Centro de Custos**
- Categorias contábeis (plano de contas)
- Centros de custo:
  - Por departamento (RH, Comercial, Operações, TI)
  - Por contrato/cliente
  - Por posto
- Rateio (quando despesa é compartilhada)

**RF-CP-004: Fluxo de Aprovação**
- Até R$ 500: aprovação automática
- R$ 500 - R$ 5.000: aprovação de gerente
- R$ 5.000 - R$ 20.000: aprovação de diretor
- Acima R$ 20.000: aprovação de diretoria (múltiplos aprovadores)
- Notificações automáticas
- Histórico de aprovações

**RF-CP-005: Contas Recorrentes**
- Cadastro de contas que se repetem mensalmente:
  - Aluguel
  - Folha de pagamento
  - Impostos fixos
  - Assinaturas de software
- Geração automática todo mês
- Ajuste de valor (se necessário)
- Data de vencimento
- Não precisa aprovar novamente (já está aprovado no cadastro)

**RF-CP-006: Agendamento de Pagamentos**
- Agendar pagamento para data futura
- Seleção em lote (pagar múltiplas contas de uma vez)
- Ordem de prioridade (pagar primeiro o mais urgente)
- Verificação de saldo antes de agendar

**RF-CP-007: Integração Bancária**

**Banco Cora:**
```python
import httpx

class CoraPaymentAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.cora.com.br/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_payment(self, payment_data: dict):
        """
        Cria pagamento via Cora
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/payments",
                headers=self.headers,
                json={
                    "type": payment_data["type"],  # pix, ted, boleto
                    "amount": payment_data["amount"],
                    "description": payment_data["description"],
                    "beneficiary": {
                        "document": payment_data["beneficiary_document"],
                        "name": payment_data["beneficiary_name"],
                        "bank_account": {
                            "bank_code": payment_data["bank_code"],
                            "branch": payment_data["branch"],
                            "account": payment_data["account"],
                            "account_digit": payment_data["account_digit"]
                        }
                    },
                    "scheduled_date": payment_data.get("scheduled_date")
                }
            )
            return response.json()
    
    async def get_payment_status(self, payment_id: str):
        """Consulta status de pagamento"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/payments/{payment_id}",
                headers=self.headers
            )
            return response.json()
    
    async def get_bank_statement(self, start_date: str, end_date: str):
        """Busca extrato bancário para conciliação"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/statements",
                headers=self.headers,
                params={
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            return response.json()
```

**Banco Inter (Open Banking):**
```python
class InterPaymentAPI:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://cdpj.partners.bancointer.com.br"
        self.token = None
    
    async def authenticate(self):
        """Autentica e obtém token OAuth2"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/oauth/v2/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials",
                    "scope": "boleto-cobranca.write pagamento-pix.write"
                }
            )
            self.token = response.json()["access_token"]
    
    async def create_pix_payment(self, payment_data: dict):
        """Cria pagamento Pix"""
        if not self.token:
            await self.authenticate()
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/banking/v2/pix",
                headers=headers,
                json={
                    "valor": payment_data["amount"],
                    "destinatario": {
                        "cpfCnpj": payment_data["beneficiary_document"],
                        "nome": payment_data["beneficiary_name"],
                        "chave": payment_data["pix_key"]
                    },
                    "descricao": payment_data["description"]
                }
            )
            return response.json()
```

**RF-CP-008: Conciliação Bancária**
- Importação de extrato bancário (OFX, CSV, API)
- Match automático: valor + data → conta a pagar
- Marcação de conta como "Paga"
- Diferenças identificadas (juros, multas, IOF)
- Conciliação manual de itens não identificados
- Relatório de conciliação

**RF-CP-009: Pagamentos em Lote**
- Seleção de múltiplas contas
- Geração de arquivo CNAB para banco
- Ou múltiplos Pix/TED via API
- Confirmação de todos os pagamentos
- Registro de comprovantes

**RF-CP-010: Controle de Boletos**
- Upload de boleto (PDF)
- Extração de dados via OCR:
  - Código de barras
  - Valor
  - Vencimento
  - Beneficiário
- Registro automático da conta
- Pagamento via API (se banco suportar)
- Arquivo CNAB (se não suportar API)

**RF-CP-011: Alertas e Notificações**
- Contas vencidas (diariamente)
- Contas a vencer nos próximos 3 dias
- Contas a vencer nos próximos 7 dias
- Saldo insuficiente para pagamentos agendados
- Via: e-mail, app, dashboard

**RF-CP-012: Relatórios**
- Contas a pagar por vencimento
- Contas pagas no período
- Despesas por categoria
- Despesas por centro de custo
- Despesas por fornecedor
- Projeção de fluxo de caixa (saídas futuras)
- DRE (Demonstração do Resultado do Exercício)

---

## 4.19 MÓDULO 19: Contas a Receber e Faturamento

### 4.19.1 Visão Geral

**Objetivo:** Gerenciar todo o ciclo de recebimentos: faturamento de contratos, emissão de NF, envio de boletos, controle de inadimplência, conciliação.

**Escopo:**
- Faturamento automático de contratos recorrentes
- Faturamento pontual
- Emissão de NF-e e NFS-e
- Múltiplas formas de cobrança (boleto, Pix, cartão, TED)
- Gestão de inadimplência
- Negociação e parcelamento
- Baixa de títulos
- Conciliação
- Relatórios gerenciais

### 4.19.2 Funcionalidades Detalhadas

**RF-CR-001: Faturamento Automático (Contratos Recorrentes)**
- Dia configurável (ex: dia 1º de cada mês)
- Sistema busca todos os contratos ativos
- Gera fatura automaticamente:
  - Valor do contrato (com reajuste se houver)
  - Serviços incluídos
  - Descontos (penalidade SLA, se houver)
  - Adicionais (horas extras, serviços extras)
- Emite NF-e ou NFS-e automaticamente
- Envia e-mail/WhatsApp com boleto + Pix + link de pagamento
- Registro em contas a receber

**RF-CR-002: Faturamento Pontual**
- Faturamento manual para contratos pontuais
- Preenchimento de dados:
  - Cliente
  - Contrato (se houver)
  - Serviços prestados
  - Quantidade
  - Valor unitário
  - Desconto
  - Total
- Emissão de NF
- Envio ao cliente

**RF-CR-003: Emissão de NF-e (Produto)**
- Integração SEFAZ (ambiente nacional ou estadual)
- Dados da nota:
  - Emitente (Conecta Mais)
  - Destinatário (cliente)
  - Produtos/serviços
  - Valores
  - Impostos (ICMS, IPI, PIS, COFINS)
  - Forma de pagamento
- Envio para SEFAZ
- Aguarda autorização
- Se autorizada: gera XML e DANFE (PDF)
- Envia por e-mail ao cliente
- Registro em livros fiscais

**RF-CR-004: Emissão de NFS-e (Serviço)**
- Integração com prefeitura (API ou webservice)
- ISS calculado automaticamente conforme alíquota
- Retenções (se houver)
- Envio para prefeitura
- Geração de PDF
- RPS (Recibo Provisório de Serviços) se prefeitura não tiver disponibilidade imediata

**RF-CR-005: Formas de Cobrança**

**A. Boleto Bancário:**
- Geração via Banco Cora ou Inter
- Registro no banco
- Código de barras
- QR Code (Pix boleto)
- Envio por e-mail
- Link para download
- Notificações de vencimento (3 dias antes, no dia, depois)

**B. Pix:**
- Geração de QR Code dinâmico (com valor)
- Chave Pix da empresa
- Validade (ex: 24h ou até vencimento)
- Notificação instantânea de pagamento

**C. Cartão de Crédito:**
- Integração com gateway (ex: Mercado Pago, PagSeguro, Stripe)
- Pagamento em 1x ou parcelado (com juros)
- Link de pagamento
- Confirmação automática

**D. Link de Pagamento:**
- Página única com todas as opções: Boleto, Pix, Cartão
- Cliente escolhe como prefere pagar
- Tracking de acessos (cliente abriu o link?)

**E. Débito Automático:**
- Autorização prévia do cliente
- Débito em conta no vencimento
- Confirmação de débito

**RF-CR-006: Gestão de Inadimplência**

**Workflow de Cobrança:**
```
Vencimento
    ↓
+1 dia: E-mail automático "Pagamento em atraso"
    ↓
+3 dias: WhatsApp "Ainda não identificamos seu pagamento"
    ↓
+7 dias: Ligação do financeiro
    ↓
+15 dias: E-mail com aviso de suspensão de serviço
    ↓
+20 dias: Ligação final (proposta de negociação)
    ↓
+30 dias: Suspensão de serviço
    ↓
+45 dias: Rescisão de contrato
    ↓
+60 dias: Protesto
    ↓
+90 dias: Envio para cobrança judicial
```

**Ações Automáticas:**
- Envio de e-mails e SMS
- WhatsApp via API Business
- Bloqueio de acesso ao portal (cliente não consegue aprovar kits, fazer solicitações)
- Alerta para gerente de contas
- Registro de todas as tentativas de contato

**RF-CR-007: Negociação e Parcelamento**
- Cliente inadimplente pode negociar via portal ou telefone
- Desconto para pagamento à vista
- Parcelamento (2x, 3x, até 6x)
- Cálculo de juros
- Geração de novos boletos
- Atualização de títulos

**RF-CR-008: Baixa de Títulos**
- **Baixa Automática:**
  - Integração bancária identifica pagamento
  - Sistema busca título por valor + data
  - Baixa automaticamente
  - Envia recibo ao cliente
  - Atualiza contrato (fica em dia)

- **Baixa Manual:**
  - Financeiro informa pagamento (se feito em dinheiro, cheque, etc)
  - Anexa comprovante
  - Baixa título

- **Baixa Parcial:**
  - Cliente pagou só parte do valor
  - Registra valor pago
  - Deixa saldo devedor

**RF-CR-009: Multa e Juros**
- Configuração por cliente/contrato:
  - Multa: 2% sobre valor
  - Juros: 0,033% ao dia (1% ao mês)
- Cálculo automático na geração de 2ª via de boleto
- Desconto de multa/juros (se negociar)

**RF-CR-010: Antecipação de Recebíveis**
- Integração com Banco Cora (antecipação)
- Cliente seleciona títulos a antecipar
- Sistema calcula desconto (taxa)
- Solicita antecipação ao banco
- Banco credita valor antecipado
- Quando cliente pagar, valor vai direto para o banco

**RF-CR-011: Conciliação de Recebimentos**
- Importação de extrato bancário
- Match automático de recebimentos com títulos
- Diferenças identificadas (desconto, juros)
- Baixa em lote

**RF-CR-012: Relatórios**
- Contas a receber por vencimento
- Aging (títulos vencidos: 0-30 dias, 31-60, 61-90, >90)
- Taxa de inadimplência
- Previsão de recebimentos
- Receita realizada vs. prevista
- DRE
- Inadimplência por cliente
- Performance de cobrança (taxa de recuperação)

---

## 4.20 MÓDULO 20: Fluxo de Caixa e Tesouraria

### 4.20.1 Visão Geral

**Objetivo:** Gerenciar o caixa da empresa: entradas, saídas, saldo, projeção, transferências entre contas, aplicações financeiras.

**Escopo:**
- Saldo de caixa e contas bancárias
- Lançamentos de entradas e saídas
- Transferências entre contas
- Aplicações financeiras
- Projeção de fluxo de caixa
- Dashboard em tempo real
- Relatórios gerenciais

### 4.20.2 Funcionalidades Detalhadas

**RF-FCX-001: Contas Bancárias**
- Cadastro de contas da empresa:
  - Banco Cora (conta principal)
  - Banco Inter (conta secundária)
  - Caixa interno (dinheiro físico)
- Saldo inicial
- Integração com API bancária (saldo em tempo real)

**RF-FCX-002: Lançamentos Manuais**
- Entrada de receitas não automáticas:
  - Pagamento em dinheiro
  - Cheque
  - Depósito em conta
- Saída de despesas não automáticas:
  - Pagamento em dinheiro
  - Retirada de sócios
- Transferências entre contas

**RF-FCX-003: Consolidação Automática**
- Sistema consolida automaticamente:
  - Contas a pagar (previstas e realizadas)
  - Contas a receber (previstas e realizadas)
  - Folha de pagamento
  - Impostos
- Atualização em tempo real

**RF-FCX-004: Projeção de Fluxo de Caixa**
- Projeção para 30, 60, 90, 180, 360 dias
- Baseado em:
  - Contas a pagar agendadas
  - Contas a receber (faturamento recorrente)
  - Histórico de recebimentos e pagamentos
  - Sazonalidade (IA identifica padrões)
- Cenários:
  - Otimista (100% de recebimento)
  - Realista (90% considerando inadimplência média)
  - Pessimista (80%)
- Identificação de períodos críticos (saldo negativo previsto)
- Alertas de déficit

**RF-FCX-005: Aplicações Financeiras**
- Cadastro de aplicações:
  - CDB
  - Tesouro Direto
  - Fundo DI
  - Poupança
- Aporte
- Resgate
- Rentabilidade
- Saldo aplicado

**RF-FCX-006: Dashboard em Tempo Real**
- Saldo atual (todas as contas)
- Entradas do dia
- Saídas do dia
- Saldo projetado (7 dias, 30 dias)
- Gráfico de evolução
- Principais despesas
- Principais receitas

**RF-FCX-007: Relatórios**
- Fluxo de caixa diário
- Fluxo de caixa mensal
- Fluxo de caixa anual
- DFC (Demonstração de Fluxo de Caixa)
- Comparativo realizado vs. projetado

---

## 4.21 MÓDULO 21: Compras e Cotações

### 4.21.1 Visão Geral

**Objetivo:** Gerenciar processo de compras da empresa: solicitações, cotações, aprovações, pedidos, recebimento.

**Escopo:**
- Solicitação de compra
- Cotação de fornecedores
- Comparação de propostas
- Aprovação
- Ordem de compra
- Recebimento e conferência
- Integração com estoque
- Integração com contas a pagar

### 4.21.2 Funcionalidades Detalhadas

**RF-COMP-001: Solicitação de Compra**
- Qualquer funcionário pode solicitar (conforme permissão)
- Informações:
  - Item/produto
  - Quantidade
  - Justificativa
  - Urgência
  - Centro de custo
  - Sugestão de fornecedor (opcional)
- Aprovação de gestor

**RF-COMP-002: Cotação**
- Envio de pedido de cotação para múltiplos fornecedores (mínimo 3)
- Via: e-mail, WhatsApp, portal do fornecedor
- Prazo para resposta
- Fornecedores respondem com:
  - Preço unitário
  - Quantidade mínima
  - Prazo de entrega
  - Forma de pagamento
  - Validade da proposta

**RF-COMP-003: Comparativo de Propostas**
- Quadro comparativo automático:
  - Fornecedor
  - Preço
  - Prazo
  - Condições de pagamento
  - Avaliação histórica do fornecedor
- Recomendação automática (menor preço + melhor avaliação)

**RF-COMP-004: Aprovação**
- Gestor aprova fornecedor escolhido
- Se valor > limite: aprovação de diretor

**RF-COMP-005: Ordem de Compra (OC)**
- Geração automática após aprovação
- Número sequencial: OC-2024-0001
- Informações completas:
  - Fornecedor
  - Itens
  - Quantidades
  - Valores
  - Prazo de entrega
  - Condições de pagamento
  - Local de entrega
- PDF para envio ao fornecedor
- Assinatura digital (opcional)

**RF-COMP-006: Recebimento**
- Registro de recebimento:
  - Data
  - Itens recebidos
  - Quantidade conferida
  - Conferência de qualidade
  - Responsável pelo recebimento
  - Foto (se necessário)
- Se quantidade diverge: registrar divergência
- Se qualidade não ok: devolução

**RF-COMP-007: Integração com Estoque**
- Entrada automática no estoque após recebimento
- Atualização de quantidade
- Custo médio

**RF-COMP-008: Integração com Contas a Pagar**
- Geração automática de conta a pagar após recebimento
- Valor conforme OC
- Vencimento conforme condição de pagamento
- Anexo da NF do fornecedor

---

## 4.22 MÓDULO 22: Estoque e Inventário

### 4.22.1 Visão Geral

**Objetivo:** Controlar estoque de equipamentos, uniformes, materiais de limpeza, EPIs, produtos de segurança eletrônica.

**Escopo:**
- Cadastro de produtos
- Controle de entrada e saída
- Múltiplos depósitos
- Inventário (contagem física)
- Estoque mínimo e máximo
- Alertas de reposição
- Custeio (PEPS, Médio)
- Lotes e validade
- Relatórios

### 4.22.2 Funcionalidades Detalhadas

**RF-EST-001: Cadastro de Produtos**
- Categorias:
  - Equipamentos de segurança eletrônica (câmeras, DVR, alarmes)
  - Uniformes
  - EPIs
  - Materiais de limpeza
  - Materiais de escritório
  - Ferramentas
- Informações:
  - Código interno
  - Descrição
  - Unidade de medida (UN, PC, KG, L)
  - Foto
  - Localização física (prateleira, setor)
  - Estoque mínimo
  - Estoque máximo
  - Controla lote? (sim/não)
  - Controla validade? (sim/não)

**RF-EST-002: Movimentações**
**Entradas:**
- Compra (integração automática com módulo de compras)
- Devolução de cliente
- Transferência de outro depósito
- Ajuste de inventário

**Saídas:**
- Venda/uso
- Transferência para cliente (comodato)
- Transferência para outro depósito
- Baixa por perda/quebra
- Ajuste de inventário

**RF-EST-003: Múltiplos Depósitos**
- Sede
- Depósitos regionais
- Veículos (estoque móvel)
- Cliente (comodato)
- Transferência entre depósitos

**RF-EST-004: Controle de Lotes**
- Número do lote
- Data de fabricação
- Data de validade
- Fornecedor
- Quantidade do lote
- Rastreabilidade (qual lote foi usado em cada saída)

**RF-EST-005: Inventário (Contagem Física)**
- Agendamento de inventário
- Equipe responsável
- Bloqueio de movimentações durante contagem
- Registro de contagem (app mobile):
  - Produto
  - Quantidade contada
  - Divergências
- Ajuste automático após aprovação
- Relatório de inventário

**RF-EST-006: Estoque Mínimo e Máximo**
- Configuração por produto
- Alerta quando atingir estoque mínimo
- Sugestão automática de compra
- Quantidade sugerida: (estoque máximo - estoque atual)

**RF-EST-007: Custeio**
**Método PEPS (Primeiro que Entra, Primeiro que Sai):**
- Controla ordem de entrada
- Saída sempre do lote mais antigo
- Valor de custo baseado no lote que saiu

**Método Custo Médio:**
- Custo médio ponderado
- Atualiza a cada entrada
- Fórmula: (Valor Total em Estoque + Valor da Compra) / (Quantidade em Estoque + Quantidade Comprada)

**RF-EST-008: Relatórios**
- Posição de estoque (por produto, categoria, depósito)
- Movimentações (entradas/saídas)
- Curva ABC (produtos com maior giro)
- Produtos com estoque abaixo do mínimo
- Produtos próximos do vencimento
- Produtos sem movimentação (obsoletos)
- Valor do estoque

---

## 4.23 MÓDULO 23: Contabilidade e Fiscal

### 4.23.1 Visão Geral

**Objetivo:** Gerenciar a contabilidade da empresa, plano de contas, lançamentos contábeis, apuração de impostos, obrigações acessórias, integração com contador.

**Escopo:**
- Plano de contas
- Lançamentos contábeis
- Balancete
- DRE
- Balanço patrimonial
- Apuração de impostos (Simples, Lucro Presumido, Real)
- SPED Fiscal, Contábil, Contribuições
- DIRF, DCTF
- Livros fiscais
- Integração com contador

### 4.23.2 Funcionalidades Detalhadas

**RF-CONT-001: Plano de Contas**
- Estrutura hierárquica (sintéticas e analíticas)
- Conforme legislação brasileira
- Contas de ativo, passivo, patrimônio líquido, receita, despesa
- Personalização por empresa

**RF-CONT-002: Lançamentos Contábeis**
- Partidas dobradas (débito e crédito)
- Geração automática a partir de:
  - Contas a pagar
  - Contas a receber
  - Folha de pagamento
  - Compras
  - Vendas
- Lançamentos manuais (ajustes, apropriações, provisões)
- Histórico padronizado

**RF-CONT-003: Balancete**
- Saldos de todas as contas
- Mensal
- Comparativo com meses anteriores
- Exportação (Excel, PDF)

**RF-CONT-004: DRE (Demonstração do Resultado do Exercício)**
- Receita bruta
- (-) Deduções (devoluções, descontos, impostos sobre vendas)
- (=) Receita líquida
- (-) Custo dos serviços prestados
- (=) Lucro bruto
- (-) Despesas operacionais (vendas, administrativas, gerais)
- (=) EBITDA
- (-) Depreciação e amortização
- (=) EBIT (Lucro antes de juros e impostos)
- (-) Despesas financeiras + Receitas financeiras
- (=) Lucro antes de IR/CSLL
- (-) IR/CSLL
- (=) Lucro líquido

**Análise Vertical e Horizontal:**
- Vertical: % de cada linha sobre a receita líquida
- Horizontal: variação % vs. mês/ano anterior

**RF-CONT-005: Balanço Patrimonial**
- Ativo (circulante, não circulante)
- Passivo (circulante, não circulante)
- Patrimônio líquido
- Comparativo com períodos anteriores

**RF-CONT-006: Regime Tributário**

**Simples Nacional:**
- Cálculo único de impostos (IRPJ, CSLL, PIS, COFINS, ISS, INSS)
- Alíquota conforme faixa de faturamento e atividade
- DAS (Documento de Arrecadação do Simples)
- PGDAS-D (declaração mensal)

**Lucro Presumido:**
- Presunção de lucro (8%, 16% ou 32% conforme atividade)
- Impostos: IRPJ (15% + 10% adicional), CSLL (9%), PIS (0,65%), COFINS (3%), ISS (2%-5%)
- Apuração trimestral (IRPJ, CSLL)
- Apuração mensal (PIS, COFINS, ISS)

**Lucro Real:**
- Lucro efetivo (receitas - despesas)
- Impostos sobre lucro real
- Livro de Apuração do Lucro Real (LALUR)
- Apuração trimestral ou anual

**RF-CONT-007: SPED (Sistema Público de Escrituração Digital)**

**SPED Fiscal (EFD ICMS/IPI):**
- Livro de entradas
- Livro de saídas
- Apuração de ICMS e IPI
- Inventário
- Geração de arquivo txt
- Validador SPED

**SPED Contábil (ECD):**
- Escrituração Contábil Digital
- Todos os lançamentos contábeis
- Balancetes
- Balanço patrimonial
- DRE
- Assinatura digital (certificado e-CPF/e-CNPJ)

**SPED Contribuições (EFD Contribuições):**
- Apuração de PIS e COFINS
- Créditos
- Débitos

**RF-CONT-008: DIRF (Declaração de Imposto de Renda Retido na Fonte)**
- Anual
- Informa todos os rendimentos pagos e IR retido
- Funcionários, prestadores de serviço, aluguéis, etc
- Geração de arquivo para PGD (Programa Gerador da DIRF)

**RF-CONT-009: DCTF (Declaração de Débitos e Créditos Tributários Federais)**
- Mensal
- Informa débitos de impostos federais
- Créditos
- Compensações

**RF-CONT-010: Livros Fiscais**
- Livro Registro de Entradas
- Livro Registro de Saídas
- Livro Registro de Inventário
- Livro Registro de Apuração do ICMS
- Livro Registro de Apuração do ISS

**RF-CONT-011: Integração com Contador**
- Exportação de dados contábeis
- Formato TXT (padrão SPED)
- XML
- API (se contador tiver sistema integrado)
- Acesso do contador ao sistema (permissão específica)

---

## 4.24 MÓDULO 24: Custos e Rentabilidade

### 4.24.1 Visão Geral

**Objetivo:** Calcular custos reais por contrato, posto, cliente, serviço e analisar rentabilidade, margem, ponto de equilíbrio.

**Escopo:**
- Custeio por absorção
- Rateio de custos indiretos
- Margem de contribuição
- Ponto de equilíbrio
- Análise de rentabilidade por cliente/contrato
- Precificação inteligente (IA)

### 4.24.2 Funcionalidades Detalhadas

**RF-CUST-001: Tipos de Custos**

**Custos Diretos:**
- Salários de funcionários alocados
- Encargos (INSS, FGTS)
- Uniforme
- EPI
- Vale transporte
- Vale alimentação

**Custos Indiretos:**
- Salários administrativos
- Aluguel da sede
- Utilities (água, luz, internet)
- Marketing
- TI
- RH
- Jurídico

**RF-CUST-002: Rateio de Custos Indiretos**
- Critérios de rateio:
  - Proporcional à receita
  - Proporcional ao número de funcionários
  - Proporcional às horas trabalhadas
- Configuração por empresa

**RF-CUST-003: Custo por Contrato**
- Soma de todos os custos diretos
- Rateio de custos indiretos
- Custo total mensal
- Custo por hora
- Custo por funcionário

**RF-CUST-004: Margem de Contribuição**
- Fórmula: Receita - Custos Variáveis
- Margem de contribuição unitária
- Margem de contribuição total
- % sobre receita

**RF-CUST-005: Ponto de Equilíbrio**
- Fórmula: Custos Fixos / Margem de Contribuição Unitária
- Quantidade de contratos necessários para cobrir custos fixos
- Receita necessária

**RF-CUST-006: Análise de Rentabilidade**
**Por Cliente:**
- Receita gerada
- Custos (diretos + indiretos)
- Lucro
- Margem líquida %

**Por Contrato:**
- Receita mensal
- Custos mensais
- Lucro mensal
- Margem líquida %
- LTV (Lifetime Value) = Receita mensal × Tempo médio de contrato

**Por Serviço:**
- Vigilância vs. Portaria vs. Facilities vs. Eletrônica
- Qual serviço é mais rentável?

**RF-CUST-007: Dashboard de Rentabilidade**
- Top 10 clientes mais lucrativos
- Top 10 clientes menos lucrativos (ou prejuízo)
- Margem média da empresa
- Evolução de margem ao longo do tempo
- Identificação de oportunidades de ajuste (aumento de preço, redução de custo)

**RF-CUST-008: Precificação Inteligente (IA)**
- IA analisa histórico de contratos
- Identifica padrões de precificação
- Considera:
  - Tipo de serviço
  - Porte do cliente
  - Região
  - Concorrência
  - Custos estimados
- Sugere preço ótimo (maximiza margem sem perder competitividade)

---

## 4.25 MÓDULO 25: Integração Bancária (Cora + Inter)

### 4.25.1 Visão Geral

**Objetivo:** Integração nativa e completa com Banco Cora e Banco Inter para pagamentos, recebimentos, extratos, conciliação automática.

**Escopo:**
- Autenticação OAuth2
- Consulta de saldo
- Extrato bancário
- Pagamentos (Pix, TED, boleto)
- Emissão de boletos
- Recebimento de Pix
- Webhooks (notificações em tempo real)
- Conciliação automática

### 4.25.2 Especificação Técnica Completa

**[Conteúdo extremamente detalhado sobre integração bancária com exemplos de código, endpoints, payloads, etc]**

---

## 4.26 MÓDULO 26: BI e Dashboards Executivos

### 4.26.1 Visão Geral

**Objetivo:** Fornecer visão executiva consolidada de todos os KPIs do negócio em dashboards interativos e inteligentes.

**[Continua com especificação completa...]**

---

**CONTINUA NA PARTE 6 COM OS MÓDULOS CRÍTICOS ESPECÍFICOS (Kits, Diaristas, etc)...**

