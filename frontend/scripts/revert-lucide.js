/**
 * Script para reverter imports do Lucide de volta para o formato original
 * Desfaz a otimização que está causando problemas com nomes de ícones
 */

const fs = require('fs');
const path = require('path');

function getAllTsxFiles(dir, fileList = []) {
  const files = fs.readdirSync(dir);

  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      if (!file.startsWith('.') && file !== 'node_modules') {
        getAllTsxFiles(filePath, fileList);
      }
    } else if (file.endsWith('.tsx') || file.endsWith('.ts')) {
      fileList.push(filePath);
    }
  });

  return fileList;
}

function revertFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf-8');
  let modified = false;
  let imports = [];

  // Extrair todos os imports do Lucide otimizados
  const importRegex = /^import\s+(\w+)\s+from\s+'lucide-react\/dist\/esm\/icons\/[^']+'/gm;

  let match;
  while ((match = importRegex.exec(content)) !== null) {
    imports.push(match[1]);
    modified = true;
  }

  // Também pegar const alias (ex: const FolderIcon = Folder)
  const aliasRegex = /^const\s+(\w+)\s+=\s+(\w+)\s*$/gm;
  const aliases = [];

  while ((match = aliasRegex.exec(content)) !== null) {
    aliases.push({ alias: match[1], original: match[2] });
    modified = true;
  }

  if (modified) {
    // Remover imports individuais e const aliases
    content = content.replace(/^import\s+\w+\s+from\s+'lucide-react\/dist\/esm\/icons\/[^']+'\s*\n?/gm, '');
    content = content.replace(/^const\s+\w+\s+=\s+\w+\s*\n?/gm, '');

    // Encontrar primeira linha de import para inserir o novo import
    const firstImportMatch = content.match(/^import\s/m);

    if (firstImportMatch && imports.length > 0) {
      const insertPosition = firstImportMatch.index;

      // Adicionar ícones dos aliases
      aliases.forEach(({ original }) => {
        if (!imports.includes(original)) {
          imports.push(original);
        }
      });

      const newImport = `import { ${imports.join(', ')} } from 'lucide-react';\n`;
      content = content.slice(0, insertPosition) + newImport + content.slice(insertPosition);
    }

    fs.writeFileSync(filePath, content, 'utf-8');
    return true;
  }

  return false;
}

// Executar
const srcDir = path.join(__dirname, '..', 'src');
const files = getAllTsxFiles(srcDir);

let modifiedCount = 0;
let errorCount = 0;

files.forEach(file => {
  try {
    if (revertFile(file)) {
      modifiedCount++;
      console.log(`✓ ${path.relative(srcDir, file)}`);
    }
  } catch (error) {
    errorCount++;
    console.error(`✗ ${path.relative(srcDir, file)}: ${error.message}`);
  }
});

console.log(`\n=== Reversão concluída ===`);
console.log(`Arquivos modificados: ${modifiedCount}`);
console.log(`Erros: ${errorCount}`);
console.log(`Total processado: ${files.length}`);
