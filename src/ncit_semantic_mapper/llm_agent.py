#!/usr/bin/env python3
"""
LangChain Agent for Neo4j Knowledge Graph Querying
Uses existing synonym finder and node matcher tools
"""
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import OpenAI
from .config import Config
from .core_tools.tools import (
    SemanticPVSearchTool,
    SemanticNCITSearchTool,
    SynonymFinderTool,
    SynonymByCodeTool,
    NodeMatcherTool,
    TermMatcherTool,
)


def create_fresh_agent():
    """Create and configure the LangChain agent"""
    
    Config.validate()
    
    # Initialize LLM
    llm = OpenAI(temperature=0, model_name="gpt-3.5-turbo-instruct")
    
    # adding tools
    tools = [
        # Exact match tools (highest priority)
        TermMatcherTool(),
        NodeMatcherTool(),
        
        # Synonym tools (medium priority) 
        SynonymFinderTool(),
        SynonymByCodeTool(),
        
        # Semantic search tools (fallback)
        SemanticPVSearchTool(),
        SemanticNCITSearchTool()
    ]
    
    # creating fresh memory instance 
    fresh_memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    # prompt engineering for the agent
    system_prompt = """
    You are an expert medical data mapper specializing in NCIT (National Cancer Institute Thesaurus) terminology.
    Your job is to help map raw medical data values to standardized NCIT terms and codes. 
    
    IMPORTANT: Focus ONLY on the current input. Do not reference previous queries or results.

    Available Tools (in order of preference):
    1. EXACT MATCH TOOLS (use first):
       - term_matcher: Find exact matches for term names
       - node_matcher: Find exact matches for NCIT codes
    
    2. SYNONYM TOOLS (use if exact match fails):
       - synonym_finder: Find synonyms for permissible values 
       - synonym_by_code: Find synonyms using NCIT codes
    
    3. SEMANTIC SEARCH TOOLS (use as fallback):
       - semantic_pv_search: Find semantically similar terms through PV matching
       - semantic_ncit_search: Find semantically similar terms through NCIT concept matching
    
    Examples of proper tool usage:
    - For a term: term_matcher -> synonym_finder -> semantic_ncit_search
    - For a code that starts with C: node_matcher -> synonym_by_code  
    - For a set of strings or phrase: term_matcher -> semantic_pv_search -> semantic_ncit_search

    Always provide:
    - The recommended NCIT code and term (if found)
    - Confidence level (High/Medium/Low)
    - Reasoning for your recommendation (along with the sequence of steps you took, and the tools you used)
    - Alternative options if available

    You MUST:
    - Only use the database as your source of truth
    - Only use the provided tools
    - Focus ONLY on the current input
    
    You MUST NOT:
    - Make up answers when the database gives no results
    - Reference previous queries or results
    - Use action names that aren't actual tools
    
    Be thorough but concise in your analysis.
    """
    
    # Initialize agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=7,
        memory = fresh_memory
    )
    
    return agent, system_prompt

def map_raw_data_isolated(agent, system_prompt, raw_value):
    """Map a raw data value to NCIT terminology"""

    prompt = f""" 

    {system_prompt}
    
    Raw medical data value to map: "{raw_value}"
    
    """
    
    try:
        response = agent.run(prompt)
        return response
    except Exception as e:
        return f"Error processing mapping: {str(e)}"

def create_agent():
    """Legacy function for backward compatibility - DEPRECATED"""
    return create_fresh_agent()

def map_raw_data(agent, system_prompt, raw_value):
    """Legacy function for backward compatibility - DEPRECATED"""
    return map_raw_data_isolated(raw_value)

