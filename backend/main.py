import uuid
import os
import requests
import openai
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
from sentence_transformers import SentenceTransformer

# ========== 配置 ==========
# Bearer Key
VALID_KEYS = os.getenv("BACKEND_API_KEYS", "test-key,another-key").split(",")

# 多家模型Key等
MODEL_CONFIG = {
    "openai_gpt4": {"type": "openai", "api_key": os.getenv("OPENAI_API_KEY", "sk-xxx")},
    "anthropic_claude": {"type": "anthropic", "api_key": os.getenv("ANTHROPIC_API_KEY", "sk-ant-xxx")},
    "baidu_ernie": {
        "type": "baidu",
        "api_key": os.getenv("ERNIE_API_KEY", ""),
        "secret_key": os.getenv("ERNIE_SECRET_KEY", ""),
        "access_token": ""
    },
    "moonshot": {"type": "moonshot", "api_key": os.getenv("MOONSHOT_API_KEY", "")},
    "zhipu": {"type": "zhipu", "api_key": os.getenv("ZHIPU_API_KEY", "")},
    # 其他厂商按需补充
}

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
app = FastAPI()
# 自动权重缓存
MODEL_HISTORY = {}

# ========== 数据结构 ==========
class ModelAnswer(BaseModel):
    model_id: str
    role: str
    content: str
    score: Optional[float] = None
    embedding: Optional[List[float]] = None
    comment: Optional[str] = None

class QARequest(BaseModel):
    question: str
    roles: List[str]
    model_ids: List[str]
    method: str                # "agreement" or "chain"
    chain_depth: int = 2
    weights: Optional[List[float]] = None
    save_log: bool = True

# ========== 鉴权 ==========
def verify_bearer(auth: str):
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required.")
    token = auth.split(" ")[1].strip()
    if token not in VALID_KEYS:
        raise HTTPException(status_code=403, detail="Invalid Bearer token.")
    return True

# ========== 多厂商 LLM ==========
def call_llm(model_id, prompt):
    conf = MODEL_CONFIG.get(model_id)
    if not conf:
        return f"[ERROR] 未配置的模型：{model_id}"
    mtype = conf['type']
    if mtype == "openai":
        openai.api_key = conf["api_key"]
        resp = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=512
        )
        return resp.choices[0].message.content.strip()
    elif mtype == "anthropic":
        # 伪代码：实际需按官方文档实现
        headers = {"x-api-key": conf["api_key"]}
        data = {
            "model": "claude-3-opus-20240229",
            "max_tokens": 512,
            "messages": [{"role": "user", "content": prompt}]
        }
        url = "https://api.anthropic.com/v1/messages"
        resp = requests.post(url, headers=headers, json=data)
        return resp.json()['content'][0]['text'].strip()
    elif mtype == "baidu":
        # token刷新
        if not conf["access_token"]:
            resp = requests.post(
                f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={conf['api_key']}&client_secret={conf['secret_key']}"
            )
            access_token = resp.json().get("access_token", "")
            conf["access_token"] = access_token
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={conf['access_token']}"
        payload = {"messages": [{"role": "user", "content": prompt}], "disable_search": False}
        resp = requests.post(url, json=payload)
        return resp.json().get("result", "[ERNIE返回缺失]")
    elif mtype == "moonshot":
        # moonshot官方API示例
        url = "https://api.moonshot.cn/v1/chat/completions"
        headers = {"Authorization": f"Bearer {conf['api_key']}"}
        payload = {
            "model": "moonshot-v1-8k",
            "messages": [{"role": "user", "content": prompt}]
        }
        resp = requests.post(url, headers=headers, json=payload)
        return resp.json().get("choices", [{}])[0].get("message", {}).get("content", "[moonshot无内容]")
    elif mtype == "zhipu":
        # 智谱GLM API
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        headers = {"Authorization": f"Bearer {conf['api_key']}"}
        payload = {
            "model": "glm-4",
            "messages": [{"role": "user", "content": prompt}]
        }
        resp = requests.post(url, headers=headers, json=payload)
        return resp.json().get("choices", [{}])[0].get("message", {}).get("content", "[zhipu无内容]")
    else:
        return f"[ERROR] 暂不支持的模型类型：{mtype}"

def get_embedding(text):
    return embedding_model.encode(text).tolist()

def agreement_score(answers: List[ModelAnswer], weights=None):
    embs = [a.embedding for a in answers]
    sim_matrix = cosine_similarity(embs)
    n = len(answers)
    if not weights:
        weights = [1.0] * n
    weighted_scores = []
    count = 0
    for i in range(n):
        for j in range(i+1, n):
            s = sim_matrix[i][j]
            w = (weights[i]+weights[j])/2
            weighted_scores.append(s*w)
            count += w
    score = sum(weighted_scores) / (count if count else 1)
    return score, [sum(sim_matrix[i])/(n-1) for i in range(n)]  # 返回平均得分&每个模型的平均共识度

def save_log(log: Dict[str, Any]):
    os.makedirs("./logs", exist_ok=True)
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    fname = f"log_{now}_{uuid.uuid4().hex[:6]}.json"
    with open(f"./logs/{fname}", "w", encoding="utf-8") as f:
        for ans in log.get("answers", []):
            if ans.get("embedding"):
                ans["embedding"] = ans["embedding"][:8] + ["..."]
        json.dump(log, f, ensure_ascii=False, indent=2)

# ========== 权重自动调度API ==========
@app.post("/llm/auto-weights")
def auto_weights(req: QARequest, authorization: str = Header(None)):
    verify_bearer(authorization)
    model_ids = req.model_ids
    # 查历史
    prev = MODEL_HISTORY.get(req.question, {})
    # 目前采用简单“上次共识得分”法，否则默认均分
    weights = prev.get("auto_weights", [1.0]*len(model_ids))
    return {"auto_weights": weights}

# ========== 多LLM主流程 ==========
@app.post("/llm/qa")
async def multi_llm_qa(req: QARequest, authorization: str = Header(None)):
    verify_bearer(authorization)
    answers: List[ModelAnswer] = []
    log = {
        "question": req.question,
        "roles": req.roles,
        "model_ids": req.model_ids,
        "weights": req.weights,
        "timestamp": str(datetime.now()),
        "method": req.method
    }
    # 1. 回答与embedding
    weights = req.weights if req.weights and len(req.weights)==len(req.model_ids) else [1.0]*len(req.model_ids)
    for model_id, role, weight in zip(req.model_ids, req.roles, weights):
        prompt = f"你的身份是{role}。请回答如下问题：\n{req.question}"
        try:
            content = call_llm(model_id, prompt)
        except Exception as e:
            content = f"[{model_id}] 调用异常: {e}"
        embedding = get_embedding(content)
        ans = ModelAnswer(
            model_id=model_id,
            role=role,
            content=content,
            score=weight,
            embedding=embedding
        )
        answers.append(ans)
    log["answers"] = [a.dict() for a in answers]
    # 2. 一致性评分与动态权重建议
    if req.method == "agreement":
        score, indiv_scores = agreement_score(answers, weights)
        log["agreement_score"] = score
        log["individual_model_agreement"] = dict(zip(req.model_ids, indiv_scores))
        verdict = "一致性高，可信" if score >= 0.9 else "一致性较低，建议进一步链式验证"
        log["verdict"] = verdict
        # 自动调度建议：以各自平均共识分归一化为新权重
        total = sum(indiv_scores)
        auto_weights = [s/total if total > 0 else 1/len(indiv_scores) for s in indiv_scores]
        log["auto_weights_suggestion"] = dict(zip(req.model_ids, auto_weights))
        # 写入缓存用于下次建议
        MODEL_HISTORY[req.question] = {"auto_weights": auto_weights}
    # 3. 链式验证
    if req.method == "chain" or (req.method == "agreement" and score < 0.85):
        chain_answers = []
        prev_answer = answers[0].content
        for i in range(req.chain_depth):
            critic_idx = (i+1) % len(req.model_ids)
            critic_id = req.model_ids[critic_idx]
            critic_prompt = f"你是批评者，请针对下述回答进行严肃批评与完善建议：\n\n回答：{prev_answer}"
            critic_content = call_llm(critic_id, critic_prompt)
            reviser_idx = (i+2) % len(req.model_ids)
            reviser_id = req.model_ids[reviser_idx]
            reviser_prompt = (
                f"你是修正者，请根据以下批评意见优化原回答，使其更科学准确。\n原回答：{prev_answer}\n批评：{critic_content}"
            )
            revised_answer = call_llm(reviser_id, reviser_prompt)
            chain_answers.append({
                "round": i+1,
                "critic_id": critic_id,
                "critic_content": critic_content,
                "reviser_id": reviser_id,
                "revised_answer": revised_answer
            })
            prev_answer = revised_answer
        log["chain_process"] = chain_answers
        log["final_answer"] = prev_answer
    # 4. 高级日志
    if req.save_log:
        save_log(log)
    return log

@app.get("/")
def root():
    return {"message": "Multi-LLM Backend with Bearer Auth, Auto-Weighting, Advanced Logging."}
