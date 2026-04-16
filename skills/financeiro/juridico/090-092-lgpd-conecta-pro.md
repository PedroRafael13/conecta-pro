# SKILL 090+092 — LGPD: Política de Privacidade + Checklist Conecta Mais
**Versão:** 2026-01
**Empresa:** JORDAN SANTOS DE JESUS LTDA (Conecta Mais — Segurança e Tecnologia)
**CNPJ:** 35.710.481/0001-03 | Manaus/AM
**Aplicação:** Compliance LGPD para sistemas de CFTV, biometria, GPS e dados operacionais

---

## 090 — Política de Privacidade e Proteção de Dados

### Controlador de Dados
**Razão Social:** JORDAN SANTOS DE JESUS LTDA
**Nome Fantasia:** Conecta Mais — Segurança e Tecnologia
**CNPJ:** 35.710.481/0001-03
**Endereço:** Manaus/AM (endereço completo conforme contrato social)
**DPO (Encarregado):** A nomear — até 2026-06-01
**E-mail privacidade:** privacidade@conectamais.pro

---

### Dados Coletados e Finalidades

#### 1. Imagens de CFTV (câmeras de segurança)
| Dado | Base Legal | Finalidade | Retenção |
|------|-----------|------------|---------|
| Imagens de áreas comuns (câmeras externas/internas) | Art. 7º VI — legítimo interesse (segurança patrimonial) | Monitoramento, investigação de incidentes, registro | 30 dias (padrão); 90 dias se houver incidente registrado |
| Imagens de faces identificáveis | Art. 11 II (a) — consentimento explícito OU Art. 11 II (g) — tutela da saúde/segurança | Controle de acesso + monitoramento | 30 dias |

> **ATENÇÃO:** Imagens com faces identificáveis são **dados sensíveis** (art. 5º II LGPD). Requerem consentimento explícito individualizado por escrito OU enquadramento em hipótese do art. 11.

#### 2. Dados biométricos (reconhecimento facial / leitura de placa LPR)
| Dado | Base Legal | Finalidade | Retenção |
|------|-----------|------------|---------|
| Template biométrico facial | Art. 11 II (a) — consentimento explícito | Autenticação/controle de acesso em Portaria Remota | Vigência do contrato + 12 meses |
| Placa de veículo (LPR) | Art. 7º VI — legítimo interesse (segurança) | Controle de acesso de veículos | 90 dias |

#### 3. Dados de colaboradores (52 CLT)
| Dado | Base Legal | Finalidade | Retenção |
|------|-----------|------------|---------|
| CPF, RG, dados admissionais | Art. 7º II — cumprimento de obrigação legal (CLT, eSocial) | Folha de pagamento, obrigações trabalhistas | 5 anos após desligamento (prazo prescricional) |
| Localização GPS (campo) | Art. 7º VI — legítimo interesse OU contrato | Rastreamento de equipes técnicas em campo | 60 dias |
| Ponto eletrônico (biometria) | Art. 7º V — execução de contrato | Controle de jornada (CLT art. 74) | 5 anos |
| Fotos para crachá/ERP | Art. 7º II — obrigação legal | Identificação funcional | Vigência do contrato de trabalho |

#### 4. Dados de clientes (condomínios — 13 clientes)
| Dado | Base Legal | Finalidade | Retenção |
|------|-----------|------------|---------|
| CNPJ, dados do síndico/administrador | Art. 7º V — execução de contrato | Gestão contratual, NFS-e, cobrança | Vigência + 5 anos |
| Dados dos moradores/condôminos | Art. 7º VI — legítimo interesse | Controle de acesso em Portaria Remota | Vigência do contrato |

---

### Direitos dos Titulares

Os titulares podem exercer os seguintes direitos através de `privacidade@conectamais.pro`:

1. **Confirmação** de que dados são tratados
2. **Acesso** aos dados tratados
3. **Correção** de dados incompletos ou desatualizados
4. **Anonimização, bloqueio ou eliminação** (dados desnecessários ou tratados em desconformidade)
5. **Portabilidade** a outro fornecedor de serviço
6. **Revogação do consentimento** (quando base legal for consentimento)
7. **Oposição** ao tratamento

**Prazo de resposta:** 15 dias úteis (conforme ANPD/Regulamento de Fiscalização)

---

### Compartilhamento de Dados

| Destinatário | Dados | Finalidade | Instrumento |
|-------------|-------|------------|-------------|
| Receita Federal / SEFAZ-AM | CNPJ, NF-e/NFS-e | Obrigação fiscal | Lei 6.404/76, CTN |
| INSS / CEF (FGTS) / eSocial | Dados trabalhistas CLT | Obrigação legal | CLT, Lei 8.036/90 |
| Banco (cobrança) | CPF/CNPJ, valor | Cobrança via boleto/PIX | Contrato financeiro |
| Hostinger (VPS 82.25.75.74) | Dados do ERP | Hospedagem do sistema | DPA Hostinger |
| Operadores de monitoramento | Imagens CFTV | Monitoramento 24h | Contrato de emprego CLT |

**Não compartilhamos** dados com terceiros para fins comerciais ou de marketing sem consentimento.

---

### Segurança dos Dados

- Acesso ao ERP restrito por autenticação JWT + 2FA
- Dados em repouso: PostgreSQL com criptografia de volume no servidor Hostinger KVM4
- Dados em trânsito: HTTPS/TLS 1.3 obrigatório
- Backup diário automatizado com retenção de 30 dias
- Logs de acesso e auditoria retidos por 6 meses
- Acesso por perfil de usuário (RBAC implementado no ERP)

---

### Incidentes de Segurança

Em caso de incidente envolvendo dados pessoais:
1. Equipe técnica identifica e contém o incidente
2. Avaliação de risco em até 24h
3. Se risco relevante: comunicação à ANPD em até **72 horas** (art. 48 LGPD)
4. Comunicação aos titulares afetados em prazo razoável
5. Registro interno no GED do ERP

---

## 092 — Checklist LGPD Operacional

### A. Antes de Implantar Sistema CFTV/Portaria Remota

- [ ] **Mapeamento de câmeras:** Identificar quais enquadram pessoas (faces visíveis)
- [ ] **Sinalização física:** Placas "ÁREA MONITORADA POR CÂMERAS" em todos os pontos de coleta
- [ ] **Aviso legal digital:** Informativo sobre CFTV no contrato de prestação de serviços (Anexo)
- [ ] **DPA assinado:** Data Processing Agreement entre Conecta Mais (operador) e condomínio (controlador)
- [ ] **Consentimento biometria:** Se sistema de reconhecimento facial, coletar consentimento escrito de CADA titular (morador/visitante frequente)
- [ ] **Base legal documentada:** Registrar no GED qual base legal justifica o tratamento (Art. 7º ou 11)
- [ ] **Período de retenção definido:** Configurar deletagem automática (30 ou 90 dias conforme caso)

### B. Dados de Colaboradores (RH/DP)

- [ ] **Aviso de privacidade no contrato CLT:** Cláusula de ciência sobre dados tratados
- [ ] **GPS em campo:** Comunicado formal aos funcionários sobre rastreamento durante expediente
- [ ] **Ponto biométrico:** Comunicado sobre coleta de digital/facial para controle de jornada
- [ ] **Acesso ao ERP:** Apenas pessoal autorizado; logs habilitados
- [ ] **Desligamento:** Procedimento de revogação de acessos e anonimização após 5 anos

### C. Dados de Clientes (CRM/GED)

- [ ] **Aviso de privacidade:** Incluído em todos os contratos (Tipo A, B, C)
- [ ] **Portal do cliente:** Informação sobre dados tratados visível no login
- [ ] **Retenção contratual:** Dados apagados ou anonimizados após 5 anos do encerramento do contrato
- [ ] **Responsabilidade do condomínio:** DPA assinado quando condomínio é o controlador dos dados de moradores

### D. Gestão Contínua

- [ ] **Registro de Operações (ROPA):** Atualizar inventário de tratamentos quando novo serviço iniciar
- [ ] **Treinamento anual:** Todos os funcionários que acessam dados pessoais — pelo menos 1h/ano
- [ ] **DPO nomeado até 06/2026:** Publicar canal de contato no site e nos contratos
- [ ] **Revisão anual da política:** Janeiro de cada ano (próxima: 01/2027)
- [ ] **Testes de acesso indevido:** Simulação trimestral de phishing/acesso não autorizado

### E. Dados Sensíveis — Atenção Redobrada

> Dados sensíveis (art. 5º II LGPD): biometria facial, dados de saúde (ocupacional), origem racial, convicções religiosas, filiação sindical.

- [ ] Mapeamento específico de todos os dados sensíveis tratados
- [ ] Base legal: exclusivamente Art. 11 (não Art. 7º)
- [ ] Consentimento explícito individualizado por escrito (quando aplicável)
- [ ] Acesso ainda mais restrito: apenas DPO e gestor direto
- [ ] Relatório de Impacto (RIPD) elaborado antes de implantar sistema biométrico

---

## Referências Legais

- Lei 13.709/2018 (LGPD) — arts. 5, 7, 11, 46, 48
- Resolução ANPD CD/ANPD nº 4/2023 (comunicação de incidentes)
- ABNT NBR ISO/IEC 29101:2023 (Privacy Architecture Framework)
- Portaria ANPD 11/2021 (comunicação de incidentes — prazo 72h)
