#!/usr/bin/env python3
"""
Interactive Semantic Search Tool for SI-Tamer Database

This script provides an interactive command-line interface for searching
the semantic infrastructure database using PV, NCIT, and definition similarity searches.
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

def print_cde_definition_results(results, search_term):
    """Format and print CDE definition similarity search results"""
    print_separator()
    print(f"CDE Definition Search Results for: '{search_term}'")
    print_separator()
    
    if not results:
        print("No results found.")
        return
    
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        print(f"\nResult {i} (Similarity Score: {metadata['score']:.4f})")
        print(f"   CDE: {metadata['cde_term']}")
        print(f"   CDE Code: {metadata['cde_code']}")
        print(f"   Node Type: {metadata['node_type']}")
        
        # Show full definition for definition searches
        definition = metadata['cde_definition']
        if definition:
            if len(definition) > 200:
                definition = definition[:197] + "..."
            print(f"   Definition: {definition}")
        else:
            print(f"   Definition: Not available")

def print_ncit_definition_results(results, search_term):
    """Format and print NCIT definition similarity search results"""
    print_separator()
    print(f"NCIT Definition Search Results for: '{search_term}'")
    print_separator()
    
    if not results:
        print("No results found.")
        return
    
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        print(f"\nResult {i} (Similarity Score: {metadata['score']:.4f})")
        print(f"   NCIT Concept: {metadata['concept_term']}")
        print(f"   Concept Code: {metadata['concept_code']}")
        print(f"   Node Type: {metadata['node_type']}")
        
        # Show full definition for definition searches
        definition = metadata['concept_definition']
        if definition:
            if len(definition) > 200:
                definition = definition[:197] + "..."
            print(f"   Definition: {definition}")
        else:
            print(f"   Definition: Not available")

def get_search_choice():
    """Get user's choice of search type"""
    print("\nSI-Tamer Enhanced Semantic Search Tool")
    print_separator()
    print("Choose your search type:")
    print("1. PV Search         - Find CDEs from Permissible Value terms")
    print("2. NCIT Search       - Find CDEs from NCI Thesaurus concepts")
    print("3. CDE Definition    - Find CDEs by definition similarity")
    print("4. NCIT Definition   - Find NCIT concepts by definition similarity")
    print("5. Exit")
    
    while True:
        choice = input("\nEnter your choice (1/2/3/4/5): ").strip()
        if choice in ['1', '2', '3', '4', '5']:
            return choice
        print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")

def get_search_term(search_type):
    """Get search term from user"""
    if search_type == '1':
        prompt = "Enter PV term to search for (e.g., 'blood pressure', 'cancer stage'): "
    elif search_type == '2':
        prompt = "Enter NCIT concept to search for (e.g., 'hypertension', 'diabetes'): "
    elif search_type == '3':
        prompt = "Enter description to find similar CDE definitions (e.g., 'patient age at diagnosis'): "
    elif search_type == '4':
        prompt = "Enter description to find similar NCIT concepts (e.g., 'cancer of the blood'): "
    
    term = input(prompt).strip()
    while not term:
        print("Please enter a search term or description.")
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

def show_examples(search_type):
    """Show examples for different search types"""
    examples = {
        '1': [
            "blood pressure",
            "cancer stage", 
            "tumor size",
            "diabetes symptoms"
        ],
        '2': [
            "hypertension",
            "diabetes mellitus",
            "lung cancer",
            "prostate"
        ],
        '3': [
            "the age of a patient when first diagnosed with cancer",
            "measurement of blood pressure during heart contraction",
            "size of tumor in centimeters",
            "patient's response to chemotherapy treatment"
        ],
        '4': [
            "a type of cancer that affects blood cells",
            "high blood pressure condition",
            "organ that pumps blood through the body",
            "disease affecting sugar levels in blood"
        ]
    }
    
    if search_type in examples:
        print(f"\nExample searches for this type:")
        for i, example in enumerate(examples[search_type], 1):
            print(f"   {i}. \"{example}\"")

def main():
    """Main interactive loop"""
    print("Initializing SI-Tamer Enhanced Semantic Search...")
    
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
            
            if choice == '5':
                print("\nThanks for using SI-Tamer Semantic Search!")
                break
            
            # show examples for the chosen search type
            show_examples(choice)
            
            search_term = get_search_term(choice)
            result_count = get_result_count()
            
            print(f"\nSearching... (generating embeddings and querying database)")
            
            try:
                if choice == '1':
                    # PV Search
                    results = searcher.find_cde_from_pv_term(search_term, top_k=result_count)
                    print_pv_results(results, search_term)
                    
                elif choice == '2':
                    # NCIT Search
                    results = searcher.find_cde_from_ncit_term(search_term, top_k=result_count)
                    print_ncit_results(results, search_term)
                    
                elif choice == '3':
                    # CDE Definition Search
                    results = searcher.find_cde_by_definition_similarity(search_term, top_k=result_count)
                    print_cde_definition_results(results, search_term)
                    
                elif choice == '4':
                    # NCIT Definition Search
                    results = searcher.find_ncit_by_definition_similarity(search_term, top_k=result_count)
                    print_ncit_definition_results(results, search_term)
                
                # Show search statistics
                if choice in ['1', '2', '3', '4']:
                    print(f"\n" + "-" * 40)
                    print(f"Search completed: Found {len(results)} results")
                    if results:
                        scores = [r['metadata']['score'] for r in results]
                        print(f"Score range: {min(scores):.4f} - {max(scores):.4f}")
                        if max(scores) > 0.95:
                            print("High confidence matches found!")
                        elif max(scores) > 0.85:
                            print("Good matches found")
                        else:
                            print("Lower confidence matches - consider refining search")
                            
            except Exception as e:
                print(f"Error during search: {e}")
                continue
            
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