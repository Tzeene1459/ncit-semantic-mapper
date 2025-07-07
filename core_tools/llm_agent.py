#!/usr/bin/env python3
"""
LangChain Agent for Neo4j Knowledge Graph Querying
Uses existing synonym finder and node matcher tools
"""

import os
from typing import Optional
from langchain.agents import initialize_agent, AgentType
from langchain_community.llms import OpenAI
from langchain_core.tools import BaseTool
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from pydantic import BaseModel, Field

from synonym_tool import get_synonyms
from exact_match import get_node_match

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
    Input should be a term like 'prostate', 'lung cancer', etc.
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
    Useful for finding synonyms using an NCIT code (like C4878).
    Input should be an NCIT code starting with 'C'.
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
    Input should be an NCIT code like 'C4878'.
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
    Input should be a term like 'Lung Carcinoma'.
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

def create_agent():
    """Create and configure the LangChain agent"""
    
    Config.validate()
    
    # Initialize LLM
    llm = OpenAI(temperature=0, model_name="gpt-3.5-turbo-instruct")
    
    # adding tools
    tools = [
        SynonymFinderTool(),
        SynonymByCodeTool(),
        NodeMatcherTool(),
        TermMatcherTool()
    ]
    
    # prompt engineering for the agent
    system_prompt = """
    You are an expert medical data mapper specializing in NCIT (National Cancer Institute Thesaurus) terminology.
    Your job is to help map raw medical data values to standardized NCIT terms and codes. 
    
    Background: 
    - In the NCI Thesaurus and associated caDSR (Cancer Data Standards Registry and Repository), Common Data Elements (CDEs) are structured data definitions that ensure standardized data collection and interoperability across cancer research studies. 
    - Every CDE is structured to be represented by a term name and a code. It also contains a set of permissible values.  
    - Every component of the CDE may be linked to an overarching biological or medical Concept 

    Input:
    As an input you might receive an NCIT code (starting with C like C8460), an NCIT term name (like Acute Myeloid Leukemia) or a permissible value (M0). 
    
    When given raw data, you should:
    1. First try to find exact matches using term_matcher if you get a term name as input, or node_matcher if you get a code as input
    2. If you are not able to find an exact match, search for synonyms using synonym_finder if you receive a permissible value as input, or synonym_by_code if you get a term code as input.
    3. If there is still no match found in the database, just say that this input does not have a synonym or an exact match in the database. 
    4. Use node_matcher to get detailed information about any codes you find
    5. Provide the best NCIT mapping recommendation with confidence level and justifications. Also state the tools you used to solve the problem. 
    
    Always provide:
    - The recommended NCIT code and term
    - Confidence level (High/Medium/Low)
    - Reasoning for your recommendation (along with the sequence of steps you took, and the tools you used)
    - Alternative options if available

    You MUST always do:
    - Only use the database as the source of truth for your answers 
    - Only use the tools I provide to you for solving a problem 

    You MUST not do:
    - Make answers up when the database doesn't give you a clear answer 
    - Try an alternative approach instead of sticking to the tools you are provided to work with
    
    Be thorough but concise in your analysis.
    """
    
    # Initialize agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )
    
    return agent, system_prompt

def map_raw_data(agent, system_prompt, raw_value):
    """Map a raw data value to NCIT terminology"""
    
    prompt = f"""
    {system_prompt}
    
    Raw medical data value to map: "{raw_value}"
    
    Please find the best NCIT mapping for this value. Provide your recommendation in this format:
    
    RECOMMENDATION:
    - NCIT Code: [code]
    - NCIT Term: [term]
    - Confidence: [High/Medium/Low]
    - Reasoning: [explanation]
    - Alternatives: [other options if any]
    """
    
    try:
        response = agent.run(prompt)
        return response
    except Exception as e:
        return f"Error processing mapping: {str(e)}"

def main():
    """Main function to run the agent"""
    
    print("=== NCIT Mapping Agent ===")
    print("Initializing agent and connecting to Neo4j...")
    
    try:
        agent, system_prompt = create_agent()
        print("Agent initialized successfully!")
        print()
        
        while True:
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
            
            result = map_raw_data(agent, system_prompt, raw_value)
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

