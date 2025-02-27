import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma
from uuid import uuid4
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DATA_PATH = "data"
CHROMA_PATH = "chroma_db"
BATCH_SIZE = 100  

# Ensure the data folder exists and has PDFs
if not os.path.exists(DATA_PATH) or not os.listdir(DATA_PATH):
    raise FileNotFoundError(f"No files found in {DATA_PATH}. Please add PDFs.")

# Initialize embedding model
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

# Initialize vector store
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings_model,
    persist_directory=CHROMA_PATH,
)

# Load PDFs
loader = PyPDFDirectoryLoader(DATA_PATH)
raw_documents = loader.load()

if not raw_documents:
    raise ValueError("No text extracted from PDFs. Check the files.")

print(f"✅ Loaded {len(raw_documents)} documents from {DATA_PATH}.")

# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
)

chunks = text_splitter.split_documents(raw_documents)

if not chunks:
    raise ValueError("No chunks created. Check the text splitting logic.")

print(f"🔹 Generated {len(chunks)} chunks.")

# Generate unique IDs
uuids = [str(uuid4()) for _ in range(len(chunks))]

# Insert in batches
for i in range(0, len(chunks), BATCH_SIZE):
    batch_chunks = chunks[i:i + BATCH_SIZE]
    batch_uuids = uuids[i:i + BATCH_SIZE]

    try:
        vector_store.add_documents(documents=batch_chunks, ids=batch_uuids)
        print(f"✅ Inserted batch {i//BATCH_SIZE + 1}: {len(batch_chunks)} chunks.")
    except Exception as e:
        raise RuntimeError(f" Error adding batch {i//BATCH_SIZE + 1}: {e}")

print(" All documents successfully added to the vector store!")
