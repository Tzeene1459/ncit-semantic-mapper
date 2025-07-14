from typing import Optional
from langchain_core.tools import BaseTool
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from pydantic import BaseModel, Field
from .synonym_tool import get_synonyms
from .exact_match import get_node_match
from .semantic_retrievers import SemanticSearcher


# Define input schemas
class QueryInput(BaseModel):
    query: str = Field(description="search term or code")

class SynonymFinderTool(BaseTool):
    name: str = "synonym_finder"
    description: str = """
    Useful for finding synonyms of a given permissible value (PV) term.
    Use this tool when the input is a permissible value like 'prostata' or 'M0'.
    Returns a list of synonyms for these permissible values from the knowledge graph, when an exact match cannot be found.
    """
    args_schema: type[BaseModel] = QueryInput

    def _run(
        self, 
        query: str, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            synonym_finder = get_synonyms()
            synonyms = synonym_finder.get_synonyms_from_pv(query.strip())
            if synonyms:
                return f"Found {len(synonyms)} synonyms for '{query}': {', '.join(synonyms)}"
            else:
                return f"No synonyms found for '{query}'"
        except Exception as e:
            return f"Error searching for synonyms: {str(e)}"
    
    async def _arun(
        self, 
        query: str, 
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        return self._run(query, run_manager=run_manager.get_sync() if run_manager else None)

class SynonymByCodeTool(BaseTool):
    name: str = "synonym_by_code"
    description: str = """
    Useful for finding synonyms using an NCIT code (like C4890).
    Use this tool when the input is an NCIT code starting with 'C'.
    Returns synonyms associated with that specific code when an exact match for the code cannot be found in the database.
    """
    args_schema: type[BaseModel] = QueryInput
    
    def _run(
        self, 
        query: str, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            synonym_finder = get_synonyms()
            code = query.strip().upper()
            synonyms = synonym_finder.get_synonyms_from_termcode(code)
            if synonyms:
                return f"Found {len(synonyms)} synonyms for code '{code}': {', '.join(synonyms)}"
            else:
                return f"No synonyms found for code '{code}'"
        except Exception as e:
            return f"Error searching for synonyms by code: {str(e)}"
    
    async def _arun(
        self, 
        query: str, 
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        return self._run(query, run_manager=run_manager.get_sync() if run_manager else None)

class NodeMatcherTool(BaseTool):
    name: str = "node_matcher"
    description: str = """
    Useful for finding exact node information by NCIT code. This tool is used to find the exact match in the database for the given code.
    Use this tool if the input is an NCIT code like 'C2357'.
    Returns detailed information about the node including term, definition, type.
    """
    args_schema: type[BaseModel] = QueryInput
    
    def _run(
        self, 
        query: str, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            matcher = get_node_match()
            code = query.strip().upper()
            result = matcher.get_exact_match_from_code(code)
            if result:
                return f"Found node for '{code}': Term='{result['term']}', Type='{result['type']}', Definition='{result['definition'][:200]}...'"
            else:
                return f"No node found for code '{code}'"
        except Exception as e:
            return f"Error finding node: {str(e)}"
    
    async def _arun(
        self, 
        query: str, 
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        return self._run(query, run_manager=run_manager.get_sync() if run_manager else None)

class TermMatcherTool(BaseTool):
    name: str = "term_matcher"
    description: str = """
    Useful for finding exact node information by term name. This tool is used to find the exact match in the database for the given term name.
    Use this tool when the input is a term like 'Lung Carcinoma'.
    Returns detailed information including NCIT code, definition, type.
    """
    args_schema: type[BaseModel] = QueryInput
    
    def _run(
        self, 
        query: str, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            matcher = get_node_match()
            term = query.strip()
            result = matcher.get_exact_match_from_term(term)
            if result:
                return f"Found node for '{term}': Code='{result['code']}', Type='{result['type']}', Definition='{result['definition'][:200]}...'"
            else:
                return f"No exact match found for term '{term}'"
        except Exception as e:
            return f"Error finding term: {str(e)}"
    
    async def _arun(
        self, 
        query: str, 
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        return self._run(query, run_manager=run_manager.get_sync() if run_manager else None)

class SemanticPVSearchTool(BaseTool):
    name: str = "semantic_pv_search"
    description: str = """
    Useful for finding semantically similar CDEs through permissible value matching.
    Use this tool when exact matches and synonyms fail, and you need to find related medical concepts.
    This performs vector-based semantic search on PV terms to find similar permissible values and their associated CDEs.
    Best for general medical terms like 'blood pressure', 'cancer staging', 'diabetes symptoms'.
    Returns similarity scores and related CDE information.
    """
    args_schema: type[BaseModel] = QueryInput
    
    def _run(
        self, 
        query: str, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            searcher = SemanticSearcher()
            results = searcher.find_cde_from_pv_term(query.strip(), top_k=3)
            searcher.close()
            
            if not results:
                return f"No semantic matches found for PV term '{query}'"
            
            response_parts = [f"Found {len(results)} semantic matches for '{query}' through PV search:"]
            
            for i, result in enumerate(results, 1):
                metadata = result['metadata']
                score = metadata['score']
                pv_term = metadata['pv_term']
                pv_code = metadata['pv_code']
                cde_term = metadata['cde_term']
                cde_code = metadata['cde']
                
                response_parts.append(
                    f"\n{i}. PV: '{pv_term}' (Code: {pv_code}) -> CDE: '{cde_term}' (Code: {cde_code}) [Similarity: {score:.4f}]"
                )
            
            return "".join(response_parts)
            
        except Exception as e:
            return f"Error in semantic PV search: {str(e)}"
    
    async def _arun(
        self, 
        query: str, 
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        return self._run(query, run_manager=run_manager.get_sync() if run_manager else None)

class SemanticNCITSearchTool(BaseTool):
    name: str = "semantic_ncit_search"
    description: str = """
    Useful for finding semantically similar CDEs through NCIT term concept matching.
    Use this tool when exact matches and synonyms fail, and you need to find related standardized medical concepts.
    This performs vector-based semantic search on NCIT terms to find similar concepts and their associated PVs and CDEs.
    Best for standardized medical terminology like 'hypertension', 'neoplasm', 'anatomical structures'.
    Returns similarity scores and comprehensive relationship information.
    """
    args_schema: type[BaseModel] = QueryInput
    
    def _run(
        self, 
        query: str, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            searcher = SemanticSearcher()
            results = searcher.find_cde_from_ncit_term(query.strip(), top_k=3)
            searcher.close()
            
            if not results:
                return f"No semantic matches found for NCIT term '{query}'"
            
            response_parts = [f"Found {len(results)} semantic matches for '{query}' through NCIT search:"]
            
            for i, result in enumerate(results, 1):
                metadata = result['metadata']
                score = metadata['score']
                concept_term = metadata['concept_term']
                concept_code = metadata['concept_code']
                pv_term = metadata['pv_term']
                pv_code = metadata['pv_code']
                cde_codes = metadata['of_cdes']
                
                cde_summary = f"{len(cde_codes)} CDEs" if cde_codes else "No CDEs"
                
                response_parts.append(
                    f"\n{i}. NCIT: '{concept_term}' (Code: {concept_code}) -> PV: '{pv_term}' (Code: {pv_code}) -> {cde_summary} [Similarity: {score:.4f}]"
                )
            
            return "".join(response_parts)
            
        except Exception as e:
            return f"Error in semantic NCIT search: {str(e)}"
    
    async def _arun(
        self, 
        query: str, 
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        return self._run(query, run_manager=run_manager.get_sync() if run_manager else None)


