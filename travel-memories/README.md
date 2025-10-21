# Travel Memories - App Mobile per Ricordi di Viaggio

Un'app mobile React Native per visualizzare i propri ricordi di viaggio in modalità orizzontale (landscape).

## Caratteristiche

- **Modalità Orizzontale**: L'app è ottimizzata per l'utilizzo del telefono in orizzontale
- **Galleria Scorrevole**: Scorri orizzontalmente tra i tuoi ricordi di viaggio
- **Design Immersivo**: Immagini a schermo intero con overlay per le informazioni
- **Dettagli Completi**: Visualizza destinazione, paese, data, descrizione, valutazione e tag per ogni viaggio
- **Interfaccia Intuitiva**: Contatore dei ricordi e navigazione fluida

## Struttura del Progetto

```
travel-memories/
├── src/
│   ├── components/
│   │   ├── MemoryCard.tsx        # Componente per visualizzare singolo ricordo
│   │   └── MemoryGallery.tsx     # Galleria orizzontale dei ricordi
│   ├── data/
│   │   └── sampleMemories.ts     # Dati di esempio dei ricordi
│   └── types/
│       └── TravelMemory.ts       # Interfaccia TypeScript per i ricordi
├── App.js                         # Componente principale
├── app.json                       # Configurazione Expo
└── package.json
```

## Installazione

1. Assicurati di avere Node.js installato
2. Naviga nella cartella del progetto:
   ```bash
   cd travel-memories
   ```
3. Installa le dipendenze:
   ```bash
   npm install
   ```

## Esecuzione dell'App

### Usando Expo Go

1. Installa l'app Expo Go sul tuo dispositivo mobile:
   - [iOS](https://apps.apple.com/app/expo-go/id982107779)
   - [Android](https://play.google.com/store/apps/details?id=host.exp.exponent)

2. Avvia il server di sviluppo:
   ```bash
   npm start
   ```

3. Scansiona il QR code con:
   - **iOS**: Camera app
   - **Android**: App Expo Go

4. **Importante**: Ruota il telefono in modalità orizzontale per la migliore esperienza!

### Altre Opzioni

```bash
# Esegui su emulatore Android
npm run android

# Esegui su simulatore iOS (solo macOS)
npm run ios

# Esegui nel browser
npm run web
```

## Personalizzazione

### Aggiungere i Tuoi Ricordi

Modifica il file `src/data/sampleMemories.ts` per aggiungere i tuoi ricordi di viaggio:

```typescript
{
  id: '7',
  destination: 'Nome Destinazione',
  country: 'Nome Paese',
  date: '2024-01-01',
  description: 'La tua descrizione del viaggio...',
  imageUrl: 'URL della tua immagine',
  rating: 5,
  tags: ['tag1', 'tag2', 'tag3'],
}
```

### Modificare i Colori e Stili

I componenti utilizzano StyleSheet di React Native. Puoi modificare i colori nei file:
- `src/components/MemoryCard.tsx`
- `src/components/MemoryGallery.tsx`

## Tecnologie Utilizzate

- **React Native**: Framework per app mobile
- **Expo**: Piattaforma per sviluppo React Native
- **TypeScript**: Per type safety nei componenti
- **React Hooks**: useState, useRef per la gestione dello stato

## Funzionalità Future

Possibili miglioramenti:
- Aggiungere persistenza dei dati con AsyncStorage
- Integrazione con fotocamera per aggiungere nuovi ricordi
- Filtri per tag e destinazioni
- Condivisione sui social media
- Mappa dei viaggi visitati
- Statistiche dei viaggi (paesi visitati, distanza percorsa, ecc.)

## Licenza

MIT

## Supporto

Per problemi o domande, apri una issue nel repository.
