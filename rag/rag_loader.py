import os
from langchain.text_splitter import CharacterTextSplitter # type: ignore
from langchain_community.vectorstores import Chroma # type: ignore
from langchain_google_genai  import GoogleGenerativeAIEmbeddings # type: ignore

# Load API key
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

# 1. Load raw text
with open("MYSQL8.4_tuning_guide.txt", "r") as f:
    raw_text = f.read()

# 2. Split into chunks
splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_text(raw_text)

# 3. Generate embeddings
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# 4. Save to Chroma vector store
vectorstore = Chroma.from_texts(
    chunks,
    embedding,
    persist_directory="embedding_store"
)
vectorstore.persist()

print("✅ Embeddings saved to embedding_store")
