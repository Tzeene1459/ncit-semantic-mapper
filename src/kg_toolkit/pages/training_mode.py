import streamlit as st
from datetime import datetime
from llm_agent_4o import map_raw_data_isolated
from utils.data_manager import save_training_data
from utils.feedback_collector import collect_feedback_data

def show_training_mode():
    """Training mode page content"""
    st.title("🎯 Training Mode")
    st.markdown("Provide feedback on search results to improve the system")
    
    if not st.session_state.agent_executor:
        st.warning("⚠️ Please initialize the agent first in the sidebar")
        return
    
    query = st.text_input(
        "Enter medical term for training:",
        value=st.session_state.get('current_query', ''),
        placeholder="e.g., patient age, chemotherapy regimen"
    )
    
    if st.button("🔍 Search for Training") or st.session_state.get('search_results'):
        if query:
            if query != st.session_state.get('current_query') or not st.session_state.get('search_results'):
                with st.spinner("Getting results for training..."):
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
                    except Exception as e:
                        st.error(f"Search failed: {str(e)}")
                        return
            
            show_training_interface()

def show_training_interface():
    """Display the training interface with feedback collection"""
    if not st.session_state.get('search_results'):
        return
    
    result = st.session_state.search_results['agent_response']
    query = st.session_state.search_results['query']
    
    st.markdown(f"### Training Session for: **{query}**")
    
    # Parse actual results from agent response or use mock data
    parsed_results = parse_agent_results(result, query)
    
    st.markdown("**Select the most relevant results:**")
    
    feedback_data = collect_feedback_data(parsed_results)
    
    # Additional feedback section
    st.markdown("""
    <div class="feedback-section">
        <h4>Additional Feedback</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        overall_quality = st.selectbox("Overall result quality:", 
                                     ["Excellent", "Good", "Fair", "Poor"])
    with col2:
        confidence_in_feedback = st.selectbox("Your confidence in this feedback:",
                                            ["Very Confident", "Confident", "Somewhat Confident", "Not Confident"])
    
    # Save training data
    if st.button("💾 Save Training Data", type="primary"):
        training_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'overall_quality': overall_quality,
            'confidence': confidence_in_feedback,
            'agent_response': result,
            **feedback_data
        }
        
        # Save using data manager
        save_training_data(training_entry)
        st.session_state.training_data.append(training_entry)
        
        st.success("✅ Training data saved! Thank you for your feedback.")
        
        with st.expander("📊 Training Session Summary"):
            st.write(f"**Query:** {query}")
            st.write(f"**Selected Results:** {len(feedback_data.get('selected_results', []))}")
            st.write(f"**Rejected Results:** {len(feedback_data.get('rejected_results', []))}")
            st.write(f"**Overall Quality:** {overall_quality}")
            st.write(f"**Your Confidence:** {confidence_in_feedback}")

def parse_agent_results(agent_response, query):
    """Parse agent response to extract individual tool results for training"""
    # This is a simplified parser - you can enhance based on your agent's output format
    mock_results = [
        {
            'id': f'result_1_{query}',
            'tool': 'exact_match',
            'content': f'Exact match analysis for: {query}',
            'score': 0.95,
            'source': 'agent_response'
        },
        {
            'id': f'result_2_{query}',
            'tool': 'semantic_search',
            'content': f'Semantic analysis for: {query}',
            'score': 0.82,
            'source': 'agent_response'
        }
    ]
    
    # TODO: Implement actual parsing of your agent response
    # Look for tool execution patterns in agent_response
    # Extract actual results, scores, and tool names
    
    return mock_results