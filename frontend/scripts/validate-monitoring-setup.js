#!/usr/bin/env node

/**
 * Script de validação do setup de monitoramento de performance
 * Verifica se todas as ferramentas e configurações estão corretas
 */

const fs = require('fs');
const path = require('path');

const REQUIRED_FILES = [
  'lighthouserc.json',
  'performance-budgets.json',
  'PERFORMANCE-MONITORING.md',
  'PERFORMANCE-QUICKSTART.md',
  '.github/workflows/performance.yml',
  '.github/workflows/performance-baseline.yml',
  'scripts/compare-bundle-size.js',
  'scripts/lighthouse-report.js',
  '.lighthouseci/.gitkeep',
  '.lighthouseci/.gitignore',
];

const REQUIRED_SCRIPTS = [
  'analyze',
  'lighthouse',
  'lighthouse:report',
  'perf:test',
  'perf:compare',
  'perf:baseline',
  'perf:all',
];

const REQUIRED_DEPS = [
  '@lhci/cli',
  '@next/bundle-analyzer',
];

console.log('🔍 Validando setup de monitoramento de performance...\n');

let hasErrors = false;

// Verificar arquivos
console.log('📁 Verificando arquivos necessários:\n');

for (const file of REQUIRED_FILES) {
  const filePath = path.join(__dirname, '..', file);
  const exists = fs.existsSync(filePath);

  if (exists) {
    console.log(`  ✅ ${file}`);
  } else {
    console.log(`  ❌ ${file} - FALTANDO`);
    hasErrors = true;
  }
}

// Verificar package.json
console.log('\n📦 Verificando package.json:\n');

const packageJsonPath = path.join(__dirname, '..', 'package.json');

if (!fs.existsSync(packageJsonPath)) {
  console.log('  ❌ package.json não encontrado');
  hasErrors = true;
} else {
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));

  // Verificar scripts
  console.log('  Scripts:');
  for (const script of REQUIRED_SCRIPTS) {
    if (packageJson.scripts && packageJson.scripts[script]) {
      console.log(`    ✅ ${script}`);
    } else {
      console.log(`    ❌ ${script} - FALTANDO`);
      hasErrors = true;
    }
  }

  // Verificar dependências
  console.log('\n  Dependências:');
  const allDeps = {
    ...packageJson.dependencies,
    ...packageJson.devDependencies,
  };

  for (const dep of REQUIRED_DEPS) {
    if (allDeps[dep]) {
      console.log(`    ✅ ${dep} (${allDeps[dep]})`);
    } else {
      console.log(`    ❌ ${dep} - FALTANDO`);
      hasErrors = true;
    }
  }
}

// Verificar configurações
console.log('\n⚙️  Verificando configurações:\n');

// Lighthouse RC
const lighthouseRcPath = path.join(__dirname, '..', 'lighthouserc.json');
if (fs.existsSync(lighthouseRcPath)) {
  try {
    const config = JSON.parse(fs.readFileSync(lighthouseRcPath, 'utf8'));

    if (config.ci && config.ci.collect && config.ci.assert) {
      console.log('  ✅ lighthouserc.json válido');

      // Verificar URLs configuradas
      if (config.ci.collect.url && config.ci.collect.url.length > 0) {
        console.log(`     URLs configuradas: ${config.ci.collect.url.length}`);
      }

      // Verificar assertions
      if (config.ci.assert.assertions) {
        const assertionCount = Object.keys(config.ci.assert.assertions).length;
        console.log(`     Assertions configuradas: ${assertionCount}`);
      }
    } else {
      console.log('  ⚠️  lighthouserc.json incompleto');
    }
  } catch (error) {
    console.log('  ❌ lighthouserc.json inválido:', error.message);
    hasErrors = true;
  }
} else {
  console.log('  ❌ lighthouserc.json não encontrado');
  hasErrors = true;
}

// Performance Budgets
const budgetsPath = path.join(__dirname, '..', 'performance-budgets.json');
if (fs.existsSync(budgetsPath)) {
  try {
    const budgets = JSON.parse(fs.readFileSync(budgetsPath, 'utf8'));

    if (budgets.budgets && Array.isArray(budgets.budgets)) {
      console.log('  ✅ performance-budgets.json válido');
      console.log(`     Budgets configurados: ${budgets.budgets.length}`);
    } else {
      console.log('  ⚠️  performance-budgets.json incompleto');
    }
  } catch (error) {
    console.log('  ❌ performance-budgets.json inválido:', error.message);
    hasErrors = true;
  }
} else {
  console.log('  ❌ performance-budgets.json não encontrado');
  hasErrors = true;
}

// Next Config
const nextConfigPath = path.join(__dirname, '..', 'next.config.ts');
if (fs.existsSync(nextConfigPath)) {
  const content = fs.readFileSync(nextConfigPath, 'utf8');

  if (content.includes('withBundleAnalyzer')) {
    console.log('  ✅ Bundle Analyzer configurado em next.config.ts');
  } else {
    console.log('  ⚠️  Bundle Analyzer não encontrado em next.config.ts');
  }

  if (content.includes('optimizePackageImports')) {
    console.log('  ✅ Package imports otimizados');
  } else {
    console.log('  ⚠️  Package imports optimization não configurado');
  }
} else {
  console.log('  ⚠️  next.config.ts não encontrado');
}

// Verificar .gitignore
console.log('\n🔒 Verificando .gitignore:\n');

const gitignorePath = path.join(__dirname, '..', '.gitignore');
if (fs.existsSync(gitignorePath)) {
  const content = fs.readFileSync(gitignorePath, 'utf8');

  const requiredEntries = [
    '.lighthouseci/*.json',
    'scripts/bundle-baseline.json',
    '.next/analyze',
  ];

  let allPresent = true;
  for (const entry of requiredEntries) {
    if (content.includes(entry)) {
      console.log(`  ✅ ${entry}`);
    } else {
      console.log(`  ⚠️  ${entry} não encontrado em .gitignore`);
      allPresent = false;
    }
  }

  if (allPresent) {
    console.log('\n  ✅ .gitignore configurado corretamente');
  }
} else {
  console.log('  ⚠️  .gitignore não encontrado');
}

// Resumo
console.log('\n' + '='.repeat(70));

if (hasErrors) {
  console.log('\n❌ VALIDAÇÃO FALHOU');
  console.log('\nCorreja os erros acima antes de prosseguir.\n');
  process.exit(1);
} else {
  console.log('\n✅ VALIDAÇÃO CONCLUÍDA COM SUCESSO!');
  console.log('\nTodas as ferramentas de monitoramento estão configuradas.');
  console.log('\nPróximos passos:');
  console.log('  1. npm run build          - Executar build');
  console.log('  2. npm run perf:baseline  - Criar baseline inicial');
  console.log('  3. npm run perf:all       - Executar análise completa');
  console.log('\nConsulte PERFORMANCE-QUICKSTART.md para começar.\n');
}
