import streamlit as st # type: ignore
from log_parser import parse_log_file
from llm import analyze_log_chunks
from llm import build_prompt_with_log
from rag.rag_ask import ask_with_rag
import os
from dotenv import load_dotenv # type: ignore
import google.generativeai as genai # type: ignore

# 1. Load Gemini API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

# 2. Set up Gemini model
model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")


# Set up the Streamlit app
st.set_page_config(page_title="MySQL Log AI Assistant", layout="wide")

# App title
st.title("MySQL Log AI Assistant")
st.write("""
Upload your MySQL slow query log and let AI analyze it for performance issues,
bottlenecks, and optimization suggestions
         """)

# Upload log file
uploaded_file = st.file_uploader("📂 Upload your MySQL slow query log (.log or .txt)", type=["log", "txt"])

if uploaded_file is not None:
    # Read the file content as string
    file_content = uploaded_file.read().decode("utf-8")

    # Parce and chunk the log
    chunks = parse_log_file(file_content)

    st.info(f"Parsed into {len(chunks)} chunk(s) for analysis.")

    # Analyze using Gemini LLM
    with st.spinner("Analyzing log chunks using AI..."):
        results = analyze_log_chunks(chunks)
    
    # Display results
    st.subheader("AI-Generated Log Analysis")
    
    for i, result in enumerate(results, 1):
        with st.expander(f"📦 Chunk {i} - Risk Score: {result.get('score', 0)}/100", expanded=True):
            st.markdown("---")

            st.markdown("### 🧠 Summary")
            st.markdown(result.get("summary", "N/A"))

            st.markdown("### ❌ Issue")
            st.markdown(result.get("issue", "N/A"))

            st.markdown("### 💡 Suggestion")
            st.markdown(result.get("suggestion", "N/A"))

            st.markdown("### 🔧 SQL Recommendations")
            sql_recs = result.get("sql_recommendation", [])
            for sql in sql_recs:
                st.code(sql, language="sql")

            st.markdown("---")
            st.metric(label="🔥 Risk Score", value=f"{result.get('score', 0)}/100")



# ===== USER CUSTOM PROMPT SECTION =====

st.subheader("💬 Ask AI About Your Log")

custom_question = st.text_area("Enter your question for the AI")

if custom_question:
    tab1, tab2 = st.tabs(["🤖 Analyze My Question", "📘 Ask with Tuning Guide"])

    with tab1:
        if st.button("Run Log-Based Analysis"):
            with st.spinner("Analyzing your prompt with log..."):
                full_log = "\n".join(chunks)
                prompt = build_prompt_with_log(custom_question, full_log)
                try:
                    response = model.generate_content(prompt)
                    content = response.text.strip() if response.text else response.parts[0].text.strip()
                    st.markdown("### 🤖 AI Response (Log-Based)")
                    st.write(content)
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab2:
        if st.button("Run Tuning Guide Analysis"):
            with st.spinner("Retrieving tuning guide info..."):
                answer = ask_with_rag(custom_question)
                st.markdown("### 📘 AI Response with Tuning Guide (RAG)")
                st.write(answer)
