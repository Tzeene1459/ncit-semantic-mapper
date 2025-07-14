from ncit_semantic_mapper.llm_agent import create_fresh_agent
from ncit_semantic_mapper.llm_agent import map_raw_data_isolated


def main():
    """Main function to run the agent"""
    
    print("=== NCIT Mapping Agent ===")
    print("Initializing agent and connecting to Neo4j...")

    try:
        
        while True:
            agent, system_prompt = create_fresh_agent()
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
            
            result = map_raw_data_isolated(agent, system_prompt, raw_value)
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
