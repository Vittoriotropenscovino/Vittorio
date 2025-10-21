#!/usr/bin/env node

/**
 * Script di verifica per Travel Memories
 * Controlla che tutti i file e le configurazioni siano corretti
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Verifica Setup Travel Memories\n');

let errors = 0;
let warnings = 0;

// Funzione helper per check
function check(condition, message, type = 'error') {
  if (condition) {
    console.log(`✅ ${message}`);
    return true;
  } else {
    if (type === 'error') {
      console.log(`❌ ${message}`);
      errors++;
    } else {
      console.log(`⚠️  ${message}`);
      warnings++;
    }
    return false;
  }
}

// 1. Verifica esistenza file principali
console.log('📁 Verifico file principali...\n');

check(fs.existsSync('App.js'), 'App.js esiste');
check(fs.existsSync('app.json'), 'app.json esiste');
check(fs.existsSync('package.json'), 'package.json esiste');
check(fs.existsSync('tsconfig.json'), 'tsconfig.json esiste');
check(fs.existsSync('README.md'), 'README.md esiste');
check(fs.existsSync('TESTING_GUIDE.md'), 'TESTING_GUIDE.md esiste');

// 2. Verifica componenti
console.log('\n🧩 Verifico componenti...\n');

check(fs.existsSync('src/components/MemoryCard.tsx'), 'MemoryCard.tsx esiste');
check(fs.existsSync('src/components/MemoryGallery.tsx'), 'MemoryGallery.tsx esiste');

// 3. Verifica dati e tipi
console.log('\n📊 Verifico dati e tipi...\n');

check(fs.existsSync('src/types/TravelMemory.ts'), 'TravelMemory.ts esiste');
check(fs.existsSync('src/data/sampleMemories.ts'), 'sampleMemories.ts esiste');

// 4. Verifica configurazione app.json
console.log('\n⚙️  Verifico configurazione...\n');

try {
  const appJson = JSON.parse(fs.readFileSync('app.json', 'utf8'));
  check(appJson.expo.orientation === 'landscape',
    'Orientamento impostato su landscape');
  check(appJson.expo.name === 'travel-memories',
    'Nome app corretto');
} catch (e) {
  check(false, 'app.json è valido JSON');
}

// 5. Verifica package.json
console.log('\n📦 Verifico dipendenze...\n');

try {
  const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));

  check(packageJson.dependencies['expo'], 'Expo installato');
  check(packageJson.dependencies['react'], 'React installato');
  check(packageJson.dependencies['react-native'], 'React Native installato');
  check(packageJson.dependencies['expo-status-bar'], 'Expo Status Bar installato');

  check(packageJson.devDependencies && packageJson.devDependencies['typescript'],
    'TypeScript installato', 'warning');
  check(packageJson.devDependencies && packageJson.devDependencies['@types/react'],
    '@types/react installato', 'warning');

  check(packageJson.scripts['start'], 'Script start presente');
  check(packageJson.scripts['web'], 'Script web presente');
  check(packageJson.scripts['android'], 'Script android presente');
  check(packageJson.scripts['ios'], 'Script ios presente');

} catch (e) {
  check(false, 'package.json è valido JSON');
}

// 6. Verifica node_modules
console.log('\n📚 Verifico installazione...\n');

check(fs.existsSync('node_modules'), 'node_modules esiste');
check(fs.existsSync('node_modules/expo'), 'Expo è installato');
check(fs.existsSync('node_modules/react'), 'React è installato');

// 7. Verifica contenuto App.js
console.log('\n📄 Verifico App.js...\n');

try {
  const appContent = fs.readFileSync('App.js', 'utf8');
  check(appContent.includes('MemoryGallery'), 'App.js importa MemoryGallery');
  check(appContent.includes('sampleMemories'), 'App.js importa sampleMemories');
  check(appContent.includes('StatusBar'), 'App.js include StatusBar');
} catch (e) {
  check(false, 'Impossibile leggere App.js');
}

// 8. Verifica sampleMemories
console.log('\n🗺️  Verifico dati di esempio...\n');

try {
  const memoriesContent = fs.readFileSync('src/data/sampleMemories.ts', 'utf8');
  const memoriesCount = (memoriesContent.match(/id: '/g) || []).length;
  check(memoriesCount === 6, `6 ricordi di viaggio presenti (trovati: ${memoriesCount})`);
  check(memoriesContent.includes('Parigi'), 'Ricordo di Parigi presente');
  check(memoriesContent.includes('Tokyo'), 'Ricordo di Tokyo presente');
  check(memoriesContent.includes('Venezia'), 'Ricordo di Venezia presente');
} catch (e) {
  check(false, 'Impossibile leggere sampleMemories.ts');
}

// Report finale
console.log('\n' + '='.repeat(50));
console.log('📊 REPORT FINALE\n');

if (errors === 0 && warnings === 0) {
  console.log('✨ PERFETTO! Tutto è configurato correttamente!');
  console.log('\n🚀 Puoi procedere con:');
  console.log('   npm start      (per mobile con QR code)');
  console.log('   npm run web    (per testare nel browser)');
} else {
  if (errors > 0) {
    console.log(`❌ ${errors} errore/i trovato/i`);
  }
  if (warnings > 0) {
    console.log(`⚠️  ${warnings} warning trovato/i`);
  }

  if (errors > 0) {
    console.log('\n⚠️  Ci sono problemi da risolvere prima di procedere.');
    console.log('   Esegui: npm install');
  } else {
    console.log('\n✅ Gli errori critici sono assenti.');
    console.log('   I warning non impediscono il funzionamento dell\'app.');
    console.log('\n🚀 Puoi procedere con:');
    console.log('   npm start');
  }
}

console.log('='.repeat(50));

process.exit(errors > 0 ? 1 : 0);
