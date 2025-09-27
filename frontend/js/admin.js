    let currentSessionId = null;

  // Fix: Use relative paths instead of absolute
  const API_BASE = '';

  async function fetchSessions() {
    try {
      const res = await fetch(`${API_BASE}/admin/sessions`);
      const data = await res.json();
      const sessionsList = document.getElementById('sessions-list');
      sessionsList.innerHTML = '';
      data.sessions.forEach(session => {
        const li = document.createElement('li');
        li.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
        li.style.cursor = 'pointer';

        const sessionInfo = document.createElement('span');
        sessionInfo.textContent = `Session: ${session.id} | Created At: ${session.created_at || 'N/A'}`;

        const actionsDiv = document.createElement('div');

        // Delete button
        const delBtn = document.createElement('button');
        delBtn.className = 'btn btn-sm btn-danger ms-2';
        delBtn.textContent = 'Delete';
        delBtn.onclick = async (e) => {
          e.stopPropagation();
          if(confirm(`Delete session ${session.id}? All related messages and documents will be lost.`)) {
            await deleteSession(session.id);
          }
        };

        actionsDiv.appendChild(delBtn);
        li.appendChild(sessionInfo);
        li.appendChild(actionsDiv);

        li.onclick = () => {
          currentSessionId = session.id;
          fetchMessages(session.id);
          fetchDocuments(session.id);
        };
        sessionsList.appendChild(li);
      });
    } catch (err) {
      alert("Failed to load sessions: " + err);
    }
  }

  async function fetchMessages(sessionId) {
    try {
      const res = await fetch(`${API_BASE}/admin/sessions/${sessionId}/messages`);
      const data = await res.json();
      const messagesList = document.getElementById('messages-list');
      messagesList.innerHTML = '';
      data.messages.forEach(msg => {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';

        const msgText = document.createElement('span');
        msgText.textContent = `[${msg.role}] ${msg.content}`;

        const delBtn = document.createElement('button');
        delBtn.className = 'btn btn-sm btn-danger ms-2';
        delBtn.textContent = 'Delete';
        delBtn.onclick = async (e) => {
          e.stopPropagation();
          if(confirm(`Delete message ${msg.id}?`)) {
            await deleteMessage(msg.id);
            fetchMessages(sessionId);
          }
        };

        li.appendChild(msgText);
        li.appendChild(delBtn);
        messagesList.appendChild(li);
      });
    } catch (err) {
      alert("Failed to load messages: " + err);
    }
  }

  async function fetchDocuments(sessionId) {
    try {
      const res = await fetch(`${API_BASE}/admin/sessions/${sessionId}/documents`);
      const data = await res.json();
      const documentsList = document.getElementById('documents-list');
      documentsList.innerHTML = '';
      data.documents.forEach(doc => {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';

        const link = document.createElement('a');
        link.href = doc.file_url || '#';
        link.target = '_blank';
        link.textContent = doc.file_name;

        const delBtn = document.createElement('button');
        delBtn.className = 'btn btn-sm btn-danger ms-2';
        delBtn.textContent = 'Delete';
        delBtn.onclick = async (e) => {
          e.stopPropagation();
          if(confirm(`Delete document ${doc.id}?`)) {
            await deleteDocument(doc.id);
            fetchDocuments(sessionId);
          }
        };

        li.appendChild(link);
        li.appendChild(delBtn);
        documentsList.appendChild(li);
      });
    } catch (err) {
      alert("Failed to load documents: " + err);
    }
  }

  async function deleteSession(id) {
    const res = await fetch(`${API_BASE}/admin/sessions/${id}`, { method: 'DELETE' });
    if(res.ok) {
      alert(`Deleted session ${id}`);
      if(currentSessionId === id) {
        document.getElementById('messages-list').innerHTML = '';
        document.getElementById('documents-list').innerHTML = '';
        currentSessionId = null;
      }
      fetchSessions();
    } else {
      alert(`Failed to delete session ${id}`);
    }
  }

  async function deleteMessage(id) {
    const res = await fetch(`${API_BASE}/admin/messages/${id}`, { method: 'DELETE' });
    if(res.ok) {
      alert(`Deleted message ${id}`);
    } else {
      alert(`Failed to delete message ${id}`);
    }
  }

  async function deleteDocument(id) {
    const res = await fetch(`${API_BASE}/admin/documents/${id}`, { method: 'DELETE' });
    if(res.ok) {
      alert(`Deleted document ${id}`);
    } else {
      alert(`Failed to delete document ${id}`);
    }
  }

  // Refresh functions
  function refreshMessages() {
    if(currentSessionId) fetchMessages(currentSessionId);
    else alert("Select a session first");
  }
  
  function refreshDocuments() {
    if(currentSessionId) fetchDocuments(currentSessionId);
    else alert("Select a session first");
  }
  
  // Initial fetch on page load
  fetchSessions();