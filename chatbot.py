from ollama import chat

def get_answer(db, query, selected_file="All Files"):

    try:

        query_lower = query.lower()

        # Multi-document summary
        if "all uploaded documents" in query_lower or \
        "summarize all" in query_lower:

            all_docs = list(db.docstore._dict.values())

            if not all_docs:
                return {
                    "title": "No Data Found",
                    "points": ["No documents indexed."],
                    "source": "System"
                }

            
            from collections import defaultdict

            grouped_docs = defaultdict(list)

            for doc in all_docs:
                source = doc.metadata.get("source", "Unknown")
                grouped_docs[source].append(doc)

            docs = []

            for source_docs in grouped_docs.values():
                docs.extend(source_docs[:5])

        # Comparison / relationship questions
        elif any(
            word in query_lower
            for word in [
                "compare",
                "difference",
                "relationship",
                "common concepts",
                "differences",
                "similarities",
                "similar",
                "contrast"
            ]
        ):
            docs = db.similarity_search(
                query,
                k=8
            )

        # Normal questions
        else:

            docs_with_scores = db.similarity_search_with_score(
                query,
                k=4
            )

            docs = [
                doc for doc, score in docs_with_scores
                if score < 1.5
            ]

            if not docs:
                return {
                    "title": "Not Found",
                    "points": [
                        "Not found in the uploaded documents."
                    ],
                    "source": selected_file
                }
        # Skip file filtering for multi-document queries
        is_multi_doc = (
            "all uploaded documents" in query_lower or
            "summarize all" in query_lower or
            any(
                word in query_lower
                for word in [
                    "compare",
                    "difference",
                    "relationship",
                    "common concepts",
                    "differences",
                    "similarities",
                    "similar",
                    "contrast"
                ]
            )
        )

        if selected_file != "All Files" and not is_multi_doc:

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
            [d.page_content[:300] for d in docs[:20]]
        )

        # Collect all sources
        sources = sorted(list(
            set(
                    d.metadata.get(
                        "source",
                        "Unknown"
                    )
                    for d in docs
                    if hasattr(d, "metadata")
            )
        ))
        title = (
            "Answer"
            if len(sources) == 1
            else "Multi-Document Answer"
        )
        prompt = f"""
        You are an Agentic Course Assistant.

        Use information from ALL retrieved documents.

        Question:
        {query}

        Documents:
        {context}

        Instructions:
        - Use ONLY the information present in Documents.
        - Do NOT use external knowledge.
        - Do NOT guess.
        - If the answer is not explicitly present in Documents,
        reply exactly:
        "Not found in the uploaded documents."
        - Answer using only the retrieved document content.
        - Combine information from multiple documents when relevant.
        - Give one clear and concise answer.
        - For "What is..." questions, provide the definition first.
        - Mention examples or applications only after the definition.
        - Keep definition answers to 2-4 sentences.
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

        if not answer.strip():
            answer = "No answer generated."

        points = [
            line.strip("-• ")
            for line in answer.split("\n")
            if line.strip()
        ]

        return {
            "title": title,
            "points": points,
            "source": ", ".join(sources)
        }

    except Exception as e:

        return {
            "title": "Error",
            "points": [str(e)],
            "source": "System"
        }