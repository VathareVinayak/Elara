    let socket;
    let sessionId = null;
    let isConnected = false;

    // DOM elements
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatMessages = document.getElementById('chat-messages');
    const welcomeMessage = document.getElementById('welcomeMessage');
    const fileUpload = document.getElementById('file-upload');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    const connectionStatus = document.getElementById('connection-status');
    const newChatBtn = document.getElementById('new-chat-btn');
    const chatMessagesContainer = document.querySelector('.chat-messages-container');

    // Initialize application
    function init() {
      setupEventListeners();
      connectWebSocket();
      
      // Add sample messages for demonstration
      setTimeout(() => {
        appendMessage("system", "Welcome to Elara AI! Start by uploading a PDF or asking a question.");
      }, 500);
    }

    // Set up event listeners
    function setupEventListeners() {
      sendBtn.addEventListener('click', sendMessage);
      chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
      });
      fileUpload.addEventListener('change', uploadDocument);
      
      // Mobile sidebar toggle
      sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('translate-x-0');
        overlay.classList.toggle('hidden');
      });
      
      overlay.addEventListener('click', function() {
        sidebar.classList.remove('translate-x-0');
        overlay.classList.add('hidden');
      });
      
      // New chat button
      if (newChatBtn) {
        newChatBtn.addEventListener('click', startNewChat);
      }
    }

    // Connect to WebSocket
    function connectWebSocket() {
      updateConnectionStatus('connecting', 'Connecting...');
      
      try {
        socket = new WebSocket("ws://localhost:8000/ws/chat");
        
        socket.onopen = () => {
          console.log("WebSocket connected");
          isConnected = true;
          updateConnectionStatus('connected', 'Connected');
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
          
          // Try to reconnect after 3 seconds
          setTimeout(connectWebSocket, 3000);
        };

        socket.onerror = (error) => {
          console.error("WebSocket error:", error);
          updateConnectionStatus('disconnected', 'Connection error');
        };
      } catch (error) {
        console.error("Failed to connect WebSocket:", error);
        updateConnectionStatus('disconnected', 'Connection failed');
        
        // Try to reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000);
      }
    }

    // Update connection status UI
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

    // Handle incoming WebSocket messages
    function handleWebSocketMessage(data) {
      if (data.type === "session_start") {
        sessionId = data.session_id;
        appendMessage("system", "Session started. You can now upload documents or ask questions.");
      }
      if (data.type === "history" && data.messages) {
        data.messages.forEach(msg => appendMessage(msg.role, msg.content));
      }
      if (data.type === "assistant_message") {
        appendMessage("assistant", data.content);
      }
      if (data.error) {
        appendMessage("system", `Error: ${data.error}`);
      }
    }

    // Send message function
    function sendMessage() {
      const message = chatInput.value.trim();
      if (message && isConnected) {
        appendMessage("user", message);
        socket.send(JSON.stringify({ query: message }));
        chatInput.value = "";
      } else if (!isConnected) {
        appendMessage("system", "Not connected to server. Please wait...");
      }
    }

    // Upload document function - Connected to your FastAPI endpoint
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

      // Connected to your document upload endpoint
      fetch("http://localhost:8000/documents/upload", {
        method: "POST",
        body: formData
      }).then(resp => resp.json())
        .then(data => {
          appendMessage("system", data.message || "Upload complete.");
          // if (data.chunks_sample) {
          //   appendMessage("system", "Preview: " + data.chunks_sample.join(" ; "));
          // }
        }).catch(err => {
          appendMessage("system", `Upload error: ${err}`);
        });
    }

    // Append message to chat with vertical scrolling
    function appendMessage(role, text) {
      // Hide welcome message when first message is added
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
        profileDiv.innerHTML = '<img src="frontend\assets\Elara_logo.png" class="w-full h-full rounded-full object-cover" alt="Elara AI">';
        // Fallback to icon if image fails to load
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
      
      // Simple markdown parsing (bold and italic)
      let formattedText = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code class="bg-gray-800 px-1 py-0.5 rounded">$1</code>');
      
      contentDiv.innerHTML = formattedText;
      
      messageDiv.appendChild(profileDiv);
      messageDiv.appendChild(contentDiv);
      
      chatMessages.appendChild(messageDiv);
      
      // Scroll to bottom to show new message
      chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }

    // Start a new conversation
    function startNewChat() {
      // Clear chat messages
      chatMessages.innerHTML = '';
      
      // Show welcome message
      welcomeMessage.style.display = 'flex';
      
      // Reset session
      sessionId = null;
      
      // Send session reset request to server if connected
      if (isConnected) {
        socket.send(JSON.stringify({ type: "new_session" }));
        appendMessage("system", "Starting new conversation...");
      } else {
        appendMessage("system", "Please wait for connection to start a new conversation.");
      }
    }

    // Initialize the application when DOM is loaded
    document.addEventListener('DOMContentLoaded', init);