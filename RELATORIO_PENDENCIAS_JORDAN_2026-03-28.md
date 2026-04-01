# Relatório de Pendências REAL — Conecta PRO

**Data:** 28/03/2026 (revisado) | **Para:** Jordan Santos de Jesus (CEO)

---

## VEREDITO: O QUE REALMENTE ESTÁ PENDENTE

Após auditoria ao vivo de todos os endpoints e serviços, a maioria do que listei antes **já está funcionando**. Peço desculpas pela confusão — o relatório anterior misturou itens já resolvidos com pendências reais.

Aqui está a verdade, testada agora:

---

## JÁ FUNCIONA (não precisa fazer nada)

| Item | Prova | Status |
|------|-------|--------|
| **NFS-e Manaus** | `nfse-manaus/status` → HTTP 200, ambiente produção, certificado OK | Funcional |
| **Certificado A1** | Válido até 13/01/2027, configurado e reconhecido | OK |
| **Bartolo IA** | `bartolo/health` → HTTP 200, "pronto para ajudar" | Funcional |
| **Briefing CEO** | `briefing/status` → HTTP 200, Telegram configurado, próximo 07:30 | Funcional |
| **Telegram Bot** | PM2 online há 18min, polling ativo | Funcional |
| **Cron Briefing** | `crontab -l` → 07:30 seg-sex configurado | Funcional |
| **Admissão** | 5 admissões no banco, fluxo E2E completo | Funcional |
| **Contratos DP** | 42+ contratos, endpoint 200 | Funcional |
| **Condominiums** | HTTP 200 (bug 500 corrigido hoje!) | Funcional |
| **Operacional** | 12 postos, escalas, alocações, tudo 200 | Funcional |
| **Clientes** | 15 clientes cadastrados | Funcional |
| **NFS-e Entrada** | resumo-fiscal → HTTP 200 | Funcional |
| **Contas Bancárias** | 2 contas cadastradas | Funcional |
| **GED** | Upload, assinatura, certidões | Funcional |
| **OpenClaw** | Quality checks e dashboard | Funcional |
| **Gov.br OAuth2** | **NÃO PRECISA** — Certificado A1 cobre tudo | Dispensável |

---

## PENDÊNCIAS REAIS (apenas 3 itens)

### 1. CRF do FGTS — VENCE EM 3 DIAS

**Quem:** Você (Jordan)
**Urgência:** CRÍTICA
**Tempo:** 30 minutos

Isso NÃO é do sistema — é uma certidão que você renova no portal da Caixa:

1. Acesse `https://fgtsdigital.caixa.gov.br` com seu certificado A1
2. Menu: Regularidade → Emitir CRF
3. Se tiver débito, gere guia e pague via PIX
4. Baixe o PDF

**Por que importa:** Sem CRF você não participa de licitações e clientes podem questionar regularidade.

---

### 2. eSocial S-2200 — Dados dos Funcionários

**Quem:** Contador
**Urgência:** ALTA (mensal)
**Tempo:** Email de 5 minutos para o contador

O sistema TEM o transmissor de eSocial implementado, mas para transmitir o evento S-2200 (admissão), precisa de dados que só o contador tem:

- Data de nascimento, sexo, estado civil de cada funcionário
- Endereço completo com CEP
- Grau de instrução, nome da mãe
- Dados de dependentes

**Email pronto para enviar ao contador:**

> Assunto: Dados para eSocial S-2200
>
> Preciso de uma planilha com os dados dos 44 funcionários ativos: data de nascimento, sexo, estado civil, raça/cor, grau de instrução, nome da mãe, naturalidade, endereço completo com CEP, e dependentes. Pode me enviar em Excel?

---

### 3. NFS-e de Março — Emitir as Notas

**Quem:** Você ou financeiro
**Urgência:** ALTA (prazo até 10/04)
**Tempo:** 1-2 horas

O sistema emite NFS-e via API (testado, conexão OK com prefeitura de Manaus). Você pode emitir:
- Pelo próprio Conecta PRO (módulo fiscal)
- Ou pelo portal da prefeitura diretamente

Cada cliente ativo recebe 1 nota com código 11.02, ISS 5%.

---

## É SÓ ISSO

**Tudo o resto já funciona.** O sistema está operacional. Os 3 itens acima são ações manuais/externas, não bugs ou implementações faltantes.

Para ficar 100% redondo, o único item de infra que seria "nice to have" (mas não bloqueia nada) é o WebSocket para alertas em tempo real — e isso pode ser feito quando houver necessidade.

---

## PARA DOWNLOAD NO MAC

```bash
scp root@SEU_IP:/opt/conecta-pro/RELATORIO_PENDENCIAS_JORDAN_2026-03-28.md ~/Downloads/
```
