# HackaPizza_2025

## Project Description
La soluzione si basa sull'utilizzo di un Knowledge Graph per salvare le principali entità presenti all'interno della Galassia (Pianeti, Ristoranti, Piatti, Ingredienti, ...) e le loro rispettive relazioni (es. un Ristorante --OFRRE_IL_PIATTO--> Piatto).

Per costruire il grafo, vengono prima processati i documenti tramite un LLM (gpt-4o-mini) per estrarre in modo strutturato entità e relazioni. L'output di questo step sono una serie di file JSON (es. script menu_to_json.py).
I file JSON vengono poi letti e utilizzati per scrivere delle query Cypher al fine di popolare il grafo (script graph_construction.py).

In fase di retrieval, le domande in linguaggio naturale vengono convertite in query Cypher al fine di ottenere tutte le entità che soddisfano una specifica domanda (script graph_retrieval.py).

## Files
### Misc/distanze.csv
Un csv che contiene la matrice delle distanze in anni luce tra i pianeti su cui si trovano i diversi ristoranti.
Serve per domande tipo "Quali sono i piatti disponibili nei ristoranti entro 126 anni luce da Cybertron, quest'ultimo incluso, che non includono Funghi dell'Etere?"

### Codice Galattico/Codice Galattico.pdf
Un documento legislativo contenente:

- Limiti quantitativi applicati all’utilizzo di alcuni ingredienti nella preparazione dei piatti
- Vincoli relativi alle certificazioni che gli chef hanno bisogno di acquisire per poter utilizzare specifiche tecniche di preparazione dei piatti

Serve per domande tipo "Che piatti posso mangiare [...] da un chef che ha le corrette licenze e certificazioni descritte dal Codice di Galattico?"

Contiene anche la descrizione degli Ordini (es. Ordine della Galassia di Andromeda, Ordine dei Naturalisti)

### Misc/Manuale di cucina.pdf
Manuale di cucina che include:

- L’elenco e la descrizione delle certificazione che uno chef può acquisire
- L’elenco degli ordini professionali gastronomici a cui uno chef può aderire
- L’elenco e la descrizione delle tecniche culinarie di preparazione esistenti

### Menu/nome_ristorante.pdf
Documenti contenenti i menù di 30 ristoranti differenti

Ogni file ha una descrizione del suo chef, le licenze ottenute (per ognuna c'è il nome della skill e il livello raggiunto) e poi il vero e proprio menu. Ogni piatto ha un nome, una descrizione, la lista degli ingredienti e la lista delle tecniche usate

### Blogpost/nome_ristorante.html
Documenti in markdown che contengono informazioni supplementari su alcuni ristoranti

Contiene le recensioni di due ristoranti con relativo voto su scala 0-10 espresso in stelle
Non sembrano esserci però domande in proposito

### Misc/dish_mapping.json
Mappatura dei piatti in id numerici progressivi, necessario per dare l’output finale

Lista di circa 300 piatti con formato "nome piatto": id_numerico
#### Note
* Menù/Datapizza.pdf: ignora testo trasparente all'interno del pdf, usa OCR per estrarre informazioni rilevanti, attenzione allo sfondo.Ignora testo in bianco all'interno del pdf, usa OCR per estrarre informazioni rilevanti, attenzione allo sfondo.
