from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
import gradio as gr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
CHROMA_PATH = "chroma_db"

# Initialize embeddings model
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

# Initialize LLM
llm = ChatOpenAI(temperature=0.5, model="gpt-4o-mini")

# Connect to ChromaDB
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings_model,
    persist_directory=CHROMA_PATH, 
)

# Set up retriever (increased k for more context)
retriever = vector_store.as_retriever(search_kwargs={'k': 1})

# Function to handle chatbot responses
def stream_response(message, history):
    # Retrieve relevant chunks
    docs = retriever.invoke(message)
    
    # Compile knowledge from retrieved chunks
    knowledge = "\n\n".join(doc.page_content for doc in docs)

    # RAG prompt
    rag_prompt = f"""
    You are an AI assistant that answers questions **only** based on the provided knowledge.
    Do not use any outside knowledge. 
    If the answer is not in "The Knowledge" section, respond with "I don't have that information."
    
    **User Question:** {message}
    
    **Conversation History:** {history}
    
    **The Knowledge:**
    {knowledge}
    """

    # Stream response
    partial_message = ""
    for response in llm.stream(rag_prompt):
        partial_message += response.content
        yield partial_message

# Initialize Gradio chatbot
chatbot = gr.ChatInterface(stream_response, textbox=gr.Textbox(
    placeholder="Ask a question...",
    container=False,
    autoscroll=True,
    scale=7),
)

# Launch app
chatbot.launch(share=True)
