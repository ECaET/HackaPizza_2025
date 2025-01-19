from dotenv import load_dotenv
import json
from neo4j import GraphDatabase
import os
from utils import (
    add_chef,
    add_menu,
    add_restaurant,
    create_indexes,
    get_graph_schema,
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


create_indexes(driver)