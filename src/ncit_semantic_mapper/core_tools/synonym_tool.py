"""
Simple Synonym Finder - Cancer Knowledge Graph
Fetches all synonym data for a given term, code or permissible value
"""

import os
from ..config import Config
from neo4j import GraphDatabase


class get_synonyms:
    """
    Get all synonym data for a given input term or permissible value
    """
    def __init__(self, uri = Config.NEO4J_URI,
                 username = Config.NEO4J_USERNAME,
                 password = Config.NEO4J_PASSWORD):
        """Initialize connection to Neo4j"""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        print("Connected to database")
    
    def get_synonyms_from_pv(self, pv):
        """ Find synonyms for a permissible value using PV -> NCIT -> SYN path

        Args: 
            pv:  the permissible value to search for (eg, prostate)

        """
        query = """
        MATCH (pv:PV {term: $pv})
        WITH pv
        MATCH (pv)-[:HAS_CONCEPT]->(c:NCIT)-[:HAS_SYNONYM]->(syn:SYN)
        RETURN syn.term
        """
        
        print(f"Finding synonyms for: '{pv}'")
        print("=" * 50)
        
        try:
            with self.driver.session() as session:
                result = session.run(query, pv=pv)
                synonyms = [record["syn.term"] for record in result if record["syn.term"]]
            
            if not synonyms:
                print("No synonyms found - term might not exist as a PV or have no exact matches for synonyms")
                return []
            
            print(f"Found {len(synonyms)} synonyms:")
            print()

            for i, synonym in enumerate(synonyms, 1):
                print(f"  {i}. {synonym}")
            
            return synonyms
            
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    def get_synonyms_from_termcode(self, code):
        """
        Find synonyms from a term using NCIT code - has synonym -> SYN
        Args: 
            NCIT code for a term, like for Lung carcinoma, code is C4878
        """
        query = """
        MATCH (n:NCIT {code: $code})-[:HAS_SYNONYM]->(syn:SYN)
        RETURN syn.term as synonym_term
        """
        print("Finding synonyms for NCIT code: {code}")
        print("=" * 50)

        try:
            with self.driver.session() as session:
                result = session.run(query, code=code)
                synonyms = [record["synonym_term"] for record in result if record["synonym_term"]]
            
            if not synonyms:
                print(f"No synonyms found for NCIT code '{code}' - code might not exist or have no synonyms")
                return []
            
            print(f"Found {len(synonyms)} synonyms:")
            print()
            for i, synonym in enumerate(synonyms, 1):
                print(f"  {i}. {synonym}")
            
            return synonyms
            
        except Exception as e:
            print(f"Query failed: {e}")
            return []

        # consider semantic types to weigh matches 
        # Match (m:semantictype) return distinct m.type
        # Match (n:NCIT {term:"Lung Carcinoma"})-[:HAS_SEMANTIC_TYPE]->(m:SemanticType)
        # Return m.type 
        # returns Neoplastic process
    
        # replace term with Biogenic Amine Metabolic Process and it returns "Phenomenon or Process"

        #1. agent tool 
        #2. Keyword search for definition (2)
        #3. show semantic type in synonyms (2)
