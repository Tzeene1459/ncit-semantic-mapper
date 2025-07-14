"""
Simple Node Matcher - Knowledge Graph
Fetches exact matches for any term, code, label or concept 
"""
from neo4j import GraphDatabase
import os
from ..config import Config

class get_node_match:
    """
    Get full node details for an exact match
    """
    def __init__(self, uri = Config.NEO4J_URI,
                 username = Config.NEO4J_USERNAME,
                 password = Config.NEO4J_PASSWORD):
        """Initialize connection to Neo4j"""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        print("Connected to database")

    def get_exact_match_from_code(self, code):
        """
        Retrieve node details by exact matching the code. 
        Return term, label, concept, embedding and definition.
        Args:
            code: NCIT code for a term (eg C40625)
        Returns:
            dict: Dictionary containing node details or None if not found
        """
        query = """
        MATCH (n:NCIT {code: $code})
        RETURN n.term as term, 
               n.definition as definition, 
               n.type as type, 
               n.openai_embedding as embedding
        """
        
        print(f"Finding exact match for code: {code}")
        print("=" * 50)
        
        try:
            with self.driver.session() as session:
                result = session.run(query, code=code)
                record = result.single()
                
                if not record:
                    print(f"No exact match found for code '{code}'")
                    return None
                
                node_data = {
                    'code': code,
                    'term': record['term'],
                    'definition': record['definition'],
                    'type': record['type'],
                    'embedding': record['embedding']
                }
                
                print("Exact match found!")
                print(f"Code: {node_data['code']}")
                print(f"Term: {node_data['term']}")
                print(f"Type: {node_data['type']}")
                print(f"Definition: {node_data['definition'][:100]}..." if node_data['definition'] and len(node_data['definition']) > 100 else f"Definition: {node_data['definition']}")
                print(f"Has Embedding: {'Yes' if node_data['embedding'] else 'No'}")
                
                return node_data
                
        except Exception as e:
            print(f"Query failed: {e}")
            return None
    
    def get_exact_match_from_term(self, term):
        """
        Retrieve node details by exact matching the term name.
        Args:
            term: Exact term name (e.g., "Lung Carcinoma")
        Returns:
            dict: Dictionary containing node details or None if not found
        """
        query = """
        MATCH (n:NCIT {term: $term})
        RETURN n.code as code,
               n.term as term, 
               n.definition as definition, 
               n.type as type, 
               n.openai_embedding as embedding
        """
        
        print(f"Finding exact match for term: '{term}'")
        print("=" * 50)
        
        try:
            with self.driver.session() as session:
                result = session.run(query, term=term)
                record = result.single()
                
                if not record:
                    print(f"No exact match found for term '{term}'")
                    return None
                
                # Extract the data
                node_data = {
                    'code': record['code'],
                    'term': record['term'],
                    'definition': record['definition'],
                    'type': record['type'],
                    'embedding': record['embedding']
                }
                
                print("Exact match found!")
                print(f"Code: {node_data['code']}")
                print(f"Term: {node_data['term']}")
                print(f"Type: {node_data['type']}")
                print(f"Definition: {node_data['definition'][:100]}..." if node_data['definition'] and len(node_data['definition']) > 100 else f"Definition: {node_data['definition']}")
                print(f"Has Embedding: {'Yes' if node_data['embedding'] else 'No'}")
                
                return node_data
                
        except Exception as e:
            print(f"Query failed: {e}")
            return None
