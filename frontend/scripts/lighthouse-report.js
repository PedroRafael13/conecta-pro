#!/usr/bin/env node

/**
 * Script para gerar relatórios customizados do Lighthouse
 */

const fs = require('fs');
const path = require('path');

const REPORTS_DIR = path.join(__dirname, '..', '.lighthouseci');

/**
 * Formata score como porcentagem com cor
 */
function formatScore(score) {
  const percent = Math.round(score * 100);
  let color = '\x1b[31m'; // Red

  if (percent >= 90) color = '\x1b[32m'; // Green
  else if (percent >= 50) color = '\x1b[33m'; // Yellow

  return `${color}${percent}%\x1b[0m`;
}

/**
 * Formata métrica de tempo
 */
function formatTime(ms) {
  if (ms < 1000) return `${Math.round(ms)}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

/**
 * Analisa relatórios do Lighthouse
 */
function analyzeReports() {
  if (!fs.existsSync(REPORTS_DIR)) {
    console.error('❌ Diretório de relatórios não encontrado.');
    console.log('Execute "npm run lighthouse" primeiro.');
    process.exit(1);
  }

  const files = fs.readdirSync(REPORTS_DIR);
  const reportFiles = files.filter(f => f.endsWith('.json') && f.startsWith('lhr-'));

  if (reportFiles.length === 0) {
    console.error('❌ Nenhum relatório encontrado.');
    process.exit(1);
  }

  console.log('\n🔍 LIGHTHOUSE PERFORMANCE REPORT\n');
  console.log('═'.repeat(80));

  const reports = [];

  for (const file of reportFiles) {
    const filePath = path.join(REPORTS_DIR, file);
    const content = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    reports.push(content);
  }

  // Agregar métricas
  const aggregated = {
    performance: [],
    accessibility: [],
    bestPractices: [],
    seo: [],
    fcp: [],
    lcp: [],
    tbt: [],
    cls: [],
    si: []
  };

  for (const report of reports) {
    const { categories, audits } = report;

    aggregated.performance.push(categories.performance.score);
    aggregated.accessibility.push(categories.accessibility.score);
    aggregated.bestPractices.push(categories['best-practices'].score);
    aggregated.seo.push(categories.seo.score);

    aggregated.fcp.push(audits['first-contentful-paint'].numericValue);
    aggregated.lcp.push(audits['largest-contentful-paint'].numericValue);
    aggregated.tbt.push(audits['total-blocking-time'].numericValue);
    aggregated.cls.push(audits['cumulative-layout-shift'].numericValue);
    aggregated.si.push(audits['speed-index'].numericValue);
  }

  // Calcular médias
  const avg = (arr) => arr.reduce((a, b) => a + b, 0) / arr.length;

  console.log('\n📊 SCORES (média de', reports.length, 'runs):\n');

  console.log('  Performance:     ', formatScore(avg(aggregated.performance)));
  console.log('  Accessibility:   ', formatScore(avg(aggregated.accessibility)));
  console.log('  Best Practices:  ', formatScore(avg(aggregated.bestPractices)));
  console.log('  SEO:             ', formatScore(avg(aggregated.seo)));

  console.log('\n⏱️  CORE WEB VITALS:\n');

  console.log('  FCP (First Contentful Paint):   ', formatTime(avg(aggregated.fcp)));
  console.log('  LCP (Largest Contentful Paint): ', formatTime(avg(aggregated.lcp)));
  console.log('  TBT (Total Blocking Time):      ', formatTime(avg(aggregated.tbt)));
  console.log('  CLS (Cumulative Layout Shift):  ', avg(aggregated.cls).toFixed(3));
  console.log('  SI (Speed Index):               ', formatTime(avg(aggregated.si)));

  console.log('\n═'.repeat(80));

  // Identificar problemas
  const issues = [];

  if (avg(aggregated.performance) < 0.8) {
    issues.push('Performance score abaixo do threshold (80%)');
  }
  if (avg(aggregated.accessibility) < 0.9) {
    issues.push('Accessibility score abaixo do threshold (90%)');
  }
  if (avg(aggregated.fcp) > 2000) {
    issues.push('FCP acima de 2s');
  }
  if (avg(aggregated.lcp) > 3000) {
    issues.push('LCP acima de 3s');
  }
  if (avg(aggregated.tbt) > 300) {
    issues.push('TBT acima de 300ms');
  }
  if (avg(aggregated.cls) > 0.1) {
    issues.push('CLS acima de 0.1');
  }

  if (issues.length > 0) {
    console.log('\n⚠️  PROBLEMAS IDENTIFICADOS:\n');
    issues.forEach(issue => console.log(`  - ${issue}`));
    console.log();
  } else {
    console.log('\n✅ Todas as métricas estão dentro dos thresholds!\n');
  }

  // Gerar relatório resumido
  const summary = {
    timestamp: new Date().toISOString(),
    runs: reports.length,
    scores: {
      performance: avg(aggregated.performance),
      accessibility: avg(aggregated.accessibility),
      bestPractices: avg(aggregated.bestPractices),
      seo: avg(aggregated.seo)
    },
    metrics: {
      fcp: avg(aggregated.fcp),
      lcp: avg(aggregated.lcp),
      tbt: avg(aggregated.tbt),
      cls: avg(aggregated.cls),
      si: avg(aggregated.si)
    },
    issues
  };

  const summaryPath = path.join(REPORTS_DIR, 'summary.json');
  fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));
  console.log('📄 Relatório resumido salvo em:', summaryPath, '\n');

  if (issues.length > 0 && process.env.CI) {
    process.exit(1);
  }
}

analyzeReports();
