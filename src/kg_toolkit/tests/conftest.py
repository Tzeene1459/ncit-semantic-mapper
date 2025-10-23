import pytest
import os
from langchain_neo4j import Neo4jGraph
from dotenv import load_dotenv


@pytest.fixture(scope="session")
def graph():
    load_dotenv()
    graph = Neo4jGraph(
        url=os.getenv('NEO4J_URI'),
        username=os.getenv('NEO4J_USERNAME'),
        password=os.getenv('NEO4J_PASSWORD')
    )
    return graph
