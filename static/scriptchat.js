window.fileCardCache = window.fileCardCache || {};

// ─── Shared download helper ───────────────────────────────────────────────
function normaliseExt(raw) {
    const m = {
        python: 'py', javascript: 'js', typescript: 'ts',
        markdown: 'md', bash: 'sh', shell: 'sh', sh: 'sh',
        jsx: 'jsx', tsx: 'tsx', html: 'html', css: 'css',
        json: 'json', yaml: 'yaml', yml: 'yml', toml: 'toml',
        rust: 'rs', go: 'go', cpp: 'cpp', c: 'c', java: 'java',
        kotlin: 'kt', swift: 'swift', rb: 'rb', ruby: 'rb',
        php: 'php', sql: 'sql', r: 'r',
    };
    const key = (raw || 'txt').toLowerCase();
    return m[key] || key;
}

function triggerDownload(filename, content) {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

document.addEventListener("DOMContentLoaded", () => {
    let chats = (JSON.parse(localStorage.getItem('iris_chats')) || []).filter(c => c.messages && c.messages.length > 0);
    let currentChatId = null;
    window.getCurrentChats = () => chats;
    window.getCurrentChatId = () => currentChatId;
    let chatActive = false;
    let currentAbortController = null;
    let isGenerating = false;
    window.selectedFiles = [];
    let chatSettings = JSON.parse(localStorage.getItem('iris_chat_settings')) || {
        max_new_tokens: 512,
        temperature: 0.6,
        top_p: 0.9,
        top_k: 40,
        repetition_penalty: 1.05,
        code_review: false
    };

    // Force migrate old bad default of 1.3 down to 1.05
    if (chatSettings.repetition_penalty === 1.3) {
        chatSettings.repetition_penalty = 1.05;
        localStorage.setItem('iris_chat_settings', JSON.stringify(chatSettings));
    }

    fetch('/get_settings')
        .then(res => res.json())
        .then(data => {
            if (Object.keys(data).length > 0) {
                chatSettings = { ...chatSettings, ...data };
                localStorage.setItem('iris_chat_settings', JSON.stringify(chatSettings));
            }
        })
        .catch(e => console.error("Failed to load backend settings:", e));

    window.getChatSettings = () => chatSettings;
    window.setChatSettings = (s) => { chatSettings = s; };
    const chatInput = document.getElementById("chatInput");
    const sendBtn = document.getElementById("sendBtn");
    const chatMessages = document.getElementById("chatMessages");
    const chatHistory = document.getElementById("chatHistory");
    const newChatBtn = document.getElementById('newChatBtn');
    const quickNewChatBtnGlobal = document.getElementById('quickNewChatBtnGlobal');
    const tempChatBtn = document.getElementById('tempChatBtn');
    const modelBtn = document.getElementById('modelBtn');
    const searchToggleBtn = document.getElementById("searchToggleBtn");
    const searchBarContainer = document.getElementById("searchBarContainer");
    const searchInput = document.getElementById("searchInput");
    const searchClearBtn = document.getElementById("searchClearBtn");
    const searchEmpty = document.getElementById("searchEmpty");
    const imageInput = document.getElementById("imageInput");
    const imagePreviewContainer = document.getElementById("imagePreviewContainer");
    const welcomeSection = document.getElementById("welcomeSection");
    const mainContent = document.getElementById("mainContent");
    const sidebar = document.querySelector(".sidebar");
    const recentLabel = document.getElementById("recentLabel") || document.querySelector(".recent-label");

    function renderSelectedFiles() {
        if (!imagePreviewContainer) return;
        imagePreviewContainer.innerHTML = '';
        window.selectedFiles.forEach((file, index) => {
            const wrapper = document.createElement('div');
            wrapper.className = 'file-preview-item';
            wrapper.innerHTML = `
                <span>${escapeHtml(file.name)}</span>
                <button onclick="window.selectedFiles.splice(${index}, 1); renderSelectedFiles();">✕</button>
            `;
            imagePreviewContainer.appendChild(wrapper);
        });
    }

    function handleFilesSelect(files) {
        if (!files) return;
        Array.from(files).forEach(file => {
            window.selectedFiles.push(file);
        });
        renderSelectedFiles();
    }

    function clearFileSelection() {
        window.selectedFiles = [];
        if (imagePreviewContainer) imagePreviewContainer.innerHTML = '';
        if (imageInput) imageInput.value = '';
    }

    function readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(reader.error);
            reader.readAsText(file);
        });
    }

    let searchOpen = false;
    let searchQuery = '';

    window.saveAppUIState = function() {
        const settingsModal = document.getElementById('settingsPanel');
        const sidebarEl = document.querySelector('.sidebar');
        const state = {
            currentChatId: currentChatId,
            isChatActive: document.body.classList.contains('chat-active'),
            isSidebarExpanded: sidebarEl ? sidebarEl.classList.contains('expanded') : false,
            isSettingsOpen: settingsModal ? settingsModal.classList.contains('open') : false
        };
        localStorage.setItem('iris_ui_state', JSON.stringify(state));
    };

    const uiObserver = new MutationObserver(() => window.saveAppUIState());
    
    // We observe after a tick to ensure elements exist
    setTimeout(() => {
        uiObserver.observe(document.body, { attributes: true, attributeFilter: ['class'] });
        const sidebarEl = document.querySelector('.sidebar');
        if (sidebarEl) uiObserver.observe(sidebarEl, { attributes: true, attributeFilter: ['class'] });
        const settingsModal = document.getElementById('settingsPanel');
        if (settingsModal) uiObserver.observe(settingsModal, { attributes: true, attributeFilter: ['class'] });
    }, 100);

    function savePersist() {
        const persistChats = chats.filter(c => !c.isTemp && c.messages.length > 0);
        localStorage.setItem('iris_chats', JSON.stringify(persistChats));
    }
    function normaliseChat(chat) {
        if (typeof chat.historyString !== 'string') chat.historyString = '';
        if (!Array.isArray(chat.messages)) chat.messages = [];
        return chat;
    }
    function highlightMatch(text, query) {
        if (!query) return escapeHtml(text);
        const escaped = escapeHtml(text);
        const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        return escaped.replace(
            new RegExp(`(${escapedQuery})`, 'gi'),
            '<mark class="search-highlight">$1</mark>'
        );
    }

    // ── Regenerate the conversation title based on actual topic ──
    function regenerateTitle(chat, debounceMs) {
        if (debounceMs === undefined) debounceMs = 3000;
        const key = chat.id;
        if (chat.title && chat.title !== "New Conversation") {
            return;
        }
        if (!regenerateTitle._pending) regenerateTitle._pending = {};
        if (regenerateTitle._pending[key]) return;
        regenerateTitle._pending[key] = true;
        setTimeout(() => {
            delete regenerateTitle._pending[key];
            const target = chats.find(c => c.id === key);
            if (!target) return;
            const msgs = target.messages || [];
            if (msgs.length === 0) return;
            fetch('/generate_title', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ messages: msgs })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.title && data.title !== "New Conversation") {
                        const t = chats.find(c => c.id === key);
                        if (t && t.title !== data.title) {
                            t.title = data.title;
                            savePersist();
                            renderChatList();
                        }
                    }
                })
                .catch(err => console.error("Title regeneration failed:", err));
        }, debounceMs);
    }
    regenerateTitle._pending = {};

    function renderChatList(query = '') {
        if (!chatHistory) return;
        chatHistory.innerHTML = '';
        const q = query.trim().toLowerCase();
        let visibleCount = 0;

        const displayChats = [
            ...chats.filter(c => c.isPinned && !c.isTemp && c.messages.length > 0),
            ...chats.filter(c => !c.isPinned && !c.isTemp && c.messages.length > 0)
        ];

        displayChats.forEach(chat => {
            if (q && !chat.title.toLowerCase().includes(q)) return;
            visibleCount++;

            const item = document.createElement('div');
            item.className = `chat-history-item${chat.id === currentChatId ? ' active' : ''}`;
            
            const pinHtml = chat.isPinned ? `<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2" style="margin-right: 6px; opacity: 0.7; vertical-align: middle;"><line x1="12" y1="17" x2="12" y2="22"></line><path d="M5 17h14v-1.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 11.64V6a3 3 0 0 0-6 0v5.64a2 2 0 0 1-1.11 1.91l-1.78.9A2 2 0 0 0 5 15.24Z"></path></svg>` : '';
            
            item.innerHTML = `
                <span class="chat-history-item-title">${pinHtml}${highlightMatch(chat.title, q)}</span>
                <button class="chat-options-btn" data-id="${chat.id}" title="Options">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <circle cx="12" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="19" r="2"/>
                    </svg>
                </button>
            `;
            item.addEventListener('click', () => loadChat(chat.id));
            item.querySelector('.chat-options-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                openContextMenu(e, chat.id);
            });
            chatHistory.appendChild(item);
        });

        if (recentLabel) recentLabel.textContent = q ? `Results (${visibleCount})` : 'Recent Chats';
        if (searchEmpty) searchEmpty.classList.toggle('visible', q !== '' && visibleCount === 0);
    }

    let currentContextId = null;
    const contextMenu = document.getElementById('chatContextMenu');
    
    function openContextMenu(e, id) {
        currentContextId = id;
        contextMenu.style.display = 'flex';
        
        const chat = chats.find(c => c.id === id);
        const pinBtn = document.getElementById('cmPinBtn');
        if (pinBtn && chat) {
            pinBtn.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="${chat.isPinned ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="17" x2="12" y2="22"></line><path d="M5 17h14v-1.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 11.64V6a3 3 0 0 0-6 0v5.64a2 2 0 0 1-1.11 1.91l-1.78.9A2 2 0 0 0 5 15.24Z"></path></svg>
                ${chat.isPinned ? 'Unpin' : 'Pin'}
            `;
        }

        const rect = e.currentTarget.getBoundingClientRect();
        let top = rect.bottom + 8;
        let left = rect.left; // Align left edge of menu with button, so it extends to the right
        
        if (top + contextMenu.offsetHeight > window.innerHeight) {
            top = rect.top - contextMenu.offsetHeight - 8;
        }
        
        contextMenu.style.top = top + 'px';
        contextMenu.style.left = Math.max(10, left) + 'px';
    }
    
    document.addEventListener('click', (e) => {
        if (contextMenu && contextMenu.style.display === 'flex') {
            if (!contextMenu.contains(e.target) && !e.target.closest('.chat-options-btn')) {
                contextMenu.style.display = 'none';
            }
        }
    });

    document.getElementById('cmDeleteBtn')?.addEventListener('click', () => {
        if (currentContextId) {
            deleteChat(currentContextId);
            contextMenu.style.display = 'none';
        }
    });
    
    document.getElementById('cmRenameBtn')?.addEventListener('click', () => {
        if (currentContextId) {
            const chat = chats.find(c => c.id === currentContextId);
            const newName = prompt("Enter new name:", chat?.title || "");
            if (newName && newName.trim()) {
                chat.title = newName.trim();
                savePersist();
                renderChatList();
            }
            contextMenu.style.display = 'none';
        }
    });
    
    document.getElementById('cmShareBtn')?.addEventListener('click', () => {
        alert("Share functionality coming soon!");
        contextMenu.style.display = 'none';
    });
    
    document.getElementById('cmPinBtn')?.addEventListener('click', () => {
        if (currentContextId) {
            const chat = chats.find(c => c.id === currentContextId);
            if (chat) {
                chat.isPinned = !chat.isPinned;
                savePersist();
                renderChatList();
            }
            contextMenu.style.display = 'none';
        }
    });

    function escapeHtml(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }

    function enterChatMode() {
        chatActive = true;
        document.body.classList.add("chat-active");
        if (chatMessages) {
            chatMessages.style.display = '';
            chatMessages.removeAttribute('hidden');
        }
        if (welcomeSection) welcomeSection.style.display = 'none';
    }

    function updatePlaceholder() {
        if (!chatInput) return;
        const currentChat = chats.find(c => c.id === currentChatId);
        const isTemp = currentChat && currentChat.isTemp;
        chatInput.placeholder = isTemp ? "Ask anything (Incognito)" : "Ask anything";
    }

    function exitChatMode() {
        chatActive = false;
        document.body.classList.remove("chat-active");
        if (welcomeSection) {
            welcomeSection.style.display = '';
        }
    }

    function startNewChat(isTemp = false) {
        // Clean up any empty chats before starting a new one
        chats = chats.filter(c => c.messages.length > 0);

        function generateId() { return Date.now().toString(); }
        const newChat = {
            id: generateId(),
            title: isTemp ? 'Temporary Chat' : 'New Conversation',
            messages: [],
            isTemp: isTemp
        };
        chats.unshift(newChat);
        if (!isTemp) savePersist();
        currentChatId = newChat.id;
        updatePlaceholder();
        renderChatList();
        
        chatMessages.innerHTML = '';
        exitChatMode();
        window.saveAppUIState();
    }

    function loadChat(id) {
        currentChatId = id;
        const chat = normaliseChat(chats.find(c => c.id === id) || {});
        if (!chat.id) return;

        chatMessages.innerHTML = '';
        chat.messages.forEach(msg => {
            appendMessageDOM(msg.role, msg.displayText || msg.content, false, msg.imageUrl, msg.attachmentName, msg.sources);
        });

        if (chat.messages.length > 0) {
            enterChatMode();
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } else {
            exitChatMode();
        }
        updatePlaceholder();
        renderChatList();
        window.saveAppUIState();
    }

    function deleteChat(id) {
        chats = chats.filter(c => c.id !== id);
        savePersist();
        if (currentChatId === id) {
            if (chats.length > 0) loadChat(chats[0].id);
            else startNewChat();
        } else {
            renderChatList();
        }
    }

    function showTypingIndicator() {
        removeTypingIndicator();
        const div = document.createElement("div");
        div.classList.add("message", "ai-message", "typing-indicator");
        div.id = "typingIndicator";
        const content = document.createElement("div");
        content.classList.add("message-content");
        content.innerHTML = `
            <div class="thinking-text">
                <div class="thinking-dot-container">
                    <span class="thinking-dot"></span>
                    <span class="thinking-dot"></span>
                    <span class="thinking-dot"></span>
                </div>
                <span class="status-text-content">Thinking and finding the best answer...</span>
            </div>
        `;
        div.appendChild(content);
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeTypingIndicator() {
        const el = document.getElementById("typingIndicator");
        if (el) el.remove();
    }

    function formatActionNormally(obj) {
        const action = (obj.action || '').trim().toLowerCase();
        const params = obj.parameters || obj || {};

        function getVal(...keys) {
            for (const k of keys) {
                if (params[k] !== undefined && params[k] !== null) return String(params[k]);
            }
            for (const k of keys) {
                if (obj[k] !== undefined && obj[k] !== null) return String(obj[k]);
            }
            return '';
        }

        if (action.includes("close") || action.includes("kill") || action === "kill_app") {
            let name = getVal("name", "app");
            if (!name) {
                for (const [k, v] of Object.entries(params)) {
                    if (String(v).toLowerCase() === "true" || String(v) === "1" || String(v).toLowerCase() === "yes" || String(v).toLowerCase() === "close" || String(v).toLowerCase() === "kill") {
                        name = k;
                        break;
                    }
                }
            }
            if (!name) {
                const parts = action.split(/\s+/);
                if (parts.length > 1) name = parts.slice(1).join(' ');
            }
            return `⚙️ Closing ${name || 'application'}...`;
        }

        if (action.includes("open") && action.includes("website")) {
            const url = getVal("url", "website", "link");
            return `⚙️ Opening website: ${url || 'URL'}...`;
        }

        if (action.includes("open")) {
            let name = getVal("name", "app");
            if (!name) {
                for (const [k, v] of Object.entries(params)) {
                    if (String(v).toLowerCase() === "true" || String(v) === "1" || String(v).toLowerCase() === "yes" || String(v).toLowerCase() === "open") {
                        name = k;
                        break;
                    }
                }
            }
            if (!name) {
                const parts = action.split(/\s+/);
                if (parts.length > 1) name = parts.slice(1).join(' ');
            }
            return `⚙️ Opening ${name || 'application'}...`;
        }

        if (action.includes("youtube") && action.includes("channel")) {
            const name = getVal("name", "channel");
            return `⚙️ Opening YouTube channel: ${name}...`;
        }

        if (action.includes("youtube")) {
            const query = getVal("query", "video", "search");
            return `⚙️ Playing '${query}' on YouTube...`;
        }

        if (action.includes("spotify")) {
            const query = getVal("query", "song", "search");
            return `⚙️ Playing '${query}' on Spotify...`;
        }

        if (action.includes("email")) {
            const to = getVal("to", "recipient");
            const subj = getVal("subject", "sub");
            const subjStr = subj ? ` (Subject: ${subj})` : '';
            return `Sending email to ${to}${subjStr}...`;
        }

        if (action.includes("search") && action.includes("file")) {
            const query = getVal("query", "name");
            const folder = getVal("folder", "dir");
            return `Searching for '${query}' in '${folder || 'Documents'}'...`;
        }

        if (action.includes("file")) {
            const path = getVal("path", "file");
            return `Opening file: ${path}...`;
        }

        if (action.includes("terminal")) {
            const cmd = getVal("command", "cmd");
            return `Opening terminal and running: \`${cmd}\`...`;
        }

        if (action.includes("command")) {
            const cmd = getVal("command", "cmd");
            return `Running command: \`${cmd}\`...`;
        }

        if (action === "volume_up") return "Increasing system volume...";
        if (action === "volume_down") return "Decreasing system volume...";
        if (action === "volume_mute") return "Muting system volume...";
        if (action.includes("volume_set") || action.includes("volume")) {
            const pct = getVal("percent", "pct", "level", "value");
            return `Setting system volume to ${pct}%...`;
        }

        if (action === "brightness_up") return "Increasing screen brightness...";
        if (action === "brightness_down") return "Decreasing screen brightness...";
        if (action.includes("brightness_set") || action.includes("brightness")) {
            const pct = getVal("percent", "pct", "level", "value");
            return `Setting screen brightness to ${pct}%...`;
        }

        if (action.includes("system")) {
            const what = getVal("what", "info", "query");
            return `Retrieving system ${what || 'information'}...`;
        }

        if (action.includes("clipboard") && action.includes("copy")) return "Copying text to clipboard...";
        if (action.includes("clipboard") && action.includes("read")) return "Reading clipboard content...";

        const cleanAction = action.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        return `Performing action: ${cleanAction}...`;
    }

    function formatMessage(text, isStreaming = false) {
        if (!text) return '';

        // Strip leading special tokens/headers that sometimes leak from certain models
        let formatted = text.replace(/^(\s|<\|endoftext\|>|<\|im_start\|>assistant<\|im_sep\|>|<\|im_end\|>)+/gi, '');

        // Strip <coding> tags as they interfere with markdown parsing and shouldn't be rendered
        formatted = formatted.replace(/<\/?coding>/gi, '');

        // Safety net: close unclosed code fences to prevent empty/broken code blocks
        // (e.g. model hit max_tokens mid-code-block, leaving ``` without a closing ```)
        const fenceCount = (formatted.match(/```/g) || []).length;
        if (fenceCount % 2 !== 0) {
            formatted += '\n```';
        }

        // Auto-wrap raw \boxed{...} blocks that are not inside math delimiters
        formatted = formatted.replace(/(\$\$?[\s\S]*?\$?\$\$)|(\\boxed\{[^{}]*\})/g, (match, mathBlock, bareBoxed) => {
            if (mathBlock) return match;
            if (bareBoxed) return `$$${bareBoxed}$$`;
            return match;
        });

        let html = _formatRefined(formatted, isStreaming);

        try {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const elements = doc.body.querySelectorAll('p, li, h1, h2, h3, h4, h5, h6, table, blockquote');
            elements.forEach(el => {
                if (el.closest('.thought-wrapper') || el.closest('.code-container') || el.closest('.file-card')) {
                    return;
                }
                if (!el.hasAttribute('dir')) {
                    el.setAttribute('dir', 'auto');
                }
            });
            html = doc.body.innerHTML;
        } catch (e) {
            console.error("Error setting dir=auto on elements:", e);
        }

        return html;
    }

    function _formatRefined(text, isStreaming = false) {
        if (!text) return '';
        let work = text;
        const blocks = [];

        // 1. Extract action JSON blocks and results FIRST so they aren't swallowed by think blocks
        let startIdx = work.indexOf('{');
        while (startIdx !== -1) {
            let braceCount = 0;
            let endIdx = -1;
            for (let i = startIdx; i < work.length; i++) {
                const char = work[i];
                if (char === '{') {
                    braceCount++;
                } else if (char === '}') {
                    braceCount--;
                    if (braceCount === 0) {
                        endIdx = i + 1;
                        break;
                    }
                }
            }
            if (endIdx !== -1) {
                const candidate = work.substring(startIdx, endIdx);
                if (candidate.includes('"action"') || candidate.includes("'action'")) {
                    const id = `@@@ACTION_${blocks.length}@@@`;
                    blocks.push({ type: 'action', content: candidate });
                    work = work.substring(0, startIdx) + id + work.substring(endIdx);
                    startIdx = work.indexOf('{', startIdx + id.length);
                    continue;
                }
            } else if (isStreaming) {
                const candidate = work.substring(startIdx);
                if (candidate.includes('"action"') || candidate.includes("'action'")) {
                    const id = `@@@ACTION_${blocks.length}@@@`;
                    blocks.push({ type: 'action', content: candidate });
                    work = work.substring(0, startIdx) + id;
                    break;
                }
            }
            startIdx = work.indexOf('{', startIdx + 1);
        }

        work = work.replace(/<action_result>([\s\S]*?)(?:<\/action_result>|$)/gi, (match, p1) => {
            const id = `@@@RESULT_${blocks.length}@@@`;
            blocks.push({ type: 'result', content: p1.trim() });
            return id;
        });

        // 2. Extract Think Block (Internal)
        let combinedThought = "";
        let isThoughtClosed = true;
        let firstThoughtId = "";

        work = work.replace(/(?:<think>|<\|thought_start\|>|<thought>|<z>|\[thinking\])([\s\S]*?)(?:<\/think>|<\|thought_end\|>|<\/thought>|<\/z>|\[answer\]|\[\/thinking\]|$)/gi, (match, p1) => {
            const content = p1.trim();
            if (!content) return '';

            const isClosed = /(?:<\/think>|<\|thought_end\|>|<\/thought>)$/i.test(match);
            isThoughtClosed = isClosed;

            if (combinedThought === "") {
                combinedThought = content;
                firstThoughtId = `@@@THOUGHT_${blocks.length}@@@`;
                blocks.push({ type: 'thought', content: '', isClosed: true });
                return firstThoughtId;
            } else {
                combinedThought += "\n\n" + content;
                return '';
            }
        });

        if (combinedThought !== "") {
            const blockIndex = parseInt(firstThoughtId.match(/\d+/)[0]);
            blocks[blockIndex].content = combinedThought;
            blocks[blockIndex].isClosed = isThoughtClosed;
        }

        work = work.replace(/<coding>([\s\S]*?)(?:<\/coding>|$)/gi, (match, p1) => {
            const id = `@@@CODING_${blocks.length}@@@`;
            blocks.push({ type: 'coding', content: p1.trim() });
            return id;
        });

        work = work.replace(/<review>([\s\S]*?)(?:<\/review>|$)/gi, (match, p1) => {
            const id = `@@@REVIEW_${blocks.length}@@@`;
            blocks.push({ type: 'review', content: p1.trim() });
            return id;
        });

        function isCommandOrShortBlock(lang, content) {
            const lowerLang = (lang || '').toLowerCase();
            if (['bash', 'sh', 'shell', 'cmd', 'powershell', 'terminal', 'run', 'install'].includes(lowerLang)) {
                return true;
            }
            const lines = content.split('\n');
            if (lines.length < 5 && content.length < 200) {
                return true;
            }
            if (lines.length <= 2 && (content.includes('python ') || content.includes('pip ') || content.includes('npm ') || content.includes('node '))) {
                return true;
            }
            return false;
        }

        function looksLikeProseLine(s) {
            s = s.trim();
            if (!s || s.length < 10) return false;
            if (/^(#|\/\/|\/\*|\*|<!--)/.test(s)) return false;
            if (/^(def |class |function |const |let |var |import |from |return |if |for |while |try |catch |elif |else:|print\(|@\w)/.test(s)) return false;
            const codeSuffixes = [';', '}', ']', ')', '>', ','];
            if (codeSuffixes.some(suf => s.endsWith(suf))) return false;
            if (/^[a-zA-Z_][\w]*\s*[=(\[]/.test(s)) return false;
            if (/[;=<>{}[\]()]/.test(s) && !/[.!?]\s*$/.test(s)) return false;
            if (/^[A-Z"'(]/.test(s) && /[a-z]/.test(s) && /\s/.test(s)) {
                const wordCount = s.split(/\s+/).length;
                if (wordCount >= 4 && (/[.!?]\s*$/.test(s) || wordCount >= 8)) return true;
            }
            return false;
        }

        function stripTrailingProseLines(content) {
            const lines = content.split('\n');
            let end = lines.length;
            while (end > 0) {
                const trimmed = lines[end - 1].trim();
                if (!trimmed) { end--; continue; }
                if (looksLikeProseLine(trimmed)) { end--; continue; }
                break;
            }
            const proseLines = lines.slice(end).map(l => l.trim()).filter(Boolean);
            return {
                content: lines.slice(0, end).join('\n').trim(),
                prose: proseLines.join(' ')
            };
        }

        function stripTrailingTextFromCode(content, lang) {
            const l = (lang || '').toLowerCase();
            const lines = content.split('\n');
            let lastCode = lines.length - 1;

            // HTML: strip after last </html>
            if (l === 'html') {
                const idx = content.lastIndexOf('</html>');
                if (idx !== -1) content = content.substring(0, idx + 7).trim();
                return stripTrailingProseLines(content);
            }

            // CSS/SCSS/LESS: strip after last } at column 0
            if (['css', 'scss', 'less'].includes(l)) {
                while (lastCode >= 0 && !lines[lastCode].trim().endsWith('}')) lastCode--;
                if (lastCode >= 0) content = lines.slice(0, lastCode + 1).join('\n').trim();
                return stripTrailingProseLines(content);
            }

            // Shell: strip after last return/exit/exec
            if (['bash', 'sh', 'shell', 'zsh'].includes(l)) {
                while (lastCode >= 0) {
                    const s = lines[lastCode].trim().toLowerCase();
                    if (s.startsWith('return ') || s.startsWith('exit ') || s.startsWith('exec ')) break;
                    lastCode--;
                }
                if (lastCode >= 0) content = lines.slice(0, lastCode + 1).join('\n').trim();
                return stripTrailingProseLines(content);
            }





            // Generic fallback: strip trailing lines that look like English prose
            lastCode = lines.length - 1;
            const codeSuffixes = [';', '}', ']', ')', '>', ','];
            while (lastCode >= 0) {
                const s = lines[lastCode].trim();
                if (!s || s.length < 10) break;
                if (codeSuffixes.some(suf => s.endsWith(suf))) break;
                if (/^(def |class |function |const |let |var |import |from |return |if |for |while |try |catch |switch |case |export |module\.|require\(|#include|<!DOCTYPE|<html|<div|<script|<style|import )/.test(s)) break;
                if (looksLikeProseLine(s)) { lastCode--; continue; }
                break;
            }
            if (lastCode >= 0) content = lines.slice(0, lastCode + 1).join('\n').trim();

            return stripTrailingProseLines(content);
        }

        // SAFETY NET: Close unclosed code blocks before <file_card> tags, remove orphaned ```
        // 1. If a <file_card> appears and the nearest preceding ``` has no closing ```, add one
        work = work.replace(/<file_card\s/gi, (match, offset) => {
            const before = work.substring(0, offset);
            // BUGFIX: the closest preceding ``` to the tag is the CLOSING marker of a complete
            // pair in the normal, correct case (block already properly closed before <file_card>).
            // The old code couldn't tell that apart from a genuinely unclosed opening fence, so it
            // always inserted a redundant second closing fence — which step 2 below then collapsed
            // together with the real one, stripping both. An even count of ``` before the tag means
            // everything so far is already matched pairs, so there's nothing to close here.
            const fenceCountBefore = (before.match(/```/g) || []).length;
            if (fenceCountBefore % 2 === 0) return match;
            const lastOpen = before.lastIndexOf('```');
            if (lastOpen === -1) return match;
            const afterOpen = work.substring(lastOpen + 3);
            const nextClosing = afterOpen.indexOf('```');
            const nextFileCard = afterOpen.indexOf('<file_card');
            if (nextClosing === -1 || (nextFileCard !== -1 && nextClosing > nextFileCard)) {
                return '\n```\n' + match;
            }
            return match;
        });
        // 2. Remove orphaned ``` (empty code fences with no content inside and nothing meaningful after)
        work = work.replace(/```\s*```/g, '');
        work = work.replace(/```\s*$/gm, (match, offset) => {
            const after = work.substring(offset + 3).trimStart();
            if (!after || after.length < 3) return '';
            return match;
        });
        // 3. If a <file_card> exists but no code block precedes it, remove the orphaned file_card
        if (/<file_card\s/i.test(work)) {
            const parts = work.split(/<file_card\s/i);
            if (parts.length > 1 && !/```[\s\S]*?```/.test(parts[0])) {
                work = work.replace(/<file_card\s[^>]*?(?:\/>|>\s*<\/file_card>|>)/gi, '');
            }
        }

        // Auto-wrap raw HTML in backticks if the model forgot them (Browser Markdown Chokehold prevention).
        //
        // BUGFIX: this used to gate on `work.includes("```html")` etc. against the WHOLE message. That
        // meant a single well-formed ```html ... ``` block earlier in the message (the normal, correct
        // case — the one that produces a proper file card) silently disabled this safety net for
        // everything AFTER it. So when the model also rambled/duplicated the file as raw, unfenced text
        // later in the same response (small local models do this, especially right after a <file_card>
        // tag), that trailing raw HTML fell straight through to marked.parse()+DOMPurify ungated and got
        // rendered as live HTML elements instead of code — the "file card followed by what looks like the
        // actual rendered webpage" bug.
        //
        // Fix: only ever look at the text AFTER the last fully-closed ``` fence, and only when every
        // fence seen so far is a matched pair (an odd count means we're still mid-stream inside an open
        // fence, in which case there's no "after" yet and this must stay out of the way, same as before).
        {
            const fenceCount = (work.match(/```/g) || []).length;
            if (fenceCount % 2 === 0) {
                const tailStart = fenceCount === 0 ? 0 : work.lastIndexOf('```') + 3;
                const head = work.slice(0, tailStart);
                let tail = work.slice(tailStart);
                
                // HTML auto-wrap
                if (!tail.includes("```html") && !tail.includes("```\n<!DOCTYPE") && !tail.includes("```\n<html") && !tail.includes("```\n<div") && !tail.includes("```\n<nav")) {
                    tail = tail.replace(/(?:^|\n)(?:html\s*\n|CODE\s*\n|CODE\s*\nhtml\s*\n)?((?:<!--|<!DOCTYPE|<html|<body|<head|<title|<meta|<link|<nav|<header|<footer|<main|<section|<aside|<article|<div|<span|<p|<a|<button|<form|<input|<textarea|<select|<label|<ul|<ol|<li|<h[1-6]|<img|<canvas|<svg|<style|<script|<table|<tr|<td|<th|<thead|<tbody|<iframe|<video|<audio)[\s\S]*)$/i, '\n```html\n$1\n```\n');
                }
                
                // Python/JS/CSS/Shell auto-wrap (catches trailing rambled code in any language)
                if (!tail.includes("```")) {
                    // CSS patterns: selectors, @ rules, or property blocks
                    tail = tail.replace(
                        /(?:^|\n)(?:css\s*\n)((?:(?:[.#@]\w|[a-z\[\]&*+>~])[^{}]*\{[^}]*\}|@\w+\s[^{;]+;?)[\s\S]*)$/im,
                        '\n```css\n$1\n```\n'
                    );
                    // Shell/bash patterns
                    if (!tail.includes("```bash") && !tail.includes("```sh")) {
                        tail = tail.replace(
                            /(?:^|\n)(?:bash\s*\n|shell\s*\n|sh\s*\n)((?:(?:#!\/|sudo |apt |pip |npm |yarn |docker |git |cd |ls |mkdir |rm |cp |mv |cat |echo |export |source |chmod |chown |curl |wget |grep |find |sed |awk |tar |unzip |python[23]? |node |rustc |cargo |go |javac |make |cmake ))[\s\S]*)$/im,
                            '\n```bash\n$1\n```\n'
                        );
                    }
                    // Generic Python/JS fallback
                    tail = tail.replace(
                        /(?:^|\n)(?:python\s*\n|js\s*\n|javascript\s*\n|CODE\s*\n)((?:def |class |import |from [\w.]+ import |function |const |let |var |async |export |require\()\s*[\s\S]*)$/m,
                        '\n```code\n$1\n```\n'
                    );
                }

                work = head + tail;
            }
        }

        work = work.replace(/```([^\n`]*)\n?([\s\S]*?)(?:```|$)/gi, (match, lang, codeContent) => {
            const id = `@@@CODE_${blocks.length}@@@`;
            let detectedLang = (lang || '').trim().replace(/@@@[A-Z0-9_]+@@@/gi, '');

            // Recover swallowed code if the model forgot a newline (e.g. ```html<div...)
            let extraCode = "";
            const tagIndex = detectedLang.search(/[<{\[]/);
            if (tagIndex !== -1 && tagIndex < 20) {
                extraCode = detectedLang.substring(tagIndex);
                detectedLang = detectedLang.substring(0, tagIndex).trim();
            }
            detectedLang = detectedLang || 'code';

            // Find all thought placeholders inside the code content and move them outside
            const thoughtRegex = /@@@THOUGHT_\d+@@@/g;
            let extractedThoughts = "";
            let matchThought;
            while ((matchThought = thoughtRegex.exec(codeContent)) !== null) {
                extractedThoughts += "\n" + matchThought[0] + "\n";
            }

            let cleanContent = (extraCode + (extraCode && !codeContent.startsWith('\n') ? '\n' : '') + codeContent).replace(/@@@THOUGHT_\d+@@@/g, '').trim();

            // Skip empty code blocks (e.g. model outputs ```python\n``` with nothing inside)
            if (!cleanContent) {
                return extractedThoughts || '';
            }

            // Infer language from filename comment when the fence has no lang tag (e.g. ```\n# app.py)
            if (detectedLang === 'code') {
                const fnMatch = cleanContent.match(/^#\s*([\w.-]+\.(py|js|ts|html|css|sh|bash|json|yaml|yml|rs|go|java|cpp|c|rb|php|vue|jsx|tsx))\s*$/m);
                if (fnMatch) {
                    detectedLang = fnMatch[2] === 'py' ? 'python' : fnMatch[2];
                }
            }

            // Extract description after <file_card> inside code block, emit as visible text outside
            let extractedFileCardDesc = '';
            const fcInsideMatch = cleanContent.match(/<file_card\s+[^>]*?>[\s\S]*?<\/file_card>\s*\n?([\s\S]*?)$/i);
            if (fcInsideMatch && fcInsideMatch[1].trim()) {
                extractedFileCardDesc = fcInsideMatch[1].trim();
            }
            // Strip any <file_card> tags that leaked inside the code block
            cleanContent = cleanContent.replace(/<file_card\s+[^>]*>[\s\S]*?<\/file_card>/gi, '').replace(/<file_card\s+[^>]*?\/>/gi, '').replace(/<file_card\s+[^>]*?>/gi, '').trim();
            // Strip trailing natural-language text from inside code blocks (all languages)
            const stripResult = stripTrailingTextFromCode(cleanContent, detectedLang);
            cleanContent = stripResult.content;
            if (stripResult.prose && !extractedFileCardDesc) {
                extractedFileCardDesc = stripResult.prose;
            }
            const isCmdOrShort = isCommandOrShortBlock(detectedLang, cleanContent);
            const isFinished = match.endsWith('```');

            blocks.push({
                type: 'code',
                lang: detectedLang,
                content: cleanContent,
                hidden: !isCmdOrShort,
                autoCard: !isCmdOrShort,
                claimed: false,
                finished: isFinished
            });
            // Inject thoughts and file_card description outside the code block placeholder
            return id + extractedThoughts + (extractedFileCardDesc ? '\n\n' + extractedFileCardDesc : '');
        });

        // Extract explicit file_card tags emitted by the AI — they override the auto-generated card
        // Match: <file_card ...></file_card>, <file_card .../>, and bare <file_card ...> (unclosed)
        work = work.replace(/<file_card\s+([^>]*?)(?:\/>|>\s*<\/file_card>|>)/gi,
            (match, attrsStr, offset) => {
                const filenameMatch = attrsStr.match(/filename=["']([^"']+)["']/i);
                const langMatch = attrsStr.match(/lang=["']([^"']+)["']/i);
                const filename = filenameMatch ? filenameMatch[1] : 'file.txt';
                const lang = langMatch ? langMatch[1] : 'text';

                // Find the closest unclaimed code block physically preceding this tag in the string
                const beforeSub = work.substring(0, offset);
                const placeholderRegex = /@@@CODE_(\d+)@@@/g;
                let matchPlaceholder;
                const blockIndices = [];
                while ((matchPlaceholder = placeholderRegex.exec(beforeSub)) !== null) {
                    blockIndices.push(parseInt(matchPlaceholder[1], 10));
                }

                let codeIndex = -1;
                // 1. Try to find a non-command/non-short block first (search from closest preceding)
                for (let j = blockIndices.length - 1; j >= 0; j--) {
                    const idx = blockIndices[j];
                    const block = blocks[idx];
                    if (block && block.type === 'code' && !block.claimed) {
                        const isCmdOrShort = isCommandOrShortBlock(block.lang, block.content);
                        if (!isCmdOrShort) {
                            codeIndex = idx;
                            break;
                        }
                    }
                }

                // 2. Fallback to the closest unclaimed preceding code block
                if (codeIndex === -1) {
                    for (let j = blockIndices.length - 1; j >= 0; j--) {
                        const idx = blockIndices[j];
                        const block = blocks[idx];
                        if (block && block.type === 'code' && !block.claimed) {
                            codeIndex = idx;
                            break;
                        }
                    }
                }

                let fileCardId = '';
                if (codeIndex !== -1) {
                    blocks[codeIndex].claimed = true;
                    blocks[codeIndex].hidden = true;
                    if (isStreaming) {
                        fileCardId = 'fc_stream_' + codeIndex;
                    } else {
                        let hash = 0;
                        const c = blocks[codeIndex].content;
                        for (let i = 0; i < c.length; i++) hash = Math.imul(31, hash) + c.charCodeAt(i) | 0;
                        fileCardId = 'fc_static_' + hash;
                    }
                    window.fileCardCache = window.fileCardCache || {};
                    window.fileCardCache[fileCardId] = blocks[codeIndex].content;
                } else {
                    // No code block found for this file_card tag, skip creating empty card
                    return '';
                }

                const id = `@@@FILECARD_${blocks.length}@@@`;
                blocks.push({ type: 'filecard', filename, lang: lang.trim(), fileCardId });
                return id;
            }
        );

        if (typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {
            if (typeof markedKatex !== 'undefined') {
                marked.use(markedKatex({ throwOnError: false }));
            }
            work = marked.parse(work, { breaks: true, gfm: true });
            const purifyConfig = {
                ADD_TAGS: ['math', 'mrow', 'mi', 'mo', 'mn', 'ms', 'mspace', 'mtext', 'menclose', 'merror', 'mphantom', 'mpadded', 'mroot', 'mfrac', 'msub', 'msup', 'msubsup', 'munder', 'mover', 'munderover', 'mmultiscripts', 'msection', 'maction', 'annotation', 'semantics'],
                ADD_ATTR: ['mathvariant', 'mathcolor', 'mathsize', 'mathbackground', 'display', 'xmlns']
            };
            work = DOMPurify.sanitize(work, purifyConfig);
            // marked wraps block-level text in <p>, which would break our injected <div>s. Let's unwrap placeholders.
            work = work.replace(/<p>(@@@[A-Z_0-9]+@@@)<\/p>/g, '$1');
        } else {
            work = escapeHtml(work);
            work = work.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            work = work.replace(/`([^`\n]+)`/g, '<code class="inline-code">$1</code>');
            work = work.replace(/\n/g, '<br>');
        }

        // 4.5 Post-processing: catch any remaining raw code that looks code-like
        //     but escaped all our auto-wrap passes. Small models sometimes output
        //     plain code with a header like "Here's the file:" but no fences.
        //     This catches: indented blocks, multi-line assignments, or code with
        //     typical structural keywords.
        {
            const hasFences = /```/g.test(work);
            if (!hasFences && work.length > 100) {
                const rawLines = work.split('\n').filter(l => l.trim());
                if (rawLines.length >= 3) {
                    const codeIndicators = rawLines.filter(l => {
                        const t = l.trim();
                        return /^(def |class |import |from |const |let |var |function |if |for |while |return |print\()/.test(t)
                            || /^[.#@]\w/.test(t)
                            || /\{\s*$/.test(t)
                            || /^\s{2,}\S/.test(l);
                    });
                    if (codeIndicators.length >= Math.min(3, rawLines.length * 0.4)) {
                        let detectedLang = 'python';
                        if (/\bfunction\b.*\(|\bconst\b|\blet\b|\bvar\b|\brequire\(|\bexport\b/.test(work)) detectedLang = 'javascript';
                        else if (/[.#@]\w+\s*\{/.test(work) && /:\s*[^;]+;/.test(work)) detectedLang = 'css';
                        else if (/^#!\/|\bsudo\b|\bapt\b|\bcurl\b/.test(work)) detectedLang = 'bash';
                        else if (/<\w+[^>]*>/.test(work)) detectedLang = 'html';
                        work = '\n```' + detectedLang + '\n' + work + '\n```\n';
                    }
                }
            }
        }

        // 5. Re-inject blocks recursively
        const blockHtmlMap = {};
        // Tracks file content that already has a visible card in this message, so a model that
        // re-emits/duplicates the same file later in its response (see the auto-wrap bugfix above)
        // doesn't produce a second, redundant card for it.
        const seenFileContents = new Set();
        blocks.forEach((block, index) => {
            let id, html;
            if (block.type === 'thought') {
                id = `@@@THOUGHT_${index}@@@`;
                const tKey = 't_' + index;
                window.toggledBlocks = window.toggledBlocks || {};
                let isExpanded = window.toggledBlocks[tKey] !== undefined ? window.toggledBlocks[tKey] : true;
                let inner = escapeHtml(block.content || '').replace(/\n/g, '<br>');

                if (!block.isClosed) {
                    const animDelay = -(Date.now() % 1000);
                    html = `
                        <div class="thought-wrapper ${isExpanded ? 'expanded' : ''}">
                            <div class="thought-header streaming" onclick="window.toggledBlocks['${tKey}'] = this.parentElement.classList.toggle('expanded')" style="cursor: pointer;">
                                <div class="thought-loader" style="animation-delay: ${animDelay}ms;"></div>
                                <span>Thinking...</span>
                            </div>
                            <div class="thought-content">${inner}</div>
                        </div>
                    `;
                } else {
                    html = `
                        <div class="thought-wrapper ${isExpanded ? 'expanded' : ''}">
                            <div class="thought-header" onclick="window.toggledBlocks['${tKey}'] = this.parentElement.classList.toggle('expanded')">
                                <svg class="chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
                                <span>Thought Process</span>
                            </div>
                            <div class="thought-content">${inner}</div>
                        </div>
                    `;
                }
            } else if (block.type === 'coding') {
                id = `@@@CODING_${index}@@@`;
                const tKey = 'c_' + index;
                window.toggledBlocks = window.toggledBlocks || {};
                let isExpanded = window.toggledBlocks[tKey] !== undefined ? window.toggledBlocks[tKey] : true;
                let inner = '';
                if (typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {
                    const purifyConfig = { ADD_TAGS: ['math', 'mrow', 'mi', 'mo', 'mn', 'ms', 'mspace', 'mtext', 'menclose', 'merror', 'mphantom', 'mpadded', 'mroot', 'mfrac', 'msub', 'msup', 'msubsup', 'munder', 'mover', 'munderover', 'mmultiscripts', 'msection', 'maction', 'annotation', 'semantics'], ADD_ATTR: ['mathvariant', 'mathcolor', 'mathsize', 'mathbackground', 'display', 'xmlns'] };
                    inner = DOMPurify.sanitize(marked.parse(block.content, { breaks: true, gfm: true }), purifyConfig).replace(/<p>(@@@[A-Z_0-9]+@@@)<\/p>/g, '$1');
                } else {
                    inner = escapeHtml(block.content).replace(/\n/g, '<br>');
                }
                html = `
                    <div class="thought-wrapper ${isExpanded ? 'expanded' : ''}">
                        <div class="thought-header" onclick="window.toggledBlocks['${tKey}'] = this.parentElement.classList.toggle('expanded')">
                            <svg class="chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
                            <span>Writing Code</span>
                        </div>
                        <div class="thought-content">${inner}</div>
                    </div>
                `;
            } else if (block.type === 'review') {
                id = `@@@REVIEW_${index}@@@`;
                const tKey = 'r_' + index;
                window.toggledBlocks = window.toggledBlocks || {};
                let isExpanded = window.toggledBlocks[tKey] !== undefined ? window.toggledBlocks[tKey] : true;
                let inner = '';
                if (typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {
                    const purifyConfig = { ADD_TAGS: ['math', 'mrow', 'mi', 'mo', 'mn', 'ms', 'mspace', 'mtext', 'menclose', 'merror', 'mphantom', 'mpadded', 'mroot', 'mfrac', 'msub', 'msup', 'msubsup', 'munder', 'mover', 'munderover', 'mmultiscripts', 'msection', 'maction', 'annotation', 'semantics'], ADD_ATTR: ['mathvariant', 'mathcolor', 'mathsize', 'mathbackground', 'display', 'xmlns'] };
                    inner = DOMPurify.sanitize(marked.parse(block.content, { breaks: true, gfm: true }), purifyConfig).replace(/<p>(@@@[A-Z_0-9]+@@@)<\/p>/g, '$1');
                } else {
                    inner = escapeHtml(block.content).replace(/\n/g, '<br>');
                }
                html = `
                    <div class="thought-wrapper ${isExpanded ? 'expanded' : ''}">
                        <div class="thought-header" onclick="window.toggledBlocks['${tKey}'] = this.parentElement.classList.toggle('expanded')">
                            <svg class="chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
                            <span>Code Review</span>
                        </div>
                        <div class="thought-content">${inner}</div>
                    </div>
                `;
            } else if (block.type === 'action') {
                id = `@@@ACTION_${index}@@@`;
                try {
                    const obj = JSON.parse(block.content);
                    if (obj.action === "chat" && obj.response) {
                        if (typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {
                            const purifyConfig = { ADD_TAGS: ['math', 'mrow', 'mi', 'mo', 'mn', 'ms', 'mspace', 'mtext', 'menclose', 'merror', 'mphantom', 'mpadded', 'mroot', 'mfrac', 'msub', 'msup', 'msubsup', 'munder', 'mover', 'munderover', 'mmultiscripts', 'msection', 'maction', 'annotation', 'semantics'], ADD_ATTR: ['mathvariant', 'mathcolor', 'mathsize', 'mathbackground', 'display', 'xmlns'] };
                            html = DOMPurify.sanitize(marked.parse(obj.response, { breaks: true, gfm: true }), purifyConfig);
                        } else {
                            html = escapeHtml(obj.response).replace(/\n/g, '<br>');
                        }
                    } else {
                        const formattedAction = formatActionNormally(obj);
                        html = `<div class="action-result-stream" style="font-size:12px; color:#a385ff; opacity:0.8;">${escapeHtml(formattedAction)}</div>`;
                    }
                } catch (e) {
                    const respMatch = block.content.match(/"response"\s*:\s*"([\s\S]*)$/);
                    if (respMatch) {
                        let partialResponse = respMatch[1];
                        if (typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {
                            const purifyConfig = { ADD_TAGS: ['math', 'mrow', 'mi', 'mo', 'mn', 'ms', 'mspace', 'mtext', 'menclose', 'merror', 'mphantom', 'mpadded', 'mroot', 'mfrac', 'msub', 'msup', 'msubsup', 'munder', 'mover', 'munderover', 'mmultiscripts', 'msection', 'maction', 'annotation', 'semantics'], ADD_ATTR: ['mathvariant', 'mathcolor', 'mathsize', 'mathbackground', 'display', 'xmlns'] };
                            html = DOMPurify.sanitize(marked.parse(partialResponse, { breaks: true, gfm: true }), purifyConfig);
                        } else {
                            html = escapeHtml(partialResponse).replace(/\n/g, '<br>');
                        }
                    } else if (block.content.includes('"action"') && !block.content.includes('"response"')) {
                        html = ''; // Still buffering action JSON, don't show raw JSON
                    } else {
                        html = escapeHtml(block.content).replace(/\n/g, '<br>');
                    }
                }
            } else if (block.type === 'result') {
                id = `@@@RESULT_${index}@@@`;
                html = `<div class='action-result-stream' style='font-size:13.5px; margin-top: 12px; padding: 12px; background: rgba(163, 133, 255, 0.05); border: 1px solid rgba(163, 133, 255, 0.2); border-radius: 8px;'><strong>Result:</strong><br>${escapeHtml(block.content).replace(/\n/g, '<br>')}</div>`;
            } else if (block.type === 'filecard') {
                id = `@@@FILECARD_${index}@@@`;
                const safeFilename = escapeHtml(block.filename);
                const safeLang = escapeHtml(block.lang);
                const safeId = escapeHtml(block.fileCardId || '');
                const isHtml = block.lang && block.lang.toLowerCase() === 'html';
                html = `
                    <div class="file-card"
                         onclick="window.openCodeViewer(this)"
                         data-filename="${safeFilename}"
                         data-lang="${safeLang}"
                         data-filecard-id="${safeId}">
                        <div class="file-card-icon">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                                 stroke="currentColor" stroke-width="1.7"
                                 stroke-linecap="round" stroke-linejoin="round">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12
                                         a2 2 0 0 0 2-2V8z"></path>
                                <polyline points="14 2 14 8 20 8"></polyline>
                                <line x1="16" y1="13" x2="8" y2="13"></line>
                                <line x1="16" y1="17" x2="8" y2="17"></line>
                                <polyline points="10 9 9 9 8 9"></polyline>
                            </svg>
                        </div>
                        <div class="file-card-meta">
                            <div class="file-card-name">${safeFilename}</div>
                            <div class="file-card-sub">${safeLang} file</div>
                        </div>
                        ${isHtml ? `
                        <button class="file-card-download"
                                onclick="event.stopPropagation(); window.previewFileCard(this)"
                                data-filename="${safeFilename}"
                                data-filecard-id="${safeId}"
                                style="background: rgba(var(--accent-rgb), 0.1); border-color: rgba(var(--accent-rgb), 0.25); color: var(--iris-purple);">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                                 stroke="currentColor" stroke-width="2"
                                 stroke-linecap="round" stroke-linejoin="round">
                                <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"></path>
                                <circle cx="12" cy="12" r="3"></circle>
                            </svg>
                            Preview
                        </button>
                        ` : ''}
                        <button class="file-card-download"
                                onclick="event.stopPropagation(); window.downloadFileCard(this)"
                                data-filename="${safeFilename}"
                                data-filecard-id="${safeId}">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                                 stroke="currentColor" stroke-width="2"
                                 stroke-linecap="round" stroke-linejoin="round">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                <polyline points="7 10 12 15 17 10"></polyline>
                                <line x1="12" y1="15" x2="12" y2="3"></line>
                            </svg>
                            Download
                        </button>
                    </div>
                `;
            } else if (block.type === 'code') {
                id = `@@@CODE_${index}@@@`;
                if (!block.finished && isStreaming) {
                    const animDelay = -(Date.now() % 1000);
                    let inner = escapeHtml(block.content);
                    let streamingStatus = `
                        <div style="display: flex; align-items: center; gap: 8px; color: #a385ff; font-size: 13px;">
                            <div style="width: 14px; height: 14px; border: 2px solid rgba(163, 133, 255, 0.3); border-top-color: #a385ff; border-radius: 50%; animation: spin-loader 1s linear infinite; animation-delay: ${animDelay}ms;"></div>
                            <span>Writing ${escapeHtml(block.lang || 'code')}...</span>
                        </div>
                    `;
                    if (typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {
                        const codeMd = "```" + (block.lang || '') + "\n" + block.content + "\n```";
                        const purifyConfig = { ADD_TAGS: ['math', 'mrow', 'mi', 'mo', 'mn', 'ms', 'mspace', 'mtext', 'menclose', 'merror', 'mphantom', 'mpadded', 'mroot', 'mfrac', 'msub', 'msup', 'msubsup', 'munder', 'mover', 'munderover', 'mmultiscripts', 'msection', 'maction', 'annotation', 'semantics'], ADD_ATTR: ['mathvariant', 'mathcolor', 'mathsize', 'mathbackground', 'display', 'xmlns', 'class'] };
                        let mdHtml = DOMPurify.sanitize(marked.parse(codeMd, { breaks: true, gfm: true }), purifyConfig);
                        html = `
                            <div class="code-container">
                                <div class="code-header" style="justify-content: flex-start; padding-top: 12px; padding-bottom: 12px;">
                                    ${streamingStatus}
                                </div>
                                ${mdHtml}
                            </div>
                        `;
                    } else {
                        html = `
                            <div class="code-container">
                                <div class="code-header" style="justify-content: flex-start; padding-top: 12px; padding-bottom: 12px;">
                                    ${streamingStatus}
                                </div>
                                <pre><code class="language-${escapeHtml(block.lang)}">${inner}</code></pre>
                            </div>
                        `;
                    }
                } else if (block.hidden) {
                    const normContent = (block.content || '').trim();
                    if (block.claimed && normContent) {
                        // This block's own card is rendered separately via its matching 'filecard' entry
                        // below (see the <file_card> tag handling above); remember its content so that if
                        // the model re-emits/duplicates the same file later in the same response, that
                        // duplicate doesn't get an extra card of its own.
                        seenFileContents.add(normContent);
                    }
                    let isDuplicate = seenFileContents.has(normContent);
                    if (!isDuplicate && normContent.length > 50) {
                        const strippedNorm = normContent.replace(/\s+/g, '');
                        for (const seen of seenFileContents) {
                            const strippedSeen = seen.replace(/\s+/g, '');
                            // If one is a substring of the other (with whitespace ignored), or they share the first 50 non-whitespace chars, it's a rambled duplicate
                            if (strippedSeen.includes(strippedNorm) || strippedNorm.includes(strippedSeen) || (strippedSeen.length > 50 && strippedNorm.length > 50 && strippedSeen.substring(0, 50) === strippedNorm.substring(0, 50))) {
                                isDuplicate = true;
                                break;
                            }
                        }
                    }

                    // Auto-generate a file card for hidden blocks that weren't claimed by an explicit <file_card> tag
                    if (block.autoCard && normContent.length > 0 && !block.claimed && !isDuplicate) {
                        seenFileContents.add(normContent);
                        const autoLang = block.lang || 'code';
                        const ext = normaliseExt(autoLang);
                        const autoFilename = window.extractFilenameFromCode ? window.extractFilenameFromCode(block.content, ext) : `snippet.${ext}`;
                        let fcId;
                        if (isStreaming) {
                            fcId = 'fc_stream_' + index;
                        } else {
                            let hash = 0;
                            const c = block.content;
                            for (let i = 0; i < c.length; i++) hash = Math.imul(31, hash) + c.charCodeAt(i) | 0;
                            fcId = 'fc_static_' + hash;
                        }
                        window.fileCardCache = window.fileCardCache || {};
                        window.fileCardCache[fcId] = block.content;
                        const safeFilename = escapeHtml(autoFilename);
                        const safeLang = escapeHtml(autoLang);
                        const isAutoHtml = autoLang && autoLang.toLowerCase() === 'html';
                        html = `
                            <div class="file-card"
                                 onclick="window.openCodeViewer(this)"
                                 data-filename="${safeFilename}"
                                 data-lang="${safeLang}"
                                 data-filecard-id="${fcId}">
                                <div class="file-card-icon">
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                                         stroke="currentColor" stroke-width="1.7"
                                         stroke-linecap="round" stroke-linejoin="round">
                                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12
                                                 a2 2 0 0 0 2-2V8z"></path>
                                        <polyline points="14 2 14 8 20 8"></polyline>
                                        <line x1="16" y1="13" x2="8" y2="13"></line>
                                        <line x1="16" y1="17" x2="8" y2="17"></line>
                                        <polyline points="10 9 9 9 8 9"></polyline>
                                    </svg>
                                </div>
                                <div class="file-card-meta">
                                    <div class="file-card-name">${safeFilename}</div>
                                    <div class="file-card-sub">${safeLang} file</div>
                                </div>
                                ${isAutoHtml ? `
                                <button class="file-card-download"
                                        onclick="event.stopPropagation(); window.previewFileCard(this)"
                                        data-filename="${safeFilename}"
                                        data-filecard-id="${fcId}"
                                        style="background: rgba(var(--accent-rgb), 0.1); border-color: rgba(var(--accent-rgb), 0.25); color: var(--iris-purple);">
                                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                                         stroke="currentColor" stroke-width="2"
                                         stroke-linecap="round" stroke-linejoin="round">
                                        <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"></path>
                                        <circle cx="12" cy="12" r="3"></circle>
                                    </svg>
                                    Preview
                                </button>
                                ` : ''}
                                <button class="file-card-download"
                                        onclick="event.stopPropagation(); window.downloadFileCard(this)"
                                        data-filename="${safeFilename}"
                                        data-filecard-id="${fcId}">
                                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                                         stroke="currentColor" stroke-width="2"
                                         stroke-linecap="round" stroke-linejoin="round">
                                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                        <polyline points="7 10 12 15 17 10"></polyline>
                                        <line x1="12" y1="15" x2="12" y2="3"></line>
                                    </svg>
                                    Download
                                </button>
                            </div>
                        `;
                    } else {
                        html = '';
                    }
                } else {
                    html = `
                        <div class="code-container">
                            <div class="code-header">
                                <span class="code-lang">${escapeHtml(block.lang)}</span>
                                <div style="display: flex; gap: 8px;">
                                    ${block.lang && block.lang.toLowerCase() === 'html' ? `
                                    <button class="copy-btn" onclick="previewHtml(this)" style="background-color: rgba(var(--accent-rgb), 0.1); border-color: rgba(var(--accent-rgb), 0.25); color: var(--iris-purple); display: flex; align-items: center; gap: 4px;">
                                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                                        Preview
                                    </button>
                                    ` : ''}
                                    <button class="copy-btn" onclick="downloadCode(this, '${escapeHtml(block.lang)}')">
                                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                                        Download
                                    </button>
                                    <button class="copy-btn" onclick="copyToClipboard(this)">
                                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                                        Copy
                                    </button>
                                </div>
                            </div>
                            <pre><code>${escapeHtml(block.content)}</code></pre>
                        </div>
                    `;
                }
            } else {
                id = `@@@${block.type.toUpperCase()}_${index}@@@`;
                html = '';
            }
            blockHtmlMap[id] = html;
        });

        let previousWork = '';
        let passCount = 0;
        while (work !== previousWork && passCount < 10) {
            previousWork = work;
            for (const [id, html] of Object.entries(blockHtmlMap)) {
                if (work.includes(id)) {
                    work = work.replace(id, html);
                }
            }
            passCount++;
        }

        return work;
    }
    window.extractFilenameFromCode = function (code, ext) {
        if (!code) return 'snippet.' + ext;
        const lines = code.trim().split('\n').slice(0, 10);
        for (const line of lines) {
            const match = line.match(/^\s*(?:#|\/\/|\/\*|<!--)\s*([\w-]+\.\w+)\s*(?:\*\/|-->)?\s*$/i);
            if (match && match[1]) return match[1];
        }
        const classMatch = code.match(/(?:public\s+)?(?:class|struct|interface)\s+([a-zA-Z0-9_]+)/);
        if (classMatch && classMatch[1]) return classMatch[1] + '.' + ext;
        if (code.match(/def\s+main\s*\(/) || code.match(/int\s+main\s*\(/) || code.match(/function\s+main\s*\(/)) return 'main.' + ext;
        const funcMatch = code.match(/(?:def|function|func)\s+([a-zA-Z0-9_]+)\s*\(/);
        if (funcMatch && funcMatch[1]) return funcMatch[1] + '.' + ext;

        // Fallback: Generate a meaningful name from the user's query
        try {
            let activeQuery = "";
            const currentChats = typeof window.getCurrentChats === 'function' ? window.getCurrentChats() : [];
            const currentChatIdVal = typeof window.getCurrentChatId === 'function' ? window.getCurrentChatId() : null;
            const chat = currentChats && currentChatIdVal ? currentChats.find(c => c.id === currentChatIdVal) : null;
            if (chat && chat.messages) {
                for (let i = chat.messages.length - 1; i >= 0; i--) {
                    if (chat.messages[i].role === 'user') {
                        const q = chat.messages[i].content || "";
                        if (q.split(/\s+/).length > 2) {
                            activeQuery = q;
                            break;
                        }
                    }
                }
                if (!activeQuery) {
                    for (let i = chat.messages.length - 1; i >= 0; i--) {
                        if (chat.messages[i].role === 'user') {
                            activeQuery = chat.messages[i].content || "";
                            break;
                        }
                    }
                }
            }
            if (activeQuery) {
                let words = activeQuery.toLowerCase().split(/\s+/);
                const filler = new Set(['ok', 'please', 'create', 'make', 'a', 'the', 'for', 'it', 'website', 'page', 'landing', 'me', 'to', 'build', 'design', 'beautiful', 'using']);
                words = words.filter(w => !filler.has(w) && w.match(/^\w+$/));
                if (words.length > 0) {
                    const slug = words.slice(0, 4).join('_');
                    if (slug) return slug + '.' + ext;
                }
            }
        } catch (e) {
            console.error("Error generating slug filename:", e);
        }

        return 'snippet.' + ext;
    };

    window.downloadCode = (btn, ext) => {
        const container = btn.closest('.code-container');
        const codeElement = container.querySelector('pre code');
        const text = codeElement.textContent;
        const filename = window.extractFilenameFromCode(text, normaliseExt(ext));
        triggerDownload(filename, text);
    };

    window.copyToClipboard = (btn) => {
        const container = btn.closest('.code-container');
        const codeElement = container.querySelector('pre code');
        const text = codeElement.textContent;

        navigator.clipboard.writeText(text).then(() => {
            const originalHtml = btn.innerHTML;
            btn.innerHTML = '<span>✓ Copied!</span>';
            btn.classList.add('copied');
            setTimeout(() => {
                btn.innerHTML = originalHtml;
                btn.classList.remove('copied');
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy: ', err);
        });
    };

    function appendMessageDOM(role, text, scroll = true, imageUrl = null, attachmentName = null, sources = null) {
        const outer = document.createElement("div");
        outer.classList.add("message", role === "user" ? "user-message" : "ai-message");

        const inner = document.createElement("div");
        inner.classList.add("message-content");
        inner.setAttribute("dir", "auto");

        if (imageUrl) {
            const img = document.createElement("img");
            img.src = imageUrl;
            img.classList.add("chat-image");
            inner.appendChild(img);
        } else if (attachmentName) {
            const fileBox = document.createElement("div");
            fileBox.className = "chat-file-attachment";
            fileBox.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <span>${escapeHtml(attachmentName)}</span>
            `;
            inner.appendChild(fileBox);
        }

        if (role === "bot") {
            const div = document.createElement("div");
            let html = formatMessage(text);
            if (sources && sources.length > 0) {
                html += '<div class="sources-container"><div class="sources-title">Sources</div><div class="sources-list">';
                sources.forEach(s => {
                    html += `<a class="source-chip" href="${s.url}" target="_blank" rel="noopener noreferrer">${s.domain}</a>`;
                });
                html += '</div></div>';
            }
            div.innerHTML = html;
            inner.appendChild(div);
            setTimeout(() => { if (typeof Prism !== 'undefined') Prism.highlightAll(); }, 50);
        } else if (text) {
            const div = document.createElement("div");
            div.textContent = text;
            inner.appendChild(div);
        }

        outer.appendChild(inner);
        chatMessages.appendChild(outer);
        if (scroll) chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function handleSendMessage() {
        const text = chatInput.value.trim();
        const hasFiles = window.selectedFiles.length > 0;
        if (!text && !hasFiles) return;

        // Prevent sending if only /route or /route <role> is provided without a prompt
        if (!hasFiles && text.match(/^\/route(?:\s+[a-zA-Z_]+)?$/i)) {
            chatInput.focus();
            return;
        }

        if (!currentChatId || !chats.find(c => c.id === currentChatId)) {
            currentChatId = Date.now().toString();
            chats.unshift({ id: currentChatId, title: 'New Conversation', messages: [], historyString: '' });
            savePersist();
            renderChatList();
        }

        const chat = normaliseChat(chats.find(c => c.id === currentChatId));

        // ── Title: regenerate after EVERY exchange based on full conversation ──
        const isFirstMessage = chat.messages.length === 0;
        if (isFirstMessage) {
            chat.title = text ? (text.length > 40 ? text.slice(0, 40) + '…' : text) : (hasFiles ? window.selectedFiles[0].name : "New Conversation");
        }
        if (text) {
            regenerateTitle(chat);
        }

        let displayImageUrl = null;
        let attachmentName = null;

        if (hasFiles) {
            const firstFile = window.selectedFiles[0];
            if (firstFile.type.startsWith('image/')) {
                displayImageUrl = URL.createObjectURL(firstFile);
            } else {
                attachmentName = window.selectedFiles.length > 1 ? `${window.selectedFiles.length} files attached` : firstFile.name;
            }
        }

        const messageObj = {
            role: 'user',
            content: text,
            displayText: text || `[Attached: ${attachmentName || 'files'}]`,
            imageUrl: displayImageUrl,
            attachmentName: attachmentName
        };

        chat.messages.push(messageObj);
        savePersist();
        renderChatList();

        enterChatMode();
        appendMessageDOM('user', messageObj.displayText, true, displayImageUrl, attachmentName);

        chatInput.value = '';
        const filesToUpload = [...window.selectedFiles];
        clearFileSelection();

        if (typeof handleInputResize === 'function') handleInputResize();

        setGeneratingState(true);
        showTypingIndicator();

        window._inThinkingStream = false;

        let fullReply = "";
        let actionResult = "";
        let aiMessageDiv = null;
        let aiContentDiv = null;

        try {
            const formData = new FormData();
            filesToUpload.forEach(f => {
                if (f.type.startsWith('image/')) {
                    formData.append('image', f);
                } else {
                    formData.append('document', f);
                }
            });
            formData.append('message', text);
            formData.append('chat_id', currentChatId);
            formData.append('messages', JSON.stringify(chat.messages));
            formData.append('history', chat.historyString);
            formData.append('settings', JSON.stringify(chatSettings));
            const modeSelector = document.getElementById("proModeSelector");
            if (modeSelector) {
                formData.append('mode', modeSelector.value);
            }

            currentAbortController = new AbortController();
            const response = await fetch('/chat', {
                method: 'POST',
                body: formData,
                signal: currentAbortController.signal
            });

            if (!response.ok) {
                let errText = await response.text().catch(() => response.status);
                try {
                    const errJson = JSON.parse(errText);
                    errText = errJson.error || errJson.message || errText;
                } catch (e) {
                    if (typeof errText === 'string' && (errText.trim().toLowerCase().startsWith('<!doctype html') || errText.trim().toLowerCase().startsWith('<html'))) {
                        errText = "Internal Server Error. Please check the backend logs.";
                    }
                }
                throw new Error(`Server error ${response.status}: ${errText}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";

            // Create the container but keep it hidden until the first text/token arrives
            aiMessageDiv = document.createElement("div");
            aiMessageDiv.classList.add("message", "ai-message");
            aiMessageDiv.style.display = "none";
            aiContentDiv = document.createElement("div");
            aiContentDiv.classList.add("message-content");
            aiContentDiv.setAttribute("dir", "auto");
            aiMessageDiv.appendChild(aiContentDiv);
            chatMessages.appendChild(aiMessageDiv);

            let currentResponseText = "";
            let rawResponseText = "";
            let lastRenderTime = 0;
            let renderTimer = null;
            let firstTokenReceived = false;
            window._pendingSources = null;

            // Throttle accumulated tokens to the DOM to max 15fps
            // This prevents "The Browser Markdown Chokehold" where marked.parse+DOMPurify freezes the main thread
            function scheduleRender() {
                if (renderTimer) return;
                const now = Date.now();
                const delay = Math.max(0, 66 - (now - lastRenderTime)); // ~15 FPS max
                renderTimer = setTimeout(() => {
                    try {
                        if (!firstTokenReceived) {
                            removeTypingIndicator();
                            aiMessageDiv.style.display = "";
                            firstTokenReceived = true;
                        }
                        const isAtBottom = chatMessages.scrollHeight - chatMessages.scrollTop <= chatMessages.clientHeight + 50;
                        aiContentDiv.innerHTML = formatMessage(currentResponseText, true);
                        if (isAtBottom) {
                            chatMessages.scrollTop = chatMessages.scrollHeight;
                        }

                        // Update code viewer if open and streaming
                        if (window.currentCardEl) {
                            const activeFcId = window.currentCardEl.dataset.filecardId;
                            if (activeFcId && activeFcId.startsWith('fc_stream_') && window.fileCardCache && window.fileCardCache[activeFcId]) {
                                const newCode = window.fileCardCache[activeFcId];
                                const cvCode = document.getElementById('cvCode');
                                if (cvCode && cvCode.textContent !== newCode) {
                                    const escaped = newCode.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                                    cvCode.innerHTML = escaped;
                                    const lines = newCode.split('\n');
                                    const gutters = document.getElementById('cvGutters');
                                    if (gutters && gutters.children.length !== lines.length) {
                                        gutters.innerHTML = lines.map((_, i) => `<div class="code-viewer-gutter-line">${i + 1}</div>`).join('');
                                        document.getElementById('cvLineCount').textContent = lines.length;
                                    }
                                    document.getElementById('cvCharCount').textContent = newCode.length.toLocaleString();

                                    // Auto-scroll the code viewer body if it was at the bottom
                                    const cvBody = document.getElementById('cvBody');
                                    if (cvBody) {
                                        const isCvAtBottom = cvBody.scrollHeight - cvBody.scrollTop <= cvBody.clientHeight + 50;
                                        if (isCvAtBottom) {
                                            cvBody.scrollTop = cvBody.scrollHeight;
                                        }
                                    }
                                }
                            }
                        }
                        lastRenderTime = Date.now();
                    } catch (e) {
                        console.error("Render error:", e);
                    } finally {
                        renderTimer = null;
                    }
                }, delay);
            }

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n\n");
                buffer = lines.pop();

                for (const line of lines) {
                    if (!line.startsWith("data: ")) continue;
                    const jsonStr = line.replace("data: ", "");
                    try {
                        const event = JSON.parse(jsonStr);
                        if (event.type === "token" || event.type === "text") {
                            if (window._inThinkingStream) {
                                currentResponseText += "\n</think>\n";
                                window._inThinkingStream = false;
                            }
                            currentResponseText += event.content;
                            scheduleRender();
                        } else if (event.type === "thinking") {
                            if (!window._inThinkingStream) {
                                currentResponseText += "\n<think>\n";
                                window._inThinkingStream = true;
                            }
                            currentResponseText += event.content;
                            scheduleRender();
                        } else if (event.type === "status") {

                            console.log("[Agent Status]", event.content);
                            if (!firstTokenReceived) {
                                const ind = document.getElementById("typingIndicator");
                                if (ind) {
                                    const span = ind.querySelector(".status-text-content");
                                    if (span) span.textContent = event.content;
                                }
                            }
                        } else if (event.type === "action_result") {
                            const isInsideThink = currentResponseText.lastIndexOf("<think>") > currentResponseText.lastIndexOf("</think>");
                            if (isInsideThink) {
                                currentResponseText += "\n</think>\n\n<action_result>" + event.content + "</action_result>\n\n<think>\n";
                            } else {
                                currentResponseText += "\n\n<action_result>" + event.content + "</action_result>";
                            }
                            scheduleRender();
                        } else if (event.type === "clear") {
                            if (renderTimer !== null) {
                                clearTimeout(renderTimer);
                                renderTimer = null;
                            }
                            lastRenderTime = 0;
                            currentResponseText = "";
                            rawResponseText = "";
                            window._pendingSources = null;
                            firstTokenReceived = false;
                            window._inThinkingStream = false;
                            aiContentDiv.innerHTML = "";
                            aiMessageDiv.style.display = "none";
                            showTypingIndicator();
                        } else if (event.type === "raw_response") {
                            rawResponseText = event.content;
                        } else if (event.type === "sources") {
                            window._pendingSources = event.sources;
                        } else if (event.type === "compact_history") {
                            chat.messages = event.messages;
                            savePersist();
                        } else if (event.type === "text" || event.type === "error") {
                            if (!firstTokenReceived) {
                                firstTokenReceived = true;
                                removeTypingIndicator();
                                aiMessageDiv.style.display = "";
                            }
                            currentResponseText += `\n\n> ⚠️ **${event.type === "error" ? "Error" : "System Notification"}**: ${event.content}\n\n`;
                            scheduleRender();
                        }
                    } catch (e) { console.error("Event parse error", e); }
                }

                const isAtBottom = chatMessages.scrollHeight - chatMessages.scrollTop <= chatMessages.clientHeight + 50;
                if (isAtBottom) {
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
            }

            setGeneratingState(false);
            if (!firstTokenReceived) {
                removeTypingIndicator();
                if (currentResponseText.trim() !== '') {
                    aiMessageDiv.style.display = "";
                } else {
                    currentResponseText = "> **System Notification**: Server closed connection without sending any response.";
                    aiMessageDiv.style.display = "";
                    aiContentDiv.innerHTML = formatMessage(currentResponseText);
                }
            }

            // Clean up currentResponseText before saving to prevent corrupting the LLM context
            let cleanResponse = currentResponseText;

            chat.messages.push({ role: 'bot', content: cleanResponse, sources: window._pendingSources });
            savePersist();

            // Regenerate title after every complete exchange (debounced 3s)
            regenerateTitle(chat);

            // Final render to apply non-streaming fallback logic (like stripping unclosed <think> tags)
            if (aiContentDiv) {
                let finalHtml = formatMessage(cleanResponse, false);
                if (window._pendingSources && window._pendingSources.length > 0) {
                    finalHtml += '<div class="sources-container"><div class="sources-title">Sources</div><div class="sources-list">';
                    window._pendingSources.forEach(s => {
                        finalHtml += `<a class="source-chip" href="${s.url}" target="_blank" rel="noopener noreferrer">${s.domain}</a>`;
                    });
                    finalHtml += '</div></div>';
                    window._pendingSources = null;
                }
                aiContentDiv.innerHTML = finalHtml;
                setTimeout(() => { if (typeof Prism !== 'undefined') Prism.highlightAll(); }, 50);
            }

        } catch (err) {
            console.error('[Iris] fetch error:', err);
            removeTypingIndicator();
            if (err.name === 'AbortError') {
                appendMessageDOM('bot', `⚠️ Generation stopped by user.`);
            } else {
                appendMessageDOM('bot', `⚠️ ${err.message || 'Could not reach the server.'}`);
            }
        } finally {
            setGeneratingState(false);
            chatInput.focus();
        }
    }

    function setGeneratingState(generating) {
        isGenerating = generating;
        chatInput.disabled = generating;

        if (generating) {
            sendBtn.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect></svg>`;
            sendBtn.setAttribute("aria-label", "Stop generation");
            sendBtn.classList.add("stop-btn");
        } else {
            sendBtn.innerHTML = `<h3>&nbsp;➤&nbsp;</h3>`;
            sendBtn.setAttribute("aria-label", "Send message");
            sendBtn.classList.remove("stop-btn");
            currentAbortController = null;
        }
    }

    const handleInputResize = () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = (chatInput.scrollHeight) + 'px';
    };

    const routeAutocomplete = document.getElementById("routeAutocomplete");
    const routeAutocompleteList = document.getElementById("routeAutocompleteList");
    const availableRoutes = [
        "code_complex", "code_simple", "math", "reasoning", "general", "control"
    ];

    chatInput.addEventListener('input', (e) => {
        handleInputResize();
        
        const val = chatInput.value;
        if (val.startsWith("/route")) {
            const parts = val.split(" ");
            const searchStr = parts.length > 1 ? parts[1].toLowerCase() : "";
            // Hide if they already typed a space after the route
            if (parts.length > 2) {
                routeAutocomplete.classList.add("hidden");
                return;
            }
            
            routeAutocompleteList.innerHTML = "";
            const matches = availableRoutes.filter(r => r.startsWith(searchStr));
            
            if (matches.length > 0) {
                matches.forEach(route => {
                    const li = document.createElement("li");
                    li.className = "route-autocomplete-item";
                    li.innerHTML = `
                        <div class="route-icon-wrapper">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                <polyline points="4 17 10 11 4 5"></polyline>
                                <line x1="12" y1="19" x2="20" y2="19"></line>
                            </svg>
                        </div>
                        <span class="route-cmd">/route</span>
                        <span class="route-name">${route}</span>
                    `;
                    li.addEventListener("click", () => {
                        chatInput.value = `/route ${route} `;
                        routeAutocomplete.classList.add("hidden");
                        chatInput.focus();
                    });
                    routeAutocompleteList.appendChild(li);
                });
                routeAutocomplete.classList.remove("hidden");
            } else {
                routeAutocomplete.classList.add("hidden");
            }
        } else {
            routeAutocomplete.classList.add("hidden");
        }
    });

    // Hide autocomplete on blur (delay to allow click to register)
    chatInput.addEventListener('blur', () => {
        setTimeout(() => {
            if (routeAutocomplete) routeAutocomplete.classList.add("hidden");
        }, 150);
    });

    sendBtn.addEventListener('click', () => {
        if (isGenerating) {
            if (currentAbortController) currentAbortController.abort();
        } else {
            handleSendMessage();
            setTimeout(handleInputResize, 10);
        }
    });

    // ── Dictation Button Logic (Local Whisper Backend) ──
    const dictationBtn = document.getElementById("dictationBtn");
    if (dictationBtn && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        let mediaRecorder = null;
        let audioChunks = [];
        let isRecording = false;

        dictationBtn.addEventListener('click', async (e) => {
            e.preventDefault();

            if (!isRecording) {
                isRecording = true; // Set instantly to prevent double clicks
                dictationBtn.classList.add('recording-active');
                dictationBtn.style.color = '#ff4d4d';
                chatInput.placeholder = "Listening...";

                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

                    let options = { mimeType: 'audio/webm' };
                    if (typeof MediaRecorder.isTypeSupported === 'function' && !MediaRecorder.isTypeSupported('audio/webm')) {
                        options = { mimeType: 'audio/mp4' };
                    }

                    mediaRecorder = new MediaRecorder(stream, options);
                    audioChunks = [];

                    mediaRecorder.ondataavailable = (event) => {
                        if (event.data && event.data.size > 0) {
                            audioChunks.push(event.data);
                        }
                    };

                    mediaRecorder.onstop = async () => {
                        isRecording = false;
                        dictationBtn.classList.remove('recording-active');
                        dictationBtn.style.color = '';
                        chatInput.placeholder = "Transcribing...";

                        if (audioChunks.length === 0) {
                            updatePlaceholder();
                            return;
                        }

                        const mimeType = options.mimeType || 'audio/webm';
                        const audioBlob = new Blob(audioChunks, { type: mimeType });
                        const formData = new FormData();
                        // Give it an extension matching the mime type
                        const filename = mimeType.includes('mp4') ? 'dictation.mp4' : 'dictation.webm';
                        formData.append("audio", audioBlob, filename);

                        try {
                            const res = await fetch('/api/transcribe', {
                                method: 'POST',
                                body: formData
                            });
                            const data = await res.json();
                            if (data.text) {
                                chatInput.value += (chatInput.value ? ' ' : '') + data.text.trim();
                                if (typeof handleInputResize === 'function') handleInputResize();

                                // Automatically send the message after dictation
                                if (!isGenerating && chatInput.value.trim() !== '') {
                                    handleSendMessage();
                                    setTimeout(handleInputResize, 10);
                                }
                            } else if (data.error) {
                                console.error("Dictation API error:", data.error);
                            }
                        } catch (err) {
                            console.error("Dictation network error:", err);
                        }

                        updatePlaceholder();
                        stream.getTracks().forEach(track => track.stop());
                    };

                    mediaRecorder.start();
                } catch (err) {
                    console.error("Microphone access error:", err);
                    isRecording = false;
                    dictationBtn.classList.remove('recording-active');
                    dictationBtn.style.color = '';
                    updatePlaceholder();
                    alert("Please allow microphone permissions to use dictation.");
                }
            } else {
                if (mediaRecorder && mediaRecorder.state !== "inactive") {
                    mediaRecorder.stop();
                } else {
                    // Fallback reset if it gets stuck
                    isRecording = false;
                    dictationBtn.classList.remove('recording-active');
                    dictationBtn.style.color = '';
                    updatePlaceholder();
                }
            }
        });
    } else if (dictationBtn) {
        dictationBtn.style.display = 'none';
    }

    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!isGenerating) {
                handleSendMessage();
                setTimeout(handleInputResize, 10);
            }
        }
    });
    
    if (newChatBtn) {
        newChatBtn.addEventListener('click', () => {
            startNewChat(false);
            if (window.innerWidth <= 768 && sidebar.classList.contains('expanded')) {
                // Assuming toggleBtn is available globally
                const toggleBtn = document.getElementById('sidebarToggleBtn');
                if (toggleBtn) toggleBtn.click();
            }
        });
    }

    if (quickNewChatBtnGlobal) {
        quickNewChatBtnGlobal.addEventListener('click', () => {
            startNewChat(false);
        });
    }

    if (tempChatBtn) {
        tempChatBtn.addEventListener('click', () => {
            startNewChat(true);
        });
    }

    function openSearch() {
        searchOpen = true;
        searchBarContainer?.classList.add('open');
        searchToggleBtn?.classList.add('active');
        if (sidebar && !sidebar.classList.contains('expanded')) {
            sidebar.classList.add('expanded');
        }
        setTimeout(() => searchInput?.focus(), 320);
    }

    function closeSearch() {
        searchOpen = false;
        searchQuery = '';
        searchBarContainer?.classList.remove('open');
        searchToggleBtn?.classList.remove('active');
        if (searchInput) searchInput.value = '';
        searchClearBtn?.classList.remove('visible');
        if (recentLabel) recentLabel.textContent = 'Recent Chats';
        if (searchEmpty) searchEmpty.classList.remove('visible');
        renderChatList();
    }

    searchToggleBtn?.addEventListener('click', () => {
        searchOpen ? closeSearch() : openSearch();
    });

    searchInput?.addEventListener('input', () => {
        searchQuery = searchInput.value;
        searchClearBtn?.classList.toggle('visible', searchQuery.length > 0);
        renderChatList(searchQuery);
    });

    searchInput?.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeSearch();
    });

    searchClearBtn?.addEventListener('click', () => {
        searchQuery = '';
        if (searchInput) searchInput.value = '';
        searchClearBtn.classList.remove('visible');
        searchInput?.focus();
        renderChatList();
        if (recentLabel) recentLabel.textContent = 'Recent Chats';
        if (searchEmpty) searchEmpty.classList.remove('visible');
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && searchOpen && document.activeElement !== chatInput) {
            closeSearch();
        }
    });

    window.appendMessage = appendMessageDOM;

    window.removeSelectedFile = function (index) {
        window.selectedFiles.splice(index, 1);
        renderSelectedFiles();
    };

    function renderSelectedFiles() {
        if (window.selectedFiles.length === 0) {
            imagePreviewContainer.innerHTML = '';
            imagePreviewContainer.classList.remove('visible');
            return;
        }

        let html = '<div style="display: flex; gap: 8px; flex-wrap: wrap;">';
        window.selectedFiles.forEach((file, index) => {
            const isImage = file.type.startsWith('image/');
            if (isImage) {
                const objectUrl = URL.createObjectURL(file);
                html += `
                    <div style="position: relative; display: inline-block;">
                        <img src="${objectUrl}" alt="Preview" style="max-height: 60px; border-radius: 6px; border: 1px solid #33334a;">
                        <button class="remove-image-btn" onclick="window.removeSelectedFile(${index})" title="Remove image">✕</button>
                    </div>
                `;
            } else {
                html += `
                    <div style="position: relative; display: inline-block;">
                        <div class="file-preview-box" style="padding: 6px 10px;">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                <polyline points="14 2 14 8 20 8"></polyline>
                            </svg>
                            <span class="file-preview-name" style="font-size: 11px;">${escapeHtml(file.name)}</span>
                        </div>
                        <button class="remove-image-btn" onclick="window.removeSelectedFile(${index})" title="Remove file" style="top: -6px; right: -6px; width: 16px; height: 16px; font-size: 10px;">✕</button>
                    </div>
                `;
            }
        });
        html += '</div>';
        imagePreviewContainer.innerHTML = html;
        imagePreviewContainer.classList.add('visible');
    }

    function handleFilesSelect(files) {
        if (!files || files.length === 0) return;
        for (let i = 0; i < files.length; i++) {
            window.selectedFiles.push(files[i]);
        }
        renderSelectedFiles();
    }

    imageInput?.addEventListener('change', (e) => {
        handleFilesSelect(e.target.files);
        imageInput.value = ''; // Reset input so the same files can be selected again if removed
    });

    let dragTimeout;
    const dragOverlay = document.getElementById('inputDragOverlay');

    window.addEventListener('dragover', (e) => {
        e.preventDefault();

        let hasFiles = false;
        if (e.dataTransfer && e.dataTransfer.types) {
            for (let i = 0; i < e.dataTransfer.types.length; i++) {
                const type = e.dataTransfer.types[i];
                if (type === 'Files' || type === 'application/x-moz-file') {
                    hasFiles = true;
                    break;
                }
            }
        }

        if (hasFiles) {
            if (dragOverlay) dragOverlay.classList.add('active');
            clearTimeout(dragTimeout);
            dragTimeout = setTimeout(() => {
                if (dragOverlay) dragOverlay.classList.remove('active');
            }, 150);
        }
    });

    window.addEventListener('drop', (e) => {
        e.preventDefault();
        clearTimeout(dragTimeout);
        if (dragOverlay) dragOverlay.classList.remove('active');
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleFilesSelect(e.dataTransfer.files);
        }
    });

    function clearFileSelection() {
        window.selectedFiles = [];
        if (imageInput) imageInput.value = '';
        imagePreviewContainer.innerHTML = '';
        imagePreviewContainer.classList.remove('visible');
    }

    chats = chats.map(normaliseChat);

    let uiState = null;
    try {
        uiState = JSON.parse(localStorage.getItem('iris_ui_state'));
    } catch (e) {}

    if (uiState) {
        if (uiState.currentChatId && chats.some(c => c.id === uiState.currentChatId)) {
            loadChat(uiState.currentChatId);
        } else {
            startNewChat();
        }

        if (uiState.isSidebarExpanded !== undefined) {
            const sb = document.querySelector('.sidebar');
            if (sb) {
                if (uiState.isSidebarExpanded) {
                    sb.classList.add('expanded');
                } else {
                    sb.classList.remove('expanded');
                }
            }
        }

        if (uiState.isSettingsOpen) {
            setTimeout(() => {
                document.getElementById('settingsBtn')?.click();
            }, 100);
        }
    } else {
        if (chats.length > 0) {
            loadChat(chats[0].id);
        } else {
            startNewChat();
        }
    }
});

// ═══════════════════════════════════════════════════════════════
//  CODE VIEWER PANEL  –  global functions
// ═══════════════════════════════════════════════════════════════
(function () {
    // Build the overlay + panel DOM once
    const overlay = document.createElement('div');
    overlay.className = 'code-viewer-overlay';
    overlay.addEventListener('click', closeViewer);

    const panel = document.createElement('div');
    panel.className = 'code-viewer-panel';
    panel.innerHTML = `
        <div class="code-viewer-header">
            <div class="code-viewer-filename" id="cvFilename">file.txt</div>
            <span class="code-viewer-lang-badge" id="cvLang">text</span>
            <div class="code-viewer-actions">
                <button class="code-viewer-btn primary" id="cvPreviewBtn" style="display: none;">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                    Preview
                </button>
                <button class="code-viewer-btn primary" id="cvDownloadBtn">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2"
                         stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                    Download
                </button>
                <button class="code-viewer-btn" id="cvCopyBtn">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2"
                         stroke-linecap="round" stroke-linejoin="round">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                    </svg>
                    Copy
                </button>
            </div>
            <button class="code-viewer-close" id="cvCloseBtn" title="Close">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-width="2"
                     stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </button>
        </div>
        <div class="code-viewer-line-numbers">
            <div class="code-viewer-gutters" id="cvGutters"></div>
            <div class="code-viewer-body" id="cvBody">
                <pre><code id="cvCode"></code></pre>
            </div>
        </div>
        <div class="code-viewer-footer">
            <div class="code-viewer-footer-stat">Lines: <span id="cvLineCount">0</span></div>
            <div class="code-viewer-footer-stat">Chars: <span id="cvCharCount">0</span></div>
        </div>
    `;

    document.body.appendChild(overlay);
    document.body.appendChild(panel);

    document.getElementById('cvCloseBtn').addEventListener('click', closeViewer);
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeViewer(); });

    document.getElementById('cvCopyBtn').addEventListener('click', () => {
        const text = document.getElementById('cvCode').textContent;
        navigator.clipboard.writeText(text).then(() => {
            const btn = document.getElementById('cvCopyBtn');
            const orig = btn.innerHTML;
            btn.innerHTML = '✓ Copied!';
            btn.style.color = '#a385ff';
            setTimeout(() => { btn.innerHTML = orig; btn.style.color = ''; }, 1800);
        });
    });

    document.getElementById('cvDownloadBtn').addEventListener('click', () => {
        const filename = document.getElementById('cvFilename').textContent;
        const content = document.getElementById('cvCode').textContent;
        triggerDownload(filename, content);
    });

    let currentCardEl = null;
    let currentViewerCode = '';

    document.getElementById('cvPreviewBtn').addEventListener('click', () => {
        if (currentViewerCode) {
            previewHtmlFromCode(currentViewerCode);
        }
    });

    function previewHtmlFromCode(htmlCode) {
        if (!document.getElementById('preview-modal-styles')) {
            const style = document.createElement('style');
            style.id = 'preview-modal-styles';
            style.textContent = `
                @keyframes preview-fade-in {
                    from { opacity: 0; transform: scale(0.98); }
                    to { opacity: 1; transform: scale(1); }
                }
                @keyframes preview-fade-out {
                    from { opacity: 1; transform: scale(1); }
                    to { opacity: 0; transform: scale(0.98); }
                }
            `;
            document.head.appendChild(style);
        }

        const modal = document.createElement('div');
        modal.className = 'html-preview-modal';
        modal.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;background:var(--overlay-bg, rgba(10,10,12,0.85));backdrop-filter:blur(16px);z-index:99999;display:flex;flex-direction:column;animation:preview-fade-in 0.25s cubic-bezier(0.16,1,0.3,1);font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;';

        const header = document.createElement('div');
        header.style.cssText = 'height:64px;background:var(--body-bg, rgba(15,15,20,0.9));border-bottom:1px solid var(--panel-border, rgba(255,255,255,0.08));display:flex;align-items:center;justify-content:space-between;padding:0 24px;color:var(--text-primary, #fff);';

        const title = document.createElement('div');
        title.textContent = 'Live Webpage Preview';
        title.style.cssText = 'font-weight:600;font-size:15px;letter-spacing:-0.01em;';
        header.appendChild(title);

        const controls = document.createElement('div');
        controls.style.cssText = 'display:flex;gap:8px;';

        const devices = [
            { name: 'Desktop', width: '100%', icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>' },
            { name: 'Tablet', width: '768px', icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>' },
            { name: 'Mobile', width: '375px', icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>' }
        ];

        const buttons = [];
        devices.forEach(device => {
            const devBtn = document.createElement('button');
            devBtn.innerHTML = `${device.icon} <span style="margin-left:6px;">${device.name}</span>`;
            devBtn.style.cssText = `background:${device.name === 'Desktop' ? 'var(--iris-purple, #a385ff)' : 'var(--input-bg, rgba(255,255,255,0.05))'};color:${device.name === 'Desktop' ? 'var(--btn-text, #fff)' : 'var(--text-primary, #fff)'};border:none;padding:8px 16px;border-radius:20px;cursor:pointer;font-size:12px;font-weight:600;display:flex;align-items:center;transition:all 0.2s;`;
            devBtn.onclick = () => {
                iframeWrapper.style.width = device.width;
                buttons.forEach(b => {
                    b.style.backgroundColor = 'var(--input-bg, rgba(255,255,255,0.05))';
                    b.style.color = 'var(--text-primary, #fff)';
                });
                devBtn.style.backgroundColor = 'var(--iris-purple, #a385ff)';
                devBtn.style.color = 'var(--btn-text, #fff)';
            };
            buttons.push(devBtn);
            controls.appendChild(devBtn);
        });
        header.appendChild(controls);

        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
        closeBtn.style.cssText = 'background:none;border:none;color:var(--text-primary, #fff);cursor:pointer;opacity:0.7;transition:opacity 0.2s;';
        closeBtn.onmouseenter = () => closeBtn.style.opacity = '1';
        closeBtn.onmouseleave = () => closeBtn.style.opacity = '0.7';
        closeBtn.onclick = () => {
            modal.style.animation = 'preview-fade-out 0.2s ease';
            setTimeout(() => modal.remove(), 180);
        };
        header.appendChild(closeBtn);
        modal.appendChild(header);

        const bodyArea = document.createElement('div');
        bodyArea.style.cssText = 'flex:1;display:flex;justify-content:center;align-items:center;padding:24px;overflow:hidden;';

        const iframeWrapper = document.createElement('div');
        iframeWrapper.style.cssText = 'width:100%;height:100%;max-width:100%;max-height:100%;background:#fff;border-radius:16px;box-shadow:0 25px 60px rgba(0,0,0,0.6);overflow:hidden;transition:width 0.4s cubic-bezier(0.16,1,0.3,1);';

        const iframe = document.createElement('iframe');
        iframe.style.cssText = 'width:100%;height:100%;border:none;';
        iframe.sandbox = 'allow-scripts allow-modals allow-same-origin';
        iframe.srcdoc = htmlCode;

        iframeWrapper.appendChild(iframe);
        bodyArea.appendChild(iframeWrapper);
        modal.appendChild(bodyArea);

        document.body.appendChild(modal);
    }

    function openViewer(filename, lang, code) {
        document.getElementById('cvFilename').textContent = filename;
        document.getElementById('cvLang').textContent = lang;
        currentViewerCode = code;

        const previewBtn = document.getElementById('cvPreviewBtn');
        if (lang && lang.toLowerCase() === 'html') {
            previewBtn.style.display = 'flex';
            previewBtn.style.alignItems = 'center';
            previewBtn.style.gap = '6px';
        } else {
            previewBtn.style.display = 'none';
        }

        const lines = code.split('\n');
        
        const esc = (str) => str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        
        let state = 'NORMAL';
        const formattedLines = lines.map(line => {
            const trimmed = line.trim();
            if (trimmed === '<<<<' || trimmed.startsWith('<<<< SEARCH')) {
                state = 'IN_SEARCH';
                return `<div class="diff-marker">${esc(line)}</div>`;
            } else if (trimmed === '====' || trimmed.startsWith('=======')) {
                state = 'IN_REPLACE';
                return `<div class="diff-marker">${esc(line)}</div>`;
            } else if (trimmed === '>>>>' || trimmed.startsWith('>>>> REPLACE')) {
                state = 'NORMAL';
                return `<div class="diff-marker">${esc(line)}</div>`;
            }

            const escaped = esc(line) || ' ';
            if (state === 'IN_SEARCH') {
                return `<div class="diff-search-line">${escaped}</div>`;
            } else if (state === 'IN_REPLACE') {
                return `<div class="diff-replace-line">${escaped}</div>`;
            } else {
                return `<div>${escaped}</div>`;
            }
        });

        document.getElementById('cvCode').innerHTML = formattedLines.join('');

        // Build line-number gutter
        const gutters = document.getElementById('cvGutters');
        gutters.innerHTML = lines
            .map((_, i) => `<div class="code-viewer-gutter-line">${i + 1}</div>`)
            .join('');

        document.getElementById('cvLineCount').textContent = lines.length;
        document.getElementById('cvCharCount').textContent = code.length.toLocaleString();

        // Sync scroll between gutter and body
        const body = document.getElementById('cvBody');
        body.addEventListener('scroll', () => { gutters.scrollTop = body.scrollTop; });

        overlay.classList.add('visible');
        requestAnimationFrame(() => panel.classList.add('open'));
        document.body.classList.add('code-viewer-open');
    }

    function closeViewer() {
        panel.classList.remove('open');
        overlay.classList.remove('visible');
        document.body.classList.remove('code-viewer-open');
        currentCardEl = null;
    }

    // Called when user clicks anywhere on the file card
    window.openCodeViewer = function (cardEl) {
        currentCardEl = cardEl;
        const filename = cardEl.dataset.filename;
        const lang = cardEl.dataset.lang;
        const fcId = cardEl.dataset.filecardId;
        const codeText = window.fileCardCache[fcId] || '';
        openViewer(filename, lang, codeText);
    };

    // Called from the Preview button inside the file card
    window.previewFileCard = function (btn) {
        const card = btn.closest('.file-card');
        const fcId = card.dataset.filecardId;
        const codeText = window.fileCardCache[fcId] || '';
        if (codeText) {
            previewHtmlFromCode(codeText);
        }
    };

    // Called from the Download button inside the file card
    window.downloadFileCard = function (btn) {
        const card = btn.closest('.file-card');
        const filename = card.dataset.filename;
        const fcId = card.dataset.filecardId;
        const codeText = window.fileCardCache[fcId] || '';
        triggerDownload(filename, codeText);
    };

    window.previewHtml = function (btn) {
        const container = btn.closest('.code-container');
        const codeEl = container.querySelector('code');
        const htmlCode = codeEl.textContent;

        if (!document.getElementById('preview-modal-styles')) {
            const style = document.createElement('style');
            style.id = 'preview-modal-styles';
            style.textContent = `
                @keyframes preview-fade-in {
                    from { opacity: 0; transform: scale(0.98); }
                    to { opacity: 1; transform: scale(1); }
                }
                @keyframes preview-fade-out {
                    from { opacity: 1; transform: scale(1); }
                    to { opacity: 0; transform: scale(0.98); }
                }
            `;
            document.head.appendChild(style);
        }

        const modal = document.createElement('div');
        modal.className = 'html-preview-modal';
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100vw';
        modal.style.height = '100vh';
        modal.style.backgroundColor = 'var(--overlay-bg, rgba(10, 10, 12, 0.85))';
        modal.style.backdropFilter = 'blur(16px)';
        modal.style.zIndex = '99999';
        modal.style.display = 'flex';
        modal.style.flexDirection = 'column';
        modal.style.animation = 'preview-fade-in 0.25s cubic-bezier(0.16, 1, 0.3, 1)';
        modal.style.fontFamily = 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

        const header = document.createElement('div');
        header.style.height = '64px';
        header.style.backgroundColor = 'var(--body-bg, rgba(15, 15, 20, 0.9))';
        header.style.borderBottom = '1px solid var(--panel-border, rgba(255, 255, 255, 0.08))';
        header.style.display = 'flex';
        header.style.alignItems = 'center';
        header.style.justifyContent = 'space-between';
        header.style.padding = '0 24px';
        header.style.color = 'var(--text-primary, #fff)';

        const title = document.createElement('div');
        title.textContent = 'Live Webpage Preview';
        title.style.fontWeight = '600';
        title.style.fontSize = '15px';
        title.style.letterSpacing = '-0.01em';
        header.appendChild(title);

        const controls = document.createElement('div');
        controls.style.display = 'flex';
        controls.style.gap = '8px';

        const devices = [
            { name: 'Desktop', width: '100%', icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>' },
            { name: 'Tablet', width: '768px', icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>' },
            { name: 'Mobile', width: '375px', icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>' }
        ];

        const buttons = [];
        devices.forEach(device => {
            const devBtn = document.createElement('button');
            devBtn.innerHTML = `${device.icon} <span style="margin-left: 6px;">${device.name}</span>`;
            devBtn.style.backgroundColor = device.name === 'Desktop' ? 'var(--iris-purple, #a385ff)' : 'var(--input-bg, rgba(255, 255, 255, 0.05))';
            devBtn.style.color = device.name === 'Desktop' ? 'var(--btn-text, #fff)' : 'var(--text-primary, #fff)';
            devBtn.style.border = 'none';
            devBtn.style.padding = '8px 16px';
            devBtn.style.borderRadius = '20px';
            devBtn.style.cursor = 'pointer';
            devBtn.style.fontSize = '12px';
            devBtn.style.fontWeight = '600';
            devBtn.style.display = 'flex';
            devBtn.style.alignItems = 'center';
            devBtn.style.transition = 'all 0.2s';

            devBtn.onclick = () => {
                iframeWrapper.style.width = device.width;
                buttons.forEach(b => {
                    b.style.backgroundColor = 'var(--input-bg, rgba(255, 255, 255, 0.05))';
                    b.style.color = 'var(--text-primary, #fff)';
                });
                devBtn.style.backgroundColor = 'var(--iris-purple, #a385ff)';
                devBtn.style.color = 'var(--btn-text, #fff)';
            };

            buttons.push(devBtn);
            controls.appendChild(devBtn);
        });
        header.appendChild(controls);

        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
        closeBtn.style.background = 'none';
        closeBtn.style.border = 'none';
        closeBtn.style.color = 'var(--text-primary, #fff)';
        closeBtn.style.cursor = 'pointer';
        closeBtn.style.opacity = '0.7';
        closeBtn.style.transition = 'opacity 0.2s';
        closeBtn.onmouseenter = () => closeBtn.style.opacity = '1';
        closeBtn.onmouseleave = () => closeBtn.style.opacity = '0.7';
        closeBtn.onclick = () => {
            modal.style.animation = 'preview-fade-out 0.2s ease';
            setTimeout(() => modal.remove(), 180);
        };
        header.appendChild(closeBtn);
        modal.appendChild(header);

        const bodyArea = document.createElement('div');
        bodyArea.style.flex = '1';
        bodyArea.style.display = 'flex';
        bodyArea.style.justifyContent = 'center';
        bodyArea.style.alignItems = 'center';
        bodyArea.style.padding = '24px';
        bodyArea.style.overflow = 'hidden';

        const iframeWrapper = document.createElement('div');
        iframeWrapper.style.width = '100%';
        iframeWrapper.style.height = '100%';
        iframeWrapper.style.maxWidth = '100%';
        iframeWrapper.style.maxHeight = '100%';
        iframeWrapper.style.backgroundColor = '#fff';
        iframeWrapper.style.borderRadius = '16px';
        iframeWrapper.style.boxShadow = '0 25px 60px rgba(0, 0, 0, 0.6)';
        iframeWrapper.style.overflow = 'hidden';
        iframeWrapper.style.transition = 'width 0.4s cubic-bezier(0.16, 1, 0.3, 1)';

        const iframe = document.createElement('iframe');
        iframe.style.width = '100%';
        iframe.style.height = '100%';
        iframe.style.border = 'none';
        iframe.sandbox = 'allow-scripts allow-modals allow-same-origin';
        iframe.srcdoc = htmlCode;

        iframeWrapper.appendChild(iframe);
        bodyArea.appendChild(iframeWrapper);
        modal.appendChild(bodyArea);

        document.body.appendChild(modal);
    };
})();
