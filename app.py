import streamlit as st
from file_processor import process_files
from vector_store import create_vector_store
from chatbot import get_answer

st.set_page_config(page_title="Course AI", layout="wide")

# ---------- SESSION ----------
if "db" not in st.session_state:
    st.session_state.db = None

if "chat" not in st.session_state:
    st.session_state.chat = []

if "selected_file" not in st.session_state:
    st.session_state.selected_file = "All Files"

# ---------- SIDEBAR ----------
with st.sidebar:
    st.title("📚 Course Assistant")

    files = st.file_uploader(
        "Upload Files",
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
            with st.spinner("Processing..."):
                docs = process_files(files)
                st.session_state.db = create_vector_store(docs)
                st.session_state.chat = []
            st.success("Ready!")

# ---------- HEADER ----------
st.markdown("""
<h1 style='text-align:center;
background: linear-gradient(to right, #22c55e, #3b82f6);
-webkit-background-clip: text;
color: transparent;'>
🚀 Smart Course Assistant
</h1>
""", unsafe_allow_html=True)

# ---------- CHAT DISPLAY ----------
for role, msg in st.session_state.chat:

    if role == "user":
        st.markdown(f"""
        <div style="
            text-align:right;
            background:#2563eb;
            color:white;
            padding:10px;
            border-radius:10px;
            margin:10px;">
            {msg}
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div style="
            background:#111827;
            padding:15px;
            border-radius:10px;
            margin:10px;
            border-left:4px solid #22c55e;">
            
            <b>{msg['title']}</b><br>
            <small>📄 {msg['source']}</small>
        """, unsafe_allow_html=True)

        for p in msg["points"]:
            st.markdown(f"• {p}")

        st.markdown("</div>", unsafe_allow_html=True)

# ---------- INPUT ----------
query = st.chat_input("Ask your question...")

if query:
    if st.session_state.db is None:
        st.warning("Upload and process files first")
    else:
        st.session_state.chat.append(("user", query))

        with st.spinner("Thinking..."):
            answer = get_answer(
                st.session_state.db,
                query,
                st.session_state.selected_file
            )

        st.session_state.chat.append(("bot", answer))
        st.rerun()
