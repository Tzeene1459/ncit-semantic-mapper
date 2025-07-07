from graphdatascience import GraphDataScience
import os

host = os.getenv("NEO4J_URI") 
user = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

gds = GraphDataScience(host, auth= (user, password))

print(gds.version())

query = """
MATCH (pv:PV {term:"Acute Myeloblastic Leukemia with Minimal Differentiation"})
WITH pv
MATCH (pv)-[:HAS_CONCEPT]->(c:NCIT)-[:HAS_SYNONYM]->(syn:SYN)
RETURN syn.term """
params = ""
result = gds.run_cypher(query)
print(result)