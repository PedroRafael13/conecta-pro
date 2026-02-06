#!/usr/bin/env node

/**
 * Script de Otimização de Imports do Lucide React
 *
 * Converte imports agrupados como:
 *   import { Icon1, Icon2 } from 'lucide-react'
 *
 * Para imports individuais:
 *   import Icon1 from 'lucide-react/dist/esm/icons/icon1'
 *   import Icon2 from 'lucide-react/dist/esm/icons/icon2'
 *
 * Redução esperada: ~1.5MB no bundle
 */

const fs = require('fs');
const path = require('path');

// Converter PascalCase para kebab-case
function toKebabCase(str) {
  return str
    .replace(/([a-z0-9])([A-Z])/g, '$1-$2')
    .replace(/([A-Z])([A-Z][a-z])/g, '$1-$2')
    .toLowerCase();
}

// Processar arquivo individual
function processFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');

  // Regex para encontrar imports do lucide-react
  const importRegex = /import\s+{\s*([^}]+)\s*}\s+from\s+['"]lucide-react['"]/g;

  let modified = false;
  let newContent = content;

  const matches = [...content.matchAll(importRegex)];

  for (const match of matches) {
    const fullImport = match[0];
    const iconsStr = match[1];

    // Extrair lista de ícones (suportando aliases: Icon as Alias)
    const icons = iconsStr
      .split(',')
      .map(icon => icon.trim())
      .filter(icon => icon.length > 0)
      .map(icon => {
        // Verificar se tem alias (Icon as Alias)
        const aliasMatch = icon.match(/^(\w+)\s+as\s+(\w+)$/);
        if (aliasMatch) {
          return {
            original: aliasMatch[1],
            alias: aliasMatch[2],
            hasAlias: true
          };
        }
        return {
          original: icon,
          alias: icon,
          hasAlias: false
        };
      });

    if (icons.length === 0) continue;

    // Gerar imports individuais
    const individualImports = icons.map(iconInfo => {
      const kebabName = toKebabCase(iconInfo.original);
      if (iconInfo.hasAlias) {
        return `import ${iconInfo.original} from 'lucide-react/dist/esm/icons/${kebabName}'\nconst ${iconInfo.alias} = ${iconInfo.original}`;
      }
      return `import ${iconInfo.original} from 'lucide-react/dist/esm/icons/${kebabName}'`;
    }).join('\n');

    // Substituir import agrupado por imports individuais
    newContent = newContent.replace(fullImport, individualImports);
    modified = true;
  }

  // Salvar arquivo modificado
  if (modified) {
    fs.writeFileSync(filePath, newContent, 'utf8');
    return true;
  }

  return false;
}

// Encontrar todos os arquivos TS/TSX recursivamente
function findTsxFiles(dir, fileList = []) {
  const files = fs.readdirSync(dir);

  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      // Ignorar node_modules e .next
      if (!file.startsWith('.') && file !== 'node_modules') {
        findTsxFiles(filePath, fileList);
      }
    } else if (file.match(/\.(ts|tsx)$/)) {
      fileList.push(filePath);
    }
  });

  return fileList;
}

// Main execution
function main() {
  const srcDir = path.join(__dirname, '..', 'src');

  console.log('🔍 Buscando arquivos TS/TSX...');
  const files = findTsxFiles(srcDir);
  console.log(`📁 Encontrados ${files.length} arquivos\n`);

  let modifiedCount = 0;
  let errorCount = 0;

  files.forEach((file, index) => {
    try {
      const wasModified = processFile(file);
      if (wasModified) {
        modifiedCount++;
        console.log(`✅ [${index + 1}/${files.length}] ${path.relative(srcDir, file)}`);
      }
    } catch (error) {
      errorCount++;
      console.error(`❌ [${index + 1}/${files.length}] ${path.relative(srcDir, file)}`);
      console.error(`   Erro: ${error.message}`);
    }
  });

  console.log('\n' + '='.repeat(60));
  console.log(`✨ Otimização concluída!`);
  console.log(`📊 Arquivos modificados: ${modifiedCount}`);
  console.log(`⚠️  Arquivos com erro: ${errorCount}`);
  console.log('='.repeat(60));

  process.exit(errorCount > 0 ? 1 : 0);
}

main();
