# modified to query the NCIT term embeddings
import os
import sqlite3
from dotenv import load_dotenv

from pdb import set_trace
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_neo4j import Neo4jGraph, Neo4jVector
from langchain_core.documents import Document
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

tbl = 'dec'
conn = sqlite3.connect('./data/cdexml/vms.db')

def create_document(rec):
    content = rec.get('definition')
    if content:
        del rec['definition']
    return Document(page_content=content or '', metadata=rec)

llm = ChatOpenAI(
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    temperature=0,
)

embedding_provider = OpenAIEmbeddings(
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    model="text-embedding-ada-002",
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
    retrieval_query=""
)

cur = conn.cursor()

docs = []
resp = cur.execute(f"select * from {tbl}")
hdrs = [x[0] for x in resp.description]
recs = resp.fetchall()
for rec in recs:
    data = {x[0]:x[1] for x in zip(hdrs,rec)}
    docs.append(create_document(data))
    pass

chunks = [docs[slice(y,y+100)] for y in range(1, len(documents),100)]

for chunk in tqdm(chunks):
    term_vector.add_documents(chunk)


set_trace()


