/**
 * Neeraj's AI Portfolio Assistant - Frontend Chatbot Widget
 * Integrates with FastAPI + LangGraph + Google Gemini backend
 */

(function () {
  // Backend API URL: Connects to backend-portfolio-b3qx.onrender.com in production, or localhost in development
  function resolveApiBaseUrl() {
    if (typeof window !== "undefined" && window.NEERAJ_AI_API_URL) {
      return window.NEERAJ_AI_API_URL.replace(/\/+$/, "");
    }
    // If running on localhost / local dev port, use local FastAPI port 8000
    if (typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")) {
      return "http://localhost:8000";
    }
    // Production Render backend service
    return "https://backend-portfolio-b3qx.onrender.com";
  }

  const API_BASE_URL = resolveApiBaseUrl();

  const STORAGE_KEY = "neeraj_ai_thread_id";

  // Session Thread ID management
  function getOrCreateThreadId() {
    let threadId = sessionStorage.getItem(STORAGE_KEY);
    if (!threadId) {
      threadId = "session-" + Math.random().toString(36).substring(2, 10) + Date.now().toString(36);
      sessionStorage.setItem(STORAGE_KEY, threadId);
    }
    return threadId;
  }

  function resetThreadId() {
    const newThreadId = "session-" + Math.random().toString(36).substring(2, 10) + Date.now().toString(36);
    sessionStorage.setItem(STORAGE_KEY, newThreadId);
    return newThreadId;
  }

  // Format assistant response text (markdown basic parsing)
  function formatAssistantMessage(rawText) {
    if (!rawText) return "";
    let formatted = rawText
      // Escape HTML entities to prevent XSS
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    // Bold **text**
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

    // Inline `code`
    formatted = formatted.replace(/`([^`]+)`/g, "<code>$1</code>");

    // URLs to clickable links
    formatted = formatted.replace(
      /(https?:\/\/[^\s<]+)/g,
      '<a href="$1" target="_blank" rel="noopener noreferrer" class="chat-inline-link">$1 <i class="fa-solid fa-arrow-up-right-from-square"></i></a>'
    );

    // Markdown bullet points (- or *)
    formatted = formatted.replace(/(?:^|\n)[-*•]\s+(.*?)(?=\n|$)/g, '<li class="chat-list-item">$1</li>');
    if (formatted.includes('<li class="chat-list-item">')) {
      formatted = formatted.replace(/(<li class="chat-list-item">.*?<\/li>)+/gs, '<ul class="chat-list">$&</ul>');
    }

    // Paragraph breaks
    formatted = formatted.replace(/\n\n+/g, "<br><br>").replace(/\n/g, "<br>");

    return formatted;
  }

  // Initialize Chatbot UI
  function initChatbot() {
    // Prevent duplicate initialization
    if (document.getElementById("neeraj-chatbot-container")) return;

    // Inject styles if needed or root elements
    const chatbotContainer = document.createElement("div");
    chatbotContainer.id = "neeraj-chatbot-container";
    chatbotContainer.className = "neeraj-chatbot-container";

    chatbotContainer.innerHTML = `
      <!-- Floating Toggle Button -->
      <button id="chatbot-launcher-btn" class="chatbot-launcher" aria-label="Open Neeraj's AI Assistant" title="Chat with Neeraj's AI Assistant">
        <div class="launcher-glow"></div>
        <div class="launcher-avatar-wrap">
          <img src="/chatbot-avatar.png" alt="Neeraj AI" class="launcher-avatar-img" />
          <span class="launcher-online-badge"></span>
        </div>
        <span class="launcher-tooltip">Ask Neeraj's AI</span>
      </button>

      <!-- Chatbot Floating Window -->
      <div id="chatbot-window" class="chatbot-window closed" role="dialog" aria-modal="true" aria-label="Neeraj's AI Assistant Chat">
        <!-- Header -->
        <div class="chatbot-header">
          <div class="header-info">
            <div class="header-avatar">
              <img src="/chatbot-avatar.png" alt="Neeraj AI Assistant" class="header-avatar-img" />
              <span class="status-pulse-dot"></span>
            </div>
            <div class="header-titles">
              <h3 class="header-name">Neeraj's AI Assistant</h3>
              <span class="header-status"><span class="status-dot"></span> Online</span>
            </div>
          </div>
          <div class="header-controls">
            <button id="chatbot-clear-btn" class="header-btn" title="Reset Conversation" aria-label="Clear chat">
              <i class="fa-solid fa-rotate-right"></i>
            </button>
            <button id="chatbot-close-btn" class="header-btn" title="Close Chat" aria-label="Close chat">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>
        </div>

        <!-- Messages Area -->
        <div id="chatbot-messages" class="chatbot-messages">
          <!-- Initial Welcome Message -->
          <div class="chat-msg assistant-msg">
            <div class="msg-avatar"><img src="/chatbot-avatar.png" alt="AI" class="msg-avatar-img" /></div>
            <div class="msg-content">
              <p>Hello! I am <strong>Neeraj's AI Assistant</strong>, representing Neeraj Kumar's AI/ML engineering portfolio.</p>
              <div class="msg-quick-actions" id="initial-quick-actions">
                <button class="quick-chip" data-query="Who is Neeraj?">About Neeraj</button>
                <button class="quick-chip" data-query="What projects has Neeraj built?">Projects</button>
                <button class="quick-chip" data-query="What are Neeraj's skills?">Skills</button>
                <button class="quick-chip" data-query="Give me his resume.">Resume</button>
                <button class="quick-chip" data-query="What is Neeraj's GitHub?">GitHub</button>
                <button class="quick-chip" data-query="What is Neeraj's Kaggle?">Kaggle</button>
                <button class="quick-chip" data-query="What is Neeraj's LinkedIn?">LinkedIn</button>
                <button class="quick-chip chip-highlight" data-query="I want to contact Neeraj.">Contact Neeraj</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Typing Indicator -->
        <div id="chatbot-typing" class="chatbot-typing hidden">
          <div class="typing-bubble">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
          </div>
          <span class="typing-text">Neeraj's AI is thinking...</span>
        </div>

        <!-- Input Area -->
        <form id="chatbot-input-form" class="chatbot-input-form">
          <textarea
            id="chatbot-textarea"
            class="chatbot-textarea"
            placeholder="Ask about projects, skills, resume, or contact Neeraj..."
            rows="1"
            maxlength="1500"
            required
          ></textarea>
          <button type="submit" id="chatbot-send-btn" class="chatbot-send-btn" aria-label="Send message" title="Send message">
            <i class="fa-solid fa-paper-plane"></i>
          </button>
        </form>
      </div>
    `;

    document.body.appendChild(chatbotContainer);

    // Elements
    const launcherBtn = document.getElementById("chatbot-launcher-btn");
    const chatWindow = document.getElementById("chatbot-window");
    const closeBtn = document.getElementById("chatbot-close-btn");
    const clearBtn = document.getElementById("chatbot-clear-btn");
    const messagesArea = document.getElementById("chatbot-messages");
    const typingIndicator = document.getElementById("chatbot-typing");
    const inputForm = document.getElementById("chatbot-input-form");
    const textarea = document.getElementById("chatbot-textarea");
    const sendBtn = document.getElementById("chatbot-send-btn");

    let isThinking = false;

    // Toggle Chat Window
    function toggleChat(open) {
      const isOpen = open !== undefined ? open : chatWindow.classList.contains("closed");
      if (isOpen) {
        chatWindow.classList.remove("closed");
        launcherBtn.classList.add("active");
        setTimeout(() => textarea.focus(), 150);
      } else {
        chatWindow.classList.add("closed");
        launcherBtn.classList.remove("active");
      }
    }

    launcherBtn.addEventListener("click", () => toggleChat());
    closeBtn.addEventListener("click", () => toggleChat(false));

    // Auto-scroll to bottom of messages
    function scrollToBottom() {
      messagesArea.scrollTop = messagesArea.scrollHeight;
    }

    // Append Message to UI
    function appendMessage(role, text, options = {}) {
      const msgWrapper = document.createElement("div");
      msgWrapper.className = `chat-msg ${role === "user" ? "user-msg" : "assistant-msg"}`;

      if (role === "assistant") {
        let contentHtml = `<div class="msg-avatar"><img src="/chatbot-avatar.png" alt="AI" class="msg-avatar-img" /></div><div class="msg-content">`;
        contentHtml += `<div class="msg-body">${formatAssistantMessage(text)}</div>`;

        // If structured action link exists
        if (options.url) {
          const actionText = options.type === "link" ? (options.url.includes("drive.google") ? "Open Resume (Google Drive)" : "Open Link") : "Open Link";
          contentHtml += `
            <div class="msg-action-card">
              <a href="${options.url}" target="_blank" rel="noopener noreferrer" class="btn-chat-action">
                <i class="fa-solid fa-arrow-up-right-from-square"></i> ${actionText}
              </a>
            </div>
          `;
        }

        // Quick action chips
        if (options.quick_actions && options.quick_actions.length > 0) {
          contentHtml += `<div class="msg-quick-actions">`;
          options.quick_actions.forEach(actionText => {
            contentHtml += `<button class="quick-chip" data-query="${actionText}">${actionText}</button>`;
          });
          contentHtml += `</div>`;
        }

        contentHtml += `</div>`;
        msgWrapper.innerHTML = contentHtml;
      } else {
        msgWrapper.innerHTML = `
          <div class="msg-content">
            <div class="msg-body">${text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}</div>
          </div>
        `;
      }

      messagesArea.appendChild(msgWrapper);
      scrollToBottom();
    }

    // Send Message to Backend
    async function sendMessage(userQuery) {
      const query = (userQuery || textarea.value).trim();
      if (!query || isThinking) return;

      // Clear input
      textarea.value = "";
      textarea.style.height = "auto";

      // Display User Message
      appendMessage("user", query);

      // Set Thinking State
      isThinking = true;
      typingIndicator.classList.remove("hidden");
      sendBtn.disabled = true;
      scrollToBottom();

      const threadId = getOrCreateThreadId();

      try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            message: query,
            thread_id: threadId
          })
        });

        if (!response.ok) {
          throw new Error(`Server returned status: ${response.status}`);
        }

        const data = await response.json();
        typingIndicator.classList.add("hidden");
        isThinking = false;
        sendBtn.disabled = false;

        appendMessage("assistant", data.response, {
          type: data.type,
          url: data.url,
          quick_actions: data.quick_actions
        });

      } catch (err) {
        console.error("Chatbot API Error:", err);
        typingIndicator.classList.add("hidden");
        isThinking = false;
        sendBtn.disabled = false;

        appendMessage(
          "assistant",
          "I'm having trouble communicating with the server right now. If you need to contact Neeraj directly, please use the Contact Us section on the page!",
          {
            quick_actions: ["Who is Neeraj?", "Skills", "Resume"]
          }
        );
      }
    }

    // Form submit handler
    inputForm.addEventListener("submit", (e) => {
      e.preventDefault();
      sendMessage();
    });

    // Auto-expand textarea & Enter to submit (Shift+Enter for newline)
    textarea.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    textarea.addEventListener("input", () => {
      textarea.style.height = "auto";
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + "px";
    });

    // Delegate Quick Chip Clicks
    messagesArea.addEventListener("click", (e) => {
      const chip = e.target.closest(".quick-chip");
      if (chip) {
        const query = chip.getAttribute("data-query") || chip.textContent;
        sendMessage(query);
      }
    });

    // Clear Chat
    clearBtn.addEventListener("click", () => {
      resetThreadId();
      messagesArea.innerHTML = `
        <div class="chat-msg assistant-msg">
          <div class="msg-avatar"><img src="/chatbot-avatar.png" alt="AI" class="msg-avatar-img" /></div>
          <div class="msg-content">
            <p>Conversation reset. How can I help you regarding Neeraj Kumar's portfolio?</p>
            <div class="msg-quick-actions">
              <button class="quick-chip" data-query="Who is Neeraj?">About Neeraj</button>
              <button class="quick-chip" data-query="What projects has Neeraj built?">Projects</button>
              <button class="quick-chip" data-query="What are Neeraj's skills?">Skills</button>
              <button class="quick-chip" data-query="Give me his resume.">Resume</button>
              <button class="quick-chip chip-highlight" data-query="I want to contact Neeraj.">Contact Neeraj</button>
            </div>
          </div>
        </div>
      `;
      scrollToBottom();
    });
  }

  // Initialize once DOM is loaded
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initChatbot);
  } else {
    initChatbot();
  }
})();
