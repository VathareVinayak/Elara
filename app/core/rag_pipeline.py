from typing import List, Optional
from app.core.embeddings import embed_text
from app.db.faiss_instance import faiss_client
from ..services.rag_service import call_llm

# Format retrieved chunks with citations
def format_context(chunks: List[str]) -> str:
    context = "\n\n".join(f"[{i+1}] {chunk}" for i, chunk in enumerate(chunks))
    return f"Based on the following documents:\n{context}\n\nAnswer the question below."

# RAG flow
async def rag_answer(query: str, top_k: int = 5, session_id: Optional[str] = None) -> str:
    # You may utilize session_id if needed here, currently unused
    query_embedding = embed_text([query])
    distances, indices = faiss_client.search(query_embedding, k=top_k)
    chunks = [faiss_client.get_chunk_text(idx) for idx in indices[0] if idx != -1]
    chunks = faiss_client.boost_results(chunks, distances, query=query)
    prompt_context = format_context(chunks)
    prompt = f"{prompt_context}\nQuestion: {query}"
    answer = await call_llm(prompt)
    return answer
