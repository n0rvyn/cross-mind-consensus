import streamlit as st
import requests

st.title("多LLM链式评审 Demo")
api_url = st.text_input("后端API地址", "http://127.0.0.1:8000/llm/qa")
bearer = st.text_input("Bearer Key", "test-key")
question = st.text_area("问题", "为什么有时连续几天都下雨？")
model_ids = st.text_input("模型ID，逗号分隔", "openai_gpt4,anthropic_claude,zhipu").split(",")
roles = st.text_input("角色，逗号分隔", "提出者,批评者,修正者").split(",")
method = st.selectbox("方法", ["agreement", "chain"])
chain_depth = st.number_input("链式轮数", 2, 5, 2)
if st.button("提交"):
    payload = {
        "question": question,
        "roles": roles,
        "model_ids": model_ids,
        "method": method,
        "chain_depth": int(chain_depth),
        "weights": [1.0] * len(model_ids),
        "save_log": True
    }
    resp = requests.post(
        api_url, json=payload,
        headers={"Authorization": f"Bearer {bearer}"}
    )
    st.json(resp.json())
