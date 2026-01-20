#!/usr/bin/env node
/**
 * Script de Sincronização API Backend -> Frontend
 *
 * Uso: npm run api:sync
 *
 * Este script:
 * 1. Verifica se o backend está rodando
 * 2. Baixa o schema OpenAPI
 * 3. Compara com snapshot anterior (se existir)
 * 4. Gera código TypeScript + React Query hooks
 * 5. Atualiza o snapshot
 */

import { execSync, spawn } from 'child_process';
import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Cores para output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

const log = {
  info: (msg) => console.log(`${colors.blue}ℹ${colors.reset} ${msg}`),
  success: (msg) => console.log(`${colors.green}✓${colors.reset} ${msg}`),
  warning: (msg) => console.log(`${colors.yellow}⚠${colors.reset} ${msg}`),
  error: (msg) => console.log(`${colors.red}✗${colors.reset} ${msg}`),
  title: (msg) => console.log(`\n${colors.bright}${colors.cyan}${msg}${colors.reset}\n`),
};

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8080';
const OPENAPI_URL = `${BACKEND_URL}/openapi.json`;
const SNAPSHOT_PATH = resolve(__dirname, '../openapi-snapshot.json');
const FRONTEND_GENERATED = resolve(__dirname, '../../frontend/src/api/generated');

async function fetchOpenAPI() {
  log.info(`Buscando schema em ${OPENAPI_URL}...`);

  try {
    const response = await fetch(OPENAPI_URL);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    const schema = await response.json();
    log.success(`Schema obtido: ${Object.keys(schema.paths || {}).length} endpoints`);
    return schema;
  } catch (error) {
    throw new Error(`Falha ao buscar OpenAPI: ${error.message}`);
  }
}

function loadSnapshot() {
  if (existsSync(SNAPSHOT_PATH)) {
    try {
      const content = readFileSync(SNAPSHOT_PATH, 'utf-8');
      return JSON.parse(content);
    } catch {
      return null;
    }
  }
  return null;
}

function saveSnapshot(schema) {
  writeFileSync(SNAPSHOT_PATH, JSON.stringify(schema, null, 2));
  log.success(`Snapshot salvo em ${SNAPSHOT_PATH}`);
}

function compareSchemas(oldSchema, newSchema) {
  if (!oldSchema) {
    return { isNew: true, changes: [] };
  }

  const changes = [];
  const oldPaths = Object.keys(oldSchema.paths || {});
  const newPaths = Object.keys(newSchema.paths || {});

  // Novos endpoints
  const added = newPaths.filter((p) => !oldPaths.includes(p));
  added.forEach((p) => changes.push({ type: 'added', path: p }));

  // Endpoints removidos
  const removed = oldPaths.filter((p) => !newPaths.includes(p));
  removed.forEach((p) => changes.push({ type: 'removed', path: p }));

  // Endpoints modificados (comparação simplificada)
  const common = newPaths.filter((p) => oldPaths.includes(p));
  common.forEach((p) => {
    const oldMethods = Object.keys(oldSchema.paths[p] || {});
    const newMethods = Object.keys(newSchema.paths[p] || {});

    if (JSON.stringify(oldMethods.sort()) !== JSON.stringify(newMethods.sort())) {
      changes.push({ type: 'modified', path: p, detail: 'methods changed' });
    }
  });

  // Schemas modificados
  const oldSchemas = Object.keys(oldSchema.components?.schemas || {});
  const newSchemas = Object.keys(newSchema.components?.schemas || {});

  const addedSchemas = newSchemas.filter((s) => !oldSchemas.includes(s));
  addedSchemas.forEach((s) => changes.push({ type: 'schema_added', schema: s }));

  const removedSchemas = oldSchemas.filter((s) => !newSchemas.includes(s));
  removedSchemas.forEach((s) => changes.push({ type: 'schema_removed', schema: s }));

  return { isNew: false, changes };
}

function printChanges(comparison) {
  if (comparison.isNew) {
    log.info('Primeira sincronização - gerando todos os tipos');
    return;
  }

  if (comparison.changes.length === 0) {
    log.info('Nenhuma mudança detectada no schema');
    return;
  }

  log.title('Mudanças Detectadas:');

  comparison.changes.forEach((change) => {
    switch (change.type) {
      case 'added':
        console.log(`  ${colors.green}+ ENDPOINT:${colors.reset} ${change.path}`);
        break;
      case 'removed':
        console.log(`  ${colors.red}- ENDPOINT:${colors.reset} ${change.path}`);
        break;
      case 'modified':
        console.log(`  ${colors.yellow}~ ENDPOINT:${colors.reset} ${change.path} (${change.detail})`);
        break;
      case 'schema_added':
        console.log(`  ${colors.green}+ SCHEMA:${colors.reset} ${change.schema}`);
        break;
      case 'schema_removed':
        console.log(`  ${colors.red}- SCHEMA:${colors.reset} ${change.schema}`);
        break;
    }
  });

  console.log(`\n  Total: ${comparison.changes.length} mudança(s)\n`);
}

async function runOrval() {
  log.info('Executando Orval para gerar código...');

  return new Promise((resolve, reject) => {
    const orval = spawn('npx', ['orval', '--config', 'orval.config.ts'], {
      cwd: dirname(__dirname),
      stdio: 'inherit',
      shell: true,
    });

    orval.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Orval falhou com código ${code}`));
      }
    });

    orval.on('error', reject);
  });
}

function countGeneratedFiles() {
  try {
    const result = execSync(`find ${FRONTEND_GENERATED} -name "*.ts" | wc -l`, {
      encoding: 'utf-8',
    });
    return parseInt(result.trim(), 10);
  } catch {
    return 0;
  }
}

async function main() {
  console.log(`
${colors.bright}${colors.magenta}╔════════════════════════════════════════════════════════╗
║           CONECTA PRO - API SYNC                       ║
║           Backend → Frontend                           ║
╚════════════════════════════════════════════════════════╝${colors.reset}
`);

  try {
    // 1. Buscar schema
    const schema = await fetchOpenAPI();

    // 2. Comparar com snapshot
    const oldSnapshot = loadSnapshot();
    const comparison = compareSchemas(oldSnapshot, schema);
    printChanges(comparison);

    // 3. Gerar código
    await runOrval();

    // 4. Salvar snapshot
    saveSnapshot(schema);

    // 5. Resumo
    const filesCount = countGeneratedFiles();

    log.title('Sincronização Concluída!');
    console.log(`
  ${colors.cyan}Estatísticas:${colors.reset}
  ├── Endpoints: ${Object.keys(schema.paths || {}).length}
  ├── Schemas: ${Object.keys(schema.components?.schemas || {}).length}
  └── Arquivos gerados: ${filesCount}

  ${colors.green}Frontend atualizado em:${colors.reset}
  └── ${FRONTEND_GENERATED}

  ${colors.yellow}Próximos passos:${colors.reset}
  └── Importe os hooks de: import { useXxx } from '@/api/generated'
`);
  } catch (error) {
    log.error(error.message);

    if (error.message.includes('Falha ao buscar OpenAPI')) {
      console.log(`
  ${colors.yellow}Dica:${colors.reset} Certifique-se que o backend está rodando:
  └── docker compose up -d backend
  └── Ou use: npm run api:generate (usa snapshot local)
`);
    }

    process.exit(1);
  }
}

main();
