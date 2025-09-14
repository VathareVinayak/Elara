# Chunking utilities

from langchain.text_splitter import CharacterTextSplitter

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    """
    Splits text into chunks of size chunk_size with chunk_overlap.
    Returns a list of text chunks.
    """
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks
