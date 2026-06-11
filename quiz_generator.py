from ollama import chat
import json
import re


def generate_quiz(db):

    docs = db.similarity_search(
        "important concepts course topics",
        k=12
    )
    if not docs:
        return []

    context = "\n\n".join(
        [d.page_content[:1000] for d in docs]
)

    context = context[:8000]

    prompt = f"""
You are an expert quiz generator.

Create EXACTLY 5 MCQs from the document.

Each MCQ must:
- Test understanding, not memorization
- Have 4 realistic options
- Have only one correct answer
- Include a short explanation
Return ONLY valid JSON.

Do NOT use markdown.
Do NOT use ```json.
Do NOT add explanations before or after the JSON.
The response must start with [ and end with ].
Format:

[
  {{
    "question":"...",
    "options":[
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "answer":"Option B",
    "explanation":"..."
  }}
]

Rules:
- Exactly 5 questions
- 4 options each
- One correct answer
- Include explanation
- Return JSON only
- No markdown
- No extra text

Document:
{context}
"""

    response = chat(
        model="qwen2.5:3b",
        messages=[
        {
            "role": "user",
            "content": prompt
        }
     ],
     options={
        "temperature": 0.7
     }
    )

    content = response["message"]["content"]

    try:
        match = re.search(
            r"\[.*\]",
            content,
            re.DOTALL
        )

        if match:
            return json.loads(match.group())
    except Exception as e:
        print("Quiz error:", e)

    return [
        {
            "question": "Quiz generation failed. Try again.",
            "options": ["Retry", "Retry", "Retry", "Retry"],
            "answer": "Retry",
            "explanation": "The model returned invalid JSON."
        }
    ]