import streamlit as st
from file_processor import process_files
from vector_store import create_vector_store
from chatbot import get_answer
from quiz_generator import generate_quiz
# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Smart Course Assistant",
    page_icon="🚀",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.stButton > button {
    width: 100%;
    height: 50px;
    border-radius: 15px;
    font-size: 16px;
    font-weight: bold;
}

.block-container {
    padding-top: 1rem;
}

.metric-card {
    background: #1e293b;
    padding: 15px;
    border-radius: 15px;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "db" not in st.session_state:
    st.session_state.db = None

if "chat" not in st.session_state:
    st.session_state.chat = []

if "selected_file" not in st.session_state:
    st.session_state.selected_file = "All Files"

if "doc_count" not in st.session_state:
    st.session_state.doc_count = 0

if "quiz" not in st.session_state:
    st.session_state.quiz = []

if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0

if "score" not in st.session_state:
    st.session_state.score = 0
if "answered" not in st.session_state:
    st.session_state.answered = False
if "feedback" not in st.session_state:
    st.session_state.feedback = ""

if "explanation" not in st.session_state:
    st.session_state.explanation = ""
# ---------------- SIDEBAR ----------------
with st.sidebar:

    st.markdown("## 📚 Course Assistant")

    files = st.file_uploader(
        "Upload PDF / PPT / TXT",
        type=["pdf", "pptx", "txt"],
        accept_multiple_files=True
    )

    if files:

        names = [f.name for f in files]

        st.session_state.selected_file = st.selectbox(
            "Select File",
            ["All Files"] + names
        )

        if st.button("⚡ Process Documents"):

            with st.spinner("Processing documents..."):

                docs = process_files(files)

                st.session_state.doc_count = len(docs)

                st.session_state.db = create_vector_store(docs)

                
                
                st.session_state.quiz = []
                st.session_state.quiz_index = 0
                st.session_state.score = 0
                st.session_state.answered = False
                st.session_state.feedback = ""
                st.session_state.explanation = ""
                st.session_state.chat = []

            st.success("✅ Ready!")

# ---------------- HEADER ----------------
st.markdown("""
<div style="
padding:25px;
border-radius:20px;
background:linear-gradient(135deg,#2563eb,#7c3aed);
color:white;
text-align:center;
margin-bottom:20px;
">
<h1>🚀 Smart Course Assistant</h1>
<p>Local AI Powered by Qwen + FAISS + Ollama</p>
</div>
""", unsafe_allow_html=True)

# ---------------- STATS ----------------
if st.session_state.db is not None:

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("📄 Files", len(files) if files else 0)

    with c2:
        st.metric("📚 Chunks", st.session_state.doc_count)

    with c3:
        st.metric("🤖 Model", "Qwen2.5:3B")
# ---------------- QUIZ ----------------

if st.session_state.quiz:

    total = len(st.session_state.quiz)
    current = st.session_state.quiz_index

    if current < total:
        
        q = st.session_state.quiz[current]

        st.subheader(
            f"🎯 Question {current + 1} of {total}"
        )

        st.progress(
            (current + 1) / total
        )

        st.metric(
            "🏆 Score",
            f"{st.session_state.score}/{total}"
        )

        st.write(q["question"])

        choice = st.radio(
            "Choose your answer",
            q["options"],
            key=f"quiz_{current}"
        )

        if st.button(
            "Submit Answer",
            key=f"submit_{current}"
        ):

            if not st.session_state.answered:

                st.session_state.answered = True

                if choice == q["answer"]:

                    st.session_state.score += 1
                    st.session_state.feedback = "✅ Correct!"

                else:

                    st.session_state.feedback = (
                        f"❌ Wrong! Correct Answer: {q['answer']}"
                )

                st.session_state.explanation = q["explanation"]

        if st.session_state.answered:

                if "✅" in st.session_state.feedback:
                    st.success(st.session_state.feedback)
                else:
                    st.error(st.session_state.feedback)
                st.info(st.session_state.explanation)

                if st.button(
                    "Next Question",
                    key=f"next_{current}"
                ):

                    st.session_state.quiz_index += 1
                    st.session_state.answered = False
                    st.session_state.feedback = ""
                    st.session_state.explanation = ""

                    st.rerun()
    else:

        st.balloons()

        st.success(
            f"🎉 Quiz Completed!\n\n"
            f"Final Score: "
            f"{st.session_state.score}/{total}"
        )

        if st.button("🔄 Restart Quiz"):

            st.session_state.quiz = []
            st.session_state.quiz_index = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.session_state.feedback = ""
            st.session_state.explanation = ""

            st.rerun()

# ---------------- WELCOME ----------------
if len(st.session_state.chat) == 0 and not st.session_state.quiz:

    st.info("""
👋 Welcome to Smart Course Assistant

✨ Upload PDF, PPT, TXT files

📚 Ask questions from your documents

📝 Generate summaries

🎯 Extract important information

⚡ Powered by Local AI
""")

# ---------------- CHAT HISTORY ----------------
for role, msg in st.session_state.chat:

    if role == "user":

        with st.chat_message("user"):
            st.write(msg)

    else:

        with st.chat_message("assistant"):

            st.markdown(f"### {msg['title']}")

            st.caption(f"📄 Source: {msg['source']}")

            for point in msg["points"]:
                st.write(point)

# ---------------- CHAT INPUT ----------------

query = st.chat_input("Ask anything about your document...")

if query:

    if st.session_state.db is None:

        st.warning("⚠️ Upload and process documents first")

    else:

        query_lower = query.lower()

        quiz_keywords = [
            "quiz",
            "mcq",
            "generate quiz",
            "create quiz",
            "quiz me",
            "test me"
        ]

        if any(
            word in query_lower
            for word in quiz_keywords
        ):

            with st.spinner("Generating Quiz..."):

                st.session_state.quiz = generate_quiz(
                    st.session_state.db
                )

                st.session_state.quiz_index = 0
                st.session_state.score = 0
                st.session_state.answered = False
                st.session_state.feedback = ""
                st.session_state.explanation = ""
                st.session_state.chat = []
            st.rerun()

        else:

            st.session_state.chat.append(
                ("user", query)
            )

            with st.spinner("🤔 Thinking..."):

                answer = get_answer(
                    st.session_state.db,
                    query,
                    st.session_state.selected_file
                )

            st.session_state.chat.append(
                ("bot", answer)
            )

            st.rerun()