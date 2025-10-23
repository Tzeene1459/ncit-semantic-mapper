#!/usr/bin/env python3
"""
Testing script to compare baseline vs context-aware semantic search
for PV -> CDE mapping.
"""

from semantic_retrievers import SemanticSearcher

def print_separator():
    print("=" * 80)

def print_results(results, title):
    """Format and print search results."""
    print_separator()
    print(f"{title} (Total Results: {len(results)})")
    print_separator()

    if not results:
        print("No results found.\n")
        return

    for i, result in enumerate(results, 1):
        meta = result['metadata']
        score = meta.get('score', 0.0)
        combined_score = meta.get('combined_score', None)
        oc_term = meta.get('oc_term', None)

        print(f"\nResult {i}")
        print(f"  CDE: {meta.get('cde_term')} (Code: {meta.get('cde')})")
        print(f"  PV: {meta.get('pv_term')} (Code: {meta.get('pv_code')})")
        print(f"  Baseline Score: {score:.4f}")
        if combined_score is not None:
            print(f"  Combined Score (with OC): {combined_score:.4f}")
        if oc_term:
            print(f"  Object Class: {oc_term}")

        definition = result['text']
        if len(definition) > 100:
            definition = definition[:97] + "..."
        print(f"  Definition: {definition}")

def main():
    print("Initializing semantic searcher for context-aware testing...\n")
    searcher = SemanticSearcher()

    try:
        while True:
            search_term = input("Enter PV term to test (or 'quit' to exit): ").strip()
            if search_term.lower() in ['quit', 'exit', 'q']:
                print("Exiting test.")
                break

            top_k = input("Number of results to display (default 5): ").strip()
            top_k = int(top_k) if top_k.isdigit() else 5

            print("\nRunning baseline search...")
            baseline_results = searcher.find_cde_from_pv_term(search_term, top_k=top_k)
            print_results(baseline_results, "Baseline Search Results")

            print("\nRunning context-aware search...")
            context_results = searcher.contextaware_cde_from_pv(search_term, top_k=top_k)
            print_results(context_results, "Context-Aware Search Results")

            print("\n" + "-" * 80)
            cont = input("Run another test? (y/n): ").strip().lower()
            if cont not in ['y', 'yes']:
                break

    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
    finally:
        searcher.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()
