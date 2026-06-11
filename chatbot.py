from ollama import chat


def get_answer(db, query, selected_file="All Files"):

    try:
        # Retrieve fewer chunks for speed
        docs = db.similarity_search(query, k=3)

        # Filter selected file
        if selected_file != "All Files":
            docs = [
                d for d in docs
                if d.metadata.get("source") == selected_file
            ]

        # No results
        if not docs:
            return {
                "title": "No Data Found",
                "points": ["No relevant content found in the selected document."],
                "source": selected_file
            }

        # Build context
        context = "\n\n".join(
            [d.page_content for d in docs]
        )

        prompt = f"""
You are a Smart Course Assistant.

Answer ONLY using the document content provided.

Rules:
- Give direct answers.
- For summaries, use bullet points.
- For date questions, list dates clearly.
- For steps/tasks, use numbered points.
- Do not mention "context".
- Do not say "the document does not reference".
- If the answer is unavailable, say:
  "Not found in the document."

Document Content:
{context}

Question:
{query}
"""

        response = chat(
            model="qwen2.5:3b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = response["message"]["content"].strip()

        points = [
            line.strip("-• ")
            for line in answer.split("\n")
            if line.strip()
        ]

        return {
            "title": "Answer",
            "points": points,
            "source": docs[0].metadata.get("source", "Unknown")
        }

    except Exception as e:

        return {
            "title": "Error",
            "points": [str(e)],
            "source": "System"
        }