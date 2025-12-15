from typing import List, Tuple
import numpy as np
import faiss
from google import genai

from app.configs.config import settings

# Create a client instance with your API key
client = genai.Client(api_key=settings.GOOGLE_API_KEY)

# Use Gemini embedding model name from settings
EMBED_MODEL = "embedding-001"
MODEL_NAME = "gemini-2.5-flash"

def embed_text(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> List[float]:
    """
    task_type: 'RETRIEVAL_DOCUMENT' for chunks, 'RETRIEVAL_QUERY' for queries
    """
    resp = client.models.embed_content(
        model=EMBED_MODEL,
        contents=text,
    )
    return resp.embeddings[0].values  # returns a list of floats

def build_index(chunks: List[str]) -> Tuple[faiss.IndexFlatIP, np.ndarray]:
    """
    Build FAISS index (cosine similarity via inner product with normalized vectors).
    """
    embeddings = [embed_text(c, task_type="RETRIEVAL_DOCUMENT") for c in chunks]
    mat = np.array(embeddings, dtype="float32")
    faiss.normalize_L2(mat)
    dim = mat.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine similarity via normalized inner product
    index.add(mat)
    return index, np.array(chunks)

def search(index: faiss.IndexFlatIP, chunks_array: np.ndarray, query: str, k: int = 4) -> List[Tuple[int, float, str]]:
    q_vec = np.array([embed_text(query, task_type="RETRIEVAL_QUERY")], dtype="float32")
    faiss.normalize_L2(q_vec)
    scores, idxs = index.search(q_vec, k)
    results = []
    for i, score in zip(idxs[0], scores[0]):
        if i != -1:
            results.append((int(i), float(score), chunks_array[int(i)]))
    return results
