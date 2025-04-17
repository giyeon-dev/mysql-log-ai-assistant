# rag_ask.py
import os
from langchain.vectorstores import Chroma # type: ignore
from langchain_google_genai import GoogleGenerativeAIEmbeddings # type: ignore
import google.generativeai as genai  # type: ignore # Gemini API

# Load keys and model
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.0-flash")

# Load embedding and vector store
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vectorstore = Chroma(persist_directory="rag/embedding_store", embedding_function=embedding)

def ask_with_rag(user_question: str, top_k: int = 3) -> str:
    docs = vectorstore.similarity_search(user_question, k=top_k)
    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
You are a MySQL performance tuning expert.

Here is an excerpt from the MySQL tuning guide:
---------------------
{context}
---------------------

Now answer the user's question below based on the guide above.

User Question:
{user_question}
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip() if hasattr(response, "text") else response.parts[0].text.strip()
    except Exception as e:
        return f"❌ Error during response generation: {e}"


# 예시 실행
if __name__ == "__main__":
    question = input("💬 Enter your tuning-related question: ")
    answer = ask_with_rag(question)
    print("\n🤖 Gemini Response:\n")
    print(answer)
