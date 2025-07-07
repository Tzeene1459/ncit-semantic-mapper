#!/usr/bin/env python3

from exact_match import get_node_match
import sys
import os

def get_search_type():
    while True:
        print("\nChoose search method:")
        print("1. Search by NCIT Code - e.g., 'C40625'")
        print("2. Search by Term - e.g., 'Lung Carcinoma'")
        print("3. Quit")
        
        choice = input("\nEnter your choice (1, 2, or 3): ").strip()
        
        if choice == '1':
            return 'code'
        elif choice == '2':
            return 'term'
        elif choice == '3':
            return 'quit'
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

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

def main():
    NEO4J_URI = os.getenv("NEO4J_URI")  
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")             
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")         
    
    print("=== Node Matcher Test ===")
    print()
    
    try:
        print("Connecting to Neo4j database...")
        matcher = get_node_match(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
        print("Connection successful!")
        print()
        
        while True:
            print("-" * 60)
            
            search_type = get_search_type()
            
            if search_type == 'quit':
                print("Ok")
                break
            
            search_successful = False
            
            if search_type == 'code':
                search_successful = search_by_code(matcher)
            elif search_type == 'term':
                search_successful = search_by_term(matcher)
            
            if search_successful:
                print()
                continue_choice = input("Would you like to perform another search? (y/n): ").strip().lower()
                if continue_choice in ['n', 'no']:
                    print("Ok")
                    break
            
    except Exception as e:
        print(f"Error during testing: {e}")
        print("Please check your database connection details and ensure Neo4j is running.")
        sys.exit(1)

if __name__ == "__main__":
    main()