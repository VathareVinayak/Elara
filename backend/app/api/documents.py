from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
from PyPDF2 import PdfReader

from backend.app.db.faiss_instance import faiss_client
from backend.app.db.crud import create_document
from backend.app.db.supabase_client import supabase
from backend.app.db.chunked_docs import chunk_text

from backend.app.core.embeddings import embed_text

import uuid
import shutil
import os

router = APIRouter()

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
    do_not_store: Optional[bool] = Form(False)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    if session_id == "":
        session_id = None  # Convert empty string to None to avoid UUID errors

    all_chunks = []

    try:
        for file in files:
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext != ".pdf":
                raise HTTPException(status_code=400, detail="Only PDF files supported")

            saved_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}{file_ext}")
            with open(saved_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            file_url = await upload_to_supabase_storage(saved_path, file.filename)

            raw_text = extract_text_from_pdf(saved_path)

            chunks = chunk_text(raw_text, chunk_size=2000, chunk_overlap=200)  # Increased chunk size

            await create_document(
                session_id=session_id,
                file_name=file.filename,
                file_url=file_url,
                do_not_store=do_not_store
            )

            if not do_not_store:
                embeddings = embed_text(chunks)
                faiss_client.add_embeddings(embeddings, chunks)

            os.remove(saved_path)
            all_chunks.extend(chunks)

        return JSONResponse(
            content={
                "message": f"{len(files)} files uploaded, {len(all_chunks)} chunks processed",
                "chunks_sample": all_chunks[:3],
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


async def upload_to_supabase_storage(file_path: str, original_filename: str) -> str:
    bucket_name = "documents"
    file_id = str(uuid.uuid4())
    file_storage_path = f"{file_id}_{original_filename}"

    with open(file_path, "rb") as file_data:
        response = supabase.storage.from_(bucket_name).upload(file_storage_path, file_data)

    if hasattr(response, "error") and response.error:
        raise Exception(f"Supabase storage upload error: {response.error.message}")

    public_url = supabase.storage.from_(bucket_name).get_public_url(file_storage_path)
    if not public_url:
        raise Exception("Failed to get public URL from Supabase storage")

    return public_url
