#!/usr/bin/env node
/**
 * Script para validar schema OpenAPI
 *
 * Uso: npm run api:validate
 *
 * Verifica:
 * - Se o backend está respondendo
 * - Se o schema é válido
 * - Estatísticas do schema
 */

import { dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
};

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8080';
const OPENAPI_URL = `${BACKEND_URL}/openapi.json`;

async function main() {
  console.log(`\n${colors.bright}${colors.cyan}Validando Schema OpenAPI${colors.reset}\n`);
  console.log(`URL: ${OPENAPI_URL}\n`);

  const checks = [];

  // Check 1: Backend está respondendo
  try {
    const healthResponse = await fetch(`${BACKEND_URL}/health`);
    checks.push({
      name: 'Backend Health',
      status: healthResponse.ok ? 'pass' : 'warn',
      detail: healthResponse.ok ? 'OK' : `Status ${healthResponse.status}`,
    });
  } catch {
    checks.push({
      name: 'Backend Health',
      status: 'fail',
      detail: 'Não foi possível conectar',
    });
  }

  // Check 2: OpenAPI endpoint
  let schema;
  try {
    const response = await fetch(OPENAPI_URL);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    schema = await response.json();
    checks.push({
      name: 'OpenAPI Endpoint',
      status: 'pass',
      detail: 'Respondendo',
    });
  } catch (error) {
    checks.push({
      name: 'OpenAPI Endpoint',
      status: 'fail',
      detail: error.message,
    });
  }

  // Check 3: Schema válido
  if (schema) {
    const hasInfo = schema.info && schema.info.title && schema.info.version;
    const hasPaths = schema.paths && Object.keys(schema.paths).length > 0;
    const hasSchemas = schema.components?.schemas && Object.keys(schema.components.schemas).length > 0;

    checks.push({
      name: 'Schema Info',
      status: hasInfo ? 'pass' : 'warn',
      detail: hasInfo ? `${schema.info.title} v${schema.info.version}` : 'Incompleto',
    });

    checks.push({
      name: 'Paths (Endpoints)',
      status: hasPaths ? 'pass' : 'fail',
      detail: hasPaths ? `${Object.keys(schema.paths).length} endpoints` : 'Nenhum endpoint',
    });

    checks.push({
      name: 'Schemas (Models)',
      status: hasSchemas ? 'pass' : 'warn',
      detail: hasSchemas ? `${Object.keys(schema.components.schemas).length} schemas` : 'Nenhum schema',
    });

    // Check 4: Métodos por endpoint
    if (hasPaths) {
      const methods = { get: 0, post: 0, put: 0, patch: 0, delete: 0 };
      Object.values(schema.paths).forEach((path) => {
        Object.keys(path).forEach((method) => {
          if (methods[method] !== undefined) methods[method]++;
        });
      });
      checks.push({
        name: 'Métodos HTTP',
        status: 'pass',
        detail: `GET:${methods.get} POST:${methods.post} PUT:${methods.put} PATCH:${methods.patch} DELETE:${methods.delete}`,
      });
    }

    // Check 5: Tags (organização)
    const tags = schema.tags || [];
    checks.push({
      name: 'Tags (Módulos)',
      status: tags.length > 0 ? 'pass' : 'warn',
      detail: tags.length > 0 ? tags.map((t) => t.name).join(', ') : 'Sem tags',
    });
  }

  // Output
  console.log('Resultados:\n');
  checks.forEach((check) => {
    const icon =
      check.status === 'pass' ? `${colors.green}✓` : check.status === 'warn' ? `${colors.yellow}⚠` : `${colors.red}✗`;
    console.log(`  ${icon} ${check.name}${colors.reset}: ${check.detail}`);
  });

  const failed = checks.filter((c) => c.status === 'fail');
  const warned = checks.filter((c) => c.status === 'warn');

  console.log();

  if (failed.length > 0) {
    console.log(`${colors.red}✗ Validação falhou com ${failed.length} erro(s)${colors.reset}\n`);
    process.exit(1);
  } else if (warned.length > 0) {
    console.log(`${colors.yellow}⚠ Validação passou com ${warned.length} aviso(s)${colors.reset}\n`);
  } else {
    console.log(`${colors.green}✓ Schema válido e completo!${colors.reset}\n`);
  }
}

main();
