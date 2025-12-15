from fastapi import FastAPI
from app.api.route import router

app = FastAPI(title="Gemini RAG Bot")
app.include_router(router)

# For local dev: uvicorn main:app --reload
