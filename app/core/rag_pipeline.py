from app.core.embeddings import embed_text
from app.db.faiss_client import FaissClient
from ..services.rag_service import call_llm
from typing import List

from app.db.faiss_instance import faiss_client

# Formats retrieved chunks with citations.
def format_context(chunks: List[str]) -> str:
    context = "\n\n".join(f"[{i+1}] {chunk}" for i, chunk in enumerate(chunks))
    return f"Based on the following documents:\n{context}\n\nAnswer the question below."

# RAG flow: embed query, search FAISS, boost results, format context, call LLM, return answer.
async def rag_answer(query: str, top_k: int = 5) -> str:
    # Normalize + embed query
    query_embedding = embed_text([query])

    # k-NN search
    distances, indices = faiss_client.search(query_embedding, k=top_k)

    # Retrieve chunk texts excluding invalid
    chunks = [faiss_client.get_chunk_text(idx) for idx in indices[0] if idx != -1]

    # Boost results
    chunks = faiss_client.boost_results(chunks, distances, query=query)

    # Format prompt context
    prompt_context = format_context(chunks)

    # Complete prompt with user query
    prompt = f"{prompt_context}\nQuestion: {query}"
    
    # Generate answer from LLM
    answer = await call_llm(prompt)

    # Optionally trim output or append citations here

    return answer
