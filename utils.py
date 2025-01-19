import csv
import fitz
import json
from langchain_neo4j import GraphCypherQAChain
from langchain_core.prompts.prompt import PromptTemplate
import os


def add_chef(driver, chef, nome_ristorante):
    query = """
    MERGE (c:Chef {nome: $chef})
    WITH c
    MATCH (r:Ristorante {nome: $nome_ristorante})
    MERGE (r)-[:GESTITO_DA]->(c)
    RETURN c
    """
    with driver.session() as session:
        result = session.run(query, chef=chef, nome_ristorante=nome_ristorante)
        return result.single()
    

def add_ingrediente(driver, ingrediente, nome_piatto):
    query = """
    MERGE (i:Ingrediente {nome: $ingrediente})
    WITH i
    MATCH (p:Piatto {nome: $nome_piatto})
    MERGE (p)-[:CONTIENE]->(i)
    RETURN i
    """
    with driver.session() as session:
        result = session.run(query, ingrediente=ingrediente, nome_piatto=nome_piatto)
        return result.single()


def add_menu(menu, nome_ristorante):
    """Ricava una lista di piatti, ogni piatto è un dizionario con chiavi:
    nome_piatto: str,
    ingredienti: list[str],
    tecniche: list [str]
    """
    
    for piatto in menu:
        nome_piatto = piatto['nome_piatto'] if 'nome_piatto' in piatto else ''
        add_piatto(nome_piatto, nome_ristorante)
                        
        if 'ingredienti' in piatto:
            ingredienti = piatto['ingredienti']
            for ingrediente in ingredienti:
                add_ingrediente(ingrediente, nome_piatto)

        if 'tecniche' in piatto:
            tecniche = piatto['tecniche']
            for tecnica in tecniche:
                add_tecnica(tecnica, nome_piatto)
    

def add_piatto(driver, piatto, nome_ristorante):
    query = """
    MERGE (p:Piatto {nome: $piatto})
    WITH p
    MATCH (r:Ristorante {nome: $nome_ristorante})
    MERGE (r)-[:OFFRE_IL_PIATTO]->(p)
    RETURN p
    """
    with driver.session() as session:
        result = session.run(query, piatto=piatto, nome_ristorante=nome_ristorante)
        return result.single()
    

def add_planet(driver, pianeta, nome_ristorante):
    query = """
    MERGE (p:Pianeta {nome: $pianeta})
    WITH p
    MATCH (r:Ristorante {nome: $nome_ristorante})
    MERGE (r)-[:SI_TROVA_SU]->(p)
    RETURN p
    """
    with driver.session() as session:
        result = session.run(query, pianeta=pianeta, nome_ristorante=nome_ristorante)
        return result.single()
    

def add_restaurant(driver, restaurant_name):
    query = """
    CREATE (r:Ristorante {nome: $nome})
    RETURN r
    """
    with driver.session() as session:
        result = session.run(query, nome=restaurant_name)
        return result.single()


def add_tecnica(driver, tecnica, nome_piatto):
    query = """
    MERGE (t:Tecnica {nome: $tecnica})
    WITH t
    MATCH (p:Piatto {nome: $nome_piatto})
    MERGE (p)-[:REALIZZATO_CON_LA_TECNICA]->(t)
    RETURN t
    """
    with driver.session() as session:
        result = session.run(query, tecnica=tecnica, nome_piatto=nome_piatto)
        return result.single()
    

def aggiorna_tecniche(driver, file_json, max_distance=2):
    # Leggi il file JSON
    with open(file_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    
    def aggiungi_descrizione(tx, nome_tecnica, descrizione, max_distance):
        query = """
        MATCH (t:Tecnica)
        WHERE apoc.text.levenshteinDistance(t.nome, $nome_tecnica) <= $max_distance
        SET t.descrizione = $descrizione
        """
        tx.run(query, nome_tecnica=nome_tecnica, descrizione=descrizione, max_distance=max_distance)
    
    # Itera attraverso i dati e aggiorna le tecniche
    with driver.session() as session:
        for gruppo in data:
            descrizione = gruppo['gruppo_tecniche']
            for tecnica in gruppo['lista tecniche']:
                session.execute_write(aggiungi_descrizione, tecnica, descrizione, max_distance)
    
    # Chiudi la connessione al database
    driver.close()


def answer_questions(llm, graph, standard_template, fuzzy_template, questions_file_path, answers_txt_path: str='lista_risposte.txt') -> None:

    chain_licenze = GraphCypherQAChain.from_llm(
        llm, 
        graph=graph, 
        verbose=True, 
        allow_dangerous_requests=True, 
        cypher_prompt=PromptTemplate(input_variables=["schema", "question"], template=standard_template),
        return_direct=True,
        top_k=50,
        validate_cypher=True
    )

    chain_licenze_fuzzy = GraphCypherQAChain.from_llm(
        llm, 
        graph=graph, 
        verbose=True, 
        allow_dangerous_requests=True, 
        cypher_prompt=PromptTemplate(input_variables=["schema", "question"], template=fuzzy_template),
        return_direct=True,
        top_k=50,
        validate_cypher=True
    )

    lista_domande = read_csv(questions_file_path)
    lista_risposte = {}

    with open(answers_txt_path, 'w') as file:
        for indice, domanda in enumerate(lista_domande):
            try:
                answer = chain_licenze.invoke(domanda)
            except:
                answer = {"result":[]}
            if not answer["result"]:
                try:
                    answer = chain_licenze_fuzzy.invoke(domanda)
                except:
                    pass
            lista_piatti = []
            for piatto in answer["result"]:
                lista_piatti.append(list(piatto.values())[0])
            lista_risposte[indice+1] = lista_piatti
            file.write(f"{indice+1}: {lista_risposte[indice+1]}\n")
    return lista_risposte
    

def call_gpt(client, msg, model_name="gpt-4o-mini"):

    result = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": msg}],
        temperature=0
    )

    return result.choices[0].message.content


def create_indexes(driver):
    with driver.session() as session:
        for label in ["Ristorante", "Chef", "Piatto", "Ingrediente", "Tecnica", "Pianeta", "Licenza"]:
            session.run(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.id IS UNIQUE")


def get_graph_schema(driver):
    with driver.session() as session:
        result = session.run("""CALL db.schema.visualization()
               """)
        return result.single()


def json_txt_to_submission(dish_mapping_path: str, input_txt_path: str, output_csv_path: str, empty_guess_filler: list=[288]) -> None:

    """
    Converte i risultati della Chain in un csv pronto alla submission su Kaggle

    ### Input
    * input_txt_path: path al file txt di input, contenente un json le cui chiavi sono l'ID intero della domanda posta
    e i valori una lista contenente le ricette restituite dalla query
    * dish_mapping_path: path al file di mapping, contenente un json le cui chiavi sono il nome della ricetta
    e i valori l'ID intero corrispondente
    * output_csv_path: path al csv di output da caricare su Kaggle
    * empty_guess_filler: lista sostituita a tutte le risposte che non contengono alcuna ricetta, con default
    """

    # Read the input file
    with open(input_txt_path, "r") as infile:
        data = json.load(infile)

    with open(dish_mapping_path) as f:
        dish_mapping = json.load(f)

    submission = {}

    for question_number, corresponding_recipies_list in data.items():
        mapped_list = []
        for elem in corresponding_recipies_list:
            if elem in dish_mapping:
                mapped_list.append(dish_mapping[elem])
            else:
                mapped_list.append(999)
                print(f"Elemento senza match: {elem}")
        
        submission[question_number] = mapped_list
        if not submission[question_number]:
            submission[question_number] = empty_guess_filler

    # Prepare the output content
    output_lines = ["row_id,result"]
    for key, values in submission.items():
        row = str(int(key)) + ',"' + ','.join(map(str, values)) + '"'
        output_lines.append(row)

    # Write the output to a new file
    with open(output_csv_path, "w") as outfile:
        outfile.write("\n".join(output_lines))

    return


def parse_pdfs_folder(pdf_folder_path, customized_prompt, model_name="gpt-4o-mini"):
    # Iterate through all PDF files in the folder
    for filename in os.listdir(pdf_folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder_path, filename)
            # Read the PDF and store the content in menu_text
            menu_text = read_pdf_to_string(pdf_path)
            
            prompt = customized_prompt + menu_text

            #result = model.chat(messages=[{'role': 'user', 'content': prompt}])

            result = call_gpt(prompt, model_name)

            #print(result['choices'][0]['message']['content'])

            #save_string_to_json_file(result['choices'][0]['message']['content'])

            save_planet_to_json_file(result)


def process_and_insert_licenses(driver, json_file_path):
    # Carica il file JSON
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Connessione al database Neo4j
    #driver = GraphDatabase.driver(neo4j_uri, auth=(user, password))
    
    def insert_license(tx, nome_licenza, sigla_licenza):
        query = (
            "CREATE (l:Licenza {nome: $nome_licenza, sigla: $sigla_licenza})"
        )
        tx.run(query, nome_licenza=nome_licenza, sigla_licenza=sigla_licenza)
    
    with driver.session() as session:
        for licenza in data:
            nome_licenza = licenza['nome_licenza']
            sigla_licenza = licenza['sigla_licenza']
            session.execute_write(insert_license, nome_licenza, sigla_licenza)
    
    driver.close()


def process_licenses(driver, directory):
    #driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def create_relationship(tx, ristorante, licenza, grado):
        query = (
            "MATCH (r:Ristorante {nome: $ristorante})-[:GESTITO_DA]->(c:Chef), "
            "(l:Licenza {nome: $licenza}) "
            "MERGE (c)-[rel:POSSIEDE_LICENZA {grado: $grado}]->(l)"
        )
        tx.run(query, ristorante=ristorante, licenza=licenza, grado=grado)
    
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                ristorante = data['nome_ristorante']
                for licenza in data['licenze']:
                    nome_licenza = licenza['nome_licenza']
                    grado_licenza = roman_to_int(licenza['grado_licenza'])
                    print(grado_licenza)
                    with driver.session() as session:
                        session.execute_write(create_relationship, ristorante, nome_licenza, grado_licenza)
    
    driver.close()


def process_planet_data(planet_data):
    cypher_queries = []
    for planet in planet_data:
        for key, values in planet.items():
            for planet, distance in values.items():
                    
                query = f"""
                MATCH (p1:Pianeta {{nome: '{key}'}})
                MATCH (p2:Pianeta {{nome: '{planet}'}})
                CREATE (p1)-[:HA_DISTANZA_ANNI_LUCE {{distanza: {distance}}}]->(p2)
                """
                cypher_queries.append(query)

    return cypher_queries


def read_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        lista_domande = []
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            lista_domande.append(row['domanda'])
        return lista_domande


def read_pdf_to_string(pdf_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    menu_text = ""

    # Iterate through each page
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        menu_text += page.get_text()

    return menu_text


def roman_to_int(roman):

    # Se l'input è già un intero, restituiscilo come stringa
    if isinstance(roman, int):
        return str(roman)
    
    # Se l'input è una stringa che rappresenta un intero, restituiscila direttamente
    if isinstance(roman, str) and roman.isdigit():
        return roman
    
    # Dizionario di mappatura dei numeri romani ai loro valori interi
    roman_to_int_map = {
        'I': '1',
        'II': '2',
        'III': '3',
        'IV': '4',
        'V': '5',
        'VI': '6',
        'VI+': '6+'
    }
    
    # Restituisce il valore intero corrispondente al numero romano come stringa, o None se non trovato
    
    return roman_to_int_map.get(roman, "0")


def save_planet_to_json_file(json_string):
    # Rimuove eventuali intestazioni ```json iniziali e ``` finali
    json_string = json_string.strip().strip('```json').strip('```')
    
    # Parse the JSON string
    data = json.loads(json_string)
    
    # Extract the restaurant name
    restaurant_name = data.get("nome_ristorante", "default_name").replace(" ", "_")
    
    # Define the file name
    file_name = f"{restaurant_name}_planet.json"
    
    # Save the JSON content to the file
    with open(file_name, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def submit_queries(driver, queries):
    with driver.session() as session:
        for query in queries:
            session.run(query)