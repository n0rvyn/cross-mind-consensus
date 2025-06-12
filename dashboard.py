"""
Advanced Dashboard for Cross-Mind Consensus System
Real-time monitoring, analytics, and management interface
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
import time
from datetime import datetime, timedelta
import asyncio
import websocket
import threading
from typing import Dict, List, Any
import sys
sys.path.append('.')
from config import settings

# Page configuration
st.set_page_config(
    page_title="Cross-Mind Consensus Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = st.sidebar.text_input("API Base URL", "http://localhost:8000")
BEARER_TOKEN = st.sidebar.text_input("Bearer Token", "test-key", type="password")
headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}

# Custom CSS
st.markdown("""
<style>
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-online {
        color: #00ff00;
    }
    .status-offline {
        color: #ff0000;
    }
    .consensus-high {
        background-color: #d4edda;
        color: #155724;
    }
    .consensus-low {
        background-color: #f8d7da;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'websocket_data' not in st.session_state:
    st.session_state.websocket_data = []
if 'real_time_queries' not in st.session_state:
    st.session_state.real_time_queries = []

# Sidebar navigation
st.sidebar.title("🧠 Cross-Mind Consensus")
page = st.sidebar.selectbox("Choose Page", [
    "📊 Dashboard",
    "🔍 Query Interface", 
    "📈 Analytics",
    "⚙️ Model Management",
    "🚀 Batch Processing",
    "💾 Cache Management",
    "⚡ Real-time Monitor"
])

# Helper functions
def make_api_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return {}
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return {}

def format_consensus_score(score: float) -> str:
    """Format consensus score with color coding"""
    if score >= settings.high_consensus_threshold:
        return f'<span class="consensus-high">🟢 {score:.3f} (High)</span>'
    elif score >= settings.low_consensus_threshold:
        return f'<span style="color: orange;">🟡 {score:.3f} (Medium)</span>'
    else:
        return f'<span class="consensus-low">🔴 {score:.3f} (Low)</span>'

# Dashboard Page
if page == "📊 Dashboard":
    st.title("🧠 Cross-Mind Consensus Dashboard")
    
    # Health check
    health_data = make_api_request("/health")
    
    if health_data:
        # Status indicators
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("System Status", "🟢 Online" if health_data.get("status") == "healthy" else "🔴 Offline")
        
        with col2:
            cache_info = health_data.get("cache", {})
            st.metric("Cache Status", "🟢 Active" if cache_info.get("enabled") else "🔴 Disabled")
        
        with col3:
            st.metric("WebSocket Connections", health_data.get("websocket_connections", 0))
        
        with col4:
            analytics_info = health_data.get("analytics", {})
            st.metric("Total Queries", analytics_info.get("total_queries", 0))
        
        # System overview
        st.subheader("📊 System Overview")
        
        # Models status
        models_data = make_api_request("/models")
        if models_data:
            models_df = pd.DataFrame.from_dict(models_data["models"], orient="index")
            st.dataframe(models_df, use_container_width=True)
        
        # Recent analytics summary
        analytics_data = make_api_request("/analytics/summary")
        if analytics_data:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Performance Metrics")
                st.metric("Average Consensus Score", f"{analytics_data.get('avg_consensus_score', 0):.3f}")
                st.metric("Average Response Time", f"{analytics_data.get('avg_response_time', 0):.2f}s")
            
            with col2:
                st.subheader("🎯 Success Metrics")
                st.metric("Success Rate", f"{analytics_data.get('success_rate', 0):.1f}%")
                st.metric("Model Combinations", analytics_data.get('unique_model_combinations', 0))

# Query Interface Page
elif page == "🔍 Query Interface":
    st.title("🔍 Query Interface")
    
    with st.form("query_form"):
        st.subheader("Submit New Query")
        
        col1, col2 = st.columns(2)
        
        with col1:
            question = st.text_area("Question", placeholder="Enter your question here...")
            method = st.selectbox("Method", ["agreement", "chain"])
            use_cache = st.checkbox("Use Cache", value=True)
        
        with col2:
            # Get available models
            models_data = make_api_request("/models")
            available_models = list(models_data.get("models", {}).keys()) if models_data else []
            
            selected_models = st.multiselect("Select Models", available_models, default=available_models[:3])
            roles = st.text_input("Roles (comma-separated)", "Expert,Reviewer,Validator").split(",")
            chain_depth = st.slider("Chain Depth", 1, 5, 2) if method == "chain" else 2
        
        submit_button = st.form_submit_button("Submit Query")
        
        if submit_button and question and selected_models:
            with st.spinner("Processing query..."):
                payload = {
                    "question": question,
                    "roles": [role.strip() for role in roles],
                    "model_ids": selected_models,
                    "method": method,
                    "chain_depth": chain_depth,
                    "use_cache": use_cache,
                    "save_log": True
                }
                
                result = make_api_request("/llm/qa", "POST", payload)
                
                if result:
                    st.success("Query completed successfully!")
                    
                    # Display results
                    st.subheader("📊 Results")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Consensus Score", f"{result.get('consensus_score', 0):.3f}")
                    with col2:
                        st.metric("Query ID", result.get('query_id', 'N/A'))
                    
                    # Consensus verdict
                    verdict = result.get('verdict', 'Unknown')
                    st.markdown(f"**Verdict:** {verdict}")
                    
                    # Model answers
                    st.subheader("🤖 Model Answers")
                    for answer in result.get('answers', []):
                        with st.expander(f"{answer['model_id']} ({answer['role']})"):
                            st.write(answer['content'])
                            st.caption(f"Individual Score: {result.get('individual_scores', {}).get(answer['model_id'], 0):.3f}")
                    
                    # Chain process (if applicable)
                    if 'chain_process' in result:
                        st.subheader("🔗 Chain Verification Process")
                        for round_data in result['chain_process']:
                            with st.expander(f"Round {round_data['round']}"):
                                st.write("**Critic:**", round_data['critic_content'])
                                st.write("**Revised Answer:**", round_data['revised_answer'])

# Analytics Page
elif page == "📈 Analytics":
    st.title("📈 Analytics & Performance")
    
    # Time range selector
    col1, col2 = st.columns(2)
    with col1:
        days = st.selectbox("Time Range", [1, 7, 30, 90], index=1)
    with col2:
        auto_refresh = st.checkbox("Auto Refresh (30s)")
    
    if auto_refresh:
        time.sleep(0.1)  # Small delay to prevent too frequent refreshes
        st.rerun()
    
    # Get analytics data
    trends_data = make_api_request(f"/analytics/trends?days={days}")
    models_data = make_api_request("/analytics/models")
    
    if trends_data and trends_data.get("dates"):
        # Consensus trends
        st.subheader("📊 Consensus Trends")
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Consensus Score Over Time', 'Query Volume'),
            vertical_spacing=0.12
        )
        
        # Consensus score trend
        fig.add_trace(
            go.Scatter(
                x=trends_data["dates"],
                y=trends_data["avg_scores"],
                mode='lines+markers',
                name='Avg Consensus Score',
                line=dict(color='blue')
            ),
            row=1, col=1
        )
        
        # Query volume
        fig.add_trace(
            go.Bar(
                x=trends_data["dates"],
                y=trends_data["query_counts"],
                name='Query Count',
                marker_color='lightblue'
            ),
            row=2, col=1
        )
        
        fig.update_layout(height=600, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    if models_data and models_data.get("model_performances"):
        # Model performance comparison
        st.subheader("🤖 Model Performance Comparison")
        
        performances = models_data["model_performances"]
        df = pd.DataFrame(performances)
        
        if not df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Response time comparison
                fig = px.bar(
                    df, 
                    x='model_id', 
                    y='avg_response_time',
                    title='Average Response Time by Model',
                    color='avg_response_time',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Consensus score comparison
                fig = px.bar(
                    df, 
                    x='model_id', 
                    y='avg_consensus_score',
                    title='Average Consensus Score by Model',
                    color='avg_consensus_score',
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Performance table
            st.subheader("📋 Detailed Performance Metrics")
            display_df = df[['model_id', 'total_queries', 'avg_response_time', 'avg_consensus_score', 'success_rate']].copy()
            display_df['avg_response_time'] = display_df['avg_response_time'].round(2)
            display_df['avg_consensus_score'] = display_df['avg_consensus_score'].round(3)
            display_df['success_rate'] = display_df['success_rate'].round(1)
            
            st.dataframe(display_df, use_container_width=True)

# Model Management Page
elif page == "⚙️ Model Management":
    st.title("⚙️ Model Management")
    
    models_data = make_api_request("/models")
    
    if models_data:
        st.subheader("🤖 Available Models")
        
        for model_id, config in models_data["models"].items():
            with st.expander(f"{model_id} ({'✅ Available' if config['available'] else '❌ Unavailable'})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Type:** {config['type']}")
                    st.write(f"**Model:** {config['model']}")
                with col2:
                    st.write(f"**Available:** {'Yes' if config['available'] else 'No'}")
                    
                    # Quick test button
                    if st.button(f"Test {model_id}", key=f"test_{model_id}"):
                        test_payload = {
                            "question": "Test question: What is 2+2?",
                            "roles": ["Expert"],
                            "model_ids": [model_id],
                            "method": "agreement",
                            "use_cache": False
                        }
                        
                        with st.spinner("Testing model..."):
                            result = make_api_request("/llm/qa", "POST", test_payload)
                            if result and result.get('answers'):
                                st.success("Model test successful!")
                                st.write("Response:", result['answers'][0]['content'][:200] + "...")
                            else:
                                st.error("Model test failed!")

# Batch Processing Page
elif page == "🚀 Batch Processing":
    st.title("🚀 Batch Processing")
    
    st.subheader("📋 Batch Query Configuration")
    
    # Batch configuration
    col1, col2 = st.columns(2)
    with col1:
        parallel_processing = st.checkbox("Parallel Processing", value=True)
        max_batch_size = st.number_input("Max Batch Size", 1, 50, 10)
    
    with col2:
        default_method = st.selectbox("Default Method", ["agreement", "chain"])
        use_cache = st.checkbox("Use Cache for Batch", value=True)
    
    # Batch input
    st.subheader("📝 Batch Questions")
    batch_text = st.text_area(
        "Enter questions (one per line)",
        placeholder="Question 1\nQuestion 2\nQuestion 3",
        height=200
    )
    
    # Model selection for batch
    models_data = make_api_request("/models")
    available_models = list(models_data.get("models", {}).keys()) if models_data else []
    selected_models = st.multiselect("Select Models for Batch", available_models, default=available_models[:2])
    
    if st.button("🚀 Submit Batch") and batch_text and selected_models:
        questions = [q.strip() for q in batch_text.split('\n') if q.strip()]
        
        if len(questions) > max_batch_size:
            st.error(f"Too many questions! Maximum allowed: {max_batch_size}")
        else:
            batch_requests = []
            for question in questions:
                batch_requests.append({
                    "question": question,
                    "roles": ["Expert", "Reviewer"],
                    "model_ids": selected_models,
                    "method": default_method,
                    "use_cache": use_cache,
                    "save_log": True
                })
            
            batch_payload = {
                "requests": batch_requests,
                "parallel": parallel_processing
            }
            
            with st.spinner("Processing batch..."):
                result = make_api_request("/llm/batch", "POST", batch_payload)
                
                if result:
                    st.success(f"Batch completed! Processed {result.get('successful_requests', 0)}/{result.get('total_requests', 0)} requests")
                    st.metric("Total Processing Time", f"{result.get('response_time', 0):.2f}s")
                    
                    # Display results
                    st.subheader("📊 Batch Results")
                    for i, res in enumerate(result.get('results', [])):
                        if 'error' not in res:
                            with st.expander(f"Question {i+1}: {questions[i][:50]}..."):
                                st.metric("Consensus Score", f"{res.get('consensus_score', 0):.3f}")
                                st.write("**Verdict:**", res.get('verdict', 'Unknown'))

# Cache Management Page
elif page == "💾 Cache Management":
    st.title("💾 Cache Management")
    
    # Cache statistics
    health_data = make_api_request("/health")
    cache_stats = health_data.get("cache", {}) if health_data else {}
    
    if cache_stats:
        st.subheader("📊 Cache Statistics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Cache Status", "🟢 Enabled" if cache_stats.get("enabled") else "🔴 Disabled")
        with col2:
            st.metric("Memory Cache Size", cache_stats.get("memory_cache_size", 0))
        with col3:
            st.metric("Embedding Cache Size", cache_stats.get("embedding_cache_size", 0))
        
        if cache_stats.get("redis_available"):
            st.subheader("🔴 Redis Cache Stats")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Redis Keys", cache_stats.get("redis_keys", 0))
            with col2:
                st.metric("Memory Used", cache_stats.get("redis_memory_used", "N/A"))
            with col3:
                hit_rate = 0
                if cache_stats.get("redis_hits", 0) + cache_stats.get("redis_misses", 0) > 0:
                    hit_rate = cache_stats.get("redis_hits", 0) / (cache_stats.get("redis_hits", 0) + cache_stats.get("redis_misses", 0)) * 100
                st.metric("Hit Rate", f"{hit_rate:.1f}%")
    
    # Cache management actions
    st.subheader("🛠️ Cache Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear All Cache"):
            result = make_api_request("/cache", "DELETE")
            if result.get("success"):
                st.success("Cache cleared successfully!")
            else:
                st.error("Failed to clear cache")
    
    with col2:
        cache_pattern = st.text_input("Clear by Pattern", placeholder="llm_response:*")
        if st.button("🗑️ Clear Pattern") and cache_pattern:
            result = make_api_request(f"/cache?pattern={cache_pattern}", "DELETE")
            if result.get("success"):
                st.success(f"Cache pattern '{cache_pattern}' cleared!")
            else:
                st.error("Failed to clear cache pattern")

# Real-time Monitor Page
elif page == "⚡ Real-time Monitor":
    st.title("⚡ Real-time Monitor")
    
    st.subheader("🔴 Live Query Stream")
    
    # WebSocket connection status
    col1, col2 = st.columns(2)
    with col1:
        websocket_status = st.empty()
        websocket_status.markdown("🔴 **WebSocket:** Disconnected")
    
    with col2:
        active_queries = st.empty()
        active_queries.metric("Active Queries", len(st.session_state.real_time_queries))
    
    # Real-time data display
    real_time_container = st.container()
    
    # Auto-refresh for real-time updates
    if st.button("🔄 Refresh"):
        st.rerun()
    
    # Display recent queries
    with real_time_container:
        if st.session_state.real_time_queries:
            st.subheader("📊 Recent Queries")
            
            for query in st.session_state.real_time_queries[-10:]:  # Show last 10
                with st.expander(f"Query: {query.get('question', 'N/A')[:50]}..."):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write("**Models:**", ", ".join(query.get('models', [])))
                    with col2:
                        st.write("**Status:**", query.get('status', 'Unknown'))
                    with col3:
                        st.write("**Time:**", query.get('timestamp', 'N/A'))
        else:
            st.info("No real-time data available. Start some queries to see live updates!")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Cross-Mind Consensus Dashboard v2.0**")
st.sidebar.markdown("Real-time monitoring and analytics")

# Auto-refresh mechanism
if st.sidebar.checkbox("Auto-refresh Dashboard"):
    time.sleep(5)
    st.rerun() 