import os
import json
from typing import Dict, Any
import openai
import anthropic
from dotenv import load_dotenv

load_dotenv()

class AIInsightsGenerator:
    def __init__(self):
        self.provider = os.getenv("USE_AI_PROVIDER", "openai")
        
        if self.provider == "openai":
            openai.api_key = os.getenv("OPENAI_API_KEY")
            self.client = openai
        elif self.provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    async def generate_study_plan(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized study plan"""
        
        prompt = self._create_study_plan_prompt(performance_data)
        
        try:
            if self.provider == "openai":
                response = await self._call_openai(prompt)
            elif self.provider == "anthropic":
                response = await self._call_anthropic(prompt)
            else:
                response = self._generate_fallback_plan(performance_data)
            
            return {
                "success": True,
                "study_plan": response,
                "provider": self.provider
            }
        except Exception as e:
            print(f"Error generating study plan: {e}")
            return {
                "success": False,
                "study_plan": self._generate_fallback_plan(performance_data),
                "error": str(e)
            }
    
    def _create_study_plan_prompt(self, performance_data: Dict[str, Any]) -> str:
        """Create prompt for LLM"""
        
        topics_performance = performance_data.get("topics_performance", {})
        weak_topics = []
        strong_topics = []
        
        for topic, data in topics_performance.items():
            accuracy = data.get("accuracy", 0)
            if accuracy < 0.6:
                weak_topics.append(f"{topic} ({accuracy:.1%} accuracy)")
            else:
                strong_topics.append(f"{topic} ({accuracy:.1%} accuracy)")
        
        prompt = f"""Create a personalized 3-step GRE study plan:

Performance Summary:
- Ability score: {performance_data.get('final_ability', 0.5):.2f}
- Questions: {performance_data.get('total_questions', 0)}
- Strong areas: {', '.join(strong_topics) if strong_topics else 'None'}
- Weak areas: {', '.join(weak_topics) if weak_topics else 'None'}

Provide a 3-step plan with:
1. Immediate focus (next 2-3 days)
2. Practice strategies (next week)
3. Advanced concepts (next 2 weeks)

Format as JSON with keys: step1, step2, step3 (each with title and description)"""
        
        return prompt
    
    async def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API"""
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert GRE tutor. Respond in JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "step1": {"title": "Foundation", "description": response.choices[0].message.content},
                "step2": {"title": "Practice", "description": "Practice with targeted questions"},
                "step3": {"title": "Advanced", "description": "Move to advanced topics"}
            }
    
    async def _call_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Call Anthropic API"""
        response = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            temperature=0.7,
            system="You are an expert GRE tutor. Always respond in JSON format.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            return json.loads(response.content[0].text)
        except:
            return self._generate_fallback_plan(performance_data)
    
    def _generate_fallback_plan(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate rule-based study plan"""
        return {
            "step1": {
                "title": "Review Fundamentals",
                "description": "Focus on core concepts in weak areas"
            },
            "step2": {
                "title": "Practice Questions",
                "description": "Complete 20-30 practice questions daily"
            },
            "step3": {
                "title": "Full-Length Tests",
                "description": "Take timed practice tests"
            }
        }