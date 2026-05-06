# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os

# Add the root directory to the system path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag_engine import ReviewAnalyzerRAG

# Initialize the API
app = FastAPI(
    title="Amazon Reviews RAG API",
    description="API for extracting insights from product reviews.",
    version="1.0.0"
)

# Initialize our ML Engine (this happens once when the server starts)
# We point it to the data folder relative to the root directory
analyzer = ReviewAnalyzerRAG(persist_dir="./data/chroma_db")

# Define the expected input data structure using Pydantic
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str

# Define the Health Check endpoint
@app.get("/")
async def root():
    return {"status": "online", "message": "RAG API is running."}

# Define the main Analysis endpoint
@app.post("/analyze", response_model=QueryResponse)
async def analyze_reviews(request: QueryRequest):
    try:
        # Pass the user's query to our RAG engine
        result = analyzer.analyze(request.query)
        return QueryResponse(answer=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))