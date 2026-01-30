# 🚀 Comandi Rapidi Build APK

## Setup (Solo Prima Volta)
```bash
npm install -g eas-cli
eas login
```

## Build APK per Test
```bash
eas build -p android --profile preview
```

## Build per Play Store
```bash
eas build -p android --profile production
```

## Controllare Stato Build
```bash
eas build:list
```

## Scaricare Ultima Build
```bash
eas build:download --platform android --latest
```

## Vedere Build su Web
```bash
eas build:view --web
```

O vai su: https://expo.dev

---

## 📋 Prima di Buildare

- [ ] Ho testato l'app: `npm start`
- [ ] Ho fatto login: `eas whoami`  
- [ ] Ho committato le modifiche
- [ ] Ho connessione internet stabile

---

## ⏱️ Tempi Stimati

- **Prima build**: ~20-25 minuti
- **Build successive**: ~15-20 minuti

---

## 📥 Installare APK

1. Scarica APK dal link ricevuto via email
2. Trasferisci sul telefono Android
3. Abilita "Installa da fonti sconosciute"
4. Apri file e installa

---

## 💡 Tips

- Piano gratuito: 30 build/mese (più che sufficiente!)
- Riceverai email quando build è pronta
- APK funziona su Android 6.0+
- Dimensione APK: ~50-70 MB

---

## ❓ Problemi?

**Build fallita?**
```bash
eas build:list
eas build:view [BUILD-ID]
```

**Reset credenziali:**
```bash
eas credentials
```

Guida completa in: `APK_BUILD_GUIDE.md`
