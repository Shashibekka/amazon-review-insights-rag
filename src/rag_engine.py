# src/rag_engine.py
import os
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables from the .env file
load_dotenv()

class ReviewAnalyzerRAG:
    def __init__(self, persist_dir="./data/chroma_db"):
        print("Initializing RAG Engine...")
        # 1. Load Embeddings via the NEW Official API
        self.embeddings = HuggingFaceEndpointEmbeddings(
            model="sentence-transformers/all-MiniLM-L6-v2",
            huggingfacehub_api_token=os.environ.get("HF_TOKEN")
        )

        # 2. Connect to existing Vector DB
        self.vector_db = Chroma(
            persist_directory=persist_dir, 
            embedding_function=self.embeddings
        )
        
        # 3. Load LLM
        self.llm = ChatGroq(
            model_name="llama-3.1-8b-instant", 
            temperature=0
        )
        
        # 4. Assemble Chain
        self.rag_chain = self._build_chain()
        print("✅ RAG Engine Ready!")

    def _build_chain(self):
        system_prompt = (
            "You are an expert product analyst. Use the following retrieved customer reviews "
            "to answer the user's question. If the answer cannot be found in the reviews, "
            "simply state that you do not have enough data. Keep your answer concise, "
            "professional, and mention specific product names when applicable.\n\n"
            "Reviews Context:\n{context}"
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        
        document_chain = create_stuff_documents_chain(self.llm, prompt)
        retriever = self.vector_db.as_retriever(search_kwargs={"k": 5})
        return create_retrieval_chain(retriever, document_chain)

    def analyze(self, query: str) -> str:
        """The main method our backend API will call."""
        response = self.rag_chain.invoke({"input": query})
        return response["answer"]

# --- Quick Local Test ---
if __name__ == "__main__":
    # Pointing to the data folder from the src directory
    analyzer = ReviewAnalyzerRAG(persist_dir="../data/chroma_db")
    test_report = analyzer.analyze("What are the biggest complaints about screen quality?")
    print("\n--- Test Report ---")
    print(test_report)