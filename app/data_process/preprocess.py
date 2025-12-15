import os
from typing import List
from PyPDF2 import PdfReader
# import docx
import pandas as pd

def load_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        reader = PdfReader(file_path)
        return "\n".join(
            page.extract_text() or "" for page in reader.pages
        )
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    # elif ext == ".docx":
    #     document = docx.Document(file_path)
    #     return "\n".join(p.text for p in document.paragraphs)
    elif ext == ".csv":
        df = pd.read_csv(file_path)
        return df.to_string(index=False)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end]
        # Simple cleanup
        chunk = " ".join(chunk.split())
        chunks.append(chunk)
        start += chunk_size - overlap
        if start <= 0:
            break
    return [c for c in chunks if c.strip()]

# import os
# from typing import List
# from PyPDF2 import PdfReader
# import pandas as pd
# import re

# HEADER_KEYS = [
#     "PETITIONER", "RESPONDENT", "DATE OF JUDGMENT", "BENCH", "CITATION", "ACT", "HEADNOTE", "JUDGMENT"
# ]

# def _extract_pdf_text(file_path: str) -> str:
#     reader = PdfReader(file_path)
#     pages_text = []
#     for page in reader.pages:
#         text = page.extract_text() or ""
#         # Preserve short lines (headers) by not collapsing them away
#         pages_text.append(text)
#     return "\n\n".join(pages_text)

# def _extract_headers(text: str) -> List[str]:
#     headers = []
#     for line in text.splitlines():
#         s = line.strip()
#         if not s:
#             continue
#         # Match headers like "PETITIONER :" or "PETITIONER:" and capture the remainder
#         if any(s.upper().startswith(key) for key in HEADER_KEYS):
#             headers.append(s)
#     return headers

# def load_text(file_path: str) -> str:
#     ext = os.path.splitext(file_path)[1].lower()
#     if ext == ".pdf":
#         text = _extract_pdf_text(file_path)
#         # Keep detected headers at the top to improve retrieval of roles/dates
#         headers = _extract_headers(text)
#         header_block = "\n".join(headers)
#         # Avoid duplicating headers: if header_block already in text, just prepend once
#         if header_block:
#             return header_block + "\n\n" + text
#         return text
#     elif ext == ".txt":
#         with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
#             return f.read()
#     elif ext == ".csv":
#         df = pd.read_csv(file_path)
#         return df.to_string(index=False)
#     else:
#         raise ValueError(f"Unsupported file type: {ext}")

# def chunk_text(text: str, chunk_size: int = 800, overlap: int = 200) -> List[str]:
#     """
#     Header-aware simple chunker:
#     - Keeps short header lines intact by not aggressively flattening whitespace
#     - Uses moderate chunk size (800) with overlap (200) to avoid burying short facts
#     """
#     # Light normalization: collapse excessive spaces but keep newlines to preserve header visibility
#     normalized = re.sub(r"[ \t]+", " ", text)

#     chunks: List[str] = []
#     start = 0
#     n = len(normalized)
#     if chunk_size <= 0:
#         raise ValueError("chunk_size must be > 0")
#     if overlap < 0 or overlap >= chunk_size:
#         raise ValueError("overlap must be >= 0 and < chunk_size")

#     while start < n:
#         end = min(start + chunk_size, n)
#         chunk = normalized[start:end].strip()
#         if chunk:
#             chunks.append(chunk)
#         if end == n:
#             break
#         start = start + (chunk_size - overlap)

#     return chunks


# import os
# from typing import List
# from PyPDF2 import PdfReader
# import pandas as pd
# import re

# HEADER_KEYS = [
#     "PETITIONER", "RESPONDENT", "DATE OF JUDGMENT", "BENCH",
#     "CITATION", "ACT", "HEADNOTE", "JUDGMENT"
# ]

# def _extract_pdf_text(file_path: str) -> str:
#     reader = PdfReader(file_path)
#     pages_text = []
#     for page in reader.pages:
#         text = page.extract_text() or ""
#         pages_text.append(text)
#     return "\n\n".join(pages_text)

# def _extract_headers(text: str) -> List[str]:
#     headers = []
#     for line in text.splitlines():
#         s = line.strip()
#         if not s:
#             continue
#         if any(s.upper().startswith(key) for key in HEADER_KEYS):
#             headers.append(s)
#     return headers

# def load_text(file_path: str) -> str:
#     ext = os.path.splitext(file_path)[1].lower()
#     if ext == ".pdf":
#         text = _extract_pdf_text(file_path)
#         return text
#     elif ext == ".txt":
#         with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
#             return f.read()
#     elif ext == ".csv":
#         df = pd.read_csv(file_path)
#         return df.to_string(index=False)
#     else:
#         raise ValueError(f"Unsupported file type: {ext}")

# def chunk_text(text: str, chunk_size: int = 800, overlap: int = 200) -> List[str]:
#     """
#     Header-aware chunker:
#     - Extracts header lines as separate chunks
#     - Splits the rest of the text into overlapping chunks
#     """
#     # Extract headers first
#     header_chunks = _extract_headers(text)

#     # Normalize spaces but keep newlines
#     normalized = re.sub(r"[ \t]+", " ", text)

#     chunks: List[str] = []
#     start = 0
#     n = len(normalized)
#     if chunk_size <= 0:
#         raise ValueError("chunk_size must be > 0")
#     if overlap < 0 or overlap >= chunk_size:
#         raise ValueError("overlap must be >= 0 and < chunk_size")

#     while start < n:
#         end = min(start + chunk_size, n)
#         chunk = normalized[start:end].strip()
#         if chunk:
#             chunks.append(chunk)
#         if end == n:
#             break
#         start = start + (chunk_size - overlap)

#     # Return headers first, then normal chunks
#     return header_chunks + chunks
