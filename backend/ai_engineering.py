"""AI Engineering Module for Cross-Mind Consensus System"""

import re
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class PromptTemplate:
    template: str
    variables: List[str]
    category: str
    safety_level: str

class PromptOptimizer:
    """Advanced prompt engineering and optimization"""
    
    def __init__(self):
        self.prompt_templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, PromptTemplate]:
        return {
            "expert": PromptTemplate(
                template="You are a {domain} expert. Analyze: {question}",
                variables=["domain", "question"],
                category="analysis",
                safety_level="safe"
            ),
            "critic": PromptTemplate(
                template="Critically review this response: {response}",
                variables=["response"],
                category="review", 
                safety_level="safe"
            )
        }
    
    def optimize_for_model(self, prompt: str, model_type: str) -> str:
        """Optimize prompt for specific model type"""
        if model_type == "openai":
            return f"{prompt}\n\nThink step by step."
        elif model_type == "anthropic":
            return f"{prompt}\n\nPlease provide a clear, well-reasoned response."
        return prompt
    
    def create_role_prompt(self, question: str, role: str) -> str:
        """Create role-based prompt"""
        domain = self._infer_domain(question)
        
        if role.lower() in ["expert", "validator"]:
            template = self.prompt_templates["expert"]
            return template.template.format(domain=domain, question=question)
        elif role.lower() in ["critic", "reviewer"]:
            template = self.prompt_templates["critic"] 
            return template.template.format(response=question)
        
        return f"As a {role}, please address: {question}"
    
    def _infer_domain(self, question: str) -> str:
        """Infer domain from question content"""
        keywords = {
            "technology": ["AI", "programming", "software"],
            "science": ["research", "study", "experiment"],
            "business": ["strategy", "market", "profit"]
        }
        
        question_lower = question.lower()
        for domain, words in keywords.items():
            if any(word.lower() in question_lower for word in words):
                return domain
        return "general"

class SafetyValidator:
    """AI safety validation"""
    
    def __init__(self):
        self.risk_patterns = [
            r"how to (?:make|create) (?:bomb|weapon)",
            r"illegal (?:drugs|activities)",
            r"harmful (?:content|instructions)"
        ]
    
    def validate_safety(self, text: str) -> Dict[str, Any]:
        """Validate text for safety concerns"""
        flags = []
        text_lower = text.lower()
        
        for pattern in self.risk_patterns:
            if re.search(pattern, text_lower):
                flags.append({"pattern": pattern, "severity": "high"})
        
        safety_score = 1.0 - (len(flags) * 0.3)
        
        return {
            "safety_score": max(0, safety_score),
            "is_safe": safety_score >= 0.7,
            "flags": flags,
            "recommendation": "Safe to proceed" if safety_score >= 0.7 else "Requires review"
        }

# Global instances
prompt_optimizer = PromptOptimizer()
safety_validator = SafetyValidator() 