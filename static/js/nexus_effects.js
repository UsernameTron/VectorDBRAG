// NEXUS AI Platform - Interactive Effects JavaScript

class NexusEffects {
    constructor() {
        this.init();
    }

    init() {
        this.createStarField();
        this.initializeAgentCards();
        this.initializeFloatingChat();
        this.initializeRealtimeUpdates();
        this.initializePerformanceMonitoring();
    }

    // Create animated star field background
    createStarField() {
        const starsContainer = document.getElementById('stars');
        if (!starsContainer) {
            // Create stars container if it doesn't exist
            const container = document.createElement('div');
            container.id = 'stars';
            container.className = 'stars';
            document.body.appendChild(container);
        }

        const stars = document.getElementById('stars');
        const numStars = 100;

        for (let i = 0; i < numStars; i++) {
            const star = document.createElement('div');
            star.className = 'star';
            star.style.left = Math.random() * 100 + '%';
            star.style.top = Math.random() * 100 + '%';
            star.style.animationDelay = Math.random() * 3 + 's';
            star.style.animationDuration = (Math.random() * 3 + 2) + 's';
            stars.appendChild(star);
        }
    }

    // Initialize agent card interactions
    initializeAgentCards() {
        const agentCards = document.querySelectorAll('.nexus-agent-card, .agent-card');
        
        agentCards.forEach(card => {
            card.addEventListener('click', (e) => {
                this.activateAgent(card);
            });

            card.addEventListener('mouseenter', (e) => {
                this.highlightAgent(card);
            });

            card.addEventListener('mouseleave', (e) => {
                this.unhighlightAgent(card);
            });
        });
    }

    // Agent activation animation
    activateAgent(card) {
        const agentName = card.querySelector('.nexus-agent-name, .agent-name')?.textContent || 'Unknown Agent';
        
        // Add activation effect
        card.style.transform = 'scale(1.05)';
        card.style.boxShadow = '0 0 40px rgba(0, 245, 255, 0.6)';
        
        // Reset after animation
        setTimeout(() => {
            card.style.transform = '';
            card.style.boxShadow = '';
        }, 300);

        // Show agent activation message
        this.showNotification(`${agentName} Activated`, 'success');

        // Open chat with selected agent
        this.openAgentChat(agentName);
    }

    // Highlight agent on hover
    highlightAgent(card) {
        const icon = card.querySelector('.nexus-agent-icon, .agent-icon');
        if (icon) {
            icon.style.transform = 'scale(1.1) rotate(5deg)';
            icon.style.boxShadow = '0 0 30px rgba(0, 245, 255, 0.8)';
        }
    }

    // Remove highlight
    unhighlightAgent(card) {
        const icon = card.querySelector('.nexus-agent-icon, .agent-icon');
        if (icon) {
            icon.style.transform = '';
            icon.style.boxShadow = '';
        }
    }

    // Initialize floating chat widget
    initializeFloatingChat() {
        const chatWidget = document.querySelector('.nexus-chat-widget, .chat-section');
        if (chatWidget) {
            // Add minimize/maximize functionality
            const header = chatWidget.querySelector('.nexus-chat-header, .chat-header');
            if (header) {
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => {
                    this.toggleChatWidget(chatWidget);
                });
            }

            // Initialize chat input
            const chatInput = chatWidget.querySelector('.nexus-input, .chat-input, input, textarea');
            if (chatInput) {
                chatInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        this.sendChatMessage(chatInput.value);
                        chatInput.value = '';
                    }
                });
            }
        }
    }

    // Toggle chat widget visibility
    toggleChatWidget(widget) {
        const isMinimized = widget.style.height === '60px';
        
        if (isMinimized) {
            widget.style.height = '500px';
            widget.style.opacity = '1';
        } else {
            widget.style.height = '60px';
            widget.style.opacity = '0.8';
        }
    }

    // Open chat with specific agent
    openAgentChat(agentName) {
        const chatWidget = document.querySelector('.nexus-chat-widget, .chat-section');
        if (chatWidget) {
            const chatTitle = chatWidget.querySelector('.nexus-chat-title, .chat-title');
            if (chatTitle) {
                chatTitle.textContent = `${agentName} Interface`;
            }

            // Add welcome message
            this.addChatMessage(`${agentName} online. How can I assist you?`, 'agent');
        }
    }

    // Send chat message
    async sendChatMessage(message) {
        if (!message.trim()) return;

        // Add user message to chat
        this.addChatMessage(message, 'user');

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send to API (assuming we have an endpoint)
            const response = await fetch('/api/agents/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    agent_type: this.getCurrentAgent()
                })
            });

            const data = await response.json();
            
            // Remove typing indicator
            this.hideTypingIndicator();

            // Add agent response
            this.addChatMessage(data.response || 'I apologize, but I encountered an error processing your request.', 'agent');

        } catch (error) {
            this.hideTypingIndicator();
            this.addChatMessage('Connection error. Please try again.', 'error');
            console.error('Chat error:', error);
        }
    }

    // Add message to chat
    addChatMessage(message, type) {
        const chatMessages = document.querySelector('.chat-messages');
        if (!chatMessages) return;

        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}`;
        messageElement.innerHTML = `
            <div class="message-content">${message}</div>
            <div class="message-time">${new Date().toLocaleTimeString()}</div>
        `;

        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Add fade-in animation
        messageElement.style.opacity = '0';
        messageElement.style.transform = 'translateY(10px)';
        
        setTimeout(() => {
            messageElement.style.opacity = '1';
            messageElement.style.transform = 'translateY(0)';
            messageElement.style.transition = 'all 0.3s ease';
        }, 10);
    }

    // Show typing indicator
    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.innerHTML = `
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
        `;
        
        const chatMessages = document.querySelector('.chat-messages');
        if (chatMessages) {
            chatMessages.appendChild(indicator);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // Hide typing indicator
    hideTypingIndicator() {
        const indicator = document.querySelector('.typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    // Get current active agent
    getCurrentAgent() {
        const chatTitle = document.querySelector('.nexus-chat-title, .chat-title');
        return chatTitle ? chatTitle.textContent.replace(' Interface', '') : 'research';
    }

    // Initialize real-time updates
    initializeRealtimeUpdates() {
        // Update agent status indicators
        setInterval(() => {
            this.updateAgentStatus();
        }, 5000);

        // Update performance metrics
        setInterval(() => {
            this.updatePerformanceMetrics();
        }, 10000);
    }

    // Update agent status
    updateAgentStatus() {
        const statusDots = document.querySelectorAll('.nexus-status-dot, .status-dot');
        statusDots.forEach(dot => {
            // Simulate status changes
            const isOnline = Math.random() > 0.1; // 90% online rate
            dot.style.background = isOnline ? '#00ff00' : '#ff6600';
        });
    }

    // Initialize performance monitoring
    initializePerformanceMonitoring() {
        // Monitor page performance
        const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.entryType === 'navigation') {
                    this.updateLoadTime(entry.loadEventEnd - entry.loadEventStart);
                }
            }
        });

        observer.observe({ entryTypes: ['navigation'] });
    }

    // Update performance metrics
    updatePerformanceMetrics() {
        const metrics = document.querySelectorAll('.nexus-metric-value');
        metrics.forEach(metric => {
            const label = metric.parentElement?.querySelector('.nexus-metric-label')?.textContent;
            
            if (label?.includes('CPU')) {
                metric.textContent = (Math.random() * 30 + 10).toFixed(1) + '%';
            } else if (label?.includes('Memory')) {
                metric.textContent = (Math.random() * 20 + 40).toFixed(1) + '%';
            } else if (label?.includes('Response')) {
                metric.textContent = (Math.random() * 2 + 1).toFixed(2) + 's';
            }
        });

        // Update progress bars
        const progressBars = document.querySelectorAll('.nexus-progress-fill');
        progressBars.forEach(bar => {
            const percentage = Math.random() * 100;
            bar.style.width = percentage + '%';
        });
    }

    // Show notification
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `nexus-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ'}</span>
                <span class="notification-message">${message}</span>
            </div>
        `;

        // Add styles
        Object.assign(notification.style, {
            position: 'fixed',
            top: '100px',
            right: '30px',
            background: 'rgba(0, 245, 255, 0.9)',
            color: '#000',
            padding: '15px 20px',
            borderRadius: '10px',
            zIndex: '1000',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease',
            backdropFilter: 'blur(10px)',
            boxShadow: '0 4px 20px rgba(0, 245, 255, 0.3)'
        });

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);

        // Auto remove
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }

    // Particle effects for interactions
    createParticleEffect(x, y) {
        const particleCount = 15;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.style.cssText = `
                position: fixed;
                width: 4px;
                height: 4px;
                background: #00f5ff;
                border-radius: 50%;
                pointer-events: none;
                z-index: 1000;
                left: ${x}px;
                top: ${y}px;
            `;

            document.body.appendChild(particle);

            // Animate particle
            const angle = (Math.PI * 2 * i) / particleCount;
            const velocity = 2 + Math.random() * 3;
            const life = 1000 + Math.random() * 500;

            let px = x, py = y;
            const animate = () => {
                px += Math.cos(angle) * velocity;
                py += Math.sin(angle) * velocity;
                
                particle.style.left = px + 'px';
                particle.style.top = py + 'px';
                particle.style.opacity = particle.style.opacity - 0.02;

                if (parseFloat(particle.style.opacity) > 0) {
                    requestAnimationFrame(animate);
                } else {
                    particle.remove();
                }
            };

            particle.style.opacity = '1';
            animate();
        }
    }

    // Add click particle effects
    addClickEffects() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.nexus-btn, .nexus-agent-card')) {
                this.createParticleEffect(e.clientX, e.clientY);
            }
        });
    }
}

// Initialize NEXUS effects when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const nexus = new NexusEffects();
    nexus.addClickEffects();
    
    // Add global keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 'k':
                    e.preventDefault();
                    // Focus chat input
                    const chatInput = document.querySelector('.nexus-input, .chat-input');
                    if (chatInput) chatInput.focus();
                    break;
                case 'm':
                    e.preventDefault();
                    // Toggle monitoring
                    nexus.showNotification('Monitoring toggled', 'info');
                    break;
            }
        }
    });
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NexusEffects;
}
