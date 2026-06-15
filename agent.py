def detect_intent(query):

    query = query.lower()

    # Assignment Evaluation
    if (
        "question:" in query
        and "answer:" in query
    ):
        return "evaluation"

    # Quiz Generation
    if any(
        word in query
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