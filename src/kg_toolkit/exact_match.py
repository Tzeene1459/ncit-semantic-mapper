"""
Simple Node Matcher - Knowledge Graph
Fetches exact matches for any term, code, label or concept 
"""
from neo4j import GraphDatabase
import os

class get_node_match:
    """
    Get full node details for an exact match
    """
    def __init__(self, uri, username, password):
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
        Retrieve node details by exact matching the term name (case-insensitive).
        Args:
            term: Term name (e.g., "prostate", "PROSTATE", "Prostate" all match "Prostate")
        Returns:
            dict: Dictionary containing node details or None if not found
        """
        # trimming whitespace
        normalized_term = term.strip()
        
        query = """
        MATCH (n:NCIT)
        WHERE toLower(n.term) = toLower($term)
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
                result = session.run(query, term=normalized_term)
                record = result.single()
                
                if not record:
                    print(f"No exact match found for term '{term}'")
                    return None
                
                
                node_data = {
                    'code': record['code'],
                    'term': record['term'],  # Return the original case from database
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

    def get_fuzzy_term_matches(self, term, limit=5):
        """
        Get multiple potential matches for a term using full-text index search when an exact match isn't found.
        
        Args:
            term: Term to search for
            limit: Maximum number of results to return
            
        Returns:
            list: List of matching nodes with code, term, definition, type
        """
        print(f"Finding fuzzy matches for term: '{term}'")
        print("=" * 50)
        
        
        try:
            with self.driver.session() as session:
                
                index_name = 'ftTermIndex'
                
                # Perform fulltext search
                search_query = f"""
                CALL db.index.fulltext.queryNodes('{index_name}', $term)
                YIELD node, score
                WHERE node:NCIT
                RETURN node.code as code,
                    node.term as term,
                    node.definition as definition,
                    node.type as type,
                    score
                ORDER BY score DESC
                LIMIT $limit
                """
                
                search_result = session.run(search_query, term=term, limit=limit)
                matches = []
                
                for record in search_result:
                    match_data = {
                        'code': record['code'],
                        'term': record['term'],
                        'definition': record['definition'],
                        'type': record['type']
                    }
                    matches.append(match_data)
                
                # Results
                if matches:
                    print(f"Found {len(matches)} fuzzy matches:")
                    for i, match in enumerate(matches, 1):
                        print(f"  {i}. {match['term']} (Code: {match['code']})")
                else:
                    print("No fuzzy matches found")
                
                return matches
                
        except Exception as e:
            print(f"Fuzzy search failed: {e}")
            return []