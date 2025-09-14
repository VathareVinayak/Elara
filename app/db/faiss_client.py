import faiss
import numpy as np
from datetime import datetime, timedelta

# Dimension matches MiniLM embedding output size
EMBEDDING_DIM = 384

class FaissClient:
    def __init__(self):
        # Useing the inner product index to approximate cosine similarity (vectors normalized are assumed)
        self.index = faiss.IndexFlatIP(EMBEDDING_DIM)
        self.chunk_text_store = []  # in-memory store of chunks matching FAISS index order
    
    # Add embeddings and their corresponding text chunks to the FAISS index and local store.
    def add_embeddings(self, embeddings: np.ndarray, chunks: list[str]):
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        self.chunk_text_store.extend(chunks)
    # Searching Relavant data Using K-NN & Cosine Similarity
    def search(self, query_embedding: np.ndarray, k: int = 5):
        """
        1) Searching for top-k nearest neighbors by cosine similarity.
        2) Return distances and indices (multiple array).
        """
        faiss.normalize_L2(query_embedding)
        distances, indices = self.index.search(query_embedding, k)
        return distances, indices

    # Retrieve chunk text by FAISS index.
    def get_chunk_text(self, idx: int) -> str:
        if 0 <= idx < len(self.chunk_text_store):
            return self.chunk_text_store[idx]
        return ""

    # Boosting for Retrived Chunks (Pending)
    def boost_results(self,chunks: list[str],distances: np.ndarray,boost_recent: bool = True,boost_exact_match: bool = True,query: str = "",
        chunk_metadata: list = None) -> list[str]:
        """
        Apply boosting heuristics to the retrieved chunks.

        Args:
          chunks: List of chunk texts.
          distances: Similarity scores from FAISS search.
          boost_recent: Whether to boost recent chunks (metadata required).
          boost_exact_match: Whether to boost chunks containing query terms.
          query: The user query string.
          chunk_metadata: Optional list of dicts with metadata, for recency boosting.

        Returns:
          Re-ranked list of chunk texts.
        """

        scores = distances.copy()

        # Boost exact matches
        if boost_exact_match:
            query_terms = set(query.lower().split())
            for i, chunk in enumerate(chunks):
                chunk_text = chunk.lower()
                if any(term in chunk_text for term in query_terms):
                    scores[0][i] *= 1.1  # 10% boost

        # Boost recent chunks if metadata available
        if boost_recent and chunk_metadata:
            now = datetime.utcnow()
            for i, meta in enumerate(chunk_metadata):
                upload_time = meta.get("upload_time")
                if upload_time and (now - upload_time) < timedelta(days=7):
                    scores[0][i] *= 1.2  # 20% boost for last 7 days

        # Sort chunks by boosted scores descending
        sorted_indices = np.argsort(-scores[0])
        boosted_chunks = [chunks[i] for i in sorted_indices]

        return boosted_chunks