# Torn Economy Analyzer and Monitor

Questo progetto consiste in due script Python:
1. UbuntuTech.py: analizza l'economia di Torn e genera file CSV con i dati.
2. Monitor.py: visualizza i dati generati da UbuntuTech.py in una GUI interattiva.

## Requisiti

- Python 3.7+
- requests
- pandas
- matplotlib
- seaborn
- PyQt5

Per installare le dipendenze, esegui:
pip install requests pandas matplotlib seaborn PyQt5


## Configurazione

1. Assicurati che entrambi gli script (UbuntuTech.py e Monitor.py) siano nella stessa directory.
2. Modifica la variabile API_KEY in UbuntuTech.py con la tua chiave API di Torn.

## Utilizzo

1. Esegui Monitor.py:


python Monitor.py


Questo avvierà l'interfaccia grafica che mostrerà i grafici dell'economia di Torn.
I dati verranno aggiornati automaticamente ogni 30 minuti.

## Note

- UbuntuTech.py può essere eseguito anche indipendentemente per generare i file CSV senza la GUI.
- Assicurati di rispettare i limiti di utilizzo dell'API di Torn per evitare di essere temporaneamente bloccato.
