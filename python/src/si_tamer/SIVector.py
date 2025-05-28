import os
from enum import Enum
from dotenv import load_dotenv
from pdb import set_trace

from langchain_openai import OpenAIEmbeddings
from langchain_neo4j import Neo4jGraph, Neo4jVector

load_dotenv()

embedding_provider = OpenAIEmbeddings(
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    model="text-embedding-ada-002",
    )
graph = Neo4jGraph(
    url=os.getenv('NEO4J_URI'),
    username=os.getenv('NEO4J_USERNAME'),
    password=os.getenv('NEO4J_PASSWORD')
)


class SINodeLabels(str, Enum):
    CDE = "CDE"
    DEC = "DEC"
    NCIT = "NCIT"
    OC = "OC"
    PR = "PR"
    PV = "PV"
    TERM = "Term"
    VDM = "VDM"


class SIIndexes(str, Enum):
    termIndex = "termIndex"
    cdeIndex = "cdeIndex"
    vdmIndex = "vdmIndex"
    pvIndex = "pvIndex"
    ncitIndex = "ncitIndex"


class SIVector(Neo4jVector):
    def __init__(
            self,
            *,
            index_name: SIIndexes = SIIndexes.termIndex,
            keyword_index_name: str = None,
            node_label: SINodeLabels = SINodeLabels.TERM,
            retrieval_query: str = """
            return node.definition as text, score,
            {score: score, type: node.type, code: node.code, term: node.term}
            as metadata
            """,
            **kwargs
            ):
        super().__init__(
            embedding_provider,
            index_name=index_name,
            keyword_index_name=keyword_index_name,
            node_label=node_label,
            retrieval_query=retrieval_query,
            graph=graph,
            text_node_property="definition",
            **kwargs
            )


class CDEVector(SIVector):
    def __init__(
            self,
            retrieval_query: str = None,
            **kwargs
            ):
        kwargs.update({
            "node_label": SINodeLabels.CDE,
            "index_name": SIIndexes.cdeIndex
        })
        if retrieval_query:
            kwargs['retrieval_query'] = retrieval_query
        super().__init__(**kwargs)


class NCITVector(SIVector):
    def __init__(
            self,
            retrieval_query: str = None,
            **kwargs
            ):
        kwargs.update({
            "node_label": SINodeLabels.NCIT,
            "index_name": SIIndexes.ncitIndex
        })
        if retrieval_query:
            kwargs['retrieval_query'] = retrieval_query
        super().__init__(**kwargs)


class PVVector(SIVector):
    def __init__(
            self,
            retrieval_query : str = None,
            **kwargs
            ):
        kwargs.update({
            "node_label": SINodeLabels.PV,
            "index_name": SIIndexes.pvIndex
        })
        if retrieval_query:
            kwargs['retrieval_query'] = retrieval_query
        super().__init__(**kwargs)

