from ollama import chat

def get_answer(db, query, selected_file="All Files"):

    try:

        # Retrieve more chunks from all documents
        docs = db.similarity_search(
            query,
            k=8
        )

        # Filter if a specific file is selected
        if selected_file != "All Files":

            docs = [
                d for d in docs
                if d.metadata.get("source") == selected_file
            ]

        if not docs:

            return {
                "title": "No Data Found",
                "points": [
                    "No relevant content found."
                ],
                "source": selected_file
            }

        context = "\n\n".join(
            [d.page_content for d in docs]
        )

        # Collect all sources
        sources = list(
            set(
                [
                    d.metadata.get(
                        "source",
                        "Unknown"
                    )
                    for d in docs
                ]
            )
        )

        prompt = f"""
You are an Agentic Course Assistant.

Use information from ALL retrieved documents.

Question:
{query}

Documents:
{context}

Instructions:
- Combine information from multiple documents.
- Give one unified answer.
- Use bullet points when needed.
- Mention relationships between concepts.
- If information comes from different documents, merge it logically.
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

        answer = response["message"]["content"]

        points = [
            line.strip("-• ")
            for line in answer.split("\n")
            if line.strip()
        ]

        return {
            "title": "Multi-Document Answer",
            "points": points,
            "source": ", ".join(sources)
        }

    except Exception as e:

        return {
            "title": "Error",
            "points": [str(e)],
            "source": "System"
        }