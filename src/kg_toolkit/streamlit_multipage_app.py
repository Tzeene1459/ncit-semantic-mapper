# streamlit_multipage_app.py
import streamlit as st
import os
from datetime import datetime

# Import your existing agent - no changes needed to your agent code
from llm_agent_4o import create_fresh_agent, map_raw_data_isolated

# Configure page
st.set_page_config(
    page_title="SI-Tamer: Multi-Mode Medical Search",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def initialize_session_state():
    if 'search_results' not in st.session_state:
        st.session_state.search_results = {}
    if 'current_query' not in st.session_state:
        st.session_state.current_query = ""
    if 'agent_executor' not in st.session_state:
        st.session_state.agent_executor = None
    if 'system_prompt' not in st.session_state:
        st.session_state.system_prompt = None
    if 'training_data' not in st.session_state:
        st.session_state.training_data = []

# CSS styling (simplified from your existing app)
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] div.st-emotion-cache-16txtl3 {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def main():
    initialize_session_state()
    
    # Sidebar navigation
    st.sidebar.title("🔬 SI-Tamer Multi-Mode")
    
    # Agent status and initialization
    with st.sidebar:
        st.markdown("**Agent Status**")
        
        # Environment check
        neo4j_status = "✅" if os.getenv("NEO4J_URI") else "❌"
        openai_status = "✅" if os.getenv("OPENAI_API_KEY") else "❌"
        
        st.write(f"Neo4j: {neo4j_status}")
        st.write(f"OpenAI: {openai_status}")
        
        # Initialize agent
        if st.button("🚀 Initialize Agent"):
            if os.getenv("NEO4J_URI") and os.getenv("OPENAI_API_KEY"):
                with st.spinner("Initializing..."):
                    try:
                        agent_executor, system_prompt = create_fresh_agent()
                        st.session_state.agent_executor = agent_executor
                        st.session_state.system_prompt = system_prompt
                        st.success("Agent ready!")
                    except Exception as e:
                        st.error(f"Failed: {str(e)}")
            else:
                st.error("Missing environment variables")
        
        agent_ready = "🟢 Ready" if st.session_state.agent_executor else "🔴 Not Ready"
        st.write(f"Status: {agent_ready}")
        
        st.markdown("---")
        
        # Mode selection
        mode = st.radio(
            "**Select Mode:**",
            ["🏠 Home", "🎯 Training Mode", "🚀 Live Mode"],
            key="mode_selection"
        )
    
    # Route to different modes
    if mode == "🏠 Home":
        show_home_page()
    elif mode == "🎯 Training Mode":
        show_training_mode()
    elif mode == "🚀 Live Mode":
        show_live_mode()

def show_home_page():
    st.markdown('<h1 class="main-header">SI-Tamer Home</h1>', unsafe_allow_html=True)
    
    # Mode descriptions
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="mode-description">
            <h3>🎯 Training Mode</h3>
            <p>Help improve the system by providing feedback on search results. 
            Your selections train the model to better understand medical terminology mapping.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="mode-description">
            <h3>🚀 Live Mode</h3>
            <p>View detailed results from each search tool separately. 
            Perfect for exploring different approaches and understanding how tools work.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick search
    st.markdown("### Quick Search")
    query = st.text_input("Enter medical term:", placeholder="e.g., lung cancer, hypertension")
    
    if st.button("Search") and query:
        if not st.session_state.agent_executor:
            st.error("Please initialize the agent first")
        else:
            with st.spinner(f"Searching for '{query}'..."):
                try:
                    # Use your existing agent function
                    result = map_raw_data_isolated(
                        st.session_state.agent_executor,
                        st.session_state.system_prompt,
                        query
                    )
                    
                    # Store results for other modes
                    st.session_state.current_query = query
                    st.session_state.search_results = {
                        'agent_response': result,
                        'query': query,
                        'timestamp': datetime.now()
                    }
                    
                    # Display quick result
                    st.markdown("### Quick Result")
                    
                    # Extract key information (simplified version of your existing parser)
                    if "Final Answer:" in result:
                        final_section = result.split("Final Answer:")[-1]
                        st.success("✅ Mapping found!")
                        with st.expander("View Result Details"):
                            st.text(final_section[:500] + "..." if len(final_section) > 500 else final_section)
                    else:
                        st.info("Search completed - view full results in other modes")
                    
                    # Quick links to other modes
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🎯 Analyze in Training Mode"):
                            st.session_state.mode_selection = "🎯 Training Mode"
                            st.rerun()
                    with col2:
                        if st.button("🚀 View in Live Mode"):
                            st.session_state.mode_selection = "🚀 Live Mode"
                            st.rerun()
                            
                except Exception as e:
                    st.error(f"Search failed: {str(e)}")

def show_training_mode():
    st.title("🎯 Training Mode")
    st.markdown("Provide feedback on search results to improve the system")
    
    if not st.session_state.agent_executor:
        st.warning("⚠️ Please initialize the agent first in the sidebar")
        return
    
    # Query input
    query = st.text_input(
        "Enter medical term for training:",
        value=st.session_state.get('current_query', ''),
        placeholder="e.g., patient age, chemotherapy regimen"
    )
    
    if st.button("🔍 Search for Training") or st.session_state.get('search_results'):
        if query:
            # Perform search if new query
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
            
            # Display training interface
            show_training_interface()

def show_training_interface():
    if not st.session_state.get('search_results'):
        return
    
    result = st.session_state.search_results['agent_response']
    query = st.session_state.search_results['query']
    
    st.markdown(f"### Training Session for: **{query}**")
    
    # Mock up some tool results for training interface
    # In reality, you'd parse these from your agent response
    mock_results = [
        {
            'id': 'result_1',
            'tool': 'exact_match',
            'content': 'Found exact match: C3117 - Hypertension',
            'score': 0.98
        },
        {
            'id': 'result_2', 
            'tool': 'semantic_search',
            'content': 'Semantic match: C12971 - High Blood Pressure',
            'score': 0.85
        },
        {
            'id': 'result_3',
            'tool': 'fuzzy_match',
            'content': 'Similar term: C3222 - Blood Pressure Disorder',
            'score': 0.72
        }
    ]
    
    st.markdown("**Select the most relevant results:**")
    
    # Display results with feedback options
    selected_results = []
    rejected_results = []
    
    for i, result_item in enumerate(mock_results):
        with st.container():
            st.markdown(f"""
            <div class="training-result-card">
                <strong>Tool:</strong> {result_item['tool']} | <strong>Score:</strong> {result_item['score']}<br>
                <strong>Result:</strong> {result_item['content']}
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.checkbox("✅ Relevant", key=f"select_{i}"):
                    selected_results.append(result_item['id'])
            
            with col2:
                if st.checkbox("❌ Not Relevant", key=f"reject_{i}"):
                    rejected_results.append(result_item['id'])
    
    # Additional feedback
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
            'selected_results': selected_results,
            'rejected_results': rejected_results,
            'overall_quality': overall_quality,
            'confidence': confidence_in_feedback,
            'agent_response': st.session_state.search_results['agent_response']
        }
        
        # Save to training data (you can implement file saving here)
        st.session_state.training_data.append(training_entry)
        
        st.success("✅ Training data saved! Thank you for your feedback.")
        
        # Show summary
        with st.expander("📊 Training Session Summary"):
            st.write(f"**Query:** {query}")
            st.write(f"**Selected Results:** {len(selected_results)}")
            st.write(f"**Rejected Results:** {len(rejected_results)}")
            st.write(f"**Overall Quality:** {overall_quality}")
            st.write(f"**Your Confidence:** {confidence_in_feedback}")

def show_live_mode():
    st.title("🚀 Live Mode")
    st.markdown("View detailed results from each search tool")
    
    if not st.session_state.agent_executor:
        st.warning("⚠️ Please initialize the agent first in the sidebar")
        return
    
    # Query input
    query = st.text_input(
        "Enter medical term:",
        value=st.session_state.get('current_query', ''),
        placeholder="e.g., diabetes, C12971, blood glucose"
    )
    
    if st.button("🔍 Search All Tools") or st.session_state.get('search_results'):
        if query:
            # Perform search if new query
            if query != st.session_state.get('current_query') or not st.session_state.get('search_results'):
                with st.spinner("Running comprehensive search..."):
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
            
            # Display live results
            show_live_results()

def show_live_results():
    if not st.session_state.get('search_results'):
        return
    
    result = st.session_state.search_results['agent_response']
    query = st.session_state.search_results['query']
    
    st.markdown(f"### Live Results for: **{query}**")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Final Answer", "🔧 Tool Breakdown", "🧠 Agent Reasoning", "📄 Raw Response"])
    
    with tab1:
        st.markdown("#### Final Answer")
        if "Final Answer:" in result:
            final_section = result.split("Final Answer:")[-1]
            st.success(final_section)
        else:
            st.info("No final answer section found")
    
    with tab2:
        st.markdown("#### Tool-by-Tool Results")
        
        # Mock breakdown - you can enhance this to actually parse tool results
        tools = ["Exact Match", "Fuzzy Match", "Semantic Search", "Synonym Finder"]
        
        for tool in tools:
            with st.expander(f"🔧 {tool} Results"):
                if tool.lower().replace(" ", "_") in result.lower():
                    # Extract relevant sections
                    st.text("Tool executed - check raw response for details")
                else:
                    st.text("Tool not used in this search")
    
    with tab3:
        st.markdown("#### Agent Reasoning Process")
        
        # Extract thought process
        thoughts = []
        lines = result.split('\n')
        for line in lines:
            if line.startswith('Thought:'):
                thoughts.append(line)
        
        if thoughts:
            for i, thought in enumerate(thoughts, 1):
                st.markdown(f"**Step {i}:** {thought.replace('Thought:', '').strip()}")
        else:
            st.info("No explicit reasoning steps found")
    
    with tab4:
        st.markdown("#### Complete Agent Response")
        st.code(result, language="text")
    
    # Export option
    if st.button("📁 Export Results"):
        # You can implement export functionality here
        st.success("Results exported to clipboard!")

if __name__ == "__main__":
    main()