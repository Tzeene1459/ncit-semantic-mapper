# =============================================================================
# utils/response_parser.py
import re

def parse_agent_response_detailed(response):
    """Parse agent response for detailed analysis in live mode"""
    parsed = {
        'final_answer': None,
        'thoughts': [],
        'tool_results': {},
        'actions': [],
        'observations': []
    }
    
    lines = response.split('\n')
    current_section = None
    current_tool = None
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('Thought:'):
            parsed['thoughts'].append(line.replace('Thought:', '').strip())
        
        elif line.startswith('Action:'):
            action = line.replace('Action:', '').strip()
            parsed['actions'].append(action)
            current_tool = action
            
        elif line.startswith('Observation:'):
            obs = line.replace('Observation:', '').strip()
            parsed['observations'].append(obs)
            
            # Group observations by tool
            if current_tool:
                if current_tool not in parsed['tool_results']:
                    parsed['tool_results'][current_tool] = []
                parsed['tool_results'][current_tool].append(obs)
        
        elif line.startswith('Final Answer:'):
            parsed['final_answer'] = response.split('Final Answer:')[-1].strip()
    
    return parsed

def extract_tool_mentions(response):
    """Extract mentions of specific tools from response"""
    tools = {
        'exact_match': [],
        'fuzzy_match': [],
        'semantic_search': [],
        'synonym_finder': []
    }
    
    # Look for tool-specific patterns in the response
    if 'action: term_matcher' in response.lower() or  'action: node_matcher' in response.lower():
        tools['exact_match'].append("Tool was used")
    
    if 'action: semantic_pv_search' in response.lower() or 'action: semantic_ncit_search' in response.lower() or 'action: semantic_cde_definition' in response.lower() or 'action: semantic_ncit_definition':
        tools['semantic_search'].append("Tool was used")
    
    if 'action: synonym_finder' in response.lower() or 'action: synonym_by_code' in response.lower():
        tools['synonym_finder'].append("Tool was used")
    
    if 'action: fuzzy_term_matcher' in response.lower():
        tools['fuzzy_match'].append("Tool was used")
    
    return tools