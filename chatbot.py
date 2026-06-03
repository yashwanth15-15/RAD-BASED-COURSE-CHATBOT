def get_answer(db, query, selected_file="All Files"):

    docs = db.similarity_search(query, k=12)

    query_lower = query.lower()

    # ---------- FILTER BY FILE ----------
    if selected_file != "All Files":
        docs = [
            d for d in docs
            if d.metadata.get("source") == selected_file
        ]

    if not docs:
        return {
            "title": "No Data Found",
            "points": ["No relevant content in selected file"],
            "example": "",
            "source": selected_file
        }

    # ---------- CLEAN TEXT ----------
    text = " ".join([d.page_content for d in docs])
    text = text.replace("\n", " ")

    sentences = [
        s.strip()
        for s in text.split(".")
        if len(s.strip()) > 40
    ]

    # ---------- SUMMARY MODE ----------
    if "summary" in query_lower or "about" in query_lower:

        unique = []
        seen = set()

        for s in sentences:
            if s not in seen:
                unique.append(s)
                seen.add(s)

        return {
            "title": "📄 Document Summary",
            "points": unique[:5],
            "example": "",
            "source": docs[0].metadata.get("source", "Unknown")
        }

    # ---------- QA MODE ----------
    scored = []

    for s in sentences:
        score = sum(
            1 for w in query_lower.split()
            if w in s.lower()
        )

        if score > 0:
            scored.append((s, score))

    scored = sorted(scored, key=lambda x: x[1], reverse=True)

    unique = []
    seen = set()

    for s, _ in scored:
        if s not in seen:
            unique.append(s)
            seen.add(s)

    if not unique:
        unique = sentences[:3]

    return {
        "title": unique[0][:120],
        "points": unique[:4],
        "example": "",
        "source": docs[0].metadata.get("source", "Unknown")
    }
