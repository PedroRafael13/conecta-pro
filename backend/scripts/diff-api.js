#!/usr/bin/env node
/**
 * Script para mostrar diferenças entre schema atual e snapshot
 *
 * Uso: npm run api:diff
 */

import { existsSync, readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
};

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8080';
const OPENAPI_URL = `${BACKEND_URL}/openapi.json`;
const SNAPSHOT_PATH = resolve(__dirname, '../openapi-snapshot.json');

async function main() {
  console.log(`\n${colors.bright}${colors.cyan}API DIFF - Comparando schemas${colors.reset}\n`);

  // Verificar snapshot
  if (!existsSync(SNAPSHOT_PATH)) {
    console.log(`${colors.yellow}⚠ Snapshot não encontrado.${colors.reset}`);
    console.log(`  Execute primeiro: npm run api:sync\n`);
    process.exit(1);
  }

  // Buscar schema atual
  let currentSchema;
  try {
    const response = await fetch(OPENAPI_URL);
    currentSchema = await response.json();
  } catch (error) {
    console.log(`${colors.red}✗ Não foi possível conectar ao backend${colors.reset}`);
    console.log(`  URL: ${OPENAPI_URL}\n`);
    process.exit(1);
  }

  // Carregar snapshot
  const snapshot = JSON.parse(readFileSync(SNAPSHOT_PATH, 'utf-8'));

  // Comparar paths
  const snapshotPaths = Object.keys(snapshot.paths || {}).sort();
  const currentPaths = Object.keys(currentSchema.paths || {}).sort();

  const added = currentPaths.filter((p) => !snapshotPaths.includes(p));
  const removed = snapshotPaths.filter((p) => !currentPaths.includes(p));

  // Comparar schemas
  const snapshotSchemas = Object.keys(snapshot.components?.schemas || {}).sort();
  const currentSchemas = Object.keys(currentSchema.components?.schemas || {}).sort();

  const addedSchemas = currentSchemas.filter((s) => !snapshotSchemas.includes(s));
  const removedSchemas = snapshotSchemas.filter((s) => !currentSchemas.includes(s));

  // Output
  console.log(`${colors.cyan}Snapshot:${colors.reset} ${snapshotPaths.length} endpoints, ${snapshotSchemas.length} schemas`);
  console.log(`${colors.cyan}Atual:${colors.reset}    ${currentPaths.length} endpoints, ${currentSchemas.length} schemas\n`);

  if (added.length === 0 && removed.length === 0 && addedSchemas.length === 0 && removedSchemas.length === 0) {
    console.log(`${colors.green}✓ Schemas idênticos - nenhuma mudança detectada${colors.reset}\n`);
    process.exit(0);
  }

  console.log(`${colors.yellow}Mudanças encontradas:${colors.reset}\n`);

  if (added.length > 0) {
    console.log(`${colors.green}Endpoints adicionados (+${added.length}):${colors.reset}`);
    added.forEach((p) => console.log(`  + ${p}`));
    console.log();
  }

  if (removed.length > 0) {
    console.log(`${colors.red}Endpoints removidos (-${removed.length}):${colors.reset}`);
    removed.forEach((p) => console.log(`  - ${p}`));
    console.log();
  }

  if (addedSchemas.length > 0) {
    console.log(`${colors.green}Schemas adicionados (+${addedSchemas.length}):${colors.reset}`);
    addedSchemas.forEach((s) => console.log(`  + ${s}`));
    console.log();
  }

  if (removedSchemas.length > 0) {
    console.log(`${colors.red}Schemas removidos (-${removedSchemas.length}):${colors.reset}`);
    removedSchemas.forEach((s) => console.log(`  - ${s}`));
    console.log();
  }

  console.log(`${colors.yellow}Execute 'npm run api:sync' para sincronizar${colors.reset}\n`);
}

main();
