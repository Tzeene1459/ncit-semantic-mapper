import os
from dotenv import load_dotenv
from exactNeo4jRetriever import ExactNeo4jRetriever, FullTextNeo4jRetriever
from langchain_neo4j import Neo4jGraph
from pdb import set_trace
load_dotenv()

graph = Neo4jGraph(
    url=os.getenv('NEO4J_URI'),
    username=os.getenv('NEO4J_USERNAME'),
    password=os.getenv('NEO4J_PASSWORD')
)

term_matcher = ExactNeo4jRetriever(
    graph=graph,
    node_label='Term',
    text_node_property='definition',
    retrieval_query='where node.term = $input',
    metadata_properties=['term', 'code', 'origin', 'type'],
    k = 10
    )

term_ft_matcher = FullTextNeo4jRetriever(
    graph=graph,
    index_name='ftTermIndex',
    node_label='Term',
    text_node_property='definition',
    metadata_properties=['term', 'code', 'origin', 'type'],
    k = 10
)


term_matcher.invoke('VHL disease')
result = term_ft_matcher.invoke('lung*')
pass

q = """
match (t:Term) where toLower(t.term) = toLower($input)
optional match (d:Definition)<-[:HAS_DEFINITION]-(t)
with coalesce(t.definition, d.definition) as text, t.type as type, t.term as term, t.code as code, t.origin as origin
return text, {term: term, type: type, code: code, origin: origin} as metadata
"""
qq = """
match (t:Term)-[:HAS_SYNONYM]->(s:Synonym) where toLower(s.synonym) = toLower($input)
match (t:Term) where toLower(t.term) = toLower($input)
optional match (d:Definition)<-[:HAS_DEFINITION]-(t)
with coalesce(t.definition, d.definition) as text, t.type as type, t.term as term, t.code as code, t.origin as origin
return text, {term: term, type: type, code: code, origin: origin} as metadata
"""
