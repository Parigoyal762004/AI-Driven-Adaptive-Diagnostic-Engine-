"""
AI-powered learning plan generator using LLM (OpenAI or Anthropic).
"""
import json
from typing import Optional
from collections import Counter
import httpx
from app.config import settings
from app.models.session import UserSessionModel
from app.utils.exceptions import AIServiceException


class LearningPlanGenerator:
    """
    Generates personalized learning plans using AI based on test performance.
    """
    
    def __init__(self):
        self.ai_provider = settings.ai_provider
        self.openai_api_key = settings.openai_api_key
        self.anthropic_api_key = settings.anthropic_api_key
        self.timeout = 30.0
    
    async def generate_plan(
        self,
        session: UserSessionModel,
        questions_map: dict[str, dict]
    ) -> dict:
        """
        Generate comprehensive learning plan from session data.
        
        Args:
            session: Completed user session
            questions_map: Map of question_id to question details
        
        Returns:
            Dictionary with learning plan components
        """
        # Analyze performance
        analysis = self._analyze_performance(session, questions_map)
        
        # Generate AI recommendations
        try:
            ai_recommendations = await self._generate_ai_recommendations(
                session, analysis, questions_map
            )
        except Exception as e:
            print(f"AI generation failed: {e}, using fallback")
            ai_recommendations = self._fallback_recommendations(analysis)
        
        return {
            "session_id": session.session_id,
            "final_ability": session.current_ability,
            "accuracy": session.accuracy,
            "strengths": analysis["strengths"],
            "weaknesses": analysis["weaknesses"],
            "recommendations": ai_recommendations["recommendations"],
            "study_plan": ai_recommendations["study_plan"],
            "estimated_study_hours": ai_recommendations["estimated_hours"]
        }
    
    def _analyze_performance(
        self,
        session: UserSessionModel,
        questions_map: dict[str, dict]
    ) -> dict:
        """Analyze session performance to identify strengths and weaknesses."""
        topic_performance = {}
        difficulty_performance = {"easy": [], "medium": [], "hard": []}
        
        for response in session.responses:
            question = questions_map.get(response.question_id, {})
            topic = question.get("topic", "Unknown")
            difficulty = question.get("difficulty", 0.5)
            
            # Track by topic
            if topic not in topic_performance:
                topic_performance[topic] = {"correct": 0, "total": 0}
            
            topic_performance[topic]["total"] += 1
            if response.is_correct:
                topic_performance[topic]["correct"] += 1
            
            # Track by difficulty
            if difficulty < 0.4:
                difficulty_performance["easy"].append(response.is_correct)
            elif difficulty < 0.7:
                difficulty_performance["medium"].append(response.is_correct)
            else:
                difficulty_performance["hard"].append(response.is_correct)
        
        # Identify strengths (>70% accuracy)
        strengths = [
            topic for topic, perf in topic_performance.items()
            if perf["total"] > 0 and (perf["correct"] / perf["total"]) >= 0.7
        ]
        
        # Identify weaknesses (<50% accuracy)
        weaknesses = [
            topic for topic, perf in topic_performance.items()
            if perf["total"] > 0 and (perf["correct"] / perf["total"]) < 0.5
        ]
        
        return {
            "topic_performance": topic_performance,
            "difficulty_performance": difficulty_performance,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "total_questions": len(session.responses),
            "accuracy": session.accuracy
        }
    
    async def _generate_ai_recommendations(
        self,
        session: UserSessionModel,
        analysis: dict,
        questions_map: dict[str, dict]
    ) -> dict:
        """Generate recommendations using AI (OpenAI or Anthropic)."""
        
        prompt = self._build_prompt(session, analysis, questions_map)
        
        if self.ai_provider == "openai":
            return await self._call_openai(prompt)
        else:
            return await self._call_anthropic(prompt)
    
    def _build_prompt(
        self,
        session: UserSessionModel,
        analysis: dict,
        questions_map: dict[str, dict]
    ) -> str:
        """Build comprehensive prompt for AI."""
        
        # Get question details for context
        questions_answered = []
        for resp in session.responses[:5]:  # Sample first 5
            q = questions_map.get(resp.question_id, {})
            questions_answered.append({
                "topic": q.get("topic", "Unknown"),
                "difficulty": q.get("difficulty", 0),
                "correct": resp.is_correct
            })
        
        prompt = f"""You are an expert GRE tutor. Analyze this student's performance and create a personalized study plan.

STUDENT PERFORMANCE:
- Final Ability Score: {session.current_ability:.2f} (range: -3 to +3)
- Overall Accuracy: {analysis['accuracy']:.1%}
- Questions Answered: {analysis['total_questions']}
- Strengths: {', '.join(analysis['strengths']) if analysis['strengths'] else 'None identified'}
- Weaknesses: {', '.join(analysis['weaknesses']) if analysis['weaknesses'] else 'None identified'}

TOPIC BREAKDOWN:
{json.dumps(analysis['topic_performance'], indent=2)}

SAMPLE QUESTIONS:
{json.dumps(questions_answered, indent=2)}

Please provide:
1. Specific, actionable recommendations (3-5 items)
2. A week-by-week study plan (2-4 weeks)
3. Estimated study hours needed

Format your response as JSON:
{{
  "recommendations": ["recommendation 1", "recommendation 2", ...],
  "study_plan": "Week 1: ...\nWeek 2: ...",
  "estimated_hours": 15
}}"""
        
        return prompt
    
    async def _call_openai(self, prompt: str) -> dict:
        """Call OpenAI API for recommendations."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4-turbo-preview",
                        "messages": [
                            {"role": "system", "content": "You are an expert GRE tutor who provides structured, actionable study advice."},
                            {"role": "user", "content": prompt}
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }
                )
                
                if response.status_code != 200:
                    raise AIServiceException(f"OpenAI API error: {response.status_code}")
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return json.loads(content)
                
            except (httpx.TimeoutException, httpx.RequestError) as e:
                raise AIServiceException(f"OpenAI API request failed: {e}")
            except (json.JSONDecodeError, KeyError) as e:
                raise AIServiceException(f"Failed to parse OpenAI response: {e}")
    
    async def _call_anthropic(self, prompt: str) -> dict:
        """Call Anthropic API for recommendations."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.anthropic_api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "claude-3-5-sonnet-20241022",
                        "max_tokens": 1024,
                        "messages": [
                            {"role": "user", "content": prompt + "\n\nRespond only with valid JSON."}
                        ]
                    }
                )
                
                if response.status_code != 200:
                    raise AIServiceException(f"Anthropic API error: {response.status_code}")
                
                result = response.json()
                content = result["content"][0]["text"]
                
                # Extract JSON from response
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                return json.loads(content)
                
            except (httpx.TimeoutException, httpx.RequestError) as e:
                raise AIServiceException(f"Anthropic API request failed: {e}")
            except (json.JSONDecodeError, KeyError) as e:
                raise AIServiceException(f"Failed to parse Anthropic response: {e}")
    
    def _fallback_recommendations(self, analysis: dict) -> dict:
        """Generate basic recommendations without AI as fallback."""
        recommendations = []
        
        if analysis["weaknesses"]:
            recommendations.append(
                f"Focus on strengthening: {', '.join(analysis['weaknesses'])}"
            )
        else:
            recommendations.append("Continue practicing across all topics to maintain skills")
        
        if analysis["accuracy"] < 0.6:
            recommendations.append("Review fundamental concepts before tackling advanced problems")
            study_hours = 20
        elif analysis["accuracy"] < 0.8:
            recommendations.append("Practice medium-difficulty problems to build confidence")
            study_hours = 15
        else:
            recommendations.append("Challenge yourself with advanced problems")
            study_hours = 10
        
        recommendations.append("Take regular practice tests to track progress")
        
        study_plan = f"""Week 1-2: Review weak areas ({', '.join(analysis['weaknesses']) if analysis['weaknesses'] else 'all topics'})
Week 3: Practice problems at increasing difficulty
Week 4: Full-length practice tests and review"""
        
        return {
            "recommendations": recommendations,
            "study_plan": study_plan,
            "estimated_hours": study_hours
        }
