document.addEventListener("DOMContentLoaded", () => {
    // 1. Create and inject chatbot HTML elements dynamically
    const chatbotContainer = document.createElement("div");
    chatbotContainer.id = "dinestay-chatbot-container";
    
    chatbotContainer.innerHTML = `
        <!-- Chat Bubble Button -->
        <button id="chatbot-bubble" class="chatbot-bubble-btn" aria-label="Open Chatbot">
            <span class="bubble-icon">💬</span>
        </button>

        <!-- Chat Popup Window -->
        <div id="chatbot-popup" class="chatbot-popup-window hidden">
            <!-- Header -->
            <div class="chatbot-header">
                <div class="chatbot-header-info">
                    <span class="chatbot-header-avatar">🏨</span>
                    <div>
                        <h3 class="chatbot-header-title">DineStay Assistant</h3>
                        <span class="chatbot-header-status">Online</span>
                    </div>
                </div>
                <button id="chatbot-close" class="chatbot-close-btn" aria-label="Close Chat">&times;</button>
            </div>

            <!-- Messages Area -->
            <div id="chatbot-messages" class="chatbot-messages-container">
                <div class="chatbot-message bot">
                    <div class="message-content">Hello! Welcome to DineStay. How can I help you with rooms, menu, pricing, or bookings today?</div>
                </div>
            </div>

            <!-- Typing Indicator (hidden by default) -->
            <div id="chatbot-typing" class="chatbot-typing-indicator hidden">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>

            <!-- Input Form Area -->
            <div class="chatbot-input-area">
                <input type="text" id="chatbot-input" placeholder="Type your message here..." autocomplete="off">
                <button id="chatbot-send" class="chatbot-send-btn" aria-label="Send Message">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                        <path d="M2 21l21-9L2 3v7l15 2-15 2v7z"/>
                    </svg>
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(chatbotContainer);

    // 2. Elements references
    const bubble = document.getElementById("chatbot-bubble");
    const popup = document.getElementById("chatbot-popup");
    const closeBtn = document.getElementById("chatbot-close");
    const input = document.getElementById("chatbot-input");
    const sendBtn = document.getElementById("chatbot-send");
    const messagesContainer = document.getElementById("chatbot-messages");
    const typingIndicator = document.getElementById("chatbot-typing");

    // Toggle chatbot popup
    bubble.addEventListener("click", () => {
        popup.classList.toggle("hidden");
        if (!popup.classList.contains("hidden")) {
            input.focus();
            scrollToBottom();
        }
    });

    closeBtn.addEventListener("click", () => {
        popup.classList.add("hidden");
    });

    // Send logic
    async function sendMessage() {
        const messageText = input.value.trim();
        if (!messageText) return;

        // Clear input
        input.value = "";

        // Add user message to UI
        appendMessage(messageText, "user");
        scrollToBottom();

        // Show typing indicator
        typingIndicator.classList.remove("hidden");
        // Move typing indicator to bottom of the container
        messagesContainer.appendChild(typingIndicator);
        scrollToBottom();

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: messageText })
            });

            if (!response.ok) {
                throw new Error("Failed to get response");
            }

            const data = await response.json();
            
            // Hide typing indicator
            typingIndicator.classList.add("hidden");

            // Add bot reply to UI
            appendMessage(data.reply, "bot");
            scrollToBottom();
        } catch (error) {
            console.error("Chat error:", error);
            typingIndicator.classList.add("hidden");
            appendMessage("Sorry, I am having trouble connecting right now. Please try again later.", "bot error-message");
            scrollToBottom();
        }
    }

    // Append message HTML
    function appendMessage(text, sender) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `chatbot-message ${sender}`;
        
        // Basic formatting for lines (converting newlines to <br>)
        const formattedText = text.replace(/\n/g, "<br>");
        
        messageDiv.innerHTML = `
            <div class="message-content">${formattedText}</div>
        `;
        messagesContainer.appendChild(messageDiv);
    }

    // Scroll container to bottom
    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Event listeners for sending
    sendBtn.addEventListener("click", sendMessage);
    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            sendMessage();
        }
    });
});
