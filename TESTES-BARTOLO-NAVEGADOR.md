# 🌐 TESTES BARTOLO - VIA NAVEGADOR (API REST)

**Data:** 31/01/2026  
**Método:** HTTP REST API  
**Ferramentas:** Console do navegador, Postman, Thunder Client, ou curl

---

## 🔧 PREPARAÇÃO

### Opção 1: Console do Navegador (Mais Fácil)

1. Abra seu navegador (Chrome, Firefox, Edge)
2. Vá para: `http://localhost:3000` (ou seu domínio)
3. Pressione `F12` para abrir DevTools
4. Vá na aba **Console**
5. Cole e execute os scripts abaixo

### Opção 2: Postman/Insomnia

1. Abra o Postman
2. Importe a collection ou crie requests manualmente
3. Execute cada teste

### Opção 3: Thunder Client (VS Code)

1. Instale extensão Thunder Client
2. Crie nova request
3. Cole os endpoints

---

## 🔑 PASSO 0 - OBTER TOKEN DE AUTENTICAÇÃO

**Execute PRIMEIRO no console do navegador:**

```javascript
// PASSO 0: Login e obter token
const API_BASE = 'http://localhost:8080';

async function login() {
  const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'username=egonzaga@conectamais.pro&password=Admin@123'
  });
  
  const data = await response.json();
  window.TOKEN = data.access_token;
  window.USER_ID = 1; // Ajuste se necessário
  
  console.log('✅ Login realizado!');
  console.log('Token:', window.TOKEN.substring(0, 30) + '...');
  return data;
}

// Execute o login
await login();
```

**Resultado esperado:**
```
✅ Login realizado!
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...
```

---

## 🟢 TESTE 1 - NÍVEL SIMPLES (Alertas)

**Complexidade:** ⭐ (30 segundos)

### Console do Navegador:
```javascript
// TESTE 1: Consultar alertas
async function teste1_alertas() {
  console.log('🟢 TESTE 1: Consultando alertas...');
  
  const response = await fetch(
    `${API_BASE}/api/v1/ai/bartolo/send?user_id=${window.USER_ID}`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${window.TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: '/alerta',
        session_id: 'test-browser-1',
        module: 'operacional'
      })
    }
  );
  
  const data = await response.json();
  
  console.log('Status:', response.status);
  console.log('Resposta do Bartolo:', data.response);
  console.log('Tempo de processamento:', data.processing_time_ms + 'ms');
  
  return data;
}

// Execute o teste
await teste1_alertas();
```

### Via cURL (Terminal):
```bash
TOKEN="SEU_TOKEN_AQUI"

curl -X POST "http://localhost:8080/api/v1/ai/bartolo/send?user_id=1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "/alerta",
    "session_id": "test-curl-1",
    "module": "operacional"
  }' | jq '.'
```

**Resultado esperado:**
- ✅ Status: 200
- ✅ Response contém lista de alertas
- ✅ Processing time < 500ms

---

## 🟡 TESTE 2 - NÍVEL MÉDIO (Listar Postos)

**Complexidade:** ⭐⭐ (1 minuto)

### Console do Navegador:
```javascript
// TESTE 2: Listar postos
async function teste2_postos() {
  console.log('🟡 TESTE 2: Listando postos...');
  
  const response = await fetch(
    `${API_BASE}/api/v1/ai/bartolo/send?user_id=${window.USER_ID}`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${window.TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: '/posto listar',
        session_id: 'test-browser-2',
        module: 'operacional'
      })
    }
  );
  
  const data = await response.json();
  
  console.log('📍 Postos encontrados:', data.response);
  
  // Verificar se há dados
  if (data.response.includes('posto') || data.response.includes('Posto')) {
    console.log('✅ Lista de postos retornada com sucesso!');
  }
  
  return data;
}

await teste2_postos();
```

**Resultado esperado:**
- ✅ Lista de postos do sistema
- ✅ Dados formatados corretamente

---

## 🟠 TESTE 3 - NÍVEL INTERMEDIÁRIO (Banco de Horas)

**Complexidade:** ⭐⭐⭐ (2 minutos)

### Console do Navegador:
```javascript
// TESTE 3: Banco de horas (multi-step)
async function teste3_bancoHoras() {
  console.log('🟠 TESTE 3: Consultando banco de horas...');
  
  // Passo 1: Resumo geral
  console.log('Passo 1: Resumo geral');
  const resumo = await fetch(
    `${API_BASE}/api/v1/ai/bartolo/send?user_id=${window.USER_ID}`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${window.TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: '/banco_horas resumo',
        session_id: 'test-browser-3',
        module: 'operacional'
      })
    }
  );
  
  const dataResumo = await resumo.json();
  console.log('📊 Resumo:', dataResumo.response);
  
  // Passo 2: Saldo
  console.log('\nPasso 2: Saldo');
  const saldo = await fetch(
    `${API_BASE}/api/v1/ai/bartolo/send?user_id=${window.USER_ID}`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${window.TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: '/banco_horas saldo',
        session_id: 'test-browser-3',
        module: 'operacional'
      })
    }
  );
  
  const dataSaldo = await saldo.json();
  console.log('💰 Saldo:', dataSaldo.response);
  
  console.log('\n✅ Teste multi-step completo!');
  
  return { resumo: dataResumo, saldo: dataSaldo };
}

await teste3_bancoHoras();
```

**Resultado esperado:**
- ✅ Resumo com totais
- ✅ Saldo retornado (pode pedir ID)
- ✅ Ambas respostas < 1s

---

## 🔴 TESTE 4 - NÍVEL AVANÇADO (Wizard de Comunicado)

**Complexidade:** ⭐⭐⭐⭐ (5 minutos)

### Console do Navegador:
```javascript
// TESTE 4: Wizard completo de comunicado
async function teste4_wizardComunicado() {
  console.log('🔴 TESTE 4: Iniciando wizard de comunicado...');
  
  // Passo 1: Iniciar wizard
  const iniciar = await fetch(
    `${API_BASE}/api/v1/ai/bartolo/wizard/start?user_id=${window.USER_ID}`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${window.TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        wizard_type: 'comunicado',
        session_id: 'wizard-test-browser'
      })
    }
  );
  
  const wizardData = await iniciar.json();
  console.log('📝 Wizard iniciado:', wizardData);
  console.log('Pergunta:', wizardData.question);
  console.log('Opções:', wizardData.options);
  console.log('Progresso:', wizardData.progress_percent + '%');
  
  window.WIZARD_ID = wizardData.wizard_id;
  
  // Passo 2: Verificar status
  const status = await fetch(
    `${API_BASE}/api/v1/ai/bartolo/wizard/status?session_id=wizard-test-browser&user_id=${window.USER_ID}`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${window.TOKEN}`
      }
    }
  );
  
  const statusData = await status.json();
  console.log('\n📊 Status do wizard:', statusData);
  console.log('Steps completados:', statusData.completed_steps?.length || 0);
  console.log('Total de steps:', statusData.total_steps);
  
  console.log('\n✅ Wizard funcionando! Para continuar, use /wizard/input');
  console.log('💡 Wizard ID:', window.WIZARD_ID);
  
  return { wizard: wizardData, status: statusData };
}

await teste4_wizardComunicado();

// Para cancelar o wizard depois:
async function cancelarWizard() {
  const response = await fetch(
    `${API_BASE}/api/v1/ai/bartolo/wizard/cancel?user_id=${window.USER_ID}`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${window.TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        session_id: 'wizard-test-browser'
      })
    }
  );
  
  const data = await response.json();
  console.log('Wizard cancelado:', data);
}
```

**Resultado esperado:**
- ✅ Wizard inicia com wizard_id
- ✅ Primeira pergunta é apresentada
- ✅ Opções são listadas
- ✅ Status mostra progresso 0/10

---

## 🔴 TESTE 5 - NÍVEL COMPLEXO (Fluxo Multi-Skill)

**Complexidade:** ⭐⭐⭐⭐⭐ (10 minutos)

### Console do Navegador:
```javascript
// TESTE 5: Fluxo completo multi-skill
async function teste5_fluxoCompleto() {
  console.log('🔴 TESTE 5: Executando fluxo completo...');
  
  const sessionId = 'test-flow-' + Date.now();
  
  // Helper function
  async function enviarMensagem(mensagem, step) {
    console.log(`\n📍 Step ${step}: ${mensagem}`);
    
    const response = await fetch(
      `${API_BASE}/api/v1/ai/bartolo/send?user_id=${window.USER_ID}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${window.TOKEN}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: mensagem,
          session_id: sessionId,
          module: 'operacional'
        })
      }
    );
    
    const data = await response.json();
    console.log('💬 Resposta:', data.response.substring(0, 200) + '...');
    
    return data;
  }
  
  // Fluxo completo
  const step1 = await enviarMensagem('/cobertura hoje', 1);
  await new Promise(r => setTimeout(r, 500)); // Delay
  
  const step2 = await enviarMensagem('/alerta', 2);
  await new Promise(r => setTimeout(r, 500));
  
  const step3 = await enviarMensagem('/posto listar', 3);
  await new Promise(r => setTimeout(r, 500));
  
  const step4 = await enviarMensagem('/banco_horas resumo', 4);
  await new Promise(r => setTimeout(r, 500));
  
  const step5 = await enviarMensagem('/substituto buscar', 5);
  
  console.log('\n✅ Fluxo completo executado!');
  console.log('📊 5 skills diferentes testadas em sequência');
  
  return { step1, step2, step3, step4, step5 };
}

await teste5_fluxoCompleto();
```

**Resultado esperado:**
- ✅ Todas as 5 skills respondem
- ✅ Dados são contextuais
- ✅ Performance consistente
- ✅ Sem erros em nenhum step

---

## 📊 FUNÇÃO AUXILIAR - EXECUTAR TODOS OS TESTES

```javascript
// Executar TODOS os 5 testes em sequência
async function executarTodosTestes() {
  console.log('🚀 Iniciando bateria completa de testes...\n');
  
  const resultados = {
    teste1: null,
    teste2: null,
    teste3: null,
    teste4: null,
    teste5: null
  };
  
  try {
    // Login
    console.log('0️⃣ Fazendo login...');
    await login();
    console.log('✅ Login OK\n');
    
    // Teste 1
    resultados.teste1 = await teste1_alertas();
    await new Promise(r => setTimeout(r, 1000));
    
    // Teste 2
    resultados.teste2 = await teste2_postos();
    await new Promise(r => setTimeout(r, 1000));
    
    // Teste 3
    resultados.teste3 = await teste3_bancoHoras();
    await new Promise(r => setTimeout(r, 1000));
    
    // Teste 4
    resultados.teste4 = await teste4_wizardComunicado();
    await new Promise(r => setTimeout(r, 2000));
    await cancelarWizard(); // Limpar wizard
    await new Promise(r => setTimeout(r, 1000));
    
    // Teste 5
    resultados.teste5 = await teste5_fluxoCompleto();
    
    // Resumo
    console.log('\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('🎉 TODOS OS TESTES EXECUTADOS!');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
    
    // Validação
    let passou = 0;
    if (resultados.teste1?.response) { console.log('✅ Teste 1: PASSOU'); passou++; }
    if (resultados.teste2?.response) { console.log('✅ Teste 2: PASSOU'); passou++; }
    if (resultados.teste3?.resumo?.response) { console.log('✅ Teste 3: PASSOU'); passou++; }
    if (resultados.teste4?.wizard?.wizard_id) { console.log('✅ Teste 4: PASSOU'); passou++; }
    if (resultados.teste5?.step1?.response) { console.log('✅ Teste 5: PASSOU'); passou++; }
    
    console.log(`\n📊 Resultado Final: ${passou}/5 testes passaram (${passou*20}%)`);
    
    if (passou >= 4) {
      console.log('🎉 BARTOLO APROVADO! Sistema funcionando corretamente!');
    } else {
      console.log('⚠️  Alguns testes falharam. Verifique os erros acima.');
    }
    
  } catch (error) {
    console.error('❌ Erro durante execução:', error);
  }
  
  return resultados;
}

// Para executar todos os testes de uma vez:
// await executarTodosTestes();
```

---

## 🎯 COMO USAR - PASSO A PASSO

### Método Rápido (Recomendado):

1. **Abra o console do navegador** (`F12` → Console)

2. **Cole TODO o código de uma vez:**
   - Copie do "PASSO 0" até o final da "FUNÇÃO AUXILIAR"
   - Cole no console
   - Pressione Enter

3. **Execute todos os testes:**
   ```javascript
   await executarTodosTestes();
   ```

4. **Aguarde** ~2 minutos

5. **Veja o resultado:**
   ```
   📊 Resultado Final: 5/5 testes passaram (100%)
   🎉 BARTOLO APROVADO!
   ```

### Método Individual:

Execute teste por teste:
```javascript
await login();           // Primeiro
await teste1_alertas();  // Depois cada teste
await teste2_postos();
await teste3_bancoHoras();
await teste4_wizardComunicado();
await teste5_fluxoCompleto();
```

---

## 🔧 TROUBLESHOOTING

### Erro de CORS
Se aparecer erro de CORS no console:
```
Access to fetch... has been blocked by CORS policy
```

**Solução:** Acesse o backend diretamente em `http://localhost:8080` primeiro para adicionar à whitelist.

### Token expirado
```javascript
// Re-fazer login
await login();
```

### API não responde
- Verifique se backend está rodando: `docker ps | grep backend`
- Teste health: `http://localhost:8080/health`

---

## 📋 CHECKLIST DE VALIDAÇÃO

Após executar todos os testes:

- [ ] Teste 1: Alertas funcionou
- [ ] Teste 2: Postos funcionou
- [ ] Teste 3: Banco horas funcionou
- [ ] Teste 4: Wizard iniciou
- [ ] Teste 5: Fluxo multi-skill funcionou
- [ ] Tempo de resposta < 3s por request
- [ ] Sem erros no console
- [ ] Dados são do sistema real

**Meta:** 4/5 ou mais = ✅ APROVADO

---

**Criado por:** Claude Sonnet 4.5  
**Data:** 31/01/2026  
**Versão:** 1.0 - Browser Edition  
**Status:** Pronto para execução no navegador
