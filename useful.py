OPENAI_API_KEY = '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'

from neo4j import GraphDatabase
import json

import os

os.environ["NEO4J_URI"] = 'neo4j://localhost:7687'
os.environ["NEO4J_USERNAME"] = 'neo4j'
os.environ["NEO4J_PASSWORD"] = '98765432'
uri = os.environ["NEO4J_URI"]

driver = GraphDatabase.driver(uri, auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]))

def get_graph_schema(driver):
    with driver.session() as session:
        result = session.run("""CALL db.schema.visualization()
               """)
        return result.single()
    
schema = get_graph_schema(driver)
print(schema)

######################################################################################

from langchain_neo4j import GraphCypherQAChain
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    api_key=OPENAI_API_KEY
)

graph = Neo4jGraph(
    url=uri, 
    username=os.environ["NEO4J_USERNAME"], 
    password=os.environ["NEO4J_PASSWORD"],
    enhanced_schema=True
)

print(graph.schema)

from langchain_core.prompts.prompt import PromptTemplate

CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
The graph database contains restaurants and dishes from an alien galaxy.
Each restaurant is located in a planet.
Each planet has a given distance from the other ones expressed in light years. 
The distance between planets is specified as a property of the 'HA_DISTANZA_ANNI_LUCE' relationship. This property is named 'distanza'.


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

CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"], template=CYPHER_GENERATION_TEMPLATE
)

chain = GraphCypherQAChain.from_llm(
    llm, 
    graph=graph, 
    verbose=True, 
    allow_dangerous_requests=True, 
    cypher_prompt=CYPHER_GENERATION_PROMPT,
    return_direct=True,
    top_k=50,
    validate_cypher=True
)

answer = chain.invoke("Quali piatti dovrei scegliere per un banchetto a tema magico che includa le celebri Cioccorane?")

type(answer)

answer["result"]

