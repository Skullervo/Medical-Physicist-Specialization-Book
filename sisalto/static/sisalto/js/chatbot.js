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
    // Add ask-AI buttons to theory section headings (after page renders)
    setTimeout(initSectionAskAI, 600);
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
    if (!statusDiv) return;
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
    if (!statusDiv) return;
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
                    Hei! Olen AI-assistentti. Voin auttaa sinua sairaalafyysikon erikoistumiseen liittyvissä kysymyksissä.
                </div>
            </div>
        `;
        const panel = document.getElementById('chatbot-settings-panel');
        if (panel) panel.style.display = 'none';
    }
}

function toggleChatbotSettings() {
    const panel = document.getElementById('chatbot-settings-panel');
    if (panel) panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
}

// Alias for onkeypress handler in template
function handleChatbotEnter(event) {
    handleChatbotKeypress(event);
}

// ── Section Ask-AI buttons ────────────────────────────────────────────────
function initSectionAskAI() {
    // Modality name from page h1
    const modalityEl = document.querySelector('.page-header h1, .modality-title, h1.page-title, header h1');
    const modalityName = modalityEl ? modalityEl.textContent.trim() : document.title.trim();

    document.querySelectorAll('.theory-content h2, .theory-content h3').forEach(heading => {
        if (heading.querySelector('.section-ask-ai-btns')) return; // already processed

        const headingText = heading.textContent.trim();

        // Which tab panel does this heading belong to?
        const panel = heading.closest('.theory-panel');
        let tabName = '';
        if (panel) {
            const tabId = panel.id ? panel.id.replace('panel-', '') : '';
            const tabBtn = tabId ? document.querySelector(`.theory-tab[data-tab="${tabId}"]`) : null;
            if (tabBtn) tabName = tabBtn.textContent.trim();
        }

        // Parent h2 heading (for h3 elements — gives hierarchy)
        let parentHeading = '';
        if (heading.tagName === 'H3') {
            let prev = heading.previousElementSibling;
            while (prev) {
                if (prev.tagName === 'H2') { parentHeading = prev.textContent.trim(); break; }
                prev = prev.previousElementSibling;
            }
        }

        // Short text context from next siblings
        let snippetText = '';
        let sibling = heading.nextElementSibling;
        while (sibling && snippetText.length < 350) {
            if (sibling.matches('h2, h3')) break;
            snippetText += sibling.textContent.trim() + ' ';
            sibling = sibling.nextElementSibling;
        }
        snippetText = snippetText.trim().slice(0, 350);

        // Build full context string for the API message
        const parts = [];
        if (modalityName) parts.push(`Modaliteetti: ${modalityName}`);
        if (tabName) parts.push(`Välilehti: ${tabName}`);
        if (parentHeading) parts.push(`Yläotsikko: ${parentHeading}`);
        if (snippetText) parts.push(`Sivun teksti: "${snippetText}…"`);
        const fullContext = parts.join(' | ');

        const wrapper = document.createElement('span');
        wrapper.className = 'section-ask-ai-btns';

        // Text (chat) button
        const textBtn = document.createElement('button');
        textBtn.className = 'section-ask-ai-btn section-ask-ai-text';
        textBtn.title = 'Kysy AI:lta tästä aiheesta';
        textBtn.innerHTML = '<i class="fas fa-robot"></i>';
        textBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            askAIAboutSection(headingText, fullContext, false);
        });

        // Voice button
        const voiceBtn = document.createElement('button');
        voiceBtn.className = 'section-ask-ai-btn section-ask-ai-voice';
        voiceBtn.title = 'Kysy AI:lta — vastaa äänellä';
        voiceBtn.innerHTML = '<i class="fas fa-robot"></i><i class="fas fa-volume-up"></i>';
        voiceBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            askAIAboutSection(headingText, fullContext, true);
        });

        wrapper.appendChild(textBtn);
        wrapper.appendChild(voiceBtn);
        heading.appendChild(wrapper);
    });
}

async function askAIAboutSection(headingText, fullContext, withVoice) {
    // Open chatbot if minimized
    if (chatbotState.isMinimized) {
        toggleChatbot();
        await new Promise(r => setTimeout(r, 350));
    }

    if (chatbotState.isProcessing) return;

    // Message shown in chat (concise)
    const displayMessage = `Kerro lisää: ${headingText}`;
    // Full message sent to AI (with context)
    const apiMessage = `${fullContext ? fullContext + '\n\n' : ''}Selitä tätä aihetta tarkemmin sairaalafyysikon erikoistumiskoulutuksen näkökulmasta: "${headingText}"`;

    addMessageToChat(displayMessage, 'user');
    // Also push the full message to history so AI has context in follow-up questions
    chatbotState.messageHistory.push({ role: 'user', content: apiMessage });

    chatbotState.isProcessing = true;
    showTypingIndicator();

    try {
        const epaId = document.body.dataset.epaId || null;
        const payload = {
            message: apiMessage,
            history: chatbotState.messageHistory.slice(-21, -1), // history before this message
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
        const reply = data.reply;
        addMessageToChat(reply, 'bot');
        if (withVoice) speakBotReply(reply);
    } catch (error) {
        addMessageToChat(error.message || 'Virhe. Yritä uudelleen.', 'bot');
    } finally {
        chatbotState.isProcessing = false;
        hideTypingIndicator();
    }
}

// ── Expand / collapse ──────────────────────────────────────────────────────
function toggleChatbotExpand() {
    const chatbot = document.getElementById('ai-chatbot');
    const btn = document.getElementById('chatbot-expand-btn');
    const isExpanded = chatbot.classList.toggle('chatbot-expanded');
    if (btn) btn.querySelector('i').className = isExpanded ? 'fas fa-compress-alt' : 'fas fa-expand-alt';
    // Scroll messages to bottom after resize
    setTimeout(() => {
        const msgs = document.getElementById('chatbot-messages');
        if (msgs) msgs.scrollTop = msgs.scrollHeight;
    }, 300);
}

// ── Voice conversation ─────────────────────────────────────────────────────
let recognition = null;
let chatbotVoiceActive = false;
let chatbotCurrentAudio = null;

function toggleChatbotMic() {
    // If bot is speaking, stop it
    if (chatbotCurrentAudio) {
        chatbotCurrentAudio.pause();
        chatbotCurrentAudio = null;
        setChatbotMicState('idle');
        return;
    }
    if (chatbotVoiceActive) {
        stopChatbotMic();
    } else {
        startChatbotMic();
    }
}

function startChatbotMic() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert('Selaimesi ei tue puheentunnistusta. Kokeile Chrome tai Edge.');
        return;
    }

    recognition = new SpeechRecognition();
    recognition.lang = 'fi-FI';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = function() {
        chatbotVoiceActive = true;
        setChatbotMicState('recording');
    };

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        const inputField = document.getElementById('chatbot-input-field');
        if (inputField) inputField.value = transcript;
        stopChatbotMic();
        sendChatbotMessageWithVoice(transcript);
    };

    recognition.onerror = function(event) {
        console.error('STT error:', event.error);
        stopChatbotMic();
    };

    recognition.onend = function() {
        if (chatbotVoiceActive) stopChatbotMic();
    };

    recognition.start();
}

function stopChatbotMic() {
    chatbotVoiceActive = false;
    setChatbotMicState('idle');
    if (recognition) {
        try { recognition.stop(); } catch(e) {}
        recognition = null;
    }
}

function setChatbotMicState(state) {
    const btn = document.getElementById('chatbot-mic-btn');
    if (!btn) return;
    btn.classList.remove('recording', 'speaking');
    if (state === 'recording') btn.classList.add('recording');
    else if (state === 'speaking') btn.classList.add('speaking');
}

async function sendChatbotMessageWithVoice(message) {
    if (!message || chatbotState.isProcessing) return;

    const inputField = document.getElementById('chatbot-input-field');
    if (inputField) inputField.value = '';
    addMessageToChat(message, 'user');

    chatbotState.isProcessing = true;
    showTypingIndicator();

    try {
        const reply = await sendToServer(message);
        addMessageToChat(reply, 'bot');
        speakBotReply(reply);
    } catch (error) {
        const errorMessage = error.message || 'Anteeksi, tapahtui virhe. Yritä uudelleen hetken päästä.';
        addMessageToChat(errorMessage, 'bot');
    } finally {
        chatbotState.isProcessing = false;
        hideTypingIndicator();
    }
}

async function speakBotReply(text) {
    setChatbotMicState('speaking');
    try {
        const response = await fetch('/modaliteetit/api/tts/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ text: text, voice: 'onyx' }),
        });
        if (!response.ok) throw new Error('TTS failed');
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        chatbotCurrentAudio = audio;
        audio.onended = function() {
            chatbotCurrentAudio = null;
            URL.revokeObjectURL(url);
            setChatbotMicState('idle');
        };
        audio.onerror = function() {
            chatbotCurrentAudio = null;
            URL.revokeObjectURL(url);
            setChatbotMicState('idle');
        };
        audio.play();
    } catch(e) {
        console.error('TTS error:', e);
        setChatbotMicState('idle');
    }
}
