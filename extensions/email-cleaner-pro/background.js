// Email Cleaner Pro - Background Service Worker

// Handle installation
chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
        console.log('[Email Cleaner Pro] Extension installed');

        // Initialize default settings
        chrome.storage.local.set({
            settings: {
                autoClean: false,
                safeMode: true,
                autoCleanDays: 7
            },
            blockedSenders: [],
            whitelistedSenders: [],
            emailStats: {
                total: 0,
                deleted: 0,
                newsletters: 0,
                promotions: 0,
                social: 0,
                notifications: 0,
                old: 0
            },
            topSenders: []
        });
    }
});

// Handle messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    switch (request.action) {
        case 'getStats':
            chrome.storage.local.get(['emailStats', 'topSenders'], (data) => {
                sendResponse(data);
            });
            return true;

        case 'updateSettings':
            chrome.storage.local.get('settings', (data) => {
                const settings = { ...data.settings, ...request.settings };
                chrome.storage.local.set({ settings }, () => {
                    sendResponse({ success: true });
                });
            });
            return true;

        case 'blockSender':
            chrome.storage.local.get('blockedSenders', (data) => {
                const blocked = data.blockedSenders || [];
                if (!blocked.includes(request.sender)) {
                    blocked.push(request.sender);
                    chrome.storage.local.set({ blockedSenders: blocked }, () => {
                        sendResponse({ success: true, blockedCount: blocked.length });
                    });
                } else {
                    sendResponse({ success: false, message: 'Already blocked' });
                }
            });
            return true;

        case 'unblockSender':
            chrome.storage.local.get('blockedSenders', (data) => {
                const blocked = (data.blockedSenders || []).filter(s => s !== request.sender);
                chrome.storage.local.set({ blockedSenders: blocked }, () => {
                    sendResponse({ success: true });
                });
            });
            return true;

        case 'getBlockedSenders':
            chrome.storage.local.get('blockedSenders', (data) => {
                sendResponse({ blockedSenders: data.blockedSenders || [] });
            });
            return true;

        case 'whitelistSender':
            chrome.storage.local.get('whitelistedSenders', (data) => {
                const whitelist = data.whitelistedSenders || [];
                if (!whitelist.includes(request.sender)) {
                    whitelist.push(request.sender);
                    chrome.storage.local.set({ whitelistedSenders: whitelist }, () => {
                        sendResponse({ success: true });
                    });
                }
            });
            return true;
    }
});

// Badge update based on email count
function updateBadge(count) {
    const text = count > 999 ? '999+' : count.toString();
    chrome.action.setBadgeText({ text: count > 0 ? text : '' });
    chrome.action.setBadgeBackgroundColor({ color: '#ef4444' });
}

// Listen for tab updates to refresh stats
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        const emailHosts = ['mail.google.com', 'outlook.live.com', 'outlook.office.com', 'mail.yahoo.com', 'mail.proton.me'];
        const isEmailTab = emailHosts.some(host => tab.url.includes(host));

        if (isEmailTab) {
            // Could trigger auto-scan here if enabled
            chrome.storage.local.get('settings', (data) => {
                if (data.settings?.autoScan) {
                    chrome.tabs.sendMessage(tabId, { action: 'scanEmails' });
                }
            });
        }
    }
});

console.log('[Email Cleaner Pro] Background service worker started');
