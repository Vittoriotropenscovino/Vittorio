# Guida Passo-Passo per Testare Travel Memories

## 🎯 OPZIONE 1: Test nel Browser (PIÙ SEMPLICE)

### Passo 1: Aprire il Terminale
- **Windows**: Premi `Win + R`, digita `cmd` e premi Invio
- **Mac**: Premi `Cmd + Spazio`, digita `Terminal` e premi Invio
- **Linux**: Premi `Ctrl + Alt + T`

### Passo 2: Navigare nella Cartella del Progetto
```bash
cd percorso/al/tuo/repository/travel-memories
```

Esempio:
- Windows: `cd C:\Users\TuoNome\Desktop\Vittorio\travel-memories`
- Mac/Linux: `cd ~/Desktop/Vittorio/travel-memories`

### Passo 3: Installare le Dipendenze
```bash
npm install
```
⏱️ Questo richiederà 1-2 minuti. Vedrai scorrere del testo.

### Passo 4: Avviare l'App in Modalità Web
```bash
npm run web
```

### Passo 5: Aprire il Browser
Dopo alcuni secondi, si dovrebbe aprire automaticamente il browser all'indirizzo:
```
http://localhost:8081
```

Se non si apre automaticamente, apri manualmente Chrome/Firefox e vai a quell'indirizzo.

### ✅ Cosa Dovresti Vedere
- Una schermata con titolo "I Miei Ricordi di Viaggio"
- Un contatore "1 / 6" in alto a destra
- Una grande immagine della Torre Eiffel di Parigi
- Informazioni sul viaggio in basso
- Puoi scorrere orizzontalmente con il mouse o le frecce

### 🔧 Problemi Comuni Browser
**Problema**: L'app è in verticale
**Soluzione**:
1. Premi `F12` per aprire Developer Tools
2. Clicca l'icona "Toggle Device Toolbar" (📱)
3. Seleziona "Responsive"
4. Imposta dimensioni: Larghezza 800px, Altezza 480px
5. Clicca l'icona di rotazione per simulare landscape

---

## 📱 OPZIONE 2: Test su Telefono Reale (ESPERIENZA COMPLETA)

### Passo 1: Installare Expo Go sul Telefono
- **iPhone**: App Store → cerca "Expo Go" → Installa
- **Android**: Google Play Store → cerca "Expo Go" → Installa

### Passo 2: Assicurati che Telefono e Computer siano sulla Stessa WiFi
⚠️ IMPORTANTE: Entrambi i dispositivi devono essere sulla stessa rete WiFi!

### Passo 3: Aprire Terminale sul Computer
(vedi Passo 1 dell'Opzione 1)

### Passo 4: Navigare nella Cartella
```bash
cd percorso/al/tuo/repository/travel-memories
```

### Passo 5: Installare Dipendenze (se non già fatto)
```bash
npm install
```

### Passo 6: Avviare Expo
```bash
npm start
```

### Passo 7: Vedrai un QR Code nel Terminale
Apparirà qualcosa tipo:
```
┌──────────────────────────────────┐
│                                  │
│  █▀▀▀▀▀█ ▄▄█ ▀▄█ █▀▀▀▀▀█        │
│  █ ███ █ ▀ ▀▀▄▀  █ ███ █        │
│  █ ▀▀▀ █ █ ▀ ▀█  █ ▀▀▀ █        │
│  ▀▀▀▀▀▀▀ ▀ ▀ ▀ ▀ ▀▀▀▀▀▀▀        │
│  [... QR CODE ...]               │
│                                  │
└──────────────────────────────────┘

› Metro waiting on exp://192.168.1.X:8081
› Scan the QR code above with Expo Go (Android) or the Camera app (iOS)
```

### Passo 8: Scansionare il QR Code
- **iPhone**:
  1. Apri l'app Fotocamera
  2. Punta verso il QR code
  3. Tocca la notifica che appare

- **Android**:
  1. Apri l'app Expo Go
  2. Tocca "Scan QR Code"
  3. Punta verso il QR code

### Passo 9: Attendere il Caricamento
- L'app si caricherà (potrebbe richiedere 10-30 secondi la prima volta)
- Vedrai una barra di progresso

### Passo 10: RUOTARE IL TELEFONO IN ORIZZONTALE! 🔄
⚠️ FONDAMENTALE: Ruota il telefono in modalità landscape (orizzontale)

### ✅ Cosa Dovresti Vedere sul Telefono
- Schermo intero con l'immagine di Parigi
- Titolo "I Miei Ricordi di Viaggio" in alto
- Informazioni del viaggio in basso
- Puoi scorrere a sinistra/destra per vedere gli altri 5 ricordi
- Ogni ricordo ha: destinazione, paese, data, descrizione, stelle ⭐, e tag

### 🎨 I 6 Ricordi Inclusi
1. **Parigi, Francia** - Torre Eiffel al tramonto
2. **Tokyo, Giappone** - Fioritura dei ciliegi
3. **Santorini, Grecia** - Case bianche e mare blu
4. **New York, USA** - Central Park in autunno
5. **Machu Picchu, Perù** - Antica città Inca
6. **Venezia, Italia** - Canali e gondole

---

## 🔧 Risoluzione Problemi

### Il QR code non appare
**Soluzione 1**: Prova con tunnel
```bash
npx expo start --tunnel
```
(Richiederà di installare ngrok, premi Y)

### "Metro bundler failed to start"
**Soluzione**: Pulisci la cache
```bash
npx expo start -c
```

### L'app si chiude subito sul telefono
**Soluzione**:
1. Controlla che telefono e PC siano sulla stessa WiFi
2. Riavvia Expo sul computer: `npm start`
3. Riprova a scansionare

### "Unable to resolve module..."
**Soluzione**: Reinstalla dipendenze
```bash
rm -rf node_modules
npm install
npm start
```

### L'app è in verticale sul telefono
**Verifica**:
1. Il file `app.json` deve avere `"orientation": "landscape"`
2. Ruota fisicamente il telefono
3. Alcuni telefoni bloccano la rotazione - controlla le impostazioni

---

## 📝 Comandi Utili

```bash
# Avviare in modalità web
npm run web

# Avviare in modalità normale (QR code)
npm start

# Pulire cache e riavviare
npx expo start -c

# Vedere tutte le opzioni
npx expo start --help
```

---

## 🎯 Checklist di Test

Quando l'app è in esecuzione, verifica:

- [ ] Il telefono è in orizzontale
- [ ] Vedo il titolo "I Miei Ricordi di Viaggio"
- [ ] Vedo il contatore "1 / 6"
- [ ] L'immagine copre tutto lo schermo
- [ ] Posso scorrere orizzontalmente
- [ ] Vedo 6 ricordi in totale
- [ ] Ogni ricordo ha stelle di valutazione ⭐
- [ ] Vedo i tag in basso (es: #città #romantico)
- [ ] Lo sfondo è scuro
- [ ] Il testo è leggibile sull'immagine

---

## 💡 Prossimi Passi

Una volta verificato che funziona:

1. **Personalizza i ricordi**: Modifica `src/data/sampleMemories.ts`
2. **Cambia colori**: Modifica gli StyleSheet nei componenti
3. **Aggiungi più ricordi**: Espandi l'array in sampleMemories
4. **Usa tue foto**: Carica su servizi come Imgur o usa foto locali

---

## ❓ Hai Bisogno di Aiuto?

Se qualcosa non funziona:
1. Controlla quale errore specifico appare
2. Verifica che Node.js sia installato: `node --version`
3. Verifica che npm funzioni: `npm --version`
4. Riprova con `npm install` e `npm start`
