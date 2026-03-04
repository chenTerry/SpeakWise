/**
 * AgentScope AI Interview - Main Application JavaScript
 * Web 界面主 JavaScript 文件
 * Version: v0.4.0
 */

// ==================== Global State ====================
const AppState = {
    currentTheme: 'dark',
    currentSession: null,
    currentScene: null,
    isTyping: false,
};

// ==================== API Helpers ====================
const API = {
    baseURL: '/api',
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        const response = await fetch(url, { ...defaultOptions, ...options });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Request failed' }));
            throw new Error(error.detail || 'Request failed');
        }
        
        return response.json();
    },
    
    // Scenes API
    scenes: {
        list(filters = {}) {
            const params = new URLSearchParams(filters);
            return API.request(`/scenes?${params}`);
        },
        get(sceneId) {
            return API.request(`/scenes/${sceneId}`);
        },
        start(sceneId, config = {}) {
            return API.request(`/scenes/${sceneId}/start`, {
                method: 'POST',
                body: JSON.stringify(config),
            });
        },
    },
    
    // Dialogue API
    dialogue: {
        createSession(sceneId, sceneName) {
            return API.request(`/dialogue/sessions?scene_id=${sceneId}&scene_name=${encodeURIComponent(sceneName)}`, {
                method: 'POST',
            });
        },
        getSession(sessionId) {
            return API.request(`/dialogue/sessions/${sessionId}`);
        },
        sendMessage(sessionId, content) {
            return API.request(`/dialogue/sessions/${sessionId}/messages`, {
                method: 'POST',
                body: JSON.stringify({ content }),
            });
        },
        complete(sessionId) {
            return API.request(`/dialogue/sessions/${sessionId}/complete`, {
                method: 'POST',
            });
        },
    },
    
    // Feedback API
    feedback: {
        generate(sessionId, messages = []) {
            return API.request('/feedback/generate', {
                method: 'POST',
                body: JSON.stringify({ session_id: sessionId, messages }),
            });
        },
        get(evaluationId) {
            return API.request(`/feedback/${evaluationId}`);
        },
        getSessionFeedback(sessionId) {
            return API.request(`/feedback/session/${sessionId}`);
        },
        exportJSON(evaluationId) {
            return `${API.baseURL}/feedback/${evaluationId}/export/json`;
        },
        exportMarkdown(evaluationId) {
            return `${API.baseURL}/feedback/${evaluationId}/export/markdown`;
        },
    },
};

// ==================== Theme Management ====================
const ThemeManager = {
    init() {
        const saved = localStorage.getItem('theme');
        if (saved) {
            this.setTheme(saved);
        }
        
        // Theme toggle button
        const toggle = document.getElementById('theme-toggle');
        if (toggle) {
            toggle.addEventListener('click', () => this.toggle());
        }
    },
    
    setTheme(theme) {
        AppState.currentTheme = theme;
        document.body.className = `theme-${theme}`;
        localStorage.setItem('theme', theme);
    },
    
    toggle() {
        const newTheme = AppState.currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    },
};

// ==================== UI Components ====================
const UI = {
    // Show loading spinner
    showLoading(container, message = '加载中...') {
        container.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <span class="loading-text">${message}</span>
            </div>
        `;
    },
    
    // Show empty state
    showEmpty(container, icon = '📭', title = '暂无数据', text = '') {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">${icon}</div>
                <h3 class="empty-state-title">${title}</h3>
                ${text ? `<p class="empty-state-text">${text}</p>` : ''}
            </div>
        `;
    },
    
    // Show error
    showError(container, message) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <h3 class="empty-state-title">出错了</h3>
                <p class="empty-state-text">${message}</p>
            </div>
        `;
    },
    
    // Create message bubble
    createMessageBubble(role, content, timestamp) {
        const bubble = document.createElement('div');
        bubble.className = `message-bubble ${role}`;
        
        const icons = {
            user: '👤',
            interviewer: '👨‍🏫',
            system: '⚙️',
        };
        
        const timeStr = timestamp 
            ? new Date(timestamp * 1000).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
            : new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
        
        bubble.innerHTML = `
            <div class="message-header">
                <span>${icons[role] || '💬'}</span>
                <span>${role === 'user' ? '你' : role === 'interviewer' ? '面试官' : '系统'}</span>
                <span>${timeStr}</span>
            </div>
            <div class="message-content">${this.escapeHtml(content)}</div>
        `;
        
        return bubble;
    },
    
    // Create typing indicator
    createTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.id = 'typing-indicator';
        indicator.innerHTML = `
            <span>面试官正在思考</span>
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        return indicator;
    },
    
    // Escape HTML
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    // Scroll to bottom
    scrollToBottom(container) {
        container.scrollTop = container.scrollHeight;
    },
};

// ==================== Scene Selection Page ====================
const SceneSelection = {
    container: null,
    filterSection: null,
    
    async init() {
        this.container = document.getElementById('scenes-container');
        this.filterSection = document.getElementById('filter-section');
        
        if (!this.container) return;
        
        await this.loadScenes();
        this.setupFilters();
    },
    
    async loadScenes(filters = {}) {
        UI.showLoading(this.container, '加载场景中...');
        
        try {
            const data = await API.scenes.list(filters);
            this.renderScenes(data.scenes);
        } catch (error) {
            UI.showError(this.container, `加载失败：${error.message}`);
        }
    },
    
    renderScenes(scenes) {
        if (!scenes || scenes.length === 0) {
            UI.showEmpty(this.container, '🎭', '暂无场景', '请稍后再试');
            return;
        }
        
        this.container.innerHTML = scenes.map(scene => `
            <div class="scene-card" data-scene-id="${scene.id}">
                <div class="scene-card-header">
                    <h3 class="scene-card-title">${this.escapeHtml(scene.name)}</h3>
                    <div class="scene-card-difficulty">
                        ${this.renderDifficultyStars(scene.difficulty)}
                    </div>
                </div>
                <p class="scene-card-description">${this.escapeHtml(scene.description)}</p>
                <div class="scene-card-tags">
                    ${scene.tags.map(tag => `<span class="scene-tag">${this.escapeHtml(tag)}</span>`).join('')}
                </div>
                <div class="scene-card-meta">
                    <span>⏱️ 约 ${scene.estimated_duration} 分钟</span>
                    <span>📂 ${this.escapeHtml(scene.domain)}</span>
                </div>
            </div>
        `).join('');
        
        // Add click handlers
        this.container.querySelectorAll('.scene-card').forEach(card => {
            card.addEventListener('click', () => this.selectScene(card.dataset.sceneId));
        });
    },
    
    renderDifficultyStars(difficulty) {
        let stars = '';
        for (let i = 1; i <= 5; i++) {
            stars += `<span class="difficulty-star ${i > difficulty ? 'empty' : ''}">★</span>`;
        }
        return stars;
    },
    
    selectScene(sceneId) {
        // Remove previous selection
        this.container.querySelectorAll('.scene-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Add selection
        const card = this.container.querySelector(`[data-scene-id="${sceneId}"]`);
        if (card) {
            card.classList.add('selected');
            AppState.currentScene = sceneId;
            
            // Show start button or redirect
            this.showStartButton(sceneId);
        }
    },
    
    showStartButton(sceneId) {
        let startBtn = document.getElementById('start-scene-btn');
        
        if (!startBtn) {
            startBtn = document.createElement('div');
            startBtn.id = 'start-scene-btn';
            startBtn.className = 'mt-4 text-center';
            startBtn.innerHTML = `
                <button class="btn btn-primary btn-lg" onclick="SceneSelection.startScene('${sceneId}')">
                    开始面试
                    <span class="btn-icon">→</span>
                </button>
            `;
            this.container.parentElement.appendChild(startBtn);
        } else {
            startBtn.innerHTML = `
                <button class="btn btn-primary btn-lg" onclick="SceneSelection.startScene('${sceneId}')">
                    开始面试
                    <span class="btn-icon">→</span>
                </button>
            `;
        }
    },
    
    async startScene(sceneId) {
        try {
            const result = await API.scenes.start(sceneId);
            
            // Create dialogue session
            const session = await API.dialogue.createSession(sceneId, result.scene_name);
            AppState.currentSession = session;
            
            // Redirect to dialogue page
            window.location.href = `/dialogue/${session.id}`;
        } catch (error) {
            alert(`启动失败：${error.message}`);
        }
    },
    
    setupFilters() {
        const domainFilter = document.getElementById('filter-domain');
        const difficultyFilter = document.getElementById('filter-difficulty');
        const styleFilter = document.getElementById('filter-style');
        
        if (domainFilter) {
            domainFilter.addEventListener('change', () => this.applyFilters());
        }
        if (difficultyFilter) {
            difficultyFilter.addEventListener('change', () => this.applyFilters());
        }
        if (styleFilter) {
            styleFilter.addEventListener('change', () => this.applyFilters());
        }
    },
    
    applyFilters() {
        const domain = document.getElementById('filter-domain')?.value || '';
        const difficulty = document.getElementById('filter-difficulty')?.value || '';
        const style = document.getElementById('filter-style')?.value || '';
        
        const filters = {};
        if (domain) filters.domain = domain;
        if (difficulty) filters.difficulty = difficulty;
        if (style) filters.style = style;
        
        this.loadScenes(filters);
    },
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
};

// ==================== Dialogue Page ====================
const DialoguePage = {
    messagesContainer: null,
    inputElement: null,
    sendButton: null,
    sessionId: null,
    
    async init() {
        // Get session ID from URL or data attribute
        const container = document.getElementById('dialogue-container');
        this.sessionId = container?.dataset.sessionId || this.getSessionIdFromURL();
        
        if (!this.sessionId) {
            alert('无效的会话 ID');
            window.location.href = '/scenes';
            return;
        }
        
        this.messagesContainer = document.getElementById('dialogue-messages');
        this.inputElement = document.getElementById('dialogue-input');
        this.sendButton = document.getElementById('send-button');
        
        if (!this.messagesContainer || !this.inputElement) return;
        
        // Load session
        await this.loadSession();
        
        // Setup event handlers
        this.setupEventHandlers();
        
        // Focus input
        this.inputElement.focus();
    },
    
    getSessionIdFromURL() {
        const match = window.location.pathname.match(/\/dialogue\/([^/]+)/);
        return match ? match[1] : null;
    },
    
    async loadSession() {
        UI.showLoading(this.messagesContainer, '加载对话历史...');
        
        try {
            const session = await API.dialogue.getSession(this.sessionId);
            AppState.currentSession = session;
            
            // Update header
            this.updateHeader(session);
            
            // Render messages
            this.renderMessages(session.messages || []);
        } catch (error) {
            UI.showError(this.messagesContainer, `加载失败：${error.message}`);
        }
    },
    
    updateHeader(session) {
        const titleEl = document.getElementById('dialogue-title');
        if (titleEl) {
            titleEl.textContent = `${session.scene_name} - 对话中`;
        }
    },
    
    renderMessages(messages) {
        this.messagesContainer.innerHTML = '';
        
        if (messages.length === 0) {
            // Show welcome message
            this.addSystemMessage('欢迎来到面试！请开始你的自我介绍。');
            return;
        }
        
        messages.forEach(msg => {
            const bubble = UI.createMessageBubble(msg.role, msg.content, msg.timestamp);
            this.messagesContainer.appendChild(bubble);
        });
        
        UI.scrollToBottom(this.messagesContainer);
    },
    
    setupEventHandlers() {
        // Send button
        this.sendButton?.addEventListener('click', () => this.sendMessage());
        
        // Enter key (Shift+Enter for new line)
        this.inputElement?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // End button
        const endBtn = document.getElementById('end-button');
        if (endBtn) {
            endBtn.addEventListener('click', () => this.endSession());
        }
    },
    
    async sendMessage() {
        const content = this.inputElement.value.trim();
        if (!content || AppState.isTyping) return;
        
        // Clear input
        this.inputElement.value = '';
        
        // Add user message
        const userBubble = UI.createMessageBubble('user', content);
        this.messagesContainer.appendChild(userBubble);
        UI.scrollToBottom(this.messagesContainer);
        
        // Show typing indicator
        AppState.isTyping = true;
        this.showTypingIndicator();
        
        try {
            // Send message
            const response = await API.dialogue.sendMessage(this.sessionId, content);
            
            // Remove typing indicator
            this.hideTypingIndicator();
            
            // Add AI response
            if (response.response) {
                const aiBubble = UI.createMessageBubble('interviewer', response.response.content, response.response.timestamp);
                this.messagesContainer.appendChild(aiBubble);
                UI.scrollToBottom(this.messagesContainer);
            }
        } catch (error) {
            this.hideTypingIndicator();
            this.addSystemMessage(`发送失败：${error.message}`);
        } finally {
            AppState.isTyping = false;
            this.inputElement.focus();
        }
    },
    
    showTypingIndicator() {
        const indicator = UI.createTypingIndicator();
        this.messagesContainer.appendChild(indicator);
        UI.scrollToBottom(this.messagesContainer);
    },
    
    hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    },
    
    addSystemMessage(content) {
        const bubble = UI.createMessageBubble('system', content);
        this.messagesContainer.appendChild(bubble);
        UI.scrollToBottom(this.messagesContainer);
    },
    
    async endSession() {
        if (!confirm('确定要结束面试吗？')) return;
        
        try {
            await API.dialogue.complete(this.sessionId);
            
            // Generate feedback
            const feedback = await API.feedback.getSessionFeedback(this.sessionId);
            
            // Redirect to feedback page
            window.location.href = `/feedback/${feedback.evaluation.id}`;
        } catch (error) {
            alert(`结束失败：${error.message}`);
        }
    },
};

// ==================== Feedback Page ====================
const FeedbackPage = {
    evaluationId: null,
    
    async init() {
        // Get evaluation ID from URL or data attribute
        const container = document.getElementById('feedback-container');
        this.evaluationId = container?.dataset.evaluationId || this.getEvaluationIdFromURL();
        
        if (!this.evaluationId) {
            alert('无效的评估 ID');
            window.location.href = '/';
            return;
        }
        
        await this.loadFeedback();
    },
    
    getEvaluationIdFromURL() {
        const match = window.location.pathname.match(/\/feedback\/([^/]+)/);
        return match ? match[1] : null;
    },
    
    async loadFeedback() {
        const container = document.getElementById('feedback-container');
        UI.showLoading(container, '加载评估报告...');
        
        try {
            const report = await API.feedback.getSessionFeedback(AppState.currentSession?.id || '');
            this.renderFeedback(report);
        } catch (error) {
            UI.showError(container, `加载失败：${error.message}`);
        }
    },
    
    renderFeedback(report) {
        const { evaluation, charts_data } = report;
        
        const container = document.getElementById('feedback-container');
        container.innerHTML = `
            <div class="feedback-header">
                <h1 class="feedback-title">面试评估报告</h1>
                <div class="feedback-rating">${evaluation.overall_score.toFixed(1)}</div>
                <div class="feedback-rating-label">/ 5.0 - 评级：${evaluation.rating}</div>
            </div>
            
            <div class="score-cards">
                ${this.renderScoreCard('总体评分', evaluation.overall_score.toFixed(1))}
                ${this.renderScoreCard('内容质量', this.getDimensionScore(evaluation, '内容质量'))}
                ${this.renderScoreCard('表达清晰度', this.getDimensionScore(evaluation, '表达清晰度'))}
                ${this.renderScoreCard('专业知识', this.getDimensionScore(evaluation, '专业知识'))}
            </div>
            
            <div class="dimension-section">
                <h2 class="dimension-section-title">📊 维度评分详情</h2>
                ${this.renderDimensionBreakdown(evaluation.dimensions)}
            </div>
            
            <div class="dimension-section">
                <h2 class="dimension-section-title">💪 优势</h2>
                <ul class="strengths-list">
                    ${evaluation.strengths.map(s => `
                        <li class="strength-item">
                            <span class="strength-icon">✓</span>
                            <span class="strength-text">${this.escapeHtml(s)}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
            
            <div class="dimension-section">
                <h2 class="dimension-section-title">📝 改进建议</h2>
                <ul class="suggestions-list">
                    ${evaluation.suggestions.map(s => `
                        <li class="suggestion-item">
                            <span class="suggestion-icon">!</span>
                            <span class="suggestion-text">${this.escapeHtml(s)}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
            
            <div class="dimension-section">
                <h2 class="dimension-section-title">📋 总结</h2>
                <p style="color: var(--color-text-secondary); line-height: 1.8;">
                    ${this.escapeHtml(evaluation.summary)}
                </p>
            </div>
            
            <div class="export-section">
                <button class="btn btn-primary" onclick="FeedbackPage.exportJSON()">
                    📥 导出 JSON
                </button>
                <button class="btn btn-secondary" onclick="FeedbackPage.exportMarkdown()">
                    📄 导出 Markdown
                </button>
                <a href="/scenes" class="btn btn-success">
                    🔄 再试一次
                </a>
            </div>
        `;
    },
    
    renderScoreCard(label, score) {
        return `
            <div class="score-card">
                <div class="score-card-value">${typeof score === 'number' ? score.toFixed(1) : 'N/A'}</div>
                <div class="score-card-label">${label}</div>
            </div>
        `;
    },
    
    getDimensionScore(dimensions, name) {
        const dim = Array.isArray(dimensions) 
            ? dimensions.find(d => d.name === name)
            : dimensions[name];
        return dim ? (dim.score || dim) : 0;
    },
    
    renderDimensionBreakdown(dimensions) {
        if (!Array.isArray(dimensions)) return '';
        
        return dimensions.map(dim => `
            <div class="dimension-item">
                <div class="dimension-name">${this.escapeHtml(dim.name)}</div>
                <div class="dimension-bar-container">
                    <div class="dimension-bar" style="width: ${(dim.score / 5) * 100}%"></div>
                </div>
                <div class="dimension-score">${dim.score.toFixed(1)}</div>
                <div class="dimension-comment">${this.escapeHtml(dim.comment || '')}</div>
            </div>
        `).join('');
    },
    
    exportJSON() {
        window.location.href = API.feedback.exportJSON(this.evaluationId);
    },
    
    exportMarkdown() {
        window.location.href = API.feedback.exportMarkdown(this.evaluationId);
    },
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
};

// ==================== Initialization ====================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize theme
    ThemeManager.init();
    
    // Initialize page-specific logic
    if (document.getElementById('scenes-container')) {
        SceneSelection.init();
    }
    
    if (document.getElementById('dialogue-container')) {
        DialoguePage.init();
    }
    
    if (document.getElementById('feedback-container')) {
        FeedbackPage.init();
    }
});

// Export for global access
window.AppState = AppState;
window.API = API;
window.ThemeManager = ThemeManager;
window.UI = UI;
window.SceneSelection = SceneSelection;
window.DialoguePage = DialoguePage;
window.FeedbackPage = FeedbackPage;
