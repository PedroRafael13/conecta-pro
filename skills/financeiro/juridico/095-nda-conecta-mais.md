# SKILL 095 — NDA: Acordo de Confidencialidade Conecta Mais
**Versão:** 2026-01
**Empresa:** JORDAN SANTOS DE JESUS LTDA (Conecta Mais — Segurança e Tecnologia)
**CNPJ:** 35.710.481/0001-03 | Manaus/AM
**Aplicação:** 3 modelos de NDA para os contextos operacionais da Conecta Mais

---

## Contexto de Uso dos NDAs

A Conecta Mais opera com informações confidenciais em 3 contextos principais:
1. **Fornecedores de TI** — acesso ao código-fonte, banco de dados e infraestrutura do ERP
2. **Parceiros de contencioso** — advogados, peritos e escritórios com acesso a dados de processo
3. **Fornecedores dos condomínios** — prestadores terceiros com acesso a sistemas de segurança dos clientes

---

## MODELO A — NDA com Fornecedor de TI

**Quando usar:** Ao contratar empresa ou profissional para desenvolvimento, manutenção ou auditoria do Conecta PRO ERP.

---

**ACORDO DE CONFIDENCIALIDADE E NÃO DIVULGAÇÃO**

**Partes:**
- **REVELADORA:** JORDAN SANTOS DE JESUS LTDA, CNPJ 35.710.481/0001-03, Manaus/AM ("Conecta Mais")
- **RECEPTORA:** [Nome/Razão Social], [CNPJ/CPF], [Endereço] ("Fornecedor")

**Data de vigência:** [DATA DE INÍCIO]

**Cláusula 1 — Definição de Informação Confidencial**
Para os fins deste acordo, são consideradas confidenciais todas as informações a que a Receptora tiver acesso no contexto da relação comercial, incluindo, mas não limitado a:
- Código-fonte do sistema Conecta PRO ERP (repositório Git privado)
- Credenciais de acesso (banco de dados, APIs, chaves JWT, certificados A1)
- Dados pessoais de colaboradores, clientes e usuários do sistema
- Arquitetura de infraestrutura (VPS, containers Docker, configurações de rede)
- Dados financeiros (MRR, DRE, fluxo de caixa, tabela de preços)
- Estratégias comerciais e roadmap de produto

**Cláusula 2 — Obrigações da Receptora**
A Receptora se compromete a:
a) Utilizar as informações exclusivamente para execução do objeto contratado;
b) Não divulgar a terceiros, mesmo após o término desta relação;
c) Adotar medidas de segurança equivalentes às aplicadas às próprias informações confidenciais;
d) Comunicar imediatamente qualquer suspeita de vazamento ou acesso não autorizado;
e) Não copiar ou reproduzir código-fonte além do estritamente necessário.

**Cláusula 3 — Exclusões**
Não são confidenciais informações que:
a) Já eram de domínio público antes da revelação;
b) Tornaram-se públicas sem culpa da Receptora;
c) Foram recebidas legitimamente de terceiro sem restrição de confidencialidade;
d) Foram desenvolvidas independentemente pela Receptora.

**Cláusula 4 — Vigência**
Este acordo tem vigência de **5 (cinco) anos** a partir da data de assinatura, independentemente do término da relação comercial.

**Cláusula 5 — Penalidade**
O descumprimento deste acordo sujeita a Receptora ao pagamento de indenização mínima de R$ 50.000,00 (cinquenta mil reais), sem prejuízo de perdas e danos adicionais comprovados.

**Cláusula 6 — Foro**
Comarca de Manaus/AM, com renúncia a qualquer outro.

---

## MODELO B — NDA com Parceiro de Contencioso

**Quando usar:** Ao compartilhar informações com advogados externos, peritos ou escritórios jurídicos envolvidos em disputas, reclamações trabalhistas (52 CLT) ou processos relacionados aos 13 condomínios clientes.

---

**ACORDO DE CONFIDENCIALIDADE — CONTENCIOSO JURÍDICO**

**Partes:**
- **CLIENTE:** JORDAN SANTOS DE JESUS LTDA, CNPJ 35.710.481/0001-03 ("Conecta Mais")
- **PROFISSIONAL/ESCRITÓRIO:** [Nome/OAB], [Endereço] ("Profissional")

**Cláusula 1 — Objeto**
Este instrumento complementa o contrato de prestação de serviços jurídicos, definindo obrigações adicionais de sigilo sobre informações operacionais e de negócio da Conecta Mais.

**Cláusula 2 — Informações Protegidas**
São protegidas por este acordo:
- Dados individuais de funcionários envolvidos em processos trabalhistas (fichas, contratos, PPP, CTPS)
- Dados de clientes (condomínios) envolvidos em disputas contratuais
- Valores pagos ou a pagar em acordos extrajudiciais
- Estratégia jurídica e pareceres
- Imagens de CFTV utilizadas como prova
- Dados biométricos eventualmente requeridos

**Cláusula 3 — Obrigações Específicas**
O Profissional se obriga a:
a) Não utilizar os dados para captação de clientes ou situações diversas do mandato;
b) Destruir ou devolver documentos físicos após o trânsito em julgado;
c) Apagar dados eletrônicos recebidos no prazo de 30 dias após encerramento do mandato;
d) Não comentar publicamente sobre o caso em qualquer meio (incluindo redes sociais).

**Cláusula 4 — Vigência**
Enquanto durar o mandato + 5 anos após o encerramento definitivo do processo.

**Cláusula 5 — Independência do Sigilo Profissional**
Este acordo não substitui o sigilo profissional do advogado (OAB, EAOAB), mas o complementa para fins contratuais.

**Cláusula 6 — Foro**
Comarca de Manaus/AM.

---

## MODELO C — NDA com Fornecedor de Condomínio (Prestador Terceiro)

**Quando usar:** Ao integrar fornecedores do condomínio (ex.: construtoras, empresas de limpeza, administradoras) que precisam de acesso temporário ao sistema de segurança (imagens, controle de acesso) nos condomínios clientes da Conecta Mais.

---

**ACORDO DE CONFIDENCIALIDADE — PRESTADOR TERCEIRO EM CONDOMÍNIO**

**Partes:**
- **OPERADOR DE SEGURANÇA:** JORDAN SANTOS DE JESUS LTDA ("Conecta Mais"), CNPJ 35.710.481/0001-03
- **CONDOMÍNIO CONTROLADOR:** [Nome do Condomínio], CNPJ [___], representado por [Síndico/Administradora]
- **PRESTADOR TERCEIRO:** [Nome/Razão Social], [CNPJ/CPF]

> **Nota LGPD:** Neste modelo, o Condomínio é o Controlador dos dados dos moradores; a Conecta Mais é Operadora; o Prestador Terceiro é Sub-operador temporário.

**Cláusula 1 — Dados Acessados**
O Prestador terá acesso temporário a:
- Imagens de CFTV de áreas específicas (definidas em Anexo)
- Registros de controle de acesso de veículos/pedestres
- Eventual dado de morador para coordenação de obras/serviços

**Cláusula 2 — Restrições Absolutas**
É vedado ao Prestador:
a) Copiar, gravar ou exportar imagens ou dados do sistema;
b) Compartilhar credenciais de acesso com terceiros;
c) Utilizar os dados para finalidade diversa do serviço contratado com o Condomínio;
d) Reter imagens ou informações após o término dos serviços.

**Cláusula 3 — Prazo de Acesso**
O acesso é temporário: [DATA INÍCIO] a [DATA FIM] (máximo 90 dias, renovável).

**Cláusula 4 — Responsabilidade Solidária**
O Prestador responde solidariamente com o Condomínio por danos decorrentes do uso indevido dos dados.

**Cláusula 5 — Foro**
Comarca de Manaus/AM.

---

## Checklist NDA

- [ ] Partes identificadas com CNPJ/CPF corretos
- [ ] Modelo adequado selecionado (A/B/C)
- [ ] Escopo de informações confidenciais definido em Anexo (quando necessário)
- [ ] Prazo de vigência definido
- [ ] Penalidade/indenização mínima definida (Modelo A)
- [ ] Assinatura das partes + 2 testemunhas
- [ ] Registro no GED do Conecta PRO
- [ ] Cópia enviada à outra parte por e-mail

---

## Referências Legais

- Código Civil arts. 421, 422 (boa-fé contratual)
- Lei 9.609/1998 (proteção de software — código-fonte)
- Lei 13.709/2018 LGPD (arts. 37, 39 — contratos entre controlador e operador)
- Código de Ética e Disciplina da OAB (sigilo profissional — Modelo B)
