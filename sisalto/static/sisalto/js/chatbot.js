// AI Chatbot — server-side endpoint version

let chatbotState = {
    isMinimized: true,
    isProcessing: false,
    messageHistory: []
};

document.addEventListener('DOMContentLoaded', function() {
    initializeChatbot();
});

function initializeChatbot() {
    updateChatbotToggleIcon();
}

function toggleChatbot() {
    const chatbot = document.getElementById('ai-chatbot');
    const toggleIcon = document.querySelector('#chatbot-toggle i');

    chatbotState.isMinimized = !chatbotState.isMinimized;

    if (chatbotState.isMinimized) {
        chatbot.classList.add('chatbot-minimized');
        toggleIcon.className = 'fas fa-chevron-up';
    } else {
        chatbot.classList.remove('chatbot-minimized');
        toggleIcon.className = 'fas fa-chevron-down';
        setTimeout(() => {
            document.getElementById('chatbot-input-field').focus();
        }, 300);
    }
}

function updateChatbotToggleIcon() {
    const toggleIcon = document.querySelector('#chatbot-toggle i');
    if (chatbotState.isMinimized) {
        toggleIcon.className = 'fas fa-chevron-up';
    } else {
        toggleIcon.className = 'fas fa-chevron-down';
    }
}

function handleChatbotKeypress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendChatbotMessage();
    }
}

async function sendChatbotMessage() {
    const inputField = document.getElementById('chatbot-input-field');
    const message = inputField.value.trim();

    if (!message || chatbotState.isProcessing) return;

    inputField.value = '';
    addMessageToChat(message, 'user');

    chatbotState.isProcessing = true;
    showTypingIndicator();

    try {
        const reply = await sendToServer(message);
        addMessageToChat(reply, 'bot');
    } catch (error) {
        let errorMessage = 'Anteeksi, tapahtui virhe. Yritä uudelleen hetken päästä.';
        if (error.message) {
            errorMessage = error.message;
        }
        addMessageToChat(errorMessage, 'bot');
    } finally {
        chatbotState.isProcessing = false;
        hideTypingIndicator();
    }
}

async function sendToServer(userMessage) {
    const epaId = document.body.dataset.epaId || null;
    const payload = {
        message: userMessage,
        history: chatbotState.messageHistory.slice(-20),
        epa_id: epaId,
    };

    const response = await fetch('/api/tutor/chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.error || `Palvelinvirhe: ${response.status}`);
    }

    const data = await response.json();
    return data.reply;
}

function addMessageToChat(message, sender) {
    const messagesContainer = document.getElementById('chatbot-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chatbot-message ${sender}-message`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = sender === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';

    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = message;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    chatbotState.messageHistory.push({
        role: sender === 'user' ? 'user' : 'assistant',
        content: message
    });
}

function showTypingIndicator() {
    const statusDiv = document.getElementById('chatbot-status');
    statusDiv.className = 'chatbot-status typing';
    statusDiv.innerHTML = `
        <div class="typing-indicator">
            <span>AI kirjoittaa</span>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
}

function hideTypingIndicator() {
    const statusDiv = document.getElementById('chatbot-status');
    statusDiv.className = 'chatbot-status';
    statusDiv.innerHTML = '';
}

function clearChatHistory() {
    if (confirm('Haluatko tyhjentää keskusteluhistorian?')) {
        chatbotState.messageHistory = [];
        const messagesContainer = document.getElementById('chatbot-messages');
        messagesContainer.innerHTML = `
            <div class="chatbot-message bot-message">
                <div class="message-avatar"><i class="fas fa-robot"></i></div>
                <div class="message-content">
                    Hei! Olen AI-tutorisitä. Voin auttaa sinua sairaalafysiikan opiskelussa. Kysy minulta mitä tahansa!
                </div>
            </div>
        `;
    }
}
