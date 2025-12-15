# from typing import List
# from google import genai
# from app.configs.config import settings

# client = genai.Client(api_key=settings.GOOGLE_API_KEY)
# MODEL_NAME = 'gemini-2.5-flash'

# def format_prompt(query: str, retrieved_chunks: List[str]) -> str:
#     context = "\n\n".join(retrieved_chunks)
#     return (
#         "You are a legal assistant. Use the provided context to answer the question.\n"
#         "Identify parties such as petitioner, respondent, contemner, etc. If the role is stated "
#         "in headings or short lines, extract it directly. If the role is implied, infer it.\n"
#         "Only say 'Not mentioned in the document' if there is truly no reference.\n\n"
#         f"Context:\n{context}\n\n"
#         f"Question: {query}\n"
#         "Answer:"
#     )




# def generate_answer(prompt: str, max_tokens: int = 512) -> str:
#     resp = client.models.generate_content(
#         model=MODEL_NAME,
#         contents=prompt,
#         config={
#             "max_output_tokens": max_tokens,
#             "temperature": 0.2,
#             "top_p": 0.9,
#         }
#     )
#     if hasattr(resp, "text") and resp.text:
#         return resp.text.strip()
#     if hasattr(resp, "candidates") and resp.candidates:
#         parts = []
#         for cand in resp.candidates:
#             if hasattr(cand, "content") and cand.content.parts:
#                 for part in cand.content.parts:
#                     if hasattr(part, "text"):
#                         parts.append(part.text)
#         return "\n".join(parts).strip()
#     return ""



# # def generate_answer(prompt: str, max_tokens: int = 512) -> str:
# #     # model = genai.GenerativeModel(MODEL_NAME)
# #     resp = client.models.generate_content(
# #         model=MODEL_NAME,
# #         contents=prompt,
# #         config={
# #             "max_output_tokens": max_tokens,
# #             "temperature": 0.2,
# #             "top_p": 0.9,
# #         }
# #     )

# #     answer = resp.text.strip() if hasattr(resp, "text") else ""
# #     return answer
#     # # Handle response
#     # if hasattr(resp, "text") and resp.text:
#     #     return resp.text.strip()
#     # # Fallback for multi-part responses
#     # if hasattr(resp, "candidates") and resp.candidates:
#     #     parts = []
#     #     for cand in resp.candidates:
#     #         for part in getattr(cand, "content", {}).get("parts", []):
#     #             if hasattr(part, "text"):
#     #                 parts.append(part.text)
#     #     return "\n".join(parts).strip() if parts else ""
#     # return ""


from typing import List
from google import genai
from app.configs.config import settings
import time
from google.genai.errors import ServerError

# Use Client style as requested
client = genai.Client(api_key=settings.GOOGLE_API_KEY)

# Prefer model name from settings; fallback to a sane default if not set
MODEL_NAME = "gemini-2.5-flash"

def format_prompt(query: str, retrieved_chunks: List[str]) -> str:
    context = "\n\n".join(retrieved_chunks)
    return (
        "You are an intelligent assistant. Use the provided context to answer the question.\n"
        "Always ground your answer in the context. If the information is explicitly present, extract it clearly.\n"
        "If the information is implied, infer it carefully and explain.\n"
        "If the context truly does not contain the answer, say 'The document does not mention it.'\n"
        "Do not cut off lists or tables — include all relevant entries from the context.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}\n"
        "Answer:"
    )



# def _parse_text_response(resp) -> str:
#     # Try simple .text first (SDK convenience)
#     if hasattr(resp, "text") and isinstance(resp.text, str) and resp.text.strip():
#         return resp.text.strip()

#     # Fallback: aggregate candidate parts
#     parts: List[str] = []
#     if hasattr(resp, "candidates") and resp.candidates:
#         for cand in resp.candidates:
#             content = getattr(cand, "content", None)
#             if content and getattr(content, "parts", None):
#                 for part in content.parts:
#                     text = getattr(part, "text", None)
#                     if isinstance(text, str) and text.strip():
#                         parts.append(text.strip())

#     return "\n".join(parts).strip()

# def generate_answer(prompt: str, max_tokens: int = 512) -> str:
#     resp = client.models.generate_content(
#         model=MODEL_NAME,
#         contents=prompt,
#         # Correct key is generation_config for the Client models API
#         config={
#             "max_output_tokens": max_tokens,
#             "temperature": 0.2,
#             "top_p": 0.9,
#         }
#     )
#     return _parse_text_response(resp) or "The document does not mention it."


def _parse_text_response(resp) -> str:
    if hasattr(resp, "text") and resp.text:
        return resp.text.strip()

    parts = []
    if hasattr(resp, "candidates") and resp.candidates:
        for cand in resp.candidates:
            content = getattr(cand, "content", None)
            if content and getattr(content, "parts", None):
                for part in content.parts:
                    text = getattr(part, "text", None)
                    if isinstance(text, str) and text.strip():
                        parts.append(text.strip())
    return "\n".join(parts).strip()



def generate_answer(prompt: str, max_tokens: int = 2000) -> str:
    for attempt in range(5):  # try up to 5 times
        try:
            resp = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config={
                    "max_output_tokens": max_tokens,
                    "temperature": 0.2,
                    "top_p": 0.9,
                }
            )
            return _parse_text_response(resp) or "The document does not mention it."
        except ServerError as e:
            if e.status_code == 503:
                # exponential backoff
                wait = 2 ** attempt
                time.sleep(wait)
                continue
            raise
    return "Service temporarily unavailable. Please try again later."
