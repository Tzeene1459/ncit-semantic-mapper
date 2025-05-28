from SIVector import (
    SIVector, CDEVector,
    NCITVector, PVVector
)

   
class CandidateCDEfromPVVector(PVVector):
    def __init__(self, **kwargs):
        kwargs['retrieval_query'] = """
        match (node)<-[:HAS_PV]-(vdm:VDM)<-[:HAS_VDM]-(cde:CDE)
        with node, cde, score
        return node.definition as text, score,
         {score:score, pv_code:node.code, pv_term:node.term,
          cde:cde.code, cde_term:cde.term, cde_defn:cde.definition} as
         metadata
        """
        super().__init__(**kwargs)


class CandidatePVfromNCITVector(NCITVector):
    def __init__(self, **kwargs):
        kwargs['retrieval_query'] = """
        match (node)<-[:HAS_CONCEPT]-(pv:PV)
        optional match (pv)<-[:HAS_PV]-(vdm:VDM)<-[:HAS_VDM]-(cde:CDE)
        with collect(cde.code) as cdes, node, pv
        return node.definition as text, score,
         {score:score, concept_code:node.code, pv_code:pv.code, pv_term:pv.term,
          of_cdes: cdes} as metadata
        """
        super().__init__(**kwargs)

