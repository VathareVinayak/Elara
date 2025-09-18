from langchain.text_splitter import CharacterTextSplitter

def chunk_text(text: str, chunk_size: int = 2000, chunk_overlap: int = 200):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks
