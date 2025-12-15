import os
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, Form
from app.configs.config import settings
from app.data_process.preprocess import load_text, chunk_text
from app.data_process.vector_store import build_index, search
from app.generator.generate import format_prompt, generate_answer

router = APIRouter()
sessions: Dict[str, Dict[str, Any]] = {}

@router.post("/upload")
async def upload(session_id: str = Form(...), file: UploadFile = File(...)):
    os.makedirs(settings.DATA_PATH, exist_ok=True)
    # Save file
    save_path = os.path.join(settings.DATA_PATH, f"{session_id}_{file.filename}")
    with open(save_path, "wb") as f:
        f.write(await file.read())
    # Process
    text = load_text(save_path)
    chunks = chunk_text(text, chunk_size=1000, overlap=200)
    index, chunk_array = build_index(chunks)
    sessions[session_id] = {"index": index, "chunks": chunk_array}
    return {"message": "File processed", "session_id": session_id, "chunks": len(chunk_array)}

@router.post("/query")
async def query(session_id: str = Form(...), q: str = Form(...), k: int = Form(4), max_tokens: int = Form(512)):
    rag = sessions.get(session_id)
    if not rag:
        return {"error": "Session not found. Upload a file first.", "session_id": session_id}
    results = search(rag["index"], rag["chunks"], q, k=k)
    # Rank already by cosine similarity via FAISS; optionally re-rank or filter here.
    top_chunks = [chunk for _, _, chunk in results]
    prompt = format_prompt(q, top_chunks)
    answer = generate_answer(prompt, max_tokens=max_tokens)
    return {
        "session_id": session_id,
        "query": q,
        "answer": answer,
        "retrieval": [{"rank": i+1, "score": s, "chunk": c} for i, (_, s, c) in enumerate(results)]
    }
