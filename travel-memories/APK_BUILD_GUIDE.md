# 📦 Guida: Creare l'APK di Travel Memories

## Sì! Puoi creare un APK in diversi modi:

### 🏆 METODO CONSIGLIATO: EAS Build (Ufficiale Expo)

**Passo 1:** Installa EAS CLI
```bash
npm install -g eas-cli
```

**Passo 2:** Login (crea account gratuito se necessario)
```bash
eas login
```

**Passo 3:** Build APK
```bash
eas build -p android --profile preview
```

**Risultato:** Dopo 15-20 minuti ricevi link per scaricare APK!

**Vantaggi:**
- ✅ Completamente gratuito (30 build/mese)
- ✅ Non serve Android Studio
- ✅ Funziona su qualsiasi computer
- ✅ Gestisce tutto automaticamente

---

### 🌐 ALTRI SITI/SERVIZI

**1. Codemagic** (https://codemagic.io)
- Piano gratuito: 500 minuti/mese
- Supporta Expo
- Interfaccia web

**2. Bitrise** (https://bitrise.io)  
- Build cloud
- Integrazione GitHub
- Piano free disponibile

**3. GitHub Actions**
- Gratuito per repo pubblici
- Richiede configurazione

---

### 📱 Installare l'APK sul Telefono

1. Scarica il file `.apk` dal link ricevuto
2. Trasferisci sul telefono (USB/email/cloud)
3. Abilita "Installa da fonti sconosciute" nelle impostazioni
4. Apri il file APK e installa

---

### 💰 Costi

**EAS Build Free:**
- 30 build al mese
- Perfetto per uso personale

**Google Play Store:**
- Se vuoi pubblicare: $25 una tantum per account sviluppatore

---

### ⚡ Quick Start

```bash
cd travel-memories
eas login
eas build -p android --profile preview
```

Aspetta 20 minuti → Scarica APK → Installa sul telefono!

Per maggiori dettagli vedi `BUILD_COMMANDS.md`
