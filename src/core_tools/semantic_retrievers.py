import os
import openai
from neo4j import GraphDatabase

class SemanticSearcher:
    def __init__(self):
        # Initialize OpenAI client
        self.openai_client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Initialize Neo4j driver
        self.driver = GraphDatabase.driver(
            os.getenv('NEO4J_URI'),
            auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
        )
    
    def get_embedding(self, text: str) -> list:
        """
        Convert text to embedding vector using OpenAI's text-embedding-ada-002 model
        """
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def find_cde_from_pv_term(self, pv_term: str, top_k: int = 5):
        """
        Search for CDEs by finding similar PV terms using semantic search
        
        Args:
            pv_term (str): The permissible value term to search for
            top_k (int): Number of top results to return
            
        Returns:
            List of dictionaries containing PV and CDE information
        """
        # Get embedding for the input term
        embedding = self.get_embedding(pv_term)
        if not embedding:
            return []
        
        # Cypher query combining vector search with graph traversal
        query = """
        CALL db.index.vector.queryNodes('pvIndex', $top_k, $embedding) 
        YIELD node, score
        WHERE node:PV
        WITH node, score
        MATCH (node)<-[:HAS_PV]-(vdm:VDM)<-[:HAS_VDM]-(cde:CDE)
        RETURN node.definition as text, score,
               {score: score, 
                pv_code: node.code, 
                pv_term: node.term,
                cde: cde.code, 
                cde_term: cde.term, 
                cde_defn: cde.definition} as metadata
        ORDER BY score DESC
        """
        
        with self.driver.session() as session:
            try:
                result = session.run(query, top_k=top_k, embedding=embedding)
                return [record.data() for record in result]
            except Exception as e:
                print(f"Error executing PV to CDE search: {e}")
                return []
    
    def find_cde_from_ncit_term(self, ncit_term: str, top_k: int = 5):
        """
        Search for CDEs by finding similar NCIT concepts using semantic search
        
        Args:
            ncit_term (str): The NCIT concept term to search for
            top_k (int): Number of top results to return
            
        Returns:
            List of dictionaries containing NCIT, PV, and CDE information
        """
        # Get embedding for the input term
        embedding = self.get_embedding(ncit_term)
        if not embedding:
            return []
        
        # Cypher query combining vector search with graph traversal
        query = """
        CALL db.index.vector.queryNodes('ncitIndex', $top_k, $embedding) 
        YIELD node, score
        WHERE node:NCIT
        WITH node, score
        MATCH (node)<-[:HAS_CONCEPT]-(pv:PV)
        OPTIONAL MATCH (pv)<-[:HAS_PV]-(vdm:VDM)<-[:HAS_VDM]-(cde:CDE)
        WITH collect(cde.code) as cdes, node, pv, score
        RETURN node.definition as text, score,
               {score: score, 
                concept_code: node.code, 
                concept_term: node.term,
                pv_code: pv.code, 
                pv_term: pv.term,
                of_cdes: cdes} as metadata
        ORDER BY score DESC
        """
        
        with self.driver.session() as session:
            try:
                result = session.run(query, top_k=top_k, embedding=embedding)
                return [record.data() for record in result]
            except Exception as e:
                print(f"Error executing NCIT to CDE search: {e}")
                return []
    
    def close(self):
        """Close the Neo4j driver connection"""
        self.driver.close()
