# Driver Behavior Dataset – Profilazione dello Stile di Guida

## Descrizione

Questo repository contiene **codice, dataset e risultati** prodotti durante il tirocinio, finalizzati alla **costruzione di un dataset per la profilazione dei conducenti** in base al loro stile di guida.  
L’obiettivo è adattare un modello di guida esistente al comportamento individuale dei conducenti, al fine di analizzare e ottimizzare raccomandazioni e strategie di **eco-driving**.

I dati raccolti includono simulazioni di conducenti in ambienti virtuali, con parametri comportamentali come stili di accelerazione, decelerazione, percorrenza dei tratti e altre variabili legate al comportamento alla guida.

---

## Struttura del repository

- `core/` – Contiene il core dell'applicazione e le sue funzioni principali   
- `past_life/` – Codice precedente o di prova, dataset e immagini di test; funziona ma non viene più utilizzato nella pipeline principale.
- `coerenza/` - Contiene il codice per generare un profilo di guida assegnandogli un’etichetta **personalizzata**, quindi non calcolata tramite IDS.
- `savage/` - Contiene il codice per generare un **profilo di guida singolo** a partire da un profilo di guida già caricato.


Per maggiori informazioni sui file contenuti nelle singole cartelle, si consiglia di consultare i **README locali** presenti in ogni cartella (quando disponibili).

---

## Come clonare il repository

```bash
git clone https://github.com/<tuo-username>/eco-driving-dataset.git
