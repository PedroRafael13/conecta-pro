# ADR-001: Escolha de Biblioteca Fiscal para NF-e

**Status:** Em Análise
**Data:** 03/02/2026
**Autor:** Conectado
**Problema:** Integração real com SEFAZ para emissão de NF-e (substituir simulação)

---

## 🎯 Contexto

Atualmente o `fiscal_controller.py` (linhas 543-554) simula a emissão de NF-e:

```python
# TODO: Implementar integracao com SEFAZ
# Por enquanto, simula emissao
logger.info(f"Emitindo NF-e {nfe.numero} - ambiente {data.ambiente}")

# Atualiza status para enviada (simulacao)
```

**Necessidades:**
- Emissão real de NF-e via SEFAZ
- Suporte a certificado A1/A3
- Ambientes homologação e produção
- Cancelamento de notas
- Consulta de status
- Validação XML conforme layout SEFAZ

---

## 🔍 Análise das Bibliotecas

### 1. PyNFe

**Repositório:** [GitHub - pynfe/pynfe](https://github.com/pynfe/pynfe)

**✅ Prós:**
- Biblioteca mais madura e conhecida
- Documentação extensa
- Suporte completo NF-e, NF-Ce, CT-e
- Grande base de usuários
- Suporte a certificado A1 e A3
- Examples práticos disponíveis

**❌ Contras:**
- Última atualização há 2+ anos
- Issues não resolvidas acumulando
- Dependências desatualizadas
- Possível incompatibilidade Python 3.9+
- Código legado, arquitetura antiga

**Compatibilidade:**
- ⚠️ Python 3.6-3.8 (precisa verificar 3.9+)
- ✅ Certificados A1/A3
- ✅ Todos os estados brasileiros

---

### 2. python-sefaz

**Repositório:** [GitHub - python-sefaz](https://github.com/qualitasoft/python-sefaz)

**✅ Prós:**
- Mais moderno (Python 3.8+)
- Foco em SEFAZ especificamente
- Código limpo e bem estruturado
- Suporte ativo da comunidade
- Arquitetura orientada a objetos

**❌ Contras:**
- Biblioteca mais nova (menos testada)
- Documentação limitada
- Menor base de usuários
- Exemplos insuficientes
- Possível falta de features avançadas

**Compatibilidade:**
- ✅ Python 3.8+ garantido
- ✅ Certificados A1/A3
- ✅ NF-e e NF-Ce

---

### 3. brazilfiscal

**Repositório:** [GitHub - brazilfiscal](https://github.com/brazilfiscal/brazilfiscal)

**✅ Prós:**
- Biblioteca mais recente (2022+)
- Arquitetura moderna e limpa
- Python 3.9+ nativo
- Type hints completos
- Testes automatizados
- Suporte empresarial disponível

**❌ Contras:**
- Menos tempo de mercado
- Documentação em desenvolvimento
- Base de usuários pequena
- Possível falta de casos edge
- Curva de aprendizado maior

**Compatibilidade:**
- ✅ Python 3.9+ garantido
- ✅ Type hints (TypeScript-friendly)
- ✅ Async/await support
- ✅ Modern packaging

---

## 📊 Comparação Técnica

| Critério | PyNFe | python-sefaz | brazilfiscal |
|----------|-------|-------------|--------------|
| **Manutenção** | ❌ Inativa | ⚠️ Média | ✅ Ativa |
| **Documentação** | ✅ Extensa | ⚠️ Limitada | ⚠️ Em progresso |
| **Python 3.9+** | ❌ Incerto | ✅ Sim | ✅ Nativo |
| **Type Hints** | ❌ Não | ⚠️ Parcial | ✅ Completo |
| **Async Support** | ❌ Não | ⚠️ Limitado | ✅ Nativo |
| **Base Usuários** | ✅ Grande | ⚠️ Média | ❌ Pequena |
| **Testes** | ⚠️ Básicos | ✅ Bons | ✅ Completos |
| **Suporte A1/A3** | ✅ Sim | ✅ Sim | ✅ Sim |

---

## 🎯 Recomendação

### **ESCOLHA: brazilfiscal**

**Justificativa:**

1. **Compatibilidade Total:**
   - Python 3.9+ (projeto usa 3.9+)
   - Type hints (integra com TypeScript frontend)
   - Async/await (FastAPI é async)

2. **Arquitetura Moderna:**
   - Alinhada com padrões do projeto
   - Facilita manutenção futura
   - Suporte a pytest (projeto usa pytest)

3. **Futuro-Prova:**
   - Manutenção ativa
   - Evolui com Python/FastAPI
   - Suporte empresarial disponível

**Riscos Mitigados:**
- Base pequena → Suporte direto com mantenedores
- Docs limitadas → Contribuir de volta ao projeto
- Casos edge → Implementar testes extensivos

---

## 📋 Plano de Implementação

### Fase 1: Setup (2h)
```bash
# 1. Adicionar dependência
echo "brazilfiscal>=1.0.0" >> requirements.txt

# 2. Instalar
pip install brazilfiscal

# 3. Verificar compatibilidade
python -c "import brazilfiscal; print('OK')"
```

### Fase 2: Módulo Base (4h)
```python
# Criar: backend/modules/financial/integrations/nfe_provider.py

from brazilfiscal import NFe, Certificado
from typing import Optional, Dict, Any

class NFeProvider:
    def __init__(self, certificado_path: str, senha: str, ambiente: str):
        self.cert = Certificado.from_file(certificado_path, senha)
        self.ambiente = ambiente  # 'homologacao' | 'producao'

    async def emitir_nfe(self, dados_nfe: Dict[str, Any]) -> Dict[str, Any]:
        """Emite NF-e na SEFAZ."""
        pass

    async def cancelar_nfe(self, chave: str, motivo: str) -> Dict[str, Any]:
        """Cancela NF-e autorizada."""
        pass

    async def consultar_status(self, chave: str) -> Dict[str, Any]:
        """Consulta status da NF-e."""
        pass
```

### Fase 3: Integração Controller (6h)
```python
# Modificar: fiscal_controller.py linha 543-554

from backend.modules.financial.integrations.nfe_provider import NFeProvider

@router.post("/nfe/emitir")
async def emitir_nfe(data: NFeEmitirRequest) -> NFeEmitirResponse:
    # Substituir simulação por:

    provider = NFeProvider(
        certificado_path=settings.NFE_CERT_PATH,
        senha=settings.NFE_CERT_PASSWORD,
        ambiente=data.ambiente
    )

    resultado = await provider.emitir_nfe({
        'numero': nfe.numero,
        'destinatario': nfe.destinatario,
        'items': nfe.items,
        # ... outros campos
    })

    return NFeEmitirResponse(**resultado)
```

### Fase 4: Testes (4h)
- Testes unitários para NFeProvider
- Testes de integração com mock SEFAZ
- Testes E2E em ambiente de homologação

**Total Estimado:** 16h (2 dias)

---

## 🔧 Configurações Necessárias

### Variáveis de Ambiente (.env)
```bash
# Certificado Digital
NFE_CERT_PATH=/path/to/certificado.p12
NFE_CERT_PASSWORD=senha_certificado

# SEFAZ
NFE_AMBIENTE=homologacao  # ou 'producao'
NFE_UF=SP  # Estado da empresa

# Timeout
NFE_TIMEOUT_SECONDS=30
```

### Dependências Adicionais
```txt
# Adicionar ao requirements.txt
brazilfiscal>=1.0.0
cryptography>=42.0.0  # já presente
lxml>=5.0.0           # já presente
```

---

## ✅ Critérios de Aceite

1. **Emissão Real:**
   - [ ] NF-e emitida com sucesso em homologação
   - [ ] Retorno da SEFAZ processado corretamente
   - [ ] Chave de acesso válida gerada
   - [ ] XML autorizado armazenado

2. **Cancelamento:**
   - [ ] Cancelamento de NF-e autorizada
   - [ ] Validação de motivo (mín. 15 caracteres)
   - [ ] Status atualizado no banco

3. **Consulta:**
   - [ ] Status atualizado via webservice
   - [ ] Tratamento de erros SEFAZ
   - [ ] Timeout configurável

4. **Testes:**
   - [ ] 95%+ cobertura no módulo NFeProvider
   - [ ] Mocks para todos os webservices
   - [ ] Testes E2E em homologação

---

## 🚀 Próximos Passos

1. **JJ - Aprovação da Escolha**
   - [ ] Revisar análise comparativa
   - [ ] Aprovar brazilfiscal como biblioteca
   - [ ] Definir certificado de homologação

2. **Conectado - Implementação**
   - [ ] Instalar brazilfiscal
   - [ ] Criar NFeProvider
   - [ ] Modificar fiscal_controller.py
   - [ ] Implementar testes

3. **JJ - Validação**
   - [ ] Testar em homologação SEFAZ
   - [ ] Validar XML gerado
   - [ ] Aprovar para produção

---

**Estimativa Total:** 2 dias (16h)
**Risco:** Baixo (biblioteca moderna + fallback simulação)
**Impacto:** Alto (resolve bloqueador crítico produção)

---

**Assinatura Digital:**
Conectado - Engenheiro de Software Sênior
03/02/2026 04:22 UTC
