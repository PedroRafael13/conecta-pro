// ═══════════════════════════════════════════════════════════════
// 🧪 TESTES BARTOLO - COPIAR/COLAR NO CONSOLE DO NAVEGADOR
// ═══════════════════════════════════════════════════════════════
// 
// INSTRUÇÕES:
// 1. Abra o navegador (Chrome/Firefox/Edge)
// 2. Pressione F12 para abrir DevTools
// 3. Vá na aba Console
// 4. Cole TODO este arquivo aqui
// 5. Pressione Enter
// 6. Digite: await executarTodosTestes()
// 7. Aguarde o resultado!
//
// ═══════════════════════════════════════════════════════════════

const API_BASE = 'http://localhost:8080';

// ═══════════════════════════════════════════════════════════════
// FUNÇÕES DE TESTE
// ═══════════════════════════════════════════════════════════════

// Login
async function login() {
  const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'username=egonzaga@conectamais.pro&password=Admin@123'
  });
  const data = await response.json();
  window.TOKEN = data.access_token;
  window.USER_ID = 1;
  console.log('✅ Login realizado!');
  return data;
}

// Teste 1: Alertas
async function teste1_alertas() {
  console.log('\n🟢 TESTE 1: Consultando alertas...');
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
  console.log('Resposta:', data.response.substring(0, 150) + '...');
  console.log('Tempo:', data.processing_time_ms + 'ms');
  return data;
}

// Teste 2: Postos
async function teste2_postos() {
  console.log('\n🟡 TESTE 2: Listando postos...');
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
  console.log('Resposta:', data.response.substring(0, 150) + '...');
  return data;
}

// Teste 3: Banco de Horas
async function teste3_bancoHoras() {
  console.log('\n🟠 TESTE 3: Consultando banco de horas...');
  
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
  console.log('Resumo:', dataResumo.response.substring(0, 100) + '...');
  
  return { resumo: dataResumo };
}

// Teste 4: Wizard
async function teste4_wizardComunicado() {
  console.log('\n🔴 TESTE 4: Iniciando wizard de comunicado...');
  
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
  console.log('Wizard ID:', wizardData.wizard_id);
  console.log('Pergunta:', wizardData.question);
  console.log('Progresso:', wizardData.progress_percent + '%');
  
  return { wizard: wizardData };
}

// Cancelar wizard
async function cancelarWizard() {
  const response = await fetch(
    `${API_BASE}/api/v1/ai/bartolo/wizard/cancel?user_id=${window.USER_ID}`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${window.TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ session_id: 'wizard-test-browser' })
    }
  );
  return await response.json();
}

// Teste 5: Fluxo completo
async function teste5_fluxoCompleto() {
  console.log('\n🔴 TESTE 5: Executando fluxo completo multi-skill...');
  
  const sessionId = 'test-flow-' + Date.now();
  
  async function enviarMensagem(mensagem, step) {
    console.log(`Step ${step}: ${mensagem}`);
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
    return await response.json();
  }
  
  const step1 = await enviarMensagem('/cobertura hoje', 1);
  await new Promise(r => setTimeout(r, 500));
  
  const step2 = await enviarMensagem('/alerta', 2);
  await new Promise(r => setTimeout(r, 500));
  
  const step3 = await enviarMensagem('/posto listar', 3);
  
  console.log('✅ Fluxo completo executado!');
  
  return { step1, step2, step3 };
}

// ═══════════════════════════════════════════════════════════════
// EXECUTAR TODOS OS TESTES
// ═══════════════════════════════════════════════════════════════

async function executarTodosTestes() {
  console.clear();
  console.log('╔═══════════════════════════════════════════════════════╗');
  console.log('║   🧪 BATERIA DE TESTES BARTOLO MVP                   ║');
  console.log('╚═══════════════════════════════════════════════════════╝\n');
  
  const resultados = {};
  let passou = 0;
  
  try {
    // Login
    console.log('0️⃣ Fazendo login...');
    await login();
    await new Promise(r => setTimeout(r, 500));
    
    // Teste 1
    resultados.teste1 = await teste1_alertas();
    await new Promise(r => setTimeout(r, 1000));
    if (resultados.teste1?.response) passou++;
    
    // Teste 2
    resultados.teste2 = await teste2_postos();
    await new Promise(r => setTimeout(r, 1000));
    if (resultados.teste2?.response) passou++;
    
    // Teste 3
    resultados.teste3 = await teste3_bancoHoras();
    await new Promise(r => setTimeout(r, 1000));
    if (resultados.teste3?.resumo?.response) passou++;
    
    // Teste 4
    resultados.teste4 = await teste4_wizardComunicado();
    await new Promise(r => setTimeout(r, 2000));
    if (resultados.teste4?.wizard?.wizard_id) passou++;
    await cancelarWizard();
    await new Promise(r => setTimeout(r, 1000));
    
    // Teste 5
    resultados.teste5 = await teste5_fluxoCompleto();
    if (resultados.teste5?.step1?.response) passou++;
    
    // Resumo
    console.log('\n\n╔═══════════════════════════════════════════════════════╗');
    console.log('║             🎉 RESULTADO FINAL                        ║');
    console.log('╚═══════════════════════════════════════════════════════╝\n');
    
    console.log(`✅ Testes aprovados: ${passou}/5 (${passou*20}%)\n`);
    
    if (resultados.teste1?.response) console.log('✅ Teste 1: PASSOU - Alertas');
    else console.log('❌ Teste 1: FALHOU');
    
    if (resultados.teste2?.response) console.log('✅ Teste 2: PASSOU - Postos');
    else console.log('❌ Teste 2: FALHOU');
    
    if (resultados.teste3?.resumo?.response) console.log('✅ Teste 3: PASSOU - Banco Horas');
    else console.log('❌ Teste 3: FALHOU');
    
    if (resultados.teste4?.wizard?.wizard_id) console.log('✅ Teste 4: PASSOU - Wizard');
    else console.log('❌ Teste 4: FALHOU');
    
    if (resultados.teste5?.step1?.response) console.log('✅ Teste 5: PASSOU - Fluxo Multi-Skill');
    else console.log('❌ Teste 5: FALHOU');
    
    console.log('\n' + '═'.repeat(55));
    
    if (passou >= 4) {
      console.log('🎉 BARTOLO APROVADO! Sistema funcionando corretamente!');
    } else if (passou >= 3) {
      console.log('⚠️  ATENÇÃO: Alguns testes falharam. Verifique acima.');
    } else {
      console.log('❌ REPROVADO: Muitos testes falharam. Correções necessárias.');
    }
    
    console.log('═'.repeat(55) + '\n');
    
  } catch (error) {
    console.error('❌ Erro durante execução:', error);
  }
  
  return resultados;
}

// ═══════════════════════════════════════════════════════════════
console.log('✅ Funções de teste carregadas!');
console.log('');
console.log('Para executar todos os testes, digite:');
console.log('  await executarTodosTestes()');
console.log('');
console.log('Ou execute individualmente:');
console.log('  await login()');
console.log('  await teste1_alertas()');
console.log('  await teste2_postos()');
console.log('  etc...');
console.log('═'.repeat(55));
