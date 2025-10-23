import os
import openai
from neo4j import GraphDatabase
import numpy as np

#from dotenv import load_dotenv

#load_dotenv()

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
    
    def cosine_similarity(self, vec1, vec2):
        if vec1 is None or vec2 is None:
            return 0
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

    
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
    
    def find_cde_by_definition_similarity(self, description: str, top_k: int = 5):
        """
        Specialized version of definition finder that searches only CDE definitions for similarity.
        Useful when you specifically need Common Data Elements.
        
        Args:
            description (str): Description of the data element you're looking for
            top_k (int): Number of top results to return
            
        Returns:
            List of dictionaries containing CDE information
        """
        # Get embedding for the input description
        embedding = self.get_embedding(description)
        if not embedding:
            return []
        
        query = """
        CALL db.index.vector.queryNodes('cdeIndex', $top_k, $embedding) 
        YIELD node, score
        WHERE node:CDE
        WITH node, score
        RETURN node.definition as text, score,
               {score: score, 
                cde_code: node.code, 
                cde_term: node.term,
                cde_definition: node.definition,
                node_type: 'CDE'} as metadata
        ORDER BY score DESC
        """
        
        with self.driver.session() as session:
            try:
                result = session.run(query, top_k=top_k, embedding=embedding)
                return [record.data() for record in result]
            except Exception as e:
                print(f"Error executing CDE definition similarity search: {e}")
                return []
    
    def find_ncit_by_definition_similarity(self, description: str, top_k: int = 5):
        """
        Specialized version of the definition finder that searches only NCIT concept definitions for similarity.
        Useful when you specifically need standardized medical concepts.
        
        Args:
            description (str): Description of the medical concept you're looking for
            top_k (int): Number of top results to return
            
        Returns:
            List of dictionaries containing NCIT concept information
        """
        # Get embedding for the input description
        embedding = self.get_embedding(description)
        if not embedding:
            return []
        
        query = """
        CALL db.index.vector.queryNodes('ncitIndex', $top_k, $embedding) 
        YIELD node, score
        WHERE node:NCIT
        WITH node, score
        RETURN node.definition as text, score,
               {score: score, 
                concept_code: node.code, 
                concept_term: node.term,
                concept_definition: node.definition,
                node_type: 'NCIT'} as metadata
        ORDER BY score DESC
        """
        
        with self.driver.session() as session:
            try:
                result = session.run(query, top_k=top_k, embedding=embedding)
                return [record.data() for record in result]
            except Exception as e:
                print(f"Error executing NCIT definition similarity search: {e}")
                return []


    def rerank_with_oc_context(self, candidates, input_embedding):
        """Re-rank candidate CDEs based on Object Class similarity."""
        reranked = []

        for candidate in candidates:
            cde_code = candidate["metadata"].get("cde") or candidate["metadata"].get("cde_code")
            
            # If no CDE code found, skip OC reranking
            if not cde_code:
                candidate["metadata"]["combined_score"] = candidate["metadata"]["score"]
                reranked.append(candidate)
                continue

            # Retrieve related Object Class
            with self.driver.session() as session:
                oc_result = session.run("""
                    MATCH (cde:CDE {code: $cde_code})-->(dec:DEC)-[:HAS_OC]->(oc:OC)
                    RETURN DISTINCT oc.term AS oc_term
                    LIMIT 1
                """, cde_code=cde_code).single()

            oc_term = oc_result["oc_term"] if oc_result else None
            
            if oc_term:
                oc_embedding = self.get_embedding(oc_term)
                oc_score = self.cosine_similarity(input_embedding, oc_embedding)
            else:
                oc_score = 0

            combined_score = 0.7 * candidate["metadata"]["score"] + 0.3 * oc_score
            candidate["metadata"]["oc_term"] = oc_term
            candidate["metadata"]["combined_score"] = combined_score
            reranked.append(candidate)

        return sorted(reranked, key=lambda x: x["metadata"]["combined_score"], reverse=True)

    def contextaware_cde_from_pv(self, pv_term: str, top_k: int = 5):
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
                results = [record.data() for record in session.run(query, top_k=top_k, embedding=embedding)]
                return self.rerank_with_oc_context(results, embedding)
            except Exception as e:
                print(f"Error executing PV to CDE search: {e}")
                return []

    def close(self):
        """Close the Neo4j driver connection"""
        self.driver.close()
        

