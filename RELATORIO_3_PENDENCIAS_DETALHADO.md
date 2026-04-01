# 3 Pendências — O Que Precisa Para Funcionar no Conecta PRO

**Data:** 28/03/2026 | **Para:** Jordan Santos de Jesus

---

## 1. NFS-e MARÇO — Emitir Notas dos Clientes

### O que já funciona no sistema

- API de emissão conectada à Prefeitura de Manaus (ABRASF 2.04) — **PRODUÇÃO**
- Certificado A1 configurado e válido
- Endpoint `POST /api/v1/government/nfse-manaus/emitir` — **FUNCIONAL**
- Consulta, cancelamento e substituição de notas — **FUNCIONAL**
- Frontend com listagem e formulário de emissão em `/modulos/fiscal/nfse`

### O que falta para emitir as notas de março

**NADA no código.** O sistema já emite. Você só precisa:

1. Acessar `https://erp.conectamais.pro/modulos/fiscal/nfse`
2. Clicar "Emitir NFS-e"
3. Para cada cliente ativo, preencher:

| Campo | O que colocar |
|-------|---------------|
| **CNPJ/CPF do tomador** | CNPJ do condomínio (já cadastrado no sistema) |
| **Razão Social** | Nome do condomínio |
| **Endereço** | Endereço do condomínio |
| **Código do serviço** | 11.02 |
| **Descrição** | "Prestação de serviços de vigilância patrimonial — competência março/2026" |
| **Valor** | Valor do contrato mensal |
| **Alíquota ISS** | 5% |

4. Clicar "Emitir"
5. O sistema envia via API para a prefeitura e retorna o número da NFS-e

### Melhoria possível (não bloqueia)

- Emissão em lote (selecionar vários clientes e emitir de uma vez) — o backend suporta via `enviar_lote_rps`, mas o frontend ainda não tem esse botão. Pode ser implementado se quiser.

### Prazo

Até **10/04/2026** (prazo municipal para emissão de NFS-e da competência anterior).

---

## 2. eSocial S-2200 — Cadastrar Funcionários no Governo

### O que já funciona no sistema

- Transmissor eSocial implementado (`esocial_transmitter.py`)
- 8 tipos de eventos suportados (S-2200 admissão, S-2299 desligamento, S-2210 CAT, etc.)
- Endpoint `POST /api/v1/government/esocial/evento` — **EXISTE**
- Modelo Employee tem **136 campos** incluindo dados pessoais, bancários, documentos

### O que falta para transmitir S-2200

O evento S-2200 exige dados específicos que **não estão no modelo Employee hoje**. Sem esses dados, o XML gerado será rejeitado pelo governo.

**Dados que faltam no cadastro de cada funcionário:**

| Campo Obrigatório | Descrição | Quem tem essa informação |
|-------------------|-----------|--------------------------|
| `data_nascimento` | Data de nascimento | Contador (folha) ou RG do funcionário |
| `sexo` | M ou F | Contador ou RG |
| `estado_civil` | 1=Solteiro, 2=Casado, 3=Divorciado, 4=Viúvo, 5=União Estável | Contador |
| `raca_cor` | 1=Branca, 2=Preta, 3=Parda, 4=Amarela, 5=Indígena | Autodeclaração do funcionário |
| `grau_instrucao` | Código (01=Fund.Incompleto até 12=Doutorado) | Contador ou escolaridade do funcionário |
| `nome_mae` | Nome completo da mãe | RG ou certidão do funcionário |
| `naturalidade` | Código IBGE do município de nascimento (ex: 1302603=Manaus) | Certidão de nascimento |
| `endereco_completo` | Logradouro, número, bairro, CEP, município, UF | Comprovante de residência |
| `dependentes` | Nome, CPF, data nascimento, tipo (cônjuge, filho) | Declaração do funcionário |

**Nota:** O modelo Employee JÁ TEM campos para `data_nascimento`, `sexo`, `estado_civil`, `nome_mae`, endereço e dependentes. O problema é que esses campos estão **vazios** no banco de dados para a maioria dos 44 funcionários.

### O que precisa ser feito

**Ação 1 — Pedir dados ao contador (5 minutos):**

Envie este email:

---

**Para:** [Contador]
**Assunto:** Dados dos funcionários para eSocial S-2200

Preciso de uma planilha Excel com os seguintes dados de cada um dos nossos 44 funcionários ativos:

1. Nome completo (como consta no CPF)
2. CPF
3. Data de nascimento (DD/MM/AAAA)
4. Sexo (M/F)
5. Estado civil (Solteiro/Casado/Divorciado/Viúvo/União Estável)
6. Raça/cor (Branca/Preta/Parda/Amarela/Indígena)
7. Grau de instrução (Fundamental/Médio/Superior/etc.)
8. Nome completo da mãe
9. Município de nascimento
10. Endereço completo com CEP
11. Dependentes (nome, CPF, data nascimento, parentesco)

Pode usar a base da folha de pagamento — a maioria desses dados já está lá.

Att, Jordan

---

**Ação 2 — Importar dados no sistema (eu faço quando receber):**

Quando o contador enviar a planilha, eu crio um script de importação que:
1. Lê o Excel
2. Atualiza cada Employee no banco com os campos faltantes
3. Valida os dados contra as regras do eSocial
4. Gera os XMLs S-2200
5. Transmite para o governo

**Ação 3 — Frontend de eSocial (eu posso implementar):**

Criar formulário em `/modulos/dp/esocial` que:
- Lista funcionários com dados incompletos
- Permite preencher campos faltantes um a um
- Botão "Transmitir S-2200" para cada funcionário pronto
- Status de transmissão (enviado, aceito, rejeitado)

### Prazo

O S-2200 deve ser transmitido **até o dia 15 do mês seguinte à admissão**. Para funcionários já ativos, o governo aceita envio retroativo desde que dentro do prazo de regularização.

---

## 3. CRF FGTS — Renovar Certidão de Regularidade

### O que já funciona no sistema

- Cálculo de FGTS (8% sobre salário) — **FUNCIONAL**
- Geração de guias GRFGTS com PIX — **FUNCIONAL**
- Cálculo de recolhimento rescisório (40%) — **FUNCIONAL**
- Endpoint `POST /api/v1/government/fgts/gerar-guia` — **EXISTE**

### O que a CRF é e por que importa

A CRF (Certificado de Regularidade do FGTS) comprova que a empresa está em dia com o FGTS de todos os funcionários. É exigida para:

- Participar de licitações públicas
- Obter financiamentos
- Distribuir lucros
- Alguns clientes exigem para manter contrato

**A CRF vence em 31/03/2026 (3 dias!).**

### O que falta

A CRF **NÃO pode ser renovada via API** — a Caixa Econômica Federal não disponibiliza essa funcionalidade via integração. É obrigatoriamente manual.

### Passo a passo para renovar

1. Acesse `https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf`
2. Digite o CNPJ: **35.710.481/0001-03**
3. Se aparecer "Regular":
   - Clique em "Emitir CRF"
   - Salve o PDF
   - Faça upload no GED do Conecta PRO (`/modulos/ged`)
4. Se aparecer "Irregular" ou "Débitos Pendentes":
   - Acesse `https://fgtsdigital.caixa.gov.br` com seu certificado A1
   - Menu: **Débitos** → ver quais meses estão pendentes
   - Menu: **Guias** → gerar GRFGTS dos meses pendentes
   - Pagar as guias via PIX (pagamento cai na hora)
   - Após pagamento, voltar ao passo 1 (CRF libera em até 24h)

### O que posso implementar para o futuro

- **Alerta automático** no sistema 30 dias antes do vencimento da CRF
- **Consulta automática** da situação de regularidade (web scraping do portal da Caixa)
- **Dashboard** mostrando status de todas as certidões (CND Federal, CRF FGTS, CND Estadual, CND Municipal)

Isso não bloqueia o uso atual, mas evitaria surpresas no futuro.

---

## RESUMO FINAL

| Pendência | Tipo | Quem Resolve | Quando | Esforço |
|-----------|------|-------------|--------|---------|
| **NFS-e março** | Ação manual | Jordan/Financeiro | Até 10/04 | 1-2h (emitir nota por nota no sistema) |
| **eSocial S-2200** | Dados + implementação | Contador + Claude | Quando contador enviar planilha | 5min email + 2h importação |
| **CRF FGTS** | Ação manual | Jordan | **ATÉ 31/03 (3 DIAS!)** | 30min no portal da Caixa |

### O que EU posso fazer agora se você quiser:

1. **NFS-e em lote** — Implementar botão de emissão em lote no frontend (seleciona clientes → emite todas as notas de uma vez)
2. **eSocial formulário** — Criar página em `/modulos/dp/esocial` para preencher dados faltantes dos funcionários e transmitir S-2200
3. **Alerta de certidões** — Implementar dashboard de vencimento de certidões com alertas automáticos

Me diz o que priorizar.

---

## DOWNLOAD

```bash
scp root@SEU_IP:/opt/conecta-pro/RELATORIO_3_PENDENCIAS_DETALHADO.md ~/Downloads/
```
