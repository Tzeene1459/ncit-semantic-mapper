import pytest # noqa-F401
import json
from si_tamer.Neo4jRetriever import Neo4jRetriever, FullTextNeo4jRetriever


def test_neoretrievers(graph):
    graph = graph
    retr = Neo4jRetriever(
        graph=graph,
        node_label="CDE",
        k=5,
        text_node_properties=['term', 'code'],
        metadata_properties=['type']
    )
    resp = retr.invoke('dummy')
    assert len(resp) == 5
    assert json.loads(resp[0].page_content)
    assert resp[0].metadata['type'] == 'CDE'
    
    retr = FullTextNeo4jRetriever(
        graph=graph,
        index_name="ftTermIndex",
        node_label="Term",
        k=3,
        text_node_properties=['term', 'code'],
        metadata_properties=['code','type']
    )
    resp = retr.invoke("cachexia")
    assert len(resp) == 3
    assert resp[0].metadata['score']
    assert resp[1].metadata['type'] in ('VDM','CDE','NCIT','PV')
    
def test_siretrievers
