# add CDEs to vector store
import os
import sqlite3
from dotenv import load_dotenv
from pdb import set_trace
from tqdm import trange
load_dotenv()

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_neo4j import Neo4jGraph, Neo4jVector
from httpx import Client

conn = sqlite3.connect('vms.db')
cur = conn.cursor()

client = Client(verify=False)
chunk_size = 100
tbl = 'cde'

embedding_provider = OpenAIEmbeddings(
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    model="text-embedding-ada-002",
    http_client=client,
    )

graph = Neo4jGraph(
    url=os.getenv('NEO4J_URI'),
    username=os.getenv('NEO4J_USERNAME'),
    password=os.getenv('NEO4J_PASSWORD')
)

term_vector = Neo4jVector.from_existing_index(
    embedding_provider,
    graph=graph,
    node_label="Term",
    index_name="termIndex",
    embedding_node_property="openai_embedding",
    text_node_property="definition",
)

cur.execute(f'select count(*) as ct from {tbl}')
row = cur.fetchone()
ct = row[0]
cur.execute(f'select * from {tbl}')
nchunks = int(ct / chunk_size) + (0 if ct % chunk_size == 0 else 1)
hdrs = [x[0] for x in cur.description]

for i in trange(nchunks):
    documents = []
    rows = cur.fetchmany(chunk_size)
    for row in rows:
        data = {}
        data.update(zip(hdrs, row))
        defn =  data['definition']
        del data['definition']
        documents.append(Document(page_content=defn,
                              metadata=data))
    term_vector.add_documents(documents)

          
