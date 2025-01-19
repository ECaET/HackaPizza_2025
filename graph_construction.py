from dotenv import load_dotenv
import json
from neo4j import GraphDatabase
import os
import pandas as pd
from utils import (
    add_chef,
    add_menu,
    add_planet,
    add_restaurant,
    aggiorna_tecniche,
    create_indexes,
    get_graph_schema,
    process_and_insert_licenses,
    process_licenses,
    process_planet_data,
    submit_queries,
)

load_dotenv()


os.environ["NEO4J_URI"] = os.getenv("NEO4J_URI")
os.environ["NEO4J_USERNAME"] = os.getenv("NEO4J_USERNAME")
os.environ["NEO4J_PASSWORD"] = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(os.environ["NEO4J_URI"], auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]))

schema = get_graph_schema(driver)
print(schema)

directory = 'menu_json'

for filename in os.listdir(directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if 'nome_ristorante' in data:
                add_restaurant(data['nome_ristorante'])

for filename in os.listdir(directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if 'nome_ristorante' in data:
                nome_ristorante = data['nome_ristorante']
                if 'nome_chef' in data:
                    add_chef(data['nome_chef'], nome_ristorante)
                if 'menu' in data:
                    add_menu(data['menu'], nome_ristorante)

# Pianeti
planet_directory = 'restaurant_planet_json'

for filename in os.listdir(planet_directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if 'nome_ristorante' in data:
                nome_ristorante = data['nome_ristorante']
                if 'nome_pianeta' in data:
                    add_planet(data['nome_pianeta'], nome_ristorante)


# Carica il file CSV in un DataFrame
df = pd.read_csv('Distanze.csv', index_col=0, delimiter=',')

# Crea la struttura dati desiderata
distanze = {}
for pianeta in df.index:
    distanze[pianeta] = df.loc[pianeta].to_dict()

# Rimuovi le distanze verso se stessi (0)
for pianeta, distanze_pianeta in distanze.items():
    if pianeta in distanze_pianeta:
        del distanze_pianeta[pianeta]

# Converti il dizionario in una lista di dizionari
distanze_pianeti = [{pianeta: distanze_pianeta} for pianeta, distanze_pianeta in distanze.items()]

print(distanze_pianeti)

queries = process_planet_data(distanze_pianeti)

submit_queries(driver, queries)

process_and_insert_licenses(driver, "licenze.json")


# Licenze

licenses_directory = "licenze_json"

process_licenses(driver, licenses_directory)

tecniche_directory = "tecniche.json"

aggiorna_tecniche(driver, tecniche_directory)


create_indexes(driver)