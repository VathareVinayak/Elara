from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv


load_dotenv()
token = os.getenv("HUGGINGFACE_HUB_TOKEN")


model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', use_auth_token=token)


def embed_text(texts: list[str]):
    """
    Generate embeddings for a list of texts using MiniLM model.
    Returns numpy array of embeddings.
    """
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings

