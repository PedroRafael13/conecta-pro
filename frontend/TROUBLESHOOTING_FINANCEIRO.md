# Troubleshooting - Módulo Financeiro

**Data**: 2026-02-02
**Status**: ✅ CORRIGIDO - Aguardando validação
**Versão**: 2.0.0

---

## 🎯 Resumo Executivo

Foram identificados e corrigidos **3 problemas críticos** no módulo Financeiro que impediam a criação de registros (Fornecedores, Clientes, Contas a Pagar/Receber):

### Problemas Identificados

1. **Missing `condominio_id` (422 Unprocessable Entity)**
   - Backend exigia `condominio_id: UUID` em todos os endpoints Financial
   - Frontend (hooks Orval) não estava enviando o parâmetro

2. **Trailing Slash (307 Redirect)**
   - URLs geradas pelo Orval terminavam com `/` (ex: `/suppliers/`)
   - FastAPI fazia redirect 307, perdendo o body das requisições POST

3. **Path Duplicado (405 Method Not Allowed)** ⭐ **CRÍTICO**
   - OpenAPI spec estava gerando rotas duplicadas:
     - `/api/v1/financial/suppliers/suppliers/` ❌
     - `/api/v1/financial/customers/customers/` ❌
   - Backend só aceita:
     - `/api/v1/financial/suppliers/` ✅
     - `/api/v1/financial/customers/` ✅

---

## 🔧 Correções Implementadas

### Arquivo: `src/lib/api-client.ts`

```typescript
export const customInstance = async <T>(
  config: AxiosRequestConfig,
): Promise<T> => {
  try {
    if (config.url) {
      // 1. Remove barra final para evitar redirect 307
      if (config.url.endsWith('/') && !config.url.endsWith('://')) {
        config.url = config.url.slice(0, -1);
      }

      // 2. Remove duplicações de path (ex: /suppliers/suppliers -> /suppliers)
      config.url = config.url.replace(/\/([^\/]+)\/\1(?:\/|$)/, '/$1');

      // 3. Adiciona condominio_id automaticamente para endpoints Financial
      if (config.url.includes('/financial/')) {
        console.log('[API Client] Financial endpoint:', config.url);

        if (!config.params) {
          config.params = {};
        }
        if (!config.params.condominio_id) {
          config.params.condominio_id = DEFAULT_CONDOMINIO_ID;
          console.log('[API Client] Added condominio_id:', DEFAULT_CONDOMINIO_ID);
        }
      }
    }

    const response: AxiosResponse<T> = await api.request<T>(config);
    return response.data;
  } catch (error) {
    throw error as AxiosError;
  }
};
```

**O que faz:**
- ✅ Remove trailing slash das URLs
- ✅ Corrige paths duplicados automaticamente
- ✅ Injeta `condominio_id` em todas requisições Financial
- ✅ Loga no console para debug

---

## 🧪 Guia de Teste

### Pré-requisitos
1. Limpar cache do navegador (obrigatório):
   - Chrome/Edge: `Ctrl+Shift+Delete` → Selecionar "Cache" → Limpar
   - Ou fazer hard refresh: `Ctrl+Shift+R`

2. Abrir Console do navegador:
   - Pressionar `F12` ou `Ctrl+Shift+I`
   - Ir na aba "Console"

### Teste 1: Criar Fornecedor

1. Acessar: https://erp.conectamais.pro/modulos/financeiro/fornecedores
2. Clicar em "Novo Fornecedor"
3. Preencher dados de teste:
   ```
   Nome: TESTE_E2E_FORNECEDOR_001
   Documento: 12345678000199
   Email: teste@teste.com
   Telefone: (11) 99999-9999
   ```
4. Clicar em "Cadastrar"

**Resultado Esperado:**
- ✅ Console mostra:
  ```
  [API Client] Financial endpoint: /api/v1/financial/suppliers
  [API Client] Added condominio_id: a1b2c3d4-e5f6-7890-abcd-ef1234567890
  ```
- ✅ Network tab mostra:
  - Request URL: `/api/v1/financial/suppliers?condominio_id=...`
  - Method: `POST`
  - Status: `201 Created` ou `200 OK`
- ✅ Fornecedor criado com sucesso
- ❌ **Se falhar**: Copiar Request URL, Method, Status e Response body

### Teste 2: Criar Cliente

1. Acessar: https://erp.conectamais.pro/modulos/financeiro/clientes
2. Clicar em "Novo Cliente"
3. Preencher dados de teste:
   ```
   Nome: TESTE_E2E_CLIENTE_001
   Documento: 12345678901
   Email: cliente@teste.com
   ```
4. Clicar em "Cadastrar"

**Resultado Esperado:**
- ✅ Console mostra URL correta: `/api/v1/financial/customers`
- ✅ Status: `201 Created`
- ✅ Cliente criado com sucesso

### Teste 3: Listar Registros

1. Verificar se Fornecedores e Clientes aparecem nas listagens
2. Console deve mostrar:
   ```
   [API Client] Financial endpoint: /api/v1/financial/suppliers
   [API Client] Added condominio_id: ...
   ```

---

## 📋 Checklist de Validação

- [ ] Fornecedores - Novo registro criado sem erro
- [ ] Clientes - Novo registro criado sem erro
- [ ] Contas a Pagar - Nova conta criada
- [ ] Contas a Receber - Nova conta criada
- [ ] Fluxo de Caixa - Novo lançamento criado
- [ ] Console mostra logs corretos do api-client
- [ ] Network tab não mostra erro 405, 422 ou Network Error

---

## 🔍 Troubleshooting

### Se ainda houver erro 405

**Sintoma**: `POST /api/v1/financial/customers HTTP/1.1 405 Method Not Allowed`

**Diagnóstico**:
1. Abrir Network tab (F12)
2. Verificar "Request URL" da requisição que falhou
3. Se a URL ainda estiver duplicada (`/customers/customers`):
   - Verificar se o cache foi limpo
   - Verificar se o frontend foi redeployado corretamente
   - Verificar logs do console: deveria mostrar URL corrigida

### Se ainda houver erro 422

**Sintoma**: `GET /api/v1/financial/customers?... HTTP/1.1 422 Unprocessable Entity`

**Diagnóstico**:
1. Ver Response body do erro (deve indicar qual campo está faltando)
2. Verificar se `condominio_id` está nos query params
3. Se não estiver, verificar console logs

### Se houver Network Error

**Sintoma**: `Error: Network Error` no console

**Possíveis causas**:
1. CORS bloqueando requisição
2. Backend não está respondendo
3. Timeout na requisição
4. SSL/TLS issues

**Diagnóstico**:
```bash
# No servidor, verificar logs do backend:
docker logs conecta-pro-backend --tail 50 | grep -E "ERROR|Exception|financial"

# Verificar se backend está rodando:
docker ps --filter "name=backend"

# Testar endpoint direto:
curl -X POST https://erp.conectamais.pro/api/v1/financial/suppliers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"nome":"Teste",...}'
```

---

## 📊 Logs e Monitoramento

### Backend Logs
```bash
# Ver logs em tempo real:
docker logs -f conecta-pro-backend | grep financial

# Ver últimos 100 erros:
docker logs conecta-pro-backend --tail 500 | grep -E "ERROR|Exception|405|422"
```

### Frontend Logs
```bash
# Ver logs do container:
docker logs -f conecta-pro-frontend

# Verificar se está rodando:
docker ps --filter "name=frontend"
```

---

## 🚀 Próximos Passos (Se Validado)

1. **Remover logs de debug** do api-client.ts (console.log)
2. **Corrigir OpenAPI spec** para evitar duplicações na origem
3. **Criar ambiente de homologação** para testes E2E sem afetar produção
4. **Adicionar testes automatizados** para validar criação de registros
5. **Documentar condominio_id** como requisito obrigatório do módulo Financial

---

## 📝 Histórico de Mudanças

| Data | Versão | Mudança |
|------|--------|---------|
| 2026-02-02 | 1.0.0 | Correções iniciais (condominio_id + trailing slash + path duplicado) |

---

## 🆘 Suporte

Se os problemas persistirem após seguir este guia:

1. Coletar dados do erro:
   - Screenshot do console (F12)
   - Network tab → Request/Response completo
   - Backend logs: `docker logs conecta-pro-backend --tail 200`

2. Verificar versões:
   ```bash
   docker images | grep conecta-pro-frontend
   docker ps --filter "name=conecta-pro-frontend" --format "{{.CreatedAt}}"
   ```

3. Reportar no GitHub Issues com:
   - Passos para reproduzir
   - Dados coletados acima
   - Módulo e operação que falhou
