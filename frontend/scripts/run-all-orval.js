const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Ler todos os configs
const configs = fs.readdirSync(path.join(__dirname, '..'))
  .filter(f => f.startsWith('orval.config.') && f.endsWith('.ts'))
  .map(f => f.replace('orval.config.', '').replace('.ts', ''));

console.log(`🚀 Regenerando ${configs.length} módulos Orval...\n`);

let successCount = 0;
let failCount = 0;

configs.forEach((module, i) => {
  console.log(`[${i+1}/${configs.length}] Gerando ${module}...`);
  try {
    execSync(`npm run orval:${module}`, {
      stdio: 'inherit',
      cwd: path.join(__dirname, '..')
    });
    console.log(`✅ ${module} concluído\n`);
    successCount++;
  } catch (error) {
    console.error(`❌ ${module} falhou\n`);
    failCount++;
  }
});

console.log('\n' + '='.repeat(50));
console.log(`🎉 Regeneração completa!`);
console.log(`✅ Sucesso: ${successCount}/${configs.length}`);
if (failCount > 0) {
  console.log(`❌ Falhas: ${failCount}/${configs.length}`);
}
console.log('='.repeat(50));
