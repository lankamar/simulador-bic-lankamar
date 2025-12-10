// Email Cleaner Pro - Popup Script

class EmailCleanerPopup {
    constructor() {
        this.stats = {
            total: 0,
            spam: 0,
            newsletters: 0,
            promotions: 0,
            social: 0,
            notifications: 0,
            old: 0
        };
        this.topSenders = [];
        this.currentProvider = null;

        this.init();
    }

    async init() {
        this.bindEvents();
        await this.detectProvider();
        await this.loadStoredData();
    }

    bindEvents() {
        // Scan button
        document.getElementById('btnScan').addEventListener('click', () => this.scanInbox());

        // Delete button
        document.getElementById('btnDelete').addEventListener('click', () => this.deleteSelected());

        // Unsubscribe button
        document.getElementById('btnUnsubscribe').addEventListener('click', () => this.unsubscribeSelected());

        // Category checkboxes
        document.querySelectorAll('.category-item input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateActionButtons());
        });

        // Settings toggles
        document.getElementById('autoClean').addEventListener('change', (e) => {
            this.saveSetting('autoClean', e.target.checked);
        });

        document.getElementById('safeMode').addEventListener('change', (e) => {
            this.saveSetting('safeMode', e.target.checked);
        });
    }

    async detectProvider() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            const url = tab?.url || '';

            let provider = { name: 'Desconocido', icon: '❓', class: '' };

            if (url.includes('mail.google.com')) {
                provider = { name: 'Gmail', icon: '📧', class: 'gmail' };
            } else if (url.includes('outlook.live.com') || url.includes('outlook.office.com')) {
                provider = { name: 'Outlook', icon: '📬', class: 'outlook' };
            } else if (url.includes('mail.yahoo.com')) {
                provider = { name: 'Yahoo', icon: '📭', class: 'yahoo' };
            } else if (url.includes('mail.proton.me')) {
                provider = { name: 'ProtonMail', icon: '🔐', class: 'protonmail' };
            }

            this.currentProvider = provider;
            this.updateProviderBadge(provider);

        } catch (error) {
            console.error('Error detecting provider:', error);
        }
    }

    updateProviderBadge(provider) {
        const badge = document.getElementById('providerBadge');
        badge.className = `provider-badge ${provider.class}`;
        badge.innerHTML = `
      <span class="provider-icon">${provider.icon}</span>
      <span class="provider-name">${provider.name}</span>
    `;
    }

    async loadStoredData() {
        try {
            const data = await chrome.storage.local.get(['emailStats', 'topSenders', 'settings']);

            if (data.emailStats) {
                this.stats = data.emailStats;
                this.updateStatsUI();
            }

            if (data.topSenders) {
                this.topSenders = data.topSenders;
                this.updateTopSendersUI();
            }

            if (data.settings) {
                document.getElementById('autoClean').checked = data.settings.autoClean || false;
                document.getElementById('safeMode').checked = data.settings.safeMode !== false;
            }
        } catch (error) {
            console.error('Error loading stored data:', error);
        }
    }

    async scanInbox() {
        const btn = document.getElementById('btnScan');
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Escaneando...';

        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

            // Send message to content script
            const response = await chrome.tabs.sendMessage(tab.id, { action: 'scanEmails' });

            if (response && response.success) {
                this.stats = response.stats;
                this.topSenders = response.topSenders;

                // Save to storage
                await chrome.storage.local.set({
                    emailStats: this.stats,
                    topSenders: this.topSenders
                });

                this.updateStatsUI();
                this.updateTopSendersUI();
                this.showNotification('✅ Escaneo completado');
            } else {
                this.showNotification('⚠️ No se pudo escanear. Asegúrate de estar en una bandeja de correo.', 'warning');
            }

        } catch (error) {
            console.error('Error scanning inbox:', error);
            this.showNotification('❌ Error al escanear. Recarga la página e intenta de nuevo.', 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<span class="btn-icon">🔍</span> Escanear Bandeja';
        }
    }

    updateStatsUI() {
        document.getElementById('totalEmails').textContent = this.formatNumber(this.stats.total);
        document.getElementById('spamCount').textContent = this.formatNumber(this.stats.spam + this.stats.promotions);
        document.getElementById('newsletterCount').textContent = this.formatNumber(this.stats.newsletters);

        // Estimate saved space (avg 50KB per email)
        const deleted = this.stats.deleted || 0;
        const savedMB = ((deleted * 50) / 1024).toFixed(1);
        document.getElementById('savedSpace').textContent = `${savedMB} MB`;

        // Update category counts
        document.getElementById('count-newsletters').textContent = this.stats.newsletters || 0;
        document.getElementById('count-promotions').textContent = this.stats.promotions || 0;
        document.getElementById('count-social').textContent = this.stats.social || 0;
        document.getElementById('count-notifications').textContent = this.stats.notifications || 0;
        document.getElementById('count-old').textContent = this.stats.old || 0;
    }

    updateTopSendersUI() {
        const list = document.getElementById('senderList');

        if (this.topSenders.length === 0) {
            list.innerHTML = `
        <div class="loading-placeholder">
          <span>📭</span>
          Escanea tu bandeja para ver remitentes
        </div>
      `;
            return;
        }

        list.innerHTML = this.topSenders.slice(0, 5).map(sender => `
      <div class="sender-item">
        <div class="sender-info">
          <div class="sender-avatar">${this.getInitials(sender.name)}</div>
          <span class="sender-name" title="${sender.email}">${sender.name}</span>
        </div>
        <span class="sender-count">${sender.count} emails</span>
      </div>
    `).join('');
    }

    getInitials(name) {
        return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
    }

    formatNumber(num) {
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    updateActionButtons() {
        const checked = document.querySelectorAll('.category-item input[type="checkbox"]:checked');
        const hasSelection = checked.length > 0;

        document.getElementById('btnDelete').disabled = !hasSelection;
        document.getElementById('btnUnsubscribe').disabled = !hasSelection;
    }

    async deleteSelected() {
        const safeMode = document.getElementById('safeMode').checked;
        const categories = this.getSelectedCategories();

        if (safeMode) {
            const count = this.getTotalSelectedCount(categories);
            if (!confirm(`¿Eliminar ${count} emails de las categorías seleccionadas?`)) {
                return;
            }
        }

        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            const response = await chrome.tabs.sendMessage(tab.id, {
                action: 'deleteEmails',
                categories: categories
            });

            if (response && response.success) {
                this.stats.deleted = (this.stats.deleted || 0) + response.deletedCount;
                await chrome.storage.local.set({ emailStats: this.stats });
                this.updateStatsUI();
                this.showNotification(`🗑️ ${response.deletedCount} emails eliminados`);
            }
        } catch (error) {
            this.showNotification('❌ Error al eliminar', 'error');
        }
    }

    async unsubscribeSelected() {
        const categories = this.getSelectedCategories();

        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            const response = await chrome.tabs.sendMessage(tab.id, {
                action: 'unsubscribe',
                categories: categories
            });

            if (response && response.success) {
                this.showNotification(`📧 Desuscrito de ${response.count} listas`);
            }
        } catch (error) {
            this.showNotification('❌ Error al desuscribirse', 'error');
        }
    }

    getSelectedCategories() {
        const checked = document.querySelectorAll('.category-item input[type="checkbox"]:checked');
        return Array.from(checked).map(cb => cb.closest('.category-item').dataset.category);
    }

    getTotalSelectedCount(categories) {
        return categories.reduce((sum, cat) => sum + (this.stats[cat] || 0), 0);
    }

    async saveSetting(key, value) {
        const settings = await chrome.storage.local.get('settings') || {};
        settings[key] = value;
        await chrome.storage.local.set({ settings });
    }

    showNotification(message, type = 'success') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: ${type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#10b981'};
      color: white;
      padding: 10px 20px;
      border-radius: 8px;
      font-size: 12px;
      z-index: 1000;
      animation: slideUp 0.3s ease;
    `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideDown 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 2500);
    }
}

// Initialize popup
document.addEventListener('DOMContentLoaded', () => {
    new EmailCleanerPopup();
});

// Add animation keyframes
const style = document.createElement('style');
style.textContent = `
  @keyframes slideUp {
    from { opacity: 0; transform: translateX(-50%) translateY(20px); }
    to { opacity: 1; transform: translateX(-50%) translateY(0); }
  }
  @keyframes slideDown {
    from { opacity: 1; transform: translateX(-50%) translateY(0); }
    to { opacity: 0; transform: translateX(-50%) translateY(20px); }
  }
`;
document.head.appendChild(style);
