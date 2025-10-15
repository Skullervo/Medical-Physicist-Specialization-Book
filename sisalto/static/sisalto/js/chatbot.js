// AI Chatbot JavaScript functionality

let chatbotState = {
    isMinimized: true,
    isProcessing: false,
    apiKey: null,
    messageHistory: []
};

// Initialize chatbot on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeChatbot();
});

function initializeChatbot() {
    // Check if API key is stored
    const storedKey = localStorage.getItem('openai_api_key');
    if (storedKey) {
        chatbotState.apiKey = storedKey;
        console.log('API key loaded from storage');
    }
    
    console.log('Chatbot initialized');
    
    // Set initial state
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
        
        // Focus input when opening
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
    
    if (!message || chatbotState.isProcessing) {
        return;
    }
    
    console.log('Sending message:', message);
    
    // Test mode - check if message starts with "test:"
    if (message.toLowerCase().startsWith('test:')) {
        const testMessage = message.substring(5).trim();
        inputField.value = '';
        addMessageToChat(testMessage, 'user');
        
        setTimeout(() => {
            addMessageToChat(
                `Tämä on testiviesti. Kysyit: "${testMessage}". ` +
                `Röntgenkuvantaminen perustuu röntgensäteiden absorptioon kudoksissa. ` +
                `Luukudos absorboi röntgensäteitä enemmän kuin pehmytkudokset, ` +
                `mikä luo kontrastin kuvaan.`,
                'bot'
            );
        }, 1000);
        return;
    }
    
    // Check if API key is available
    if (!chatbotState.apiKey) {
        console.log('No API key, prompting user');
        await promptForApiKey();
        if (!chatbotState.apiKey) {
            console.log('User cancelled API key prompt');
            return;
        }
    }
    
    // Clear input
    inputField.value = '';
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    
    // Set processing state
    chatbotState.isProcessing = true;
    showTypingIndicator();
    
    try {
        console.log('Calling OpenAI API...');
        // Send message to ChatGPT API
        const response = await sendToOpenAI(message);
        console.log('Received response:', response);
        
        // Add AI response to chat
        addMessageToChat(response, 'bot');
        
    } catch (error) {
        console.error('Chatbot error:', error);
        let errorMessage = 'Anteeksi, tapahtui virhe. Yritä uudelleen hetken päästä.';
        
        if (error.message.includes('API-avain')) {
            errorMessage = 'Virheellinen API-avain. Tarkista avaimesi ja yritä uudelleen.';
            chatbotState.apiKey = null;
            localStorage.removeItem('openai_api_key');
        } else if (error.message.includes('429')) {
            errorMessage = 'API-kutsurajat ylitetty. Yritä hetken päästä.';
        }
        
        addMessageToChat(errorMessage, 'bot');
        showErrorStatus(error.message);
    } finally {
        chatbotState.isProcessing = false;
        hideTypingIndicator();
        clearStatus();
    }
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
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Store in history
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

function showErrorStatus(message) {
    const statusDiv = document.getElementById('chatbot-status');
    statusDiv.className = 'chatbot-status error';
    statusDiv.textContent = message;
}

function clearStatus() {
    setTimeout(() => {
        const statusDiv = document.getElementById('chatbot-status');
        statusDiv.className = 'chatbot-status';
        statusDiv.innerHTML = '';
    }, 3000);
}

async function promptForApiKey() {
    const apiKey = prompt(
        'Anna OpenAI API-avaimesi käyttääksesi AI-assistenttia:\n\n' +
        'Voit hankkia API-avaimen osoitteesta: https://platform.openai.com/api-keys'
    );
    
    if (apiKey && apiKey.trim()) {
        chatbotState.apiKey = apiKey.trim();
        // Store in localStorage for session (consider more secure storage for production)
        localStorage.setItem('openai_api_key', apiKey.trim());
        return true;
    }
    
    return false;
}

async function sendToOpenAI(userMessage) {
    // Check for stored API key first
    if (!chatbotState.apiKey) {
        const storedKey = localStorage.getItem('openai_api_key');
        if (storedKey) {
            chatbotState.apiKey = storedKey;
        }
    }
    
    if (!chatbotState.apiKey) {
        throw new Error('API key not available');
    }
    
    console.log('Preparing API request...');
    
    // Prepare messages for API call
    const messages = [
        {
            role: 'system',
            content: `Olet asiantunteva AI-assistentti, joka auttaa sairaalafysiikan opiskelijoita. 
            Sinun erikoisalueesi ovat:
            - Radiologia (natiivikuvantaminen, tietokonetomografia, magneettikuvaus, ultraääni, mammografia, läpivalaisu, angiografia)
            - Sädehoito (ulkoinen ja sisäinen sädehoito, dosimetria, sädebiologia, suojelu)
            - Isotooppilääketiede (gammakuvaus, PET, SPECT, radionuklidihoidot, radiofarmasia)
            - Kliininen neurofysiologia (EEG, EMG, herätevastetutkimukset, IOM, TMS)
            - Fysiologia (verenkierto, hengitys, EKG, keuhkofunktio, luuston mineraalitiheys)
            
            Vastaa aina suomeksi. Ole käytännönläheinen ja selitä asiat selkeästi. 
            Jos kysymys ei liity sairaalafysiikkaan, ohjaa opiskelija takaisin aihealueelle.`
        },
        ...chatbotState.messageHistory.slice(-10), // Keep last 10 messages for context
        {
            role: 'user',
            content: userMessage
        }
    ];
    
    console.log('Making API request to OpenAI...');
    
    try {
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${chatbotState.apiKey}`
            },
            body: JSON.stringify({
                model: 'gpt-3.5-turbo',
                messages: messages,
                max_tokens: 500,
                temperature: 0.7,
                presence_penalty: 0.1,
                frequency_penalty: 0.1
            })
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('API Error Response:', errorText);
            
            if (response.status === 401) {
                // Invalid API key
                localStorage.removeItem('openai_api_key');
                chatbotState.apiKey = null;
                throw new Error('Virheellinen API-avain. Tarkista avaimesi.');
            } else if (response.status === 429) {
                throw new Error('API-kutsurajat ylitetty. Yritä hetken päästä.');
            } else if (response.status === 403) {
                throw new Error('API-avain ei ole aktivoitu tai sinulla ei ole oikeuksia.');
            } else {
                throw new Error(`API-virhe: ${response.status} - ${errorText}`);
            }
        }
        
        const data = await response.json();
        console.log('API Response data:', data);
        
        if (data.choices && data.choices.length > 0) {
            return data.choices[0].message.content.trim();
        } else {
            throw new Error('Tyhjä vastaus API:sta');
        }
    } catch (error) {
        if (error instanceof TypeError && error.message.includes('fetch')) {
            throw new Error('Verkkovirhe: Tarkista internetyhteytesi');
        }
        throw error;
    }
}

// Utility function to clear chat history
function clearChatHistory() {
    if (confirm('Haluatko tyhjentää keskusteluhistorian?')) {
        chatbotState.messageHistory = [];
        const messagesContainer = document.getElementById('chatbot-messages');
        
        // Keep only the initial welcome message
        messagesContainer.innerHTML = `
            <div class="chatbot-message bot-message">
                <div class="message-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    Hei! Olen AI-assistenttisi. Voin auttaa sinua sairaalafysiikan opiskelussa. Kysy minulta mitä tahansa radiologiasta, sädehoidosta, isotooppilääketieteestä tai KNF:stä!
                </div>
            </div>
        `;
    }
}

// Add clear history button functionality (you can add this to the UI if needed)
function addClearHistoryButton() {
    const header = document.querySelector('.chatbot-header .chatbot-controls');
    const clearBtn = document.createElement('button');
    clearBtn.className = 'chatbot-btn-icon';
    clearBtn.innerHTML = '<i class="fas fa-trash"></i>';
    clearBtn.title = 'Tyhjennä historia';
    clearBtn.onclick = function(e) {
        e.stopPropagation();
        clearChatHistory();
    };
    
    header.insertBefore(clearBtn, header.firstChild);
}