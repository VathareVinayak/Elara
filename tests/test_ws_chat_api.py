import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from unittest.mock import AsyncMock, patch

client = TestClient(app)

@patch("backend.app.api.ws_chat.get_session", new_callable=AsyncMock)
@patch("backend.app.api.ws_chat.create_session", new_callable=AsyncMock)
@patch("backend.app.api.ws_chat.get_messages_by_session", new_callable=AsyncMock)
@patch("backend.app.api.ws_chat.create_message", new_callable=AsyncMock)
@patch("backend.app.api.ws_chat.rag_answer", new_callable=AsyncMock)
def test_websocket_chat(mock_rag_answer, mock_create_message, mock_get_messages, mock_create_session, mock_get_session):
    session_id = "test-session"
    mock_get_session.return_value = {"id": session_id}
    mock_create_session.return_value = session_id
    mock_get_messages.return_value = [{"role": "user", "content": "hi"}]
    mock_create_message.return_value = None
    mock_rag_answer.return_value = "response"

    with client.websocket_connect(f"/ws/chat?session_id={session_id}") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "session_start"
        assert data["session_id"] == session_id

        data = websocket.receive_json()
        assert data["type"] == "history"
        assert len(data["messages"]) > 0

        websocket.send_json({"query": "hello"})
        response = websocket.receive_json()
        assert response["type"] == "assistant_message"
        assert "response" in response["content"]
