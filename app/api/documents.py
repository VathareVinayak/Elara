# Document upload API
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
from PyPDF2 import PdfReader
from app.db.chunked_docs import chunk_text
from app.core.embeddings import embed_text
from app.db.faiss_client import FaissClient
import uuid
import shutil
import os

from app.db.faiss_instance import faiss_client


router = APIRouter()



@router.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
    do_not_store: Optional[bool] = Form(False)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    # Example save directory, adjust as needed
    UPLOAD_DIR = "uploaded_files"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    try:
        all_chunks = []
        for file in files:
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext != ".pdf":
                raise HTTPException(status_code=400, detail="Only PDF files supported")

            # Save locally (optional, for PyPDF2 read)
            saved_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}{file_ext}")
            with open(saved_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Extract raw text
            raw_text = extract_text_from_pdf(saved_path)

            # Chunk text
            chunks = chunk_text(raw_text)

            if not do_not_store:
                # Persist document metadata here: session_id, filename, etc.
                # store_document_metadata(session_id, file.filename, saved_path)

                # Generate embeddings
                embeddings = embed_text(chunks)

                # Add embeddings to FAISS index
                faiss_client.add_embeddings(embeddings, chunks)


                # Persist chunk metadata as needed
                # store_chunk_metadata(session_id, chunks)

            # Keep all chunks for response or logging
            all_chunks.extend(chunks)

        return JSONResponse(
            content={
                "message": f"{len(files)} files uploaded, {len(all_chunks)} chunks processed",
                "chunks_sample": all_chunks[:3],  # sample to show
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text
