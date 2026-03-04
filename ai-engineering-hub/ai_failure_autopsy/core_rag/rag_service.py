from pathlib import Path

from langchain_ollama import OllamaLLM
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

# -------------------------
# Config
# -------------------------
VECTOR_DB_PATH = "data/chroma"
FAILURE_DATA_PATH = "data/failures"
from pathlib import Path

REPAIR_DIR = Path("data/repairs")

repair_docs = []
for file in REPAIR_DIR.glob("*.txt"):
    text = file.read_text(encoding="utf-8")
    repair_docs.append(
        Document(
            page_content=text,
            metadata={"source": "repair", "incident": file.stem}
        )
    )


# -------------------------
# Local LLM
# -------------------------
llm = OllamaLLM(model="llama3")

# -------------------------
# Load real failure documents
# -------------------------
failure_dir = Path(FAILURE_DATA_PATH)

docs = []
for file in failure_dir.glob("*.txt"):
    text = file.read_text(encoding="utf-8")
    docs.append(
        Document(
            page_content=text,
            metadata={"source": file.name}
        )
    )

if not docs:
    raise RuntimeError("No failure documents found in data/failures")

# -------------------------
# Chunking
# -------------------------
splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=40
)
all_docs = docs + repair_docs
chunks = splitter.split_documents(all_docs)


# -------------------------
# Embeddings
# -------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

# -------------------------
# Vector Store (persistent)
# -------------------------
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=VECTOR_DB_PATH
)

# -------------------------
# Query
# -------------------------
query = "What caused the failure in incident 001 and how could it be prevented?"

retrieved_docs = vectorstore.similarity_search(query, k=3)
context = "\n\n".join(d.page_content for d in retrieved_docs)

prompt = f"""
You are an AI reliability analyst.

Answer ONLY using the context below.

Context:
{context}

Question:
{query}
"""

# -------------------------
# Run LLM
# -------------------------
response = llm.invoke(prompt)
print(response)
