import requests

API_URL = "http://127.0.0.1:8000/llm/qa"
BEARER_KEY = "test-key"  # 替换为你的Key

payload = {
    "question": "为什么有时连续几天都下雨？",
    "roles": ["提出者", "批评者", "修正者"],
    "model_ids": ["openai_gpt4", "anthropic_claude", "zhipu"],
    "method": "agreement",
    "chain_depth": 2,
    "weights": [1, 1, 1],
    "save_log": True
}

headers = {"Authorization": f"Bearer {BEARER_KEY}"}
resp = requests.post(API_URL, json=payload, headers=headers)
print(resp.json())
