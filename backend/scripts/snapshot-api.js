#!/usr/bin/env node
/**
 * Script para salvar snapshot do schema OpenAPI
 *
 * Uso: npm run api:snapshot
 *
 * Útil para:
 * - Salvar estado atual antes de mudanças
 * - Criar backup do schema
 * - Usar quando backend está offline
 */

import { writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  cyan: '\x1b[36m',
};

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8080';
const OPENAPI_URL = `${BACKEND_URL}/openapi.json`;
const SNAPSHOT_PATH = resolve(__dirname, '../openapi-snapshot.json');

async function main() {
  console.log(`\n${colors.cyan}Salvando snapshot do OpenAPI...${colors.reset}\n`);

  try {
    const response = await fetch(OPENAPI_URL);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const schema = await response.json();
    const endpointsCount = Object.keys(schema.paths || {}).length;
    const schemasCount = Object.keys(schema.components?.schemas || {}).length;

    writeFileSync(SNAPSHOT_PATH, JSON.stringify(schema, null, 2));

    console.log(`${colors.green}✓ Snapshot salvo com sucesso!${colors.reset}`);
    console.log(`  ├── Arquivo: ${SNAPSHOT_PATH}`);
    console.log(`  ├── Endpoints: ${endpointsCount}`);
    console.log(`  └── Schemas: ${schemasCount}\n`);
  } catch (error) {
    console.log(`${colors.red}✗ Erro ao salvar snapshot: ${error.message}${colors.reset}`);
    console.log(`  Certifique-se que o backend está rodando em ${BACKEND_URL}\n`);
    process.exit(1);
  }
}

main();
