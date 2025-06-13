import json
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Cross-Mind Consensus Dashboard", layout="wide")

st.title("🧠 Cross-Mind Consensus Dashboard")

# Configuration
API_URL = st.sidebar.text_input("API URL", "http://localhost:8000")
BEARER_TOKEN = st.sidebar.text_input("Bearer Token", "test-key", type="password")

headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}

# Health check
try:
    response = requests.get(f"{API_URL}/health", headers=headers, timeout=5)
    if response.status_code == 200:
        health_data = response.json()
        st.success("🟢 System Online")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Cache Status",
                "Active" if health_data.get("cache", {}).get("enabled") else "Inactive",
            )
        with col2:
            st.metric(
                "WebSocket Connections", health_data.get("websocket_connections", 0)
            )
        with col3:
            st.metric("System Status", health_data.get("status", "Unknown"))
    else:
        st.error("🔴 System Offline")
except Exception as e:
    st.error(f"🔴 Cannot connect to API: {e}")

# Query interface
st.header("🔍 Submit Query")
with st.form("query_form"):
    question = st.text_area("Question")
    model_ids = st.multiselect("Models", ["openai_gpt4", "anthropic_claude", "zhipu"])
    roles = st.text_input("Roles (comma-separated)", "Expert,Reviewer")

    if st.form_submit_button("Submit"):
        if question and model_ids:
            payload = {
                "question": question,
                "roles": roles.split(","),
                "model_ids": model_ids,
                "method": "agreement",
            }

            try:
                response = requests.post(
                    f"{API_URL}/llm/qa", json=payload, headers=headers
                )
                if response.status_code == 200:
                    result = response.json()
                    st.success("Query completed!")
                    st.json(result)
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Request failed: {e}")

# Analytics section
st.header("📊 Analytics")
try:
    analytics_response = requests.get(f"{API_URL}/analytics/summary", headers=headers)
    if analytics_response.status_code == 200:
        analytics_data = analytics_response.json()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Queries", analytics_data.get("total_queries", 0))
        with col2:
            st.metric(
                "Avg Consensus Score",
                f"{analytics_data.get('avg_consensus_score', 0):.3f}",
            )
        with col3:
            st.metric("Success Rate", f"{analytics_data.get('success_rate', 0):.1f}%")
except Exception as e:
    st.info(f"Analytics data not available: {e}")
