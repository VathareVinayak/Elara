let socket;
let sessionId = null;
let isConnected = false;

// DOM elements
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');

const chatMessages = document.getElementById('chat-messages');
const welcomeMessage = document.getElementById('welcomeMessage');
const newChatBtn = document.getElementById('new-chat-btn');
const chatMessagesContainer = document.querySelector('.chat-messages-container');

const fileUpload = document.getElementById('file-upload');

const sidebarToggle = document.getElementById('sidebar-toggle');
const sidebar = document.getElementById('sidebar');

const overlay = document.getElementById('overlay');
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const connectionStatus = document.getElementById('connection-status');


// Find or create sessions list container
let sessionsListContainer = document.getElementById('sessionsListContainer');
if (!sessionsListContainer) {
    sessionsListContainer = document.createElement('div');
    sessionsListContainer.id = "sessionsListContainer";
    sessionsListContainer.className = "sessions-list";
    
    // Find the sidebar section label and insert container after it
    const sidebarLabel = document.querySelector('.sidebar-section-label');
    if (sidebarLabel && sidebarLabel.parentNode) {
        sidebarLabel.parentNode.insertBefore(sessionsListContainer, sidebarLabel.nextSibling);
    }
}

function init() {
    setupEventListeners();
    connectWebSocket();

    // Add sample welcome message
    setTimeout(() => {
        appendMessage("system", "Welcome to Elara AI! Start by uploading a PDF or asking a question.");
    }, 500);
}

function setupEventListeners() {
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });
    fileUpload.addEventListener('change', uploadDocument);

    // Mobile sidebar toggle
    sidebarToggle.addEventListener('click', function() {
        toggleSidebar();
    });

    overlay.addEventListener('click', function() {
        hideSidebar();
    });

    if (newChatBtn) {
        newChatBtn.addEventListener('click', startNewChat);
    }
}

// Sidebar management functions
function toggleSidebar() {
    sidebar.classList.toggle('translate-x-0');
    overlay.classList.toggle('hidden');
}

// Hiding Slidebar 
function hideSidebar() {
    sidebar.classList.remove('translate-x-0');
    overlay.classList.add('hidden');
}

// Show Slidebar
function showSidebar() {
    sidebar.classList.add('translate-x-0');
    overlay.classList.remove('hidden');
}

// Connection with Websocket
function connectWebSocket() {
    updateConnectionStatus('connecting', 'Connecting...');

    try {
        socket = new WebSocket("ws://localhost:8000/ws/chat");

        socket.onopen = () => {
            console.log("WebSocket connected");
            isConnected = true;
            updateConnectionStatus('connected', 'Connected');
            // Request all sessions when connection opens
            socket.send(JSON.stringify({ type: "get_sessions" }));
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };

        socket.onclose = () => {
            console.log("WebSocket disconnected");
            isConnected = false;
            updateConnectionStatus('disconnected', 'Disconnected');
            appendMessage("system", "Connection closed. Attempting to reconnect...");
            setTimeout(connectWebSocket, 3000);
        };

        socket.onerror = (error) => {
            console.error("WebSocket error:", error);
            updateConnectionStatus('disconnected', 'Connection error');
        };
    } catch (error) {
        console.error("Failed to connect WebSocket:", error);
        updateConnectionStatus('disconnected', 'Connection failed');
        setTimeout(connectWebSocket, 5000);
    }
}

// Status
function updateConnectionStatus(status, text) {
    statusIndicator.className = 'status-indicator w-2.5 h-2.5 rounded-full';

    switch(status) {
        case 'connected': 
            statusIndicator.classList.add('bg-green-500'); 
            break;
        case 'connecting': 
            statusIndicator.classList.add('bg-yellow-500'); 
            break;
        case 'disconnected': 
            statusIndicator.classList.add('bg-red-500'); 
            break;
    }
    statusText.textContent = text;
}

// Fetch Message 
function handleWebSocketMessage(data) {
    if (data.type === "session_start") {
        sessionId = data.session_id;
        appendMessage("system", "Session started. You can now upload documents or ask questions.");
        // Refresh sessions list to highlight current session
        socket.send(JSON.stringify({ type: "get_sessions" }));
    }
    else if (data.type === "sessions_list" && data.sessions) {
        renderSessionsList(data.sessions);
    }
    else if (data.type === "history" && data.messages) {
        sessionId = data.session_id || sessionId;  // Update sessionId if provided
        clearChatMessages();
        data.messages.forEach(msg => appendMessage(msg.role, msg.content));
        // Refresh sessions list to highlight current session
        socket.send(JSON.stringify({ type: "get_sessions" }));
        
        // Hide sidebar on mobile after selecting a session
        if (window.innerWidth <= 768) {
            hideSidebar();
        }
    }
    else if (data.type === "assistant_message") {
        appendMessage("assistant", data.content);
    }
    else if (data.error) {
        appendMessage("system", `Error: ${data.error}`);
    }
}

// Fetch All session by ID
function renderSessionsList(sessions) {
    sessionsListContainer.innerHTML = ""; // Clear existing

    // Sort sessions by creation date (newest first)
    sessions.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    sessions.forEach(session => {
        const sessionElem = document.createElement("div");
        sessionElem.className = "session-item";

        // display only active session
        if (session.id === sessionId) {
            sessionElem.classList.add("active-session");
        }
        
        const sessionIdShort = session.id.substring(0, 8) + '...';
        const sessionDate = new Date(session.created_at).toLocaleDateString();
        const sessionTime = new Date(session.created_at).toLocaleTimeString();
        
        sessionElem.innerHTML = `
            <div class="font-medium">Session: ${sessionIdShort}</div>
            <div class="session-date">${sessionDate} ${sessionTime}</div>
        `;
        
        sessionElem.onclick = () => {
            if (sessionId !== session.id) {
                // Request chat history for selected session
                socket.send(JSON.stringify({ 
                    type: "select_session", 
                    session_id: session.id 
                }));
            }
        };
        
        sessionsListContainer.appendChild(sessionElem);
    });

    // Add message if no sessions
    if (sessions.length === 0) {
        const noSessionsElem = document.createElement("div");
        noSessionsElem.className = "session-item text-center text-gray-400";
        noSessionsElem.textContent = "No recent sessions";
        sessionsListContainer.appendChild(noSessionsElem);
    }
}


function sendMessage() {
    const message = chatInput.value.trim();
    if (message && isConnected) {
        appendMessage("user", message);
        socket.send(JSON.stringify({
            type: "query",
            query: message,
            session_id: sessionId
        }));
        chatInput.value = "";
    }
    else if (!isConnected) {
        appendMessage("system", "Not connected to server. Please wait...");
    }
}

function uploadDocument(event) {
    const files = event.target.files;
    if (!files.length) return;
    if (!sessionId) {
        appendMessage("system", "Session not established yet. Please wait...");
        return;
    }

    appendMessage("system", "Uploading document...");

    const formData = new FormData();
    formData.append("files", files[0]);
    formData.append("session_id", sessionId);
    formData.append("do_not_store", "false");

    fetch("http://localhost:8000/documents/upload", {
        method: "POST",
        body: formData
    }).then(resp => resp.json())
    .then(data => {
        appendMessage("system", data.message || "Upload complete.");
    }).catch(err => {
        appendMessage("system", `Upload error: ${err}`);
    });
}

function appendMessage(role, text) {
    if (welcomeMessage.style.display !== 'none') {
        welcomeMessage.style.display = 'none';
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `flex items-end gap-3 ${role === 'user' ? 'ml-auto flex-row-reverse' : ''} ${role === 'system' ? 'mx-auto italic' : ''}`;

    const profileDiv = document.createElement('div');
    profileDiv.className = 'w-9 h-9 rounded-full bg-gray-800 flex items-center justify-center text-xl shrink-0';

    if (role === 'user') {
        profileDiv.innerHTML = '<i class="fa-solid fa-user"></i>';
    } else if (role === 'assistant') {
        profileDiv.innerHTML = '<img src="frontend/assets/Elara_logo.png" class="w-full h-full rounded-full object-cover" alt="Elara AI">';
        const img = profileDiv.querySelector('img');
        img.onerror = function() {
            profileDiv.innerHTML = '<i class="fa-solid fa-robot"></i>';
        };
    } else {
        profileDiv.innerHTML = '<i class="fa-solid fa-info-circle"></i>';
    }

    const contentDiv = document.createElement('div');
    contentDiv.className = 'rounded-2xl p-4 break-words text-base max-w-lg';

    if (role === 'user') {
        contentDiv.classList.add('bg-gradient-to-r', 'from-purple-600', 'to-purple-800', 'text-white');
    } else if (role === 'assistant') {
        contentDiv.classList.add('bg-gray-700', 'border-l-4', 'border-purple-500', 'text-white');
    } else {
        contentDiv.classList.add('bg-purple-900', 'bg-opacity-20', 'border', 'border-purple-500', 'border-opacity-50', 'text-purple-300', 'text-sm', 'text-center', 'max-w-md');
    }

    let formattedText = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code class="bg-gray-800 px-1 py-0.5 rounded">$1</code>');

    contentDiv.innerHTML = formattedText;

    messageDiv.appendChild(profileDiv);
    messageDiv.appendChild(contentDiv);

    chatMessages.appendChild(messageDiv);
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
}

function clearChatMessages() {
    chatMessages.innerHTML = '';
    welcomeMessage.style.display = 'flex';
}

function startNewChat() {
    clearChatMessages();
    sessionId = null;

    if (isConnected) {
        socket.send(JSON.stringify({ type: "new_session" }));
        appendMessage("system", "Starting new conversation...");
        
        // Hide sidebar on mobile after starting new chat
        if (window.innerWidth <= 768) {
            hideSidebar();
        }
    } else {
        appendMessage("system", "Please wait for connection to start a new conversation.");
    }
}

// Handle window resize to manage sidebar behavior
window.addEventListener('resize', function() {
    if (window.innerWidth > 768) {
        // On desktop, ensure sidebar is visible
        sidebar.classList.remove('translate-x-0');
        overlay.classList.add('hidden');
    } else {
        // On mobile, ensure sidebar is hidden by default
        sidebar.classList.add('translate-x-0');
    }
});

document.addEventListener('DOMContentLoaded', init);