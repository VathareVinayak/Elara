import faiss
import numpy as np
from datetime import datetime, timedelta

EMBEDDING_DIM = 384

class FaissClient:
    def __init__(self):
        self.index = faiss.IndexFlatIP(EMBEDDING_DIM)
        self.chunk_text_store = []

    def add_embeddings(self, embeddings: np.ndarray, chunks: list[str]):
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        self.chunk_text_store.extend(chunks)

    def search(self, query_embedding: np.ndarray, k: int = 5):
        faiss.normalize_L2(query_embedding)
        distances, indices = self.index.search(query_embedding, k)
        return distances, indices

    def get_chunk_text(self, idx: int) -> str:
        if 0 <= idx < len(self.chunk_text_store):
            return self.chunk_text_store[idx]
        return ""

    def boost_results(
        self,
        chunks: list[str],
        distances: np.ndarray,
        boost_recent: bool = True,
        boost_exact_match: bool = True,
        query: str = "",
        chunk_metadata: list = None
    ) -> list[str]:
        scores = distances.copy()

        # Filter valid chunk indices (exclude invalid -1 index)
        valid_indices = [i for i in range(len(chunks)) if i >= 0 and i < len(chunks)]

        # Boost exact match chunks by increasing their scores
        if boost_exact_match:
            query_terms = set(query.lower().split())
            for i in valid_indices:
                chunk_text = chunks[i].lower()
                if any(term in chunk_text for term in query_terms):
                    scores[0][i] *= 1.1

        # Boost recent chunks uploaded within last 7 days
        if boost_recent and chunk_metadata:
            now = datetime.utcnow()
            for i in valid_indices:
                meta = chunk_metadata[i] if i < len(chunk_metadata) else None
                if meta:
                    upload_time = meta.get("upload_time")
                    if upload_time and (now - upload_time) < timedelta(days=7):
                        scores[0][i] *= 1.2

        # Sort indices based on boosted scores in descending order
        sorted_indices = np.argsort(-scores[0])

        # Filter sorted indices to valid range before accessing chunks
        filtered_sorted_indices = [i for i in sorted_indices if 0 <= i < len(chunks)]

        boosted_chunks = [chunks[i] for i in filtered_sorted_indices]

        return boosted_chunks
