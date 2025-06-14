"""
Simplified Streamlit dashboard for testing the Cross-Mind Consensus API
"""

import streamlit as st
import requests
import json
import os
from datetime import datetime

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Set page configuration
st.set_page_config(
    page_title="Cross-Mind Consensus Dashboard",
    page_icon="🧠",
    layout="wide",
)

# Title and description
st.title("🧠 Cross-Mind Consensus Dashboard")
st.markdown("A dashboard for testing the Cross-Mind Consensus API")

# API Health Check
st.sidebar.header("API Status")
try:
    health_response = requests.get(f"{API_URL}/health", timeout=5)
    if health_response.status_code == 200:
        st.sidebar.success(f"API Connected: {API_URL}")
        health_data = health_response.json()
        st.sidebar.json(health_data)
    else:
        st.sidebar.error(f"API Error: Status {health_response.status_code}")
except Exception as e:
    st.sidebar.error(f"API Connection Error: {e}")

# Main form
st.header("Get Consensus")

with st.form("consensus_form"):
    query = st.text_area(
        "Query or Question",
        value="Which is the best programming language for beginners?",
        height=100,
    )
    
    context = st.text_area(
        "Context (optional)",
        value="",
        height=100,
    )
    
    # Dynamic options input
    st.subheader("Options")
    
    default_options = [
        {"id": "1", "text": "Python", "description": "Easy syntax, great for beginners"},
        {"id": "2", "text": "JavaScript", "description": "Web development focused"},
        {"id": "3", "text": "Scratch", "description": "Visual programming language for kids"}
    ]
    
    options_json = st.text_area(
        "Options (JSON)",
        value=json.dumps(default_options, indent=2),
        height=200,
    )
    
    models = st.multiselect(
        "Models",
        ["gpt-4", "claude-3", "gemini-pro", "mistral", "llama-3"],
        default=["gpt-4", "claude-3", "gemini-pro"],
    )
    
    submitted = st.form_submit_button("Get Consensus")

# Process form submission
if submitted:
    try:
        # Parse options from JSON
        options = json.loads(options_json)
        
        # Prepare request payload
        payload = {
            "query": query,
            "options": options,
            "models": models,
        }
        
        if context:
            payload["context"] = context
        
        # Display the request
        st.subheader("Request")
        st.json(payload)
        
        # Send API request
        with st.spinner("Getting consensus..."):
            response = requests.post(
                f"{API_URL}/consensus",
                json=payload,
                timeout=30,
            )
            
        # Display the response
        st.subheader("Response")
        if response.status_code == 200:
            response_data = response.json()
            
            # Show the consensus result prominently
            consensus = response_data.get("consensus", {})
            selected_option = consensus.get("selected_option", {})
            
            st.success(f"Consensus: {selected_option.get('text', 'Unknown')}")
            
            # Create columns for consensus details
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Agreement", f"{consensus.get('agreement_percentage', 0):.1f}%")
            with col2:
                st.metric("Vote Count", consensus.get('vote_count', 0))
            with col3:
                st.metric("Processing Time", f"{response_data.get('processing_time', 0):.2f}s")
            
            # Show individual model responses
            st.subheader("Model Responses")
            for model_response in response_data.get("model_responses", []):
                option_id = model_response.get("selected_option_id")
                option_text = next(
                    (opt.get("text", "") for opt in options if opt.get("id") == option_id),
                    f"Option {option_id}"
                )
                
                st.write(f"**{model_response.get('model')}** selected: {option_text}")
                st.write(f"Reasoning: {model_response.get('reasoning', 'No reasoning provided')}")
                st.write("---")
            
            # Show full response as JSON for debugging
            with st.expander("Full API Response"):
                st.json(response_data)
        else:
            st.error(f"API Error: {response.status_code}")
            st.json(response.json() if response.content else {})
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown(f"Dashboard last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 