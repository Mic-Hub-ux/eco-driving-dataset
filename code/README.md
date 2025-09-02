# Code – Eco-Driving Dataset

Questa cartella contiene **tutti gli script principali** utilizzati per la costruzione e l'analisi del dataset sul comportamento dei conducenti.  
Il codice permette di processare i dati raccolti dalle simulazioni, generare il dataset finale e produrre visualizzazioni come scatterplot per l’analisi dello stile di guida.

## Script principali

- `estrai_profilo_guida.py`  
  Estrae e struttura i dati relativi a ciascun conducente per la costruzione del dataset.

- `analisi_correlazione_IDS_pesato_V4.py`  
  Analizza la correlazione tra variabili del dataset e genera scatterplot e statistiche di sintesi.

- `trend_classification.py` e `trend_extraction.py`
  Contengono la logica per il calcolo dell'IDS relativo ad una singola guida e la conseguente generazione di un'etichetta

## Note operative

- È consigliabile eseguire `estrai_profilo_guida.py` **prima** di `analisi_correlazione_IDS_pesato_V4.py`.
- Tutti i dati di input devono essere presenti nella cartella `input_dataset` del repository principale.
