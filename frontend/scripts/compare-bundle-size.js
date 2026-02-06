#!/usr/bin/env node

/**
 * Script para comparar o tamanho do bundle com baseline
 * Alerta se o bundle cresceu mais que 5%
 */

const fs = require('fs');
const path = require('path');

const BUILD_DIR = path.join(__dirname, '..', '.next');
const BASELINE_FILE = path.join(__dirname, 'bundle-baseline.json');
const THRESHOLD = 0.05; // 5%

/**
 * Calcula tamanho total de um diretório recursivamente
 */
function getDirSize(dirPath) {
  let totalSize = 0;

  if (!fs.existsSync(dirPath)) {
    return 0;
  }

  const files = fs.readdirSync(dirPath);

  for (const file of files) {
    const filePath = path.join(dirPath, file);
    const stats = fs.statSync(filePath);

    if (stats.isDirectory()) {
      totalSize += getDirSize(filePath);
    } else {
      totalSize += stats.size;
    }
  }

  return totalSize;
}

/**
 * Formata bytes em formato legível
 */
function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Analisa o bundle e retorna estatísticas
 */
function analyzeBuild() {
  const staticDir = path.join(BUILD_DIR, 'static');

  if (!fs.existsSync(BUILD_DIR) || !fs.existsSync(staticDir)) {
    console.error('❌ Build não encontrado. Execute "npm run build" primeiro.');
    process.exit(1);
  }

  const stats = {
    timestamp: new Date().toISOString(),
    total: getDirSize(BUILD_DIR),
    static: getDirSize(staticDir),
    chunks: getDirSize(path.join(staticDir, 'chunks')),
    css: getDirSize(path.join(staticDir, 'css')),
    media: getDirSize(path.join(staticDir, 'media'))
  };

  return stats;
}

/**
 * Carrega baseline existente
 */
function loadBaseline() {
  if (!fs.existsSync(BASELINE_FILE)) {
    return null;
  }

  try {
    const content = fs.readFileSync(BASELINE_FILE, 'utf8');
    return JSON.parse(content);
  } catch (error) {
    console.warn('⚠️  Erro ao ler baseline:', error.message);
    return null;
  }
}

/**
 * Salva novo baseline
 */
function saveBaseline(stats) {
  try {
    fs.writeFileSync(BASELINE_FILE, JSON.stringify(stats, null, 2));
    console.log('✅ Baseline salvo em:', BASELINE_FILE);
  } catch (error) {
    console.error('❌ Erro ao salvar baseline:', error.message);
  }
}

/**
 * Compara stats atual com baseline
 */
function compare(current, baseline) {
  console.log('\n📊 ANÁLISE DE BUNDLE SIZE\n');
  console.log('═'.repeat(70));

  const categories = [
    { key: 'total', label: 'Total' },
    { key: 'static', label: 'Static Files' },
    { key: 'chunks', label: 'JS Chunks' },
    { key: 'css', label: 'CSS' },
    { key: 'media', label: 'Media' }
  ];

  let hasIssues = false;

  for (const { key, label } of categories) {
    const currentSize = current[key] || 0;
    const baselineSize = baseline ? baseline[key] || 0 : 0;
    const diff = currentSize - baselineSize;
    const diffPercent = baselineSize > 0 ? (diff / baselineSize) * 100 : 0;

    let status = '  ';
    let color = '';

    if (baseline) {
      if (diffPercent > THRESHOLD * 100) {
        status = '⚠️ ';
        color = '\x1b[33m'; // Yellow
        hasIssues = true;
      } else if (diffPercent < -THRESHOLD * 100) {
        status = '✅';
        color = '\x1b[32m'; // Green
      } else {
        status = '➡️ ';
        color = '\x1b[37m'; // White
      }
    }

    const diffText = baseline
      ? ` (${diff > 0 ? '+' : ''}${formatBytes(diff)} / ${diffPercent > 0 ? '+' : ''}${diffPercent.toFixed(2)}%)`
      : '';

    console.log(
      `${status} ${label.padEnd(15)}: ${color}${formatBytes(currentSize)}${diffText}\x1b[0m`
    );
  }

  console.log('═'.repeat(70));

  if (baseline) {
    console.log(`\nBaseline: ${baseline.timestamp}`);
    console.log(`Current:  ${current.timestamp}\n`);
  } else {
    console.log('\n⚠️  Nenhum baseline encontrado. Este será o baseline inicial.\n');
  }

  return hasIssues;
}

/**
 * Main
 */
function main() {
  const args = process.argv.slice(2);
  const shouldUpdateBaseline = args.includes('--update-baseline') || args.includes('-u');

  console.log('🔍 Analisando bundle...\n');

  const currentStats = analyzeBuild();
  const baseline = loadBaseline();

  const hasIssues = compare(currentStats, baseline);

  if (shouldUpdateBaseline || !baseline) {
    saveBaseline(currentStats);
  }

  if (hasIssues) {
    console.log('⚠️  ATENÇÃO: Bundle cresceu mais que o limite permitido (5%)!');
    console.log('   Considere:');
    console.log('   - Verificar imports desnecessários');
    console.log('   - Usar dynamic imports para code splitting');
    console.log('   - Otimizar dependências pesadas');
    console.log('   - Revisar imagens e assets\n');

    if (process.env.CI) {
      process.exit(1); // Falhar no CI
    }
  } else {
    console.log('✅ Bundle size dentro dos limites!\n');
  }
}

main();
