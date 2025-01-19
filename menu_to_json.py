import json
from openai import OpenAI
import os
from utils import parse_pdfs_folder


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# Path to the PDF folder
pdf_folder_path = "../Menu"


PROMPT_RESTAURANT_MENU_TO_JSON = """
Ti fornirò in input il testo di un menù di un ristorante, contenente informazioni riguardo il suo chef, i piatti proposti nel ristorante con relativi ingredienti e tecniche.
Voglio che tu estragga le informazioni e le strutturi in modo rigoroso in un JSON avente la seguente struttura di esempio:
{
  "nome_ristorante": "Anima Cosmica",
  "nome_chef": "Aurora Stellaris",
  "menu": [
      {
        "nome_piatto": "Nebulosa Celestiale alla Stellaris",
        "ingredienti": [
          "Shard di Materia Oscura",
          "Carne di Balena Spaziale"
        ],
        "tecniche": [
          "Cottura a Vapore con Flusso di Particelle Isoarmoniche",
          "Cottura a Vapore Termocinetica Multipla"
        ]
      },
            {
        "nome_piatto": "Sinfonia Tempolare Galattica",
        "ingredienti": [
          "Polvere di Crononite",
          "Carne di Kraken"
        ],
        "tecniche": [
          "Bollitura Infrasonica Armonizzata",
          "Cottura con Microonde Entropiche Sincronizzate"
        ]
      }
    ]
}

Produci in output solo il JSON corretto. Non aggiungere altri commenti o testo superfluo.

Testo da convertire in JSON:

"""

parse_pdfs_folder(pdf_folder_path, PROMPT_RESTAURANT_MENU_TO_JSON)


PROMPT_RESTAURANT_MENU_TO_PLANET = """
Ti fornirò in input il testo di un menù di un ristorante, contenente informazioni riguardo il suo chef, i piatti proposti nel ristorante con relativi ingredienti e tecniche.
Voglio che tu estragga due informazioni (nome_ristorante e nome_pianeta) e le strutturi in modo rigoroso in un JSON avente la seguente struttura:
{
  "nome_ristorante": "Anima Cosmica",
  "nome_pianeta": "Aurora Pandora"
}

I nomi possibili dei Pianeti sono: Arrakis, Pandora, Cybertron, Ego, Montressor, Krypton, Namecc, Klyntar, Asgard, Tatooine

Produci in output solo il JSON corretto. Non aggiungere altri commenti o testo superfluo.

Testo da convertire in JSON:

"""

parse_pdfs_folder(pdf_folder_path, PROMPT_RESTAURANT_MENU_TO_PLANET)