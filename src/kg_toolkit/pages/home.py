import streamlit as st
from datetime import datetime
from llm_agent_4o import map_raw_data_isolated

def show_home_page():
    """Home page content - can be imported into main app if needed"""
    st.markdown('<h1 class="main-header">SI-Tamer Home</h1>', unsafe_allow_html=True)

    
    # Quick search
    st.markdown("### Quick Search")
    query = st.text_input("Enter medical term:", placeholder="e.g., lung cancer, hypertension")
    
    if st.button("Search") and query:
        if not st.session_state.agent_executor:
            st.error("Please initialize the agent first")
        else:
            with st.spinner(f"Searching for '{query}'..."):
                try:
                    result = map_raw_data_isolated(
                        st.session_state.agent_executor,
                        st.session_state.system_prompt,
                        query
                    )
                    
                    st.session_state.current_query = query
                    st.session_state.search_results = {
                        'agent_response': result,
                        'query': query,
                        'timestamp': datetime.now()
                    }
                    
                    st.markdown("### Quick Result")
                    
                    if "Final Answer:" in result:
                        final_section = result.split("Final Answer:")[-1]
                        st.success("✅ Mapping found!")
                        with st.expander("View Result Details"):
                            st.text(final_section)
                            st.caption("For detailed results, switch to Training or Live Mode from the sidebar.")
                    else:
                        st.info("Search completed - view full results in other modes")
                        
                    
                    
                            
                except Exception as e:
                    st.error(f"Search failed: {str(e)}")
