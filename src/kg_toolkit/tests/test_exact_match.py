#!/usr/bin/env python3
from exact_match import get_node_match
import sys
import os

def get_search_type():
    while True:
        print("\nChoose search method:")
        print("1. Search by NCIT Code - e.g., 'C40625'")
        print("2. Search by Term - e.g., 'Lung Carcinoma'")
        print("3. Fuzzy Search by Term - e.g., 'lung' (finds all terms containing 'lung')")
        print("4. Quit")
        
        choice = input("\nEnter your choice (1, 2, 3, or 4): ").strip()
        
        if choice == '1':
            return 'code'
        elif choice == '2':
            return 'term'
        elif choice == '3':
            return 'fuzzy'
        elif choice == '4':
            return 'quit'
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

def search_by_code(matcher):
    code = input("Enter an NCIT code to search for: ").strip()
    
    if not code:
        print("Please enter a valid NCIT code.")
        return False
    
    print()
    result = matcher.get_exact_match_from_code(code.upper())
    
    if result:
        print()
        print(f"Found exact match for NCIT code '{code.upper()}'")
    else:
        print(f"No exact match found for NCIT code '{code.upper()}'")
    
    return True

def search_by_term(matcher):
    term = input("Enter a term to search for: ").strip()
    
    if not term:
        print("Please enter a valid term.")
        return False
    
    print()
    result = matcher.get_exact_match_from_term(term)
    
    if result:
        print()
        print(f"Found exact match for term '{term}'")
    else:
        print(f"No exact match found for term '{term}'")
    
    return True

def fuzzy_search_by_term(matcher):
    term = input("Enter a term to fuzzy search for: ").strip()
    
    if not term:
        print("Please enter a valid term.")
        return False
    
    # Get number of results to show
    while True:
        try:
            limit = input("How many results would you like? (default: 5, max: 20): ").strip()
            if not limit:
                limit = 5
            else:
                limit = int(limit)
                if limit < 1 or limit > 20:
                    print("Please enter a number between 1 and 20.")
                    continue
            break
        except ValueError:
            print("Please enter a valid number.")
    
    print()
    print("Performing full-text index search...")
    print("=" * 60)
    
    # Call the updated fuzzy search function
    results = matcher.get_fuzzy_term_matches(term, limit=limit)
    
    if results:
        print()
        print(f"Full-text search completed for '{term}' - showing up to {limit} results")
        print("\nDetailed Results:")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Term: {result['term']}")
            print(f"   Code: {result['code']}")
            print(f"   Type: {result['type']}")
            
            # Show definition with proper truncation
            definition = result['definition']
            if definition:
                if len(definition) > 150:
                    definition = definition[:147] + "..."
                print(f"   Definition: {definition}")
            else:
                print(f"   Definition: Not available")
        
        # Ask if user wants to get exact details for any of the results
        print(f"\n" + "-" * 60)
        while True:
            choice = input(f"Would you like detailed info for any result? (Enter 1-{len(results)} or 'n' for no): ").strip().lower()
            
            if choice in ['n', 'no']:
                break
            
            try:
                result_num = int(choice)
                if 1 <= result_num <= len(results):
                    selected_result = results[result_num - 1]
                    print(f"\nGetting detailed info for: {selected_result['term']}")
                    print("=" * 60)
                    
                    # Get full details using the exact match function
                    detailed_result = matcher.get_exact_match_from_code(selected_result['code'])
                    if detailed_result:
                        print(f"Retrieved detailed information for '{selected_result['term']}'")
                    break
                else:
                    print(f"Please enter a number between 1 and {len(results)}")
            except ValueError:
                print("Please enter a valid number or 'n'")
    else:
        print(f"No full-text matches found for term '{term}'")
        
        # Updated suggestions for full-text search
        print("\nPossible reasons:")
        print("- No full-text index available for NCIT nodes")
        print("- Search term doesn't match any indexed content")
        print("\nTips:")
        print("- Try searching for key medical terms: 'cancer', 'lung', 'blood', 'pressure'")
        print("- Use broader terms rather than very specific phrases")
        print("- Check if full-text index exists: CREATE FULLTEXT INDEX ncit_fulltext FOR (n:NCIT) ON EACH [n.term, n.definition]")
    
    return True

def main():
    NEO4J_URI = os.getenv("NEO4J_URI")  
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")             
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")         
    
    print("=== Enhanced Node Matcher Test with Fuzzy Search ===")
    print()
    
    # Check environment variables
    if not all([NEO4J_URI, NEO4J_USERNAME]):
        print("Error: Missing required environment variables.")
        print("Please set: NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD")
        sys.exit(1)
    
    try:
        print("Connecting to Neo4j database...")
        matcher = get_node_match(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
        print("Connection successful!")
        print()
        
        while True:
            print("-" * 60)
            
            search_type = get_search_type()
            
            if search_type == 'quit':
                print("\nThanks for testing the Node Matcher!")
                break
            
            search_successful = False
            
            if search_type == 'code':
                search_successful = search_by_code(matcher)
            elif search_type == 'term':
                search_successful = search_by_term(matcher)
            elif search_type == 'fuzzy':
                search_successful = fuzzy_search_by_term(matcher)
            
            if search_successful:
                print()
                continue_choice = input("Would you like to perform another search? (y/n): ").strip().lower()
                if continue_choice in ['n', 'no']:
                    print("\nThanks for testing!")
                    break
        
        # Clean up
        if hasattr(matcher, 'close'):
            matcher.close()
            
    except Exception as e:
        print(f"Error during testing: {e}")
        print("Please check your database connection details and ensure Neo4j is running.")
        sys.exit(1)

if __name__ == "__main__":
    main()