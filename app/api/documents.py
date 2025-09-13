from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")
    
    # Implement chunking here(pending)
    
    # Now, just mentioned about upload
    return JSONResponse(content={"filename": file.filename, "message": "File uploaded successfully."})
