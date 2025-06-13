# 3️⃣ 自动评分/仲裁提示词（Auto-Scoring/Arbitration Prompts）

你是一个专业评审员。请对下面同一问题的多个回答，按照准确性、逻辑性、表述清晰度三项，每项0-10分打分，并简要说明理由。

问题：
{question}

回答A（模型{model_a}）：
{answer_a}

回答B（模型{model_b}）：
{answer_b}

回答C（模型{model_c}）：
{answer_c}

请输出：
1. 各回答每项得分
2. 总结你的打分理由
3. 指出哪个答案最优，并解释原因
4. 如有分歧，建议如何进一步验证

---

You are a professional referee. Please score the following answers to the same question based on accuracy, logic, and clarity (0-10 each), and briefly explain your reasons.

Question:
{question}

Answer A (model {model_a}):
{answer_a}

Answer B (model {model_b}):
{answer_b}

Answer C (model {model_c}):
{answer_c}

Please output:
1. Score for each answer in each category
2. Summary of your scoring rationale
3. Point out the best answer and explain why
4. If there is disagreement, suggest how to further verify
