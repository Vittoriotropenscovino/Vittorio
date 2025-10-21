# 🚀 Quickstart - Travel Memories

## Verifica Setup (PRIMA DI TUTTO)

```bash
node verify-setup.js
```

Se vedi ✨ **PERFETTO!**, puoi procedere!

---

## 🌐 Opzione 1: Test Veloce nel Browser (2 minuti)

```bash
npm run web
```

Vai su `http://localhost:8081` e ruota la vista in landscape (F12 → Device Toolbar → Landscape)

---

## 📱 Opzione 2: Test su Telefono Reale

### Setup Una-Tantum:
1. Installa **Expo Go** sul telefono (App Store / Play Store)
2. Collega telefono e PC alla stessa WiFi

### Ogni Volta:
```bash
npm start
```

Scansiona il QR code con:
- **iOS**: App Fotocamera
- **Android**: App Expo Go

**IMPORTANTE**: Ruota il telefono in orizzontale! 🔄

---

## ❓ Problemi?

### Non vedo il QR code?
```bash
npx expo start --tunnel
```

### Errori strani?
```bash
rm -rf node_modules
npm install
npm start
```

### Ancora problemi?
Leggi la guida completa in `TESTING_GUIDE.md`

---

## ✅ Cosa Dovresti Vedere

- Titolo: "I Miei Ricordi di Viaggio"
- Contatore: "1 / 6"
- Immagini a schermo intero
- 6 destinazioni da scorrere orizzontalmente
- Valutazioni con stelle ⭐
- Tag come #città #romantico

---

## 🎯 Primi Passi Dopo il Test

1. **Personalizza i ricordi**: Modifica `src/data/sampleMemories.ts`
2. **Cambia i colori**: Modifica i file in `src/components/`
3. **Aggiungi foto tue**: Usa URL di immagini online

Buon viaggio! 🌍
