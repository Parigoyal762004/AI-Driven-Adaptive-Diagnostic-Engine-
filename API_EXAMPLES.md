# API Usage Examples

This document provides practical examples of using the Adaptive Testing Engine API.

## Prerequisites

```bash
# Start the server
uvicorn app.main:app --reload

# Or use the run script
./run.sh
```

Base URL: `http://localhost:8000`

## Example 1: Complete Test Session

### Step 1: Create a Session

```bash
curl -X POST "http://localhost:8000/api/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "student_001",
    "user_name": "Alice Johnson",
    "test_type": "GRE",
    "max_questions": 10
  }'
```

**Response:**
```json
{
  "session_id": "sess_a1b2c3d4e5f6",
  "message": "Session created successfully. Ready to start adaptive testing.",
  "initial_ability": 0.0,
  "max_questions": 10
}
```

### Step 2: Get First Question

```bash
curl "http://localhost:8000/api/sessions/sess_a1b2c3d4e5f6/next-question"
```

**Response:**
```json
{
  "question_id": "507f1f77bcf86cd799439011",
  "question_text": "What is 15% of 200?",
  "options": ["20", "25", "30", "35"],
  "topic": "Arithmetic",
  "estimated_time_seconds": 60,
  "question_number": 1,
  "total_questions": 10
}
```

### Step 3: Submit Answer

```bash
curl -X POST "http://localhost:8000/api/sessions/sess_a1b2c3d4e5f6/answers" \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": "507f1f77bcf86cd799439011",
    "user_answer": "30",
    "time_spent_seconds": 45
  }'
```

**Response:**
```json
{
  "is_correct": true,
  "correct_answer": "30",
  "explanation": "15% of 200 = 0.15 × 200 = 30",
  "updated_ability": 0.25,
  "standard_error": 0.85,
  "questions_remaining": 9,
  "session_complete": false
}
```

### Step 4: Continue Testing

Repeat steps 2-3 until `session_complete` is `true`.

### Step 5: Get Learning Plan

```bash
curl "http://localhost:8000/api/sessions/sess_a1b2c3d4e5f6/learning-plan"
```

**Response:**
```json
{
  "session_id": "sess_a1b2c3d4e5f6",
  "final_ability": 0.45,
  "accuracy": 0.7,
  "strengths": ["Arithmetic", "Algebra"],
  "weaknesses": ["Geometry", "Probability"],
  "recommendations": [
    "Focus on geometry fundamentals, especially area and perimeter calculations",
    "Practice probability problems with real-world scenarios",
    "Review coordinate geometry and graphing"
  ],
  "study_plan": "Week 1: Review geometry basics...\nWeek 2: Practice probability...",
  "estimated_study_hours": 15
}
```

## Example 2: Python Client

```python
import requests

BASE_URL = "http://localhost:8000"

class AdaptiveTestClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session_id = None
    
    def create_session(self, user_id, user_name="", max_questions=10):
        """Create a new test session."""
        response = requests.post(
            f"{self.base_url}/api/sessions",
            json={
                "user_id": user_id,
                "user_name": user_name,
                "test_type": "GRE",
                "max_questions": max_questions
            }
        )
        data = response.json()
        self.session_id = data["session_id"]
        return data
    
    def get_next_question(self):
        """Get the next adaptive question."""
        response = requests.get(
            f"{self.base_url}/api/sessions/{self.session_id}/next-question"
        )
        return response.json()
    
    def submit_answer(self, question_id, user_answer, time_spent=None):
        """Submit an answer."""
        response = requests.post(
            f"{self.base_url}/api/sessions/{self.session_id}/answers",
            json={
                "question_id": question_id,
                "user_answer": user_answer,
                "time_spent_seconds": time_spent
            }
        )
        return response.json()
    
    def get_learning_plan(self):
        """Get personalized learning plan."""
        response = requests.get(
            f"{self.base_url}/api/sessions/{self.session_id}/learning-plan"
        )
        return response.json()
    
    def run_full_test(self, user_id, answers_callback):
        """
        Run a complete adaptive test.
        
        Args:
            user_id: User identifier
            answers_callback: Function that takes a question and returns an answer
        """
        # Create session
        session = self.create_session(user_id)
        print(f"Session created: {session['session_id']}")
        
        # Answer questions
        while True:
            # Get question
            question = self.get_next_question()
            print(f"\nQuestion {question['question_number']}/{question['total_questions']}")
            print(f"Topic: {question['topic']}")
            print(f"Q: {question['question_text']}")
            
            # Get answer from callback
            user_answer = answers_callback(question)
            
            # Submit answer
            result = self.submit_answer(
                question['question_id'],
                user_answer
            )
            
            print(f"Correct: {result['is_correct']}")
            print(f"Ability: {result['updated_ability']:.2f} (±{result['standard_error']:.2f})")
            
            if result['session_complete']:
                print("\nTest completed!")
                break
        
        # Get learning plan
        plan = self.get_learning_plan()
        print(f"\nFinal Ability: {plan['final_ability']:.2f}")
        print(f"Accuracy: {plan['accuracy']:.1%}")
        print(f"Strengths: {', '.join(plan['strengths'])}")
        print(f"Weaknesses: {', '.join(plan['weaknesses'])}")
        
        return plan

# Usage example
if __name__ == "__main__":
    client = AdaptiveTestClient()
    
    # Simple callback that always picks first option (for demo)
    def answer_callback(question):
        return question['options'][0]
    
    # Run test
    plan = client.run_full_test("demo_user", answer_callback)
```

## Example 3: JavaScript/TypeScript Client

```typescript
interface Question {
  question_id: string;
  question_text: string;
  options: string[];
  topic: string;
  question_number: number;
  total_questions: number;
}

interface AnswerResult {
  is_correct: boolean;
  correct_answer: string;
  updated_ability: number;
  standard_error: number;
  questions_remaining: number;
  session_complete: boolean;
}

class AdaptiveTestClient {
  private baseUrl: string;
  private sessionId: string | null = null;

  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async createSession(userId: string, maxQuestions = 10) {
    const response = await fetch(`${this.baseUrl}/api/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        test_type: 'GRE',
        max_questions: maxQuestions
      })
    });
    const data = await response.json();
    this.sessionId = data.session_id;
    return data;
  }

  async getNextQuestion(): Promise<Question> {
    const response = await fetch(
      `${this.baseUrl}/api/sessions/${this.sessionId}/next-question`
    );
    return response.json();
  }

  async submitAnswer(
    questionId: string,
    userAnswer: string,
    timeSpent?: number
  ): Promise<AnswerResult> {
    const response = await fetch(
      `${this.baseUrl}/api/sessions/${this.sessionId}/answers`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question_id: questionId,
          user_answer: userAnswer,
          time_spent_seconds: timeSpent
        })
      }
    );
    return response.json();
  }

  async getLearningPlan() {
    const response = await fetch(
      `${this.baseUrl}/api/sessions/${this.sessionId}/learning-plan`
    );
    return response.json();
  }
}

// Usage
const client = new AdaptiveTestClient();
await client.createSession('user_123');

const question = await client.getNextQuestion();
console.log(question.question_text);

const result = await client.submitAnswer(question.question_id, 'x = 5');
console.log(`Correct: ${result.is_correct}`);
console.log(`New ability: ${result.updated_ability}`);
```

## Example 4: Health Check & Monitoring

```bash
# Check API health
curl "http://localhost:8000/api/health"

# Get system statistics
curl "http://localhost:8000/api/stats"

# Get session details
curl "http://localhost:8000/api/sessions/sess_a1b2c3d4e5f6"

# Get session history
curl "http://localhost:8000/api/sessions/sess_a1b2c3d4e5f6/history"
```

## Error Handling Examples

### Session Not Found
```bash
curl "http://localhost:8000/api/sessions/invalid_id/next-question"
```
Response (404):
```json
{
  "error": "SessionNotFoundException",
  "detail": "Session not found: invalid_id",
  "path": "/api/sessions/invalid_id/next-question"
}
```

### Invalid Answer
```bash
curl -X POST "http://localhost:8000/api/sessions/sess_123/answers" \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": "q123",
    "user_answer": "invalid option"
  }'
```
Response (400):
```json
{
  "error": "InvalidAnswerException",
  "detail": "Answer must be one of: x = 3, x = 5, x = 7, x = 10",
  "path": "/api/sessions/sess_123/answers"
}
```

## Best Practices

1. **Store session IDs**: Save the session_id for continued access
2. **Handle errors**: Check HTTP status codes and error responses
3. **Respect rate limits**: Don't spam the API
4. **Track timing**: Submit `time_spent_seconds` for better analytics
5. **Complete sessions**: Always get the learning plan after completion
6. **Monitor ability**: Track `standard_error` to see estimate confidence

## Rate Limiting

Current limits:
- No hard rate limits in development
- Production deployment should implement rate limiting
- Recommended: 100 requests/minute per IP

## Support

For issues or questions:
- Check the main README.md
- Review API docs at `/docs`
- Open an issue on GitHub
