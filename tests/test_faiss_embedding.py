from app.core.embeddings import embed_text
#from app.db.faiss_client import FaissClient
from ..app.db.faiss_client import FaissClient
import numpy as np

if __name__ == "__main__":
    texts = ["Hello world", "AI chatbot", "Vector search"]
    embeddings = embed_text(texts)
    client = FaissClient()
    client.add_embeddings(np.array(embeddings))
    query = embed_text(["Hello AI"])
    distances, indices = client.search(np.array(query), k=2)
    print("Indices:", indices)
    print("Distances:", distances)
