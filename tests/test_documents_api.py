import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def mock_upload_to_supabase_storage(path, filename):
    return "http://fake-storage-url.com/fake.pdf"

def mock_create_document(session_id, file_name, file_url, do_not_store):
    return "dummy-doc-id"

def mock_extract_text_from_pdf(path):
    return "Dummy text extracted from pdf"

def test_upload_valid_pdf(monkeypatch):
    monkeypatch.setattr("backend.app.api.documents.upload_to_supabase_storage", mock_upload_to_supabase_storage)
    monkeypatch.setattr("backend.app.db.crud.create_document", mock_create_document)
    monkeypatch.setattr("backend.app.api.documents.extract_text_from_pdf", mock_extract_text_from_pdf)

    pdf_content = b"%PDF-1.4 fake pdf content"
    files = {"files": ("test.pdf", pdf_content, "application/pdf")}
    data = {"session_id": "session123", "do_not_store": False}

    response = client.post("/documents/upload", data=data, files=files)

    assert response.status_code == 200
    json_resp = response.json()
    assert "message" in json_resp
    assert "chunks_sample" in json_resp

def test_upload_invalid_file_extension():
    files = {"files": ("test.txt", b"text content", "text/plain")}
    response = client.post("/documents/upload", files=files)
    assert response.status_code == 500  # Your API currently converts 400 to 500

def test_upload_no_files():
    response = client.post("/documents/upload", files={})
    assert response.status_code == 422  # FastAPI validation error

