#!/usr/bin/env python3
"""
Test script for the synonym finder
Allows user to choose between searching by PV term or NCIT code
"""
from synonym_tool import get_synonyms  
import sys
import os

def get_search_type():
    """Get user's choice for search type"""
    while True:
        print("\nChoose search method:")
        print("1. Search by Permissible Value (PV) - e.g., 'prostate'")
        print("2. Search by NCIT Code - e.g., 'C4878'")
        print("3. Quit")
        
        choice = input("\nEnter your choice (1, 2, or 3): ").strip()
        
        if choice == '1':
            return 'pv'
        elif choice == '2':
            return 'code'
        elif choice == '3':
            return 'quit'
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def search_by_pv(synonym_finder):
    """Handle PV-based search"""
    pv_term = input("Enter a permissible value to search for: ").strip()
    
    if not pv_term:
        print("Please enter a valid permissible value.")
        return False
    
    print()
    synonyms = synonym_finder.get_synonyms_from_pv(pv_term)
    
    if synonyms:
        print()
        print(f"Found {len(synonyms)} synonyms for PV '{pv_term}'")
    else:
        print(f"No synonyms found for PV '{pv_term}'")
    
    return True

def search_by_code(synonym_finder):
    """Handle NCIT code-based search"""
    code = input("Enter an NCIT code to search for (e.g., C4878): ").strip()
    
    if not code:
        print("Please enter a valid NCIT code.")
        return False
    
    print()
    synonyms = synonym_finder.get_synonyms_from_termcode(code.upper())
    
    if synonyms:
        print()
        print(f"Found {len(synonyms)} synonyms for NCIT code '{code.upper()}'")
    else:
        print(f"No synonyms found for NCIT code '{code.upper()}'")
    
    return True

def main():
    """Main test function"""
    
    NEO4J_URI = os.getenv("NEO4J_URI")  
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")             
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")          
    
    print("=== Cancer Knowledge Graph Synonym Finder Test ===")
    print()
    
    try:
        print("Connecting to Neo4j database...")
        synonym_finder = get_synonyms(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
        print("Connection successful!")
        print()
        
        # Interactive testing loop
        while True:
            print("-" * 60)
            
            # Get search type from user
            search_type = get_search_type()
            
            if search_type == 'quit':
                print("Ok")
                break
            
            search_successful = False
            
            if search_type == 'pv':
                search_successful = search_by_pv(synonym_finder)
            elif search_type == 'code':
                search_successful = search_by_code(synonym_finder)
            
            # Ask to continue if search was successful
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