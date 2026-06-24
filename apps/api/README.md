# A Step Forward API

FastAPI gateway for the A Step Forward learning center.

## Assessment API

### GET /v1/assessment

Generate 3-5 assessment questions for a topic.

**Query parameters:**

- `topic` (string, required): The topic to generate questions for
- `level` (string, required): Difficulty level - `beginner`, `intermediate`, or `advanced`

**Example:**

```bash
curl "https://asf-api-q566.onrender.com/v1/assessment?topic=derivatives&level=beginner" \
  -H "Authorization: Bearer <token>"
```

**Response:**

```json
[
  {
    "id": "q1",
    "question": "What does a derivative represent geometrically?",
    "type": "multiple_choice",
    "options": ["Slope of tangent", "Area under curve", "Length of curve", "Volume"],
    "answer_key": "Slope of tangent"
  }
]
```

### POST /v1/grade

Evaluate a learner's answer to a question.

**Request body:**

```json
{"question": "What is the derivative of x²?", "answer": "2x"}
```

**Example:**

```bash
curl -X POST "https://asf-api-q566.onrender.com/v1/grade" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the derivative of x²?", "answer": "2x"}'
```

**Response:**

```json
{"correct": true, "score": 1.0, "feedback": "Correct! The power rule gives d/dx(x²) = 2x."}
```
