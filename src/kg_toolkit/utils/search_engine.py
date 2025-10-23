from llm_agent_4o import map_raw_data_isolated
import re
from datetime import datetime

class SearchEngine:
    """Wrapper around your existing agent for consistent interface"""
    
    def __init__(self, agent_executor=None, system_prompt=None):
        self.agent_executor = agent_executor
        self.system_prompt = system_prompt
    
    def search(self, query):
        """Perform search using your existing agent"""
        if not self.agent_executor or not self.system_prompt:
            raise ValueError("Agent not initialized")
        
        result = map_raw_data_isolated(
            self.agent_executor,
            self.system_prompt,
            query
        )
        
        return {
            'raw_response': result,
            'query': query,
            'timestamp': datetime.now(),
            'parsed_data': self.parse_response(result)
        }
    
    def parse_response(self, response):
        """Parse agent response for structured data"""
        parsed = {
            'final_answer': None,
            'ncit_code': None,
            'ncit_term': None,
            'confidence': None,
            'tool_results': {}
        }
        
        # Extract final answer
        if "Final Answer:" in response:
            parsed['final_answer'] = response.split("Final Answer:")[-1].strip()
        
        # Extract NCIT code patterns
        code_match = re.search(r'([A-Z]\d+)', response)
        if code_match:
            parsed['ncit_code'] = code_match.group(1)
        
        # Extract confidence if mentioned
        conf_match = re.search(r'Confidence[:\s]*(High|Medium|Low)', response, re.IGNORECASE)
        if conf_match:
            parsed['confidence'] = conf_match.group(1)
        
        return parsed

