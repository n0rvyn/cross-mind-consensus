"""
AI Engineering Module for Cross-Mind Consensus System
Advanced prompt optimization, model ensemble strategies, and AI safety
"""

import re
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from collections import defaultdict
import tiktoken

import sys
sys.path.append('..')
from config import settings, MODEL_CONFIG

@dataclass
class PromptTemplate:
    """Structured prompt template with variables"""
    template: str
    variables: List[str]
    category: str
    expected_response_type: str
    safety_level: str  # "safe", "moderate", "high_risk"

@dataclass
class ModelEnsembleStrategy:
    """Configuration for model ensemble strategies"""
    strategy_name: str
    model_weights: Dict[str, float]
    aggregation_method: str  # "weighted_average", "majority_vote", "confidence_weighted"
    confidence_threshold: float
    fallback_models: List[str]

class PromptOptimizer:
    """Advanced prompt engineering and optimization"""
    
    def __init__(self):
        self.prompt_templates = self._load_prompt_templates()
        self.encoding = tiktoken.encoding_for_model("gpt-4")
    
    def _load_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Load optimized prompt templates"""
        templates = {
            "expert_analysis": PromptTemplate(
                template="""You are a {expertise_domain} expert with {experience_years} years of experience.
                
Analyze the following question with rigorous academic standards:
Question: {question}

Provide your analysis using this structure:
1. **Initial Assessment**: Your immediate expert perspective
2. **Key Considerations**: Critical factors that influence the answer
3. **Analysis**: Detailed examination with reasoning
4. **Confidence Level**: Rate your confidence (1-10) and explain why
5. **Potential Limitations**: What might you be missing or uncertain about?

Maintain objectivity and cite relevant principles from {expertise_domain}.""",
                variables=["expertise_domain", "experience_years", "question"],
                category="analysis",
                expected_response_type="structured_analysis",
                safety_level="safe"
            ),
            
            "critical_reviewer": PromptTemplate(
                template="""You are a critical reviewer and fact-checker with expertise in identifying logical fallacies, factual errors, and biased reasoning.

Review this response for accuracy and logical consistency:
Response: {response_to_review}

Your critical review should address:
1. **Factual Accuracy**: Verify claims and identify any factual errors
2. **Logical Consistency**: Check for logical fallacies or contradictions
3. **Bias Detection**: Identify potential cognitive biases or unfounded assumptions
4. **Missing Perspectives**: What important viewpoints or evidence are overlooked?
5. **Strength Assessment**: Rate the overall strength of the argument (1-10)
6. **Improvement Suggestions**: Specific recommendations for enhancement

Be thorough but constructive in your criticism.""",
                variables=["response_to_review"],
                category="review",
                expected_response_type="critical_analysis",
                safety_level="safe"
            ),
            
            "synthesis_expert": PromptTemplate(
                template="""You are a synthesis expert skilled at integrating multiple perspectives into coherent, nuanced conclusions.

Synthesize these diverse viewpoints into a comprehensive response:
{multiple_responses}

Your synthesis should:
1. **Common Ground**: Identify areas of agreement across responses
2. **Key Disagreements**: Highlight and analyze conflicting viewpoints
3. **Evidence Weighing**: Evaluate the strength of evidence for each position
4. **Integrated Conclusion**: Provide a nuanced synthesis that acknowledges complexity
5. **Uncertainty Acknowledgment**: Clearly state what remains uncertain or debatable
6. **Practical Implications**: What does this mean for real-world application?

Strive for intellectual honesty and avoid false balance.""",
                variables=["multiple_responses"],
                category="synthesis",
                expected_response_type="integrated_analysis",
                safety_level="safe"
            )
        }
        return templates
    
    def optimize_prompt_for_model(self, base_prompt: str, model_id: str, 
                                 optimization_target: str = "accuracy") -> str:
        """Optimize prompt based on specific model characteristics"""
        
        model_config = MODEL_CONFIG.get(model_id, {})
        model_type = model_config.get("type", "unknown")
        
        # Model-specific optimizations
        if model_type == "openai":
            return self._optimize_for_openai(base_prompt, optimization_target)
        elif model_type == "anthropic":
            return self._optimize_for_anthropic(base_prompt, optimization_target)
        elif model_type == "cohere":
            return self._optimize_for_cohere(base_prompt, optimization_target)
        else:
            return self._apply_generic_optimizations(base_prompt, optimization_target)
    
    def _optimize_for_openai(self, prompt: str, target: str) -> str:
        """OpenAI-specific prompt optimizations"""
        optimizations = {
            "accuracy": [
                "Think step by step.",
                "Show your reasoning process.",
                "Double-check your answer before providing it."
            ],
            "creativity": [
                "Be creative and think outside the box.",
                "Consider multiple perspectives.",
                "Generate novel insights."
            ],
            "safety": [
                "Ensure your response is helpful, harmless, and honest.",
                "Avoid speculation beyond your knowledge.",
                "Acknowledge limitations and uncertainties."
            ]
        }
        
        enhancements = optimizations.get(target, optimizations["accuracy"])
        enhanced_prompt = f"{prompt}\n\n{' '.join(enhancements)}"
        
        return enhanced_prompt
    
    def _optimize_for_anthropic(self, prompt: str, target: str) -> str:
        """Anthropic Claude-specific optimizations"""
        # Claude responds well to clear structure and explicit instructions
        if "Think step by step" not in prompt:
            prompt = f"{prompt}\n\nPlease think through this step by step and provide a clear, well-reasoned response."
        
        return prompt
    
    def _optimize_for_cohere(self, prompt: str, target: str) -> str:
        """Cohere-specific optimizations"""
        # Cohere models benefit from clear context and examples
        return f"Context: {prompt}\n\nPlease provide a comprehensive and accurate response based on the above context."
    
    def _apply_generic_optimizations(self, prompt: str, target: str) -> str:
        """Generic prompt optimizations"""
        return f"{prompt}\n\nPlease provide a thorough and accurate response."
    
    def estimate_token_count(self, text: str) -> int:
        """Estimate token count for text"""
        try:
            return len(self.encoding.encode(text))
        except Exception:
            # Fallback estimation: ~4 characters per token
            return len(text) // 4
    
    def create_role_based_prompt(self, question: str, role: str, 
                                context: Optional[str] = None) -> str:
        """Create role-based prompts with context"""
        
        role_templates = {
            "expert": self.prompt_templates["expert_analysis"],
            "critic": self.prompt_templates["critical_reviewer"],
            "synthesizer": self.prompt_templates["synthesis_expert"]
        }
        
        # Default role mapping
        role_mapping = {
            "Expert": "expert",
            "Reviewer": "critic", 
            "Validator": "expert",
            "Critic": "critic",
            "Synthesizer": "synthesizer"
        }
        
        template_key = role_mapping.get(role, "expert")
        template = role_templates.get(template_key, role_templates["expert"])
        
        # Fill template variables
        if template_key == "expert":
            prompt = template.template.format(
                expertise_domain=self._infer_domain(question),
                experience_years="10+",
                question=question
            )
        elif template_key == "critic":
            prompt = template.template.format(
                response_to_review=context or question
            )
        else:
            prompt = template.template.format(
                multiple_responses=context or question
            )
        
        return prompt
    
    def _infer_domain(self, question: str) -> str:
        """Infer expertise domain from question content"""
        domain_keywords = {
            "technology": ["AI", "machine learning", "programming", "software", "computer", "algorithm"],
            "science": ["research", "study", "hypothesis", "experiment", "data", "analysis"],
            "business": ["strategy", "market", "revenue", "profit", "investment", "management"],
            "health": ["medical", "health", "treatment", "diagnosis", "symptoms", "therapy"],
            "education": ["learning", "teaching", "curriculum", "student", "academic", "education"]
        }
        
        question_lower = question.lower()
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                return domain
        
        return "general knowledge"

class EnsembleManager:
    """Advanced model ensemble management"""
    
    def __init__(self):
        self.strategies = self._load_ensemble_strategies()
        self.model_performance_cache = {}
    
    def _load_ensemble_strategies(self) -> Dict[str, ModelEnsembleStrategy]:
        """Load predefined ensemble strategies"""
        strategies = {
            "balanced": ModelEnsembleStrategy(
                strategy_name="balanced",
                model_weights={"openai_gpt4": 0.3, "anthropic_claude": 0.3, "cohere_command": 0.2, "google_gemini": 0.2},
                aggregation_method="weighted_average",
                confidence_threshold=0.8,
                fallback_models=["openai_gpt4", "anthropic_claude"]
            ),
            
            "speed_optimized": ModelEnsembleStrategy(
                strategy_name="speed_optimized",
                model_weights={"openai_gpt35": 0.4, "cohere_command": 0.3, "moonshot": 0.3},
                aggregation_method="majority_vote",
                confidence_threshold=0.7,
                fallback_models=["openai_gpt4"]
            ),
            
            "accuracy_focused": ModelEnsembleStrategy(
                strategy_name="accuracy_focused",
                model_weights={"openai_gpt4": 0.4, "anthropic_claude": 0.4, "google_gemini": 0.2},
                aggregation_method="confidence_weighted",
                confidence_threshold=0.9,
                fallback_models=["anthropic_claude", "openai_gpt4"]
            )
        }
        return strategies
    
    def select_optimal_models(self, question: str, requirements: Dict[str, Any]) -> List[str]:
        """Select optimal model combination based on question and requirements"""
        
        # Analyze question characteristics
        question_analysis = self._analyze_question(question)
        
        # Consider requirements
        speed_priority = requirements.get("speed_priority", False)
        accuracy_priority = requirements.get("accuracy_priority", True)
        cost_conscious = requirements.get("cost_conscious", False)
        
        # Select strategy
        if speed_priority:
            strategy = self.strategies["speed_optimized"]
        elif accuracy_priority:
            strategy = self.strategies["accuracy_focused"]
        else:
            strategy = self.strategies["balanced"]
        
        # Filter available models
        available_models = [model for model in strategy.model_weights.keys() 
                          if self._is_model_available(model)]
        
        return available_models[:5]  # Limit to 5 models max
    
    def _analyze_question(self, question: str) -> Dict[str, Any]:
        """Analyze question characteristics for model selection"""
        analysis = {
            "complexity": self._estimate_complexity(question),
            "domain": self._classify_domain(question),
            "length": len(question),
            "question_type": self._classify_question_type(question)
        }
        return analysis
    
    def _estimate_complexity(self, question: str) -> str:
        """Estimate question complexity"""
        complexity_indicators = {
            "high": ["analyze", "compare", "evaluate", "synthesize", "critique", "multiple factors"],
            "medium": ["explain", "describe", "how", "why", "what if"],
            "low": ["what", "when", "where", "who", "define"]
        }
        
        question_lower = question.lower()
        
        for level, indicators in complexity_indicators.items():
            if any(indicator in question_lower for indicator in indicators):
                return level
        
        return "medium"
    
    def _classify_domain(self, question: str) -> str:
        """Classify question domain"""
        # Reuse domain classification from PromptOptimizer
        optimizer = PromptOptimizer()
        return optimizer._infer_domain(question)
    
    def _classify_question_type(self, question: str) -> str:
        """Classify type of question"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["opinion", "think", "believe", "feel"]):
            return "opinion"
        elif any(word in question_lower for word in ["fact", "true", "false", "verify"]):
            return "factual"
        elif any(word in question_lower for word in ["how to", "step", "process", "guide"]):
            return "procedural"
        elif any(word in question_lower for word in ["compare", "versus", "difference", "similar"]):
            return "comparative"
        else:
            return "general"
    
    def _is_model_available(self, model_id: str) -> bool:
        """Check if model is available and configured"""
        config = MODEL_CONFIG.get(model_id, {})
        return bool(config.get("api_key") and config["api_key"] != "")

class SafetyValidator:
    """AI safety validation and monitoring"""
    
    def __init__(self):
        self.safety_patterns = self._load_safety_patterns()
        self.risk_threshold = 0.7
    
    def _load_safety_patterns(self) -> Dict[str, List[str]]:
        """Load safety validation patterns"""
        return {
            "harmful_content": [
                r"how to (?:make|create|build) (?:bomb|weapon|explosive)",
                r"instructions? for (?:suicide|self-harm|violence)",
                r"illegal (?:drugs|activities|hacking)",
            ],
            "misinformation": [
                r"(?:covid|vaccine|pandemic) (?:hoax|conspiracy|fake)",
                r"(?:election|vote) (?:fraud|rigged|stolen)",
                r"(?:climate|global warming) (?:hoax|fake|conspiracy)",
            ],
            "bias_indicators": [
                r"(?:all|most) (?:women|men|people of) (?:are|can't|cannot|always)",
                r"(?:inherently|naturally|biologically) (?:superior|inferior|better|worse)",
            ],
            "privacy_violations": [
                r"personal (?:information|data|details|address|phone)",
                r"(?:social security|credit card|bank account) number",
            ]
        }
    
    def validate_question_safety(self, question: str) -> Dict[str, Any]:
        """Validate question for safety concerns"""
        safety_score = 1.0
        flags = []
        
        question_lower = question.lower()
        
        for category, patterns in self.safety_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    flags.append({
                        "category": category,
                        "pattern": pattern,
                        "severity": "high" if category in ["harmful_content", "privacy_violations"] else "medium"
                    })
                    safety_score -= 0.3 if category in ["harmful_content"] else 0.1
        
        return {
            "safety_score": max(0, safety_score),
            "is_safe": safety_score >= self.risk_threshold,
            "flags": flags,
            "recommendation": self._get_safety_recommendation(safety_score, flags)
        }
    
    def validate_response_safety(self, response: str) -> Dict[str, Any]:
        """Validate response for safety and quality"""
        # Check for harmful content
        safety_assessment = self.validate_question_safety(response)  # Reuse question validation
        
        # Additional response-specific checks
        quality_indicators = {
            "speculation": len(re.findall(r"(?:i think|i believe|probably|maybe|might be)", response.lower())),
            "uncertainty_acknowledgment": len(re.findall(r"(?:uncertain|unclear|unknown|not sure)", response.lower())),
            "factual_claims": len(re.findall(r"(?:research shows|studies indicate|according to)", response.lower())),
        }
        
        return {
            **safety_assessment,
            "quality_indicators": quality_indicators,
            "response_length": len(response),
            "coherence_score": self._assess_coherence(response)
        }
    
    def _assess_coherence(self, text: str) -> float:
        """Simple coherence assessment based on structure"""
        sentences = text.split('.')
        
        if len(sentences) < 2:
            return 0.5
        
        # Simple heuristics for coherence
        avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()])
        
        # Penalize very short or very long sentences
        coherence_score = 1.0
        if avg_sentence_length < 5 or avg_sentence_length > 50:
            coherence_score -= 0.2
        
        return max(0, min(1, coherence_score))
    
    def _get_safety_recommendation(self, score: float, flags: List[Dict]) -> str:
        """Generate safety recommendations"""
        if score >= 0.9:
            return "Safe to proceed"
        elif score >= 0.7:
            return "Proceed with caution - monitor response quality"
        elif score >= 0.5:
            return "High risk - require human review"
        else:
            return "Unsafe - do not process"

# Global instances
prompt_optimizer = PromptOptimizer()
ensemble_manager = EnsembleManager()
safety_validator = SafetyValidator() 