from dotenv import load_dotenv

from langchain_neo4j import Neo4jGraph
from langchain_openai import ChatOpenAI

import os
from utils import answer_questions


load_dotenv()


os.environ["NEO4J_URI"] = os.getenv("NEO4J_URI")
os.environ["NEO4J_USERNAME"] = os.getenv("NEO4J_USERNAME")
os.environ["NEO4J_PASSWORD"] = os.getenv("NEO4J_PASSWORD")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

model_name = 'gpt-4o'


llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    api_key=OPENAI_API_KEY
)

graph = Neo4jGraph(
    url=os.environ["NEO4J_URI"],
    username=os.environ["NEO4J_USERNAME"], 
    password=os.environ["NEO4J_PASSWORD"],
    enhanced_schema=True
)

print(graph.schema)

questions_file_path = 'domande.csv'
answers_txt_path = 'lista_risposte.txt'


CYPHER_GENERATION_TEMPLATE_STANDARD = """Task:Generate Cypher statement to query a graph database.
The graph database contains restaurants and dishes from an alien galaxy.
Each restaurant is located in a planet.
Each planet has a given distance from the other ones expressed in light years. 
The distance between planets is specified as a property of the 'HA_DISTANZA_ANNI_LUCE' relationship. This property is named 'distanza'.
Each Chef can have one or more licenses with a specific grade/score. The score is specified as an attribute in the relationship POSSIEDE_LICENZA that connects the nodes Chef and Licenza.
When you need to find a node Licenza, you must use his attributes 'nome' and 'sigla' in OR condition to find the match.


Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Your goal is always to find a dish (Piatto) or a list of dishes starting from some filters.
You will never be provided with a name of a dish in the initial question.

 
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.

Examples: Here are a few examples of generated Cypher statements for particular questions:
# Quali sono i piatti disponibili nei ristoranti entro 200 anni luce da Pandora?

MATCH (p1:Pianeta {{nome: "Pandora"}})-[rel:HA_DISTANZA_ANNI_LUCE]->(p2:Pianeta),
      (r:Ristorante)-[:SI_TROVA_SU]->(p2),
      (r)-[:OFFRE_IL_PIATTO]->(piatto:Piatto)
WHERE rel.distanza <= 200
RETURN DISTINCT piatto.nome


The question is:
{question}"""


CYPHER_GENERATION_TEMPLATE_FUZZY = """Task:Generate Cypher statement to query a graph database.
The graph database contains restaurants and dishes from an alien galaxy.
Each restaurant is located in a planet.
Each planet has a given distance from the other ones expressed in light years. 
The distance between planets is specified as a property of the 'HA_DISTANZA_ANNI_LUCE' relationship. This property is named 'distanza'.
Each Chef can have one or more licenses with a specific grade/score. The score is specified as an attribute in the relationship POSSIEDE_LICENZA that connects the nodes Chef and Licenza.
When you need to find a node Licenza, you must use his attributes 'nome' and 'sigla' in OR condition to find the match.


Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Your goal is always to find a dish (Piatto) or a list of dishes starting from some filters.
You will never be provided with a name of a dish in the initial question.
In order to be resilient to possible mispelling, always use the Levenshtein Distance with a threshold of 3, after converting to lower case. 

 
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.

Examples: Here are a few examples of generated Cypher statements for particular questions:
# Quali sono i piatti disponibili nei ristoranti entro 200 anni luce da Pandora?

MATCH (p1:Pianeta {{nome: "Pandora"}})-[rel:HA_DISTANZA_ANNI_LUCE]->(p2:Pianeta),
      (r:Ristorante)-[:SI_TROVA_SU]->(p2),
      (r)-[:OFFRE_IL_PIATTO]->(piatto:Piatto)
WHERE rel.distanza <= 200
RETURN DISTINCT piatto.nome


The question is:
{question}"""


answer_questions(llm=llm, graph=graph, standard_template=CYPHER_GENERATION_TEMPLATE_STANDARD, fuzzy_template=CYPHER_GENERATION_TEMPLATE_FUZZY, questions_file_path=questions_file_path, answers_txt_path=answers_txt_path)