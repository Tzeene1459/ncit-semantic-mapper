#!/usr/bin/env python3
"""
Interactive Semantic Search Tool for SI-Tamer Database

This script provides an interactive command-line interface for searching
the semantic infrastructure database using either PV (Permissible Value)
or NCIT (NCI Thesaurus) term searches.
"""

import sys
from semantic_retrievers import SemanticSearcher

def print_separator():
    """Print a visual separator line"""
    print("=" * 80)

def print_pv_results(results, search_term):
    """Format and print PV search results"""
    print_separator()
    print(f"PV Search Results for: '{search_term}'")
    print_separator()
    
    if not results:
        print("No results found.")
        return
    
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        print(f"\nResult {i} (Similarity Score: {metadata['score']:.4f})")
        print(f"   Permissible Value: {metadata['pv_term']}")
        print(f"   PV Code: {metadata['pv_code']}")
        print(f"   Related CDE: {metadata['cde_term']}")
        print(f"   CDE Code: {metadata['cde']}")
        
        # Truncate long definitions
        definition = result['text']
        if len(definition) > 100:
            definition = definition[:97] + "..."
        print(f"   Definition: {definition}")

def print_ncit_results(results, search_term):
    """Format and print NCIT search results"""
    print_separator()
    print(f"NCIT Search Results for: '{search_term}'")
    print_separator()
    
    if not results:
        print("No results found.")
        return
    
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        print(f"\nResult {i} (Similarity Score: {metadata['score']:.4f})")
        print(f"   NCIT Concept: {metadata['concept_term']}")
        print(f"   Concept Code: {metadata['concept_code']}")
        print(f"   Related PV: {metadata['pv_term']}")
        print(f"   PV Code: {metadata['pv_code']}")
        
        # Handle CDE list
        cde_count = len(metadata['of_cdes'])
        if cde_count > 0:
            if cde_count <= 5:
                print(f"   Related CDEs: {', '.join(metadata['of_cdes'])}")
            else:
                first_five = ', '.join(metadata['of_cdes'][:5])
                print(f"   Related CDEs: {first_five} ... (+{cde_count-5} more)")
        else:
            print(f"   Related CDEs: None")
        
        # Truncate long definitions
        definition = result['text']
        if len(definition) > 100:
            definition = definition[:97] + "..."
        print(f"   Definition: {definition}")

def get_search_choice():
    """Get user's choice of search type"""
    print("\nSI-Tamer Semantic Search Tool")
    print_separator()
    print("Choose your search type:")
    print("1. PV Search  - Find CDEs from Permissible Value terms")
    print("2. NCIT Search - Find CDEs from NCI Thesaurus concepts")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1/2/3): ").strip()
        if choice in ['1', '2', '3']:
            return choice
        print("Invalid choice. Please enter 1, 2, or 3.")

def get_search_term(search_type):
    """Get search term from user"""
    if search_type == '1':
        prompt = "Enter PV term to search for (e.g., 'blood pressure', 'cancer stage'): "
    else:
        prompt = "Enter NCIT concept to search for (e.g., 'hypertension', 'diabetes'): "
    
    term = input(prompt).strip()
    while not term:
        print("Please enter a search term.")
        term = input(prompt).strip()
    
    return term

def get_result_count():
    """Get number of results to display"""
    while True:
        try:
            count = input("How many results would you like? (default: 5): ").strip()
            if not count:
                return 5
            count = int(count)
            if 1 <= count <= 20:
                return count
            else:
                print("Please enter a number between 1 and 20.")
        except ValueError:
            print("Please enter a valid number.")

def main():
    """Main interactive loop"""
    print("Initializing SI-Tamer Semantic Search...")
    
    try:
        searcher = SemanticSearcher()
        print("Connected to database successfully!")
    except Exception as e:
        print(f"Failed to initialize searcher: {e}")
        print("Please check your environment variables:")
        print("   - OPENAI_API_KEY")
        print("   - NEO4J_URI")
        print("   - NEO4J_USERNAME")
        print("   - NEO4J_PASSWORD")
        return
    
    try:
        while True:
            choice = get_search_choice()
            
            if choice == '3':
                print("\nThanks for using SI-Tamer Semantic Search!")
                break
            
            search_term = get_search_term(choice)
            result_count = get_result_count()
            
            print(f"\nSearching... (generating embeddings and querying database)")
            
            if choice == '1':
                # PV Search
                results = searcher.find_cde_from_pv_term(search_term, top_k=result_count)
                print_pv_results(results, search_term)
            else:
                # NCIT Search
                results = searcher.find_cde_from_ncit_term(search_term, top_k=result_count)
                print_ncit_results(results, search_term)
            
            # Ask if user wants to continue
            print(f"\n" + "-" * 80)
            continue_choice = input("Would you like to perform another search? (y/n): ").strip().lower()
            if continue_choice not in ['y', 'yes']:
                print("\nThanks for using SI-Tamer Semantic Search!")
                break
                
    except KeyboardInterrupt:
        print("\n\nSearch interrupted. Goodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        searcher.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()