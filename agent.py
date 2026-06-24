def detect_intent(query):

    query_lower = query.lower()

    # Assignment Evaluation
    if (
        "question:" in query_lower
        and "answer:" in query_lower
    ):
        return "evaluation"

    # Quiz Generation
    if any(
        word in query_lower
        for word in [
            "quiz",
            "mcq",
            "generate quiz",
            "create quiz",
            "test me",
            "quiz me"
        ]
    ):
        return "quiz"

    # Normal Chat
    return "chat"