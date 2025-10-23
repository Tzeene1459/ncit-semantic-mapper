# pages/live_mode.py
import streamlit as st
from datetime import datetime
from llm_agent_4o import map_raw_data_isolated
from utils.response_parser import parse_agent_response_detailed

def show_live_mode():
    """Live mode page content"""
    st.title("🚀 Live Mode")
    st.markdown("View detailed results from each search tool")
    
    if not st.session_state.agent_executor:
        st.warning("⚠️ Please initialize the agent first in the sidebar")
        return
    
    query = st.text_input(
        "Enter medical term:",
        value=st.session_state.get('current_query', ''),
        placeholder="e.g., diabetes, C12971, blood glucose"
    )
    
    if st.button("🔍 Search All Tools") or st.session_state.get('search_results'):
        if query:
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
            
            show_live_results()

def show_live_results():
    """Display live results in tabbed interface"""
    if not st.session_state.get('search_results'):
        return
    
    result = st.session_state.search_results['agent_response']
    query = st.session_state.search_results['query']
    
    st.markdown(f"### Live Results for: **{query}**")
    
    # Parse the response for detailed view
    parsed_data = parse_agent_response_detailed(result)
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Final Answer", "🔧 Tool Breakdown", "🧠 Agent Reasoning", "📄 Raw Response"])
    
    with tab1:
        st.markdown("#### Final Answer")
        if parsed_data.get('final_answer'):
            st.success(parsed_data['final_answer'])
        else:
            st.info("No final answer section found")
    
    with tab2:
        st.markdown("#### Tool-by-Tool Results")
        display_tool_breakdown(parsed_data.get('tool_results', {}))
    
    with tab3:
        st.markdown("#### Agent Reasoning Process")
        display_reasoning_steps(parsed_data.get('thoughts', []))
    
    with tab4:
        st.markdown("#### Complete Agent Response")
        st.code(result, language="text")
    
    # Export option
    if st.button("📁 Export Results"):
        export_results_to_json(st.session_state.search_results)

def display_tool_breakdown(tool_results):
    """Display results breakdown by tool"""
    if not tool_results:
        st.info("No tool breakdown available")
        return
    
    for tool_name, results in tool_results.items():
        with st.expander(f"🔧 {tool_name.replace('_', ' ').title()} Results"):
            if results:
                for i, result in enumerate(results):
                    st.markdown(f"**Result {i+1}:** {result}")
            else:
                st.text("No results from this tool")

def display_reasoning_steps(thoughts):
    """Display agent reasoning steps"""
    if thoughts:
        for i, thought in enumerate(thoughts, 1):
            st.markdown(f"**Step {i}:** {thought}")
    else:
        st.info("No explicit reasoning steps found")

def export_results_to_json(search_results):
    """Export search results to JSON format"""
    import json
    
    export_data = {
        'query': search_results['query'],
        'timestamp': search_results['timestamp'].isoformat(),
        'agent_response': search_results['agent_response']
    }
    
    # Create downloadable JSON
    json_str = json.dumps(export_data, indent=2)
    st.download_button(
        label="⬇️ Download JSON",
        data=json_str,
        file_name=f"search_results_{search_results['query'].replace(' ', '_')}.json",
        mime="application/json"
    )
