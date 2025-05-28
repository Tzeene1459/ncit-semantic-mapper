"""
Plain retrievers (not Vector-based) for Neo4j.
Includes full text search index retrievers.
"""

import json
from typing import List
from dataclasses import KW_ONLY
from langchain.schema import BaseRetriever, Document
from langchain_neo4j import Neo4jGraph
from neo4j_graphrag.indexes import retrieve_fulltext_index_info


class Neo4jRetriever(BaseRetriever):
    """
    A custom retriever that returns Neo4j Nodes as Langchain Documents.
    Document.page_content is returned as a JSON string of text_node_properties.
    Use retrieval_query to add constraints on 'node'.

    node_label: node type to retrieve (with no retrieval_query, returns
                all these nodes)
    text_node_properties: return the values of these properties in the "page_content"
                          of the Document
    metatdata_properties: list of property names on a node: return names and values in the
                          'metadata' dict of the Document
    retrieval_query: Cypher fragment that performs additional search on the built-in query
                     'MATCH (node: <node_label>) WITH node'
    params: dict of cypher parameters for retrieval_query
    k: integer, limit number of nodes returned to k
    """
    _: KW_ONLY
    graph: Neo4jGraph
    node_label: str
    text_node_properties: List[str]
    metadata_properties: List[str] = []
    k: int = 4
    retrieval_query: str = ""
    params: dict = {}

    match_clause: str = ""
    limit_clause: str  = ""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.match_clause = f"""MATCH (node:{self.node_label}) WITH node"""
        self.limit_clause = f"""LIMIT {self.k}""" if self.k and self.k > 0 else ""
        
    def _get_relevant_documents(self, input: str) -> list[Document]:
        """
        Run the retrieval query and return results as LangChain Documents.
        
        Returns:
            list[Document]: A list of LangChain Document objects.
        """
        params = self.params
        params['input'] = input

        if self.retrieval_query:
            return_clause = self.retrieval_query
        else:
            return_clause = f"""
            WITH node {{ {','.join(['.'+x for x in self.text_node_properties])} }}
            AS text,
            node {{ {','.join(['.'+x for x in self.metadata_properties])} }}
            AS metadata
            RETURN text, metadata
            """
        query = f"""{self.match_clause} {return_clause} {self.limit_clause}"""
        results = self.graph.query(query, params)
        documents = [
            Document(page_content=json.dumps(result["text"]) if result["text"]
                     else "<empty>", metadata=result["metadata"])
            for result in results
        ]
        return documents

    async def _aget_relevant_documents(self, input: str) -> list[Document]:
        """
        Asynchronous version of _get_relevant_documents.
        
        Args:
            query (str): The input query
        
        Returns:
            list[Document]: A list of LangChain Document objects.
        """
        return self._get_relevant_documents(input)


class FullTextNeo4jRetriever(Neo4jRetriever):
    """
    Neo4j Retriever that uses a named fulltext index.
    Input is a Lucene search string (when invoke()'ed)

    index_name: name of full text index present in database
    node_label: label of node that is indexed
    text_node_properties: list of names of properties indexed
    graph: Neo4jGraph
    k: number of matches to return
    retrieval_query (optional): Cypher query
    
    """
    _: KW_ONLY
    index_name: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not retrieve_fulltext_index_info(self.graph._driver, self.index_name,
                                            self.text_node_properties):
            self.logger.exception(
                RuntimeError(f"""Database has no fulltext index named '{self.index_name}'""")
            )
        self.match_clause = f"""
        CALL db.index.fulltext.queryNodes('{kwargs['index_name']}',$input)
        YIELD node, score
        """
        if not self.retrieval_query:
            attrs = ['.'+x for x in self.metadata_properties]
            attrs.append("score:score")
            self.retrieval_query = f"""
            WITH node {{ {','.join(['.'+x for x in self.text_node_properties])} }}
            AS text,
            node {{ {','.join(attrs)} }}
            AS metadata
            RETURN text, metadata
            """
        self.limit_clause  = f"""
        ORDER BY metadata.score DESC
        LIMIT {self.k}""" if self.k and self.k > 0 else ""
