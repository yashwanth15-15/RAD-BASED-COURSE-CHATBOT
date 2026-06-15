import ollama

def evaluate_answer(db, student_answer):

    docs = db.similarity_search(
        student_answer,
        k=10
    )

    context = "\n".join(
        [doc.page_content for doc in docs]
    )

    prompt = f"""
You are an expert Assignment Evaluator.

Use ONLY the provided course material.

Course Material:
{context}

Student Answer:
{student_answer}

Evaluate strictly based on the course material.

Provide:

Score: X/10

Strengths:
- ...

Missing Concepts:
- ...

Suggestions:
- ...

Be objective and concise.
"""

    response = ollama.chat(
        model="qwen2.5:3b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response["message"]["content"]