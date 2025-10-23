#!/usr/bin/env python3
"""
LangChain Agent for Neo4j Knowledge Graph Querying
Uses existing synonym finder and node matcher tools
Updated for GPT-4o compatibility
"""

import os
from typing import Optional
from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from pydantic import BaseModel, Field

from synonym_tool import get_synonyms
from exact_match import get_node_match
from semantic_retrievers import SemanticSearcher


class Config:
    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        
        if not cls.NEO4J_URI or not cls.NEO4J_USERNAME:
            raise ValueError(
                "Neo4j credentials not found. Please set these environment variables:\n"
                "NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD"
            )


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
            synonym_finder = get_synonyms(
                uri=Config.NEO4J_URI,
                username=Config.NEO4J_USERNAME, 
                password= Config.NEO4J_PASSWORD 
            )
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
            synonym_finder = get_synonyms(
                uri=Config.NEO4J_URI,
                username=Config.NEO4J_USERNAME, 
                password= Config.NEO4J_PASSWORD 
            )
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
            matcher = get_node_match(
                uri=Config.NEO4J_URI,
                username=Config.NEO4J_USERNAME, 
                password= Config.NEO4J_PASSWORD 
            )
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
            matcher = get_node_match(
                uri=Config.NEO4J_URI,
                username=Config.NEO4J_USERNAME, 
                password= Config.NEO4J_PASSWORD 
            )
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

class FuzzyTermMatcherTool(BaseTool):
    name: str = "fuzzy_term_matcher"
    description: str = """
    Useful for finding similar terms when exact matches fail. This tool helps discover what related terms exist in the database.
    Use this tool when exact term matching fails and you want to see what similar terms are available.
    Best for exploring database content or suggesting alternative terms to the user.
    Returns a list of terms that contain the search string.
    """
    args_schema: type[BaseModel] = QueryInput
    
    def _run(
        self, 
        query: str, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            matcher = get_node_match(
                uri=Config.NEO4J_URI,
                username=Config.NEO4J_USERNAME, 
                password= Config.NEO4J_PASSWORD 
            )
            term = query.strip()
            results = matcher.get_fuzzy_term_matches(term, limit=5)
            
            if results:
                response_parts = [f"Found {len(results)} similar terms for '{term}':"]
                for i, result in enumerate(results, 1):
                    response_parts.append(f"\n{i}. {result['term']} (Code: {result['code']})")
                response_parts.append(f"\nSuggestion: Try exact search with one of these terms.")
                return "".join(response_parts)
            else:
                return f"No similar terms found for '{term}'"
        except Exception as e:
            return f"Error in fuzzy term search: {str(e)}"
    
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

class SemanticCDEDefinitionTool(BaseTool):
    name: str = "semantic_cde_definition"
    description: str = """
    Useful for finding CDEs by searching definitions using semantic similarity.
    Use this tool when you have a description of what data element you're looking for.
    This performs vector-based search on CDE definitions to find conceptually similar data elements.
    Best for descriptions like 'patient age at diagnosis', 'blood pressure measurement', 'tumor size in cm'.
    Returns CDEs with similar definitions and similarity scores.
    """
    args_schema: type[BaseModel] = QueryInput
    
    def _run(
        self, 
        query: str, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            searcher = SemanticSearcher()
            results = searcher.find_cde_by_definition_similarity(query.strip(), top_k=3)
            searcher.close()
            
            if not results:
                return f"No CDE definition matches found for '{query}'"
            
            response_parts = [f"Found {len(results)} CDE definition matches for '{query}':"]
            
            for i, result in enumerate(results, 1):
                metadata = result['metadata']
                score = metadata['score']
                cde_term = metadata['cde_term']
                cde_code = metadata['cde_code']
                cde_definition = metadata['cde_definition']
                
                # Truncate long definitions
                truncated_def = cde_definition[:150] + "..." if len(cde_definition) > 150 else cde_definition
                
                response_parts.append(
                    f"\n{i}. CDE: '{cde_term}' (Code: {cde_code}) [Similarity: {score:.4f}]"
                    f"\n   Definition: {truncated_def}"
                )
            
            return "".join(response_parts)
            
        except Exception as e:
            return f"Error in semantic CDE definition search: {str(e)}"
    
    async def _arun(
        self, 
        query: str, 
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        return self._run(query, run_manager=run_manager.get_sync() if run_manager else None)

class SemanticNCITDefinitionTool(BaseTool):
    name: str = "semantic_ncit_definition"
    description: str = """
    Useful for finding NCIT concepts by searching definitions using semantic similarity.
    Use this tool when you have a description of a medical concept you're looking for.
    This performs vector-based search on NCIT definitions to find conceptually similar medical terms.
    Best for descriptions like 'cancer of the blood', 'high blood pressure condition', 'organ that pumps blood'.
    Returns NCIT concepts with similar definitions and similarity scores.
    """
    args_schema: type[BaseModel] = QueryInput
    
    def _run(
        self, 
        query: str, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            searcher = SemanticSearcher()
            results = searcher.find_ncit_by_definition_similarity(query.strip(), top_k=3)
            searcher.close()
            
            if not results:
                return f"No NCIT definition matches found for '{query}'"
            
            response_parts = [f"Found {len(results)} NCIT definition matches for '{query}':"]
            
            for i, result in enumerate(results, 1):
                metadata = result['metadata']
                score = metadata['score']
                concept_term = metadata['concept_term']
                concept_code = metadata['concept_code']
                concept_definition = metadata['concept_definition']
                
                # Truncate long definitions
                truncated_def = concept_definition[:150] + "..." if len(concept_definition) > 150 else concept_definition
                
                response_parts.append(
                    f"\n{i}. NCIT: '{concept_term}' (Code: {concept_code}) [Similarity: {score:.4f}]"
                    f"\n   Definition: {truncated_def}"
                )
            
            return "".join(response_parts)
            
        except Exception as e:
            return f"Error in semantic NCIT definition search: {str(e)}"
    
    async def _arun(
        self, 
        query: str, 
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        return self._run(query, run_manager=run_manager.get_sync() if run_manager else None)


def create_fresh_agent():
    """Create and configure the LangChain agent"""
    
    Config.validate()
    
    # Initialize LLM with GPT-4o
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        openai_api_key=Config.OPENAI_API_KEY
    )
    
     # adding tools in priority order
    tools = [
        # Exact match tools (highest priority)
        TermMatcherTool(),
        NodeMatcherTool(),
        
        # Fuzzy match tool (for exploration)
        FuzzyTermMatcherTool(),
        
        # Synonym tools (medium priority) 
        SynonymFinderTool(),
        SynonymByCodeTool(),
        
        # Semantic search tools (fallback)
        SemanticPVSearchTool(),
        SemanticNCITSearchTool(),
        
        # Definition-based semantic search (specialized)
        SemanticCDEDefinitionTool(),
        SemanticNCITDefinitionTool()
    ]
    
    # Create the prompt template for ReAct agent
    prompt_template = """
    You are an expert medical data mapper specializing in NCIT (National Cancer Institute Thesaurus) terminology.
    Your job is to help map raw medical data values to standardized NCIT terms and codes. 
    
    IMPORTANT: Focus ONLY on the current input. Do not reference previous queries or results.

    1. EXACT MATCH TOOLS (use first):
       - term_matcher: Find exact matches for term names
       - node_matcher: Find exact matches for NCIT codes
    
    2. EXPLORATION TOOL (use when exact match fails):
       - fuzzy_term_matcher: Find similar terms to discover available options
    
    3. SYNONYM TOOLS (use if exact match fails):
       - synonym_finder: Find synonyms for permissible values 
       - synonym_by_code: Find synonyms using NCIT codes
    
    4. SEMANTIC SEARCH TOOLS (use as fallback):
       - semantic_pv_search: Find semantically similar terms through PV matching
       - semantic_ncit_search: Find semantically similar terms through NCIT concept matching
    
    5. DEFINITION-BASED SEMANTIC SEARCH (use for descriptions):
       - semantic_cde_definition: Find CDEs by description similarity
       - semantic_ncit_definition: Find NCIT concepts by description similarity
    
    Examples of proper tool usage:
    - For a term: term_matcher -> fuzzy_term_matcher -> semantic_ncit_search
    - For a code that starts with C: node_matcher -> synonym_by_code
    - For a phrase like input that contains over 4 words -> semantic_cde_definition -> semantic_ncit_definition  
    - For a set of strings or phrase: term_matcher -> semantic_pv_search -> semantic_ncit_search -> semantic_cde_definition -> semantic_ncit_definition

    Always provide:
    - The recommended NCIT code and term (if found)
    - Confidence level (High/Medium/Low)
    - Reasoning for your recommendation (along with the sequence of steps you took, and the tools you used)
    - Alternative options if available

    You MUST:
    - Only use the database as your source of truth
    - Only use the provided tools
    - Focus ONLY on the current input
    - Start again if you end up finding nothing
    
    You MUST NOT:
    - Make up answers when the database gives no results
    - Reference previous queries or results
    - Use action names that aren't actual tools
    
    Be thorough but concise in your analysis.

    You have access to the following tools:

    {tools}

    Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    Question: {input}
    Thought: {agent_scratchpad}
    """
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["input", "agent_scratchpad"],
        partial_variables={"tools": "\n".join([f"{tool.name}: {tool.description}" for tool in tools]),
                          "tool_names": ", ".join([tool.name for tool in tools])}
    )
    
    # Create the ReAct agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10
    )
    
    return agent_executor, prompt_template

def map_raw_data_isolated(agent_executor, system_prompt, raw_value):
    """Map a raw data value to NCIT terminology"""
    
    try:
        response = agent_executor.invoke({"input": f"Raw medical data value to map: \"{raw_value}\""})
        return response["output"]
    except Exception as e:
        return f"Error processing mapping: {str(e)}"

def create_agent():
    """Legacy function for backward compatibility - DEPRECATED"""
    return create_fresh_agent()

def map_raw_data(agent, system_prompt, raw_value):
    """Legacy function for backward compatibility - DEPRECATED"""
    return map_raw_data_isolated(agent, system_prompt, raw_value)

def main():
    """Main function to run the agent"""
    
    print("=== NCIT Mapping Agent ===")
    print("Initializing agent and connecting to Neo4j...")
    
    try:
        
        while True:
            agent_executor, system_prompt = create_fresh_agent()
            print("Agent initialized successfully!")
            print()

            print("-" * 60)
            raw_value = input("Enter raw medical data to map (or 'quit' to exit): ").strip()
            
            if raw_value.lower() in ['quit', 'exit', 'q']:
                print("Ok")
                break
            
            if not raw_value:
                print("Please enter a valid value.")
                continue
            
            print()
            print(f"Mapping: '{raw_value}'")
            print("=" * 50)
            
            result = map_raw_data_isolated(agent_executor, system_prompt, raw_value)
            print(result)
            print()
            
            continue_choice = input("Map another value? (y/n): ").strip().lower()
            if continue_choice in ['n', 'no']:
                print("Ok")
                break
                
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have set your OpenAI API key and Neo4j is running.")

if __name__ == "__main__":
    main()