// let socket;
// let sessionId = null;

// window.onload = function() {
//   socket = new WebSocket("ws://http:/127.0.0.1:8000/ws/chat");
//   socket.onopen = () => appendMessage("system", "✅ Connected to server");

//   socket.onmessage = (event) => {
//     const data = JSON.parse(event.data);

//     if (data.type === "session_start") {
//       sessionId = data.session_id;
//       appendMessage("system", "🟢 Session started");
//     }
//     if (data.type === "history" && data.messages) {
//       data.messages.forEach(msg => appendMessage(msg.role, msg.content));
//     }
//     if (data.type === "assistant_message") {
//       appendMessage("assistant", data.content);
//     }
//     if (data.error) {
//       appendMessage("system", `⚠️ Error: ${data.error}`);
//     }
//   };

//   socket.onclose = () => appendMessage("system", "❌ Connection closed");

//   document.getElementById('send-btn').onclick = sendMessage;
//   document.getElementById('chat-input').addEventListener('keydown', function(e) {
//     if (e.key === "Enter" && !e.shiftKey) {
//       e.preventDefault();
//       sendMessage();
//     }
//   });
//   document.getElementById('file-upload').addEventListener('change', uploadDocument);
// };

// function sendMessage() {
//   const input = document.getElementById('chat-input');
//   const text = input.value.trim();
//   if (text && socket.readyState === WebSocket.OPEN) {
//     appendMessage("user", text);
//     socket.send(JSON.stringify({ query: text, session_id: sessionId }));
//     input.value = "";
//   }
// }

// function appendMessage(role, text) {
//   const parent = document.getElementById("chat-messages");
//   const div = document.createElement("div");
//   div.className = "mb-2";

//   if (role === "user") div.classList.add("text-end", "text-primary");
//   if (role === "assistant") div.classList.add("text-start", "text-info");
//   if (role === "system") div.classList.add("text-center", "text-warning", "small");

//   let prefix = role === "user" ? "You: " : role === "assistant" ? "Elara: " : "";
//   div.textContent = prefix + text;

//   parent.appendChild(div);
//   parent.scrollTop = parent.scrollHeight;
// }

// function uploadDocument(event) {
//   const files = event.target.files;
//   if (!files.length) return alert("Select a PDF file to upload.");
//   if (!sessionId) return alert("Session not established yet.");

//   const formData = new FormData();
//   formData.append("files", files[0]);
//   formData.append("session_id", sessionId);
//   formData.append("do_not_store", "false");

//   fetch("http://localhost:8000/documents/upload", {
//     method: "POST",
//     body: formData
//   }).then(resp => resp.json())
//     .then(data => {
//       appendMessage("system", data.message || "Upload complete.");
//       if (data.chunks_sample) {
//         appendMessage("system", "📄 Preview: " + data.chunks_sample.join(" ; "));
//       }
//     }).catch(err => {
//       appendMessage("system", `Upload error: ${err}`);
//     });
// }

let socket;
let sessionId = null;

window.onload = function() {
  socket = new WebSocket("ws://localhost:8000/ws/chat");
  socket.onopen = () => console.log("WebSocket connected");

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === "session_start") {
      sessionId = data.session_id;
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
  };

  socket.onclose = () => appendMessage("system", "Connection closed.");

  document.getElementById('send-btn').onclick = sendMessage;
  document.getElementById('chat-input').addEventListener('keydown', function(e) {
    if (e.key === "Enter") sendMessage();
  });
  document.getElementById('file-upload').addEventListener('change', uploadDocument);
};

function sendMessage() {
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (text && socket.readyState === WebSocket.OPEN) {
    appendMessage("user", text);
    socket.send(JSON.stringify({ query: text }));
    input.value = "";
  }
}

function appendMessage(role, text) {
  const parent = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.className = "mb-2";
  if (role === "user") div.classList.add("text-end");
  if (role === "assistant") div.classList.add("text-start", "text-blue-700");
  if (role === "system") div.classList.add("text-danger");
  let prefix = (role === "user") ? "You: " : (role === "assistant") ? "Elara: " : "";
  div.textContent = prefix + text;
  parent.appendChild(div);
  parent.scrollTop = parent.scrollHeight;
}

function uploadDocument(event) {
  const files = event.target.files;
  if (!files.length) return alert("Select a PDF file to upload.");
  if (!sessionId) return alert("Session not established yet.");
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
      if (data.chunks_sample) {
        appendMessage("system", "Preview: " + data.chunks_sample.join(" ; "));
      }
    }).catch(err => {
      appendMessage("system", `Upload error: ${err}`);
    });
}
