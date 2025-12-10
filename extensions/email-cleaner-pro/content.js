// Email Cleaner Pro - Content Script
// Detects email provider and scans inbox

(function () {
    'use strict';

    // Provider detection patterns
    const PROVIDERS = {
        gmail: {
            name: 'Gmail',
            detect: () => window.location.hostname === 'mail.google.com',
            selectors: {
                emailRow: 'tr.zA',
                sender: '.yW .yP, .yW .zF',
                subject: '.y6 .bog',
                date: '.xW.xY span[title]',
                checkbox: '.oZ-jc',
                unsubscribeLink: 'a[href*="unsubscribe"]'
            }
        },
        outlook: {
            name: 'Outlook',
            detect: () => window.location.hostname.includes('outlook'),
            selectors: {
                emailRow: '[data-convid]',
                sender: '[data-testid="SenderInfo"]',
                subject: '[data-testid="subjectLine"]',
                date: 'time',
                checkbox: 'input[type="checkbox"]',
                unsubscribeLink: 'a[href*="unsubscribe"]'
            }
        },
        yahoo: {
            name: 'Yahoo',
            detect: () => window.location.hostname.includes('mail.yahoo'),
            selectors: {
                emailRow: '[data-test-id="message-list-item"]',
                sender: '[data-test-id="sender"]',
                subject: '[data-test-id="subject"]',
                date: 'time',
                checkbox: 'input[type="checkbox"]',
                unsubscribeLink: 'a[href*="unsubscribe"]'
            }
        },
        protonmail: {
            name: 'ProtonMail',
            detect: () => window.location.hostname === 'mail.proton.me',
            selectors: {
                emailRow: '[data-element-id]',
                sender: '.item-sender',
                subject: '.item-subject',
                date: '.item-date',
                checkbox: '.item-checkbox',
                unsubscribeLink: 'a[href*="unsubscribe"]'
            }
        }
    };

    // Categorization patterns
    const CATEGORIES = {
        newsletters: {
            patterns: ['newsletter', 'digest', 'weekly', 'daily', 'update', 'bulletin', 'roundup'],
            senderPatterns: ['news@', 'newsletter@', 'digest@', 'updates@', 'noreply@']
        },
        promotions: {
            patterns: ['sale', 'discount', 'offer', 'deal', 'promo', 'off', 'save', 'free', 'limited'],
            senderPatterns: ['promo@', 'marketing@', 'offers@', 'deals@', 'sales@']
        },
        social: {
            patterns: ['friend', 'follow', 'like', 'comment', 'mention', 'share', 'tagged'],
            senderPatterns: ['@facebook', '@twitter', '@linkedin', '@instagram', '@tiktok', '@youtube']
        },
        notifications: {
            patterns: ['notification', 'alert', 'update', 'confirm', 'verify', 'security'],
            senderPatterns: ['notification@', 'alerts@', 'noreply@', 'no-reply@']
        }
    };

    class EmailCleanerContent {
        constructor() {
            this.provider = null;
            this.emails = [];
            this.detectProvider();
            this.setupMessageListener();
        }

        detectProvider() {
            for (const [key, provider] of Object.entries(PROVIDERS)) {
                if (provider.detect()) {
                    this.provider = { key, ...provider };
                    console.log(`[Email Cleaner Pro] Detected: ${provider.name}`);
                    return;
                }
            }
            console.log('[Email Cleaner Pro] Unknown email provider');
        }

        setupMessageListener() {
            chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
                switch (request.action) {
                    case 'scanEmails':
                        this.scanEmails().then(result => sendResponse(result));
                        return true; // Keep channel open for async

                    case 'deleteEmails':
                        this.deleteEmails(request.categories).then(result => sendResponse(result));
                        return true;

                    case 'unsubscribe':
                        this.unsubscribeFromEmails(request.categories).then(result => sendResponse(result));
                        return true;

                    case 'getProvider':
                        sendResponse({ provider: this.provider?.name || 'Unknown' });
                        break;
                }
            });
        }

        async scanEmails() {
            if (!this.provider) {
                return { success: false, error: 'Provider not detected' };
            }

            try {
                const emails = this.getVisibleEmails();
                const categorized = this.categorizeEmails(emails);
                const topSenders = this.getTopSenders(emails);

                return {
                    success: true,
                    stats: {
                        total: emails.length,
                        newsletters: categorized.newsletters.length,
                        promotions: categorized.promotions.length,
                        social: categorized.social.length,
                        notifications: categorized.notifications.length,
                        old: categorized.old.length,
                        spam: categorized.promotions.length + categorized.newsletters.length
                    },
                    topSenders: topSenders
                };
            } catch (error) {
                console.error('[Email Cleaner Pro] Scan error:', error);
                return { success: false, error: error.message };
            }
        }

        getVisibleEmails() {
            const selectors = this.provider.selectors;
            const rows = document.querySelectorAll(selectors.emailRow);
            const emails = [];

            rows.forEach((row, index) => {
                try {
                    const senderEl = row.querySelector(selectors.sender);
                    const subjectEl = row.querySelector(selectors.subject);
                    const dateEl = row.querySelector(selectors.date);

                    const sender = senderEl?.textContent?.trim() || 'Unknown';
                    const subject = subjectEl?.textContent?.trim() || '';
                    const dateStr = dateEl?.getAttribute('title') || dateEl?.textContent || '';

                    emails.push({
                        index,
                        element: row,
                        sender,
                        senderEmail: this.extractEmail(sender),
                        subject: subject.toLowerCase(),
                        date: this.parseDate(dateStr),
                        hasUnsubscribe: !!row.querySelector(selectors.unsubscribeLink)
                    });
                } catch (e) {
                    // Skip invalid rows
                }
            });

            return emails;
        }

        extractEmail(senderText) {
            const emailMatch = senderText.match(/[\w.-]+@[\w.-]+\.\w+/);
            return emailMatch ? emailMatch[0].toLowerCase() : senderText.toLowerCase();
        }

        parseDate(dateStr) {
            try {
                return new Date(dateStr);
            } catch {
                return new Date();
            }
        }

        categorizeEmails(emails) {
            const now = new Date();
            const thirtyDaysAgo = new Date(now - 30 * 24 * 60 * 60 * 1000);

            const categorized = {
                newsletters: [],
                promotions: [],
                social: [],
                notifications: [],
                old: [],
                uncategorized: []
            };

            emails.forEach(email => {
                let matched = false;

                // Check newsletters
                if (this.matchesCategory(email, CATEGORIES.newsletters)) {
                    categorized.newsletters.push(email);
                    matched = true;
                }

                // Check promotions
                if (this.matchesCategory(email, CATEGORIES.promotions)) {
                    categorized.promotions.push(email);
                    matched = true;
                }

                // Check social
                if (this.matchesCategory(email, CATEGORIES.social)) {
                    categorized.social.push(email);
                    matched = true;
                }

                // Check notifications
                if (this.matchesCategory(email, CATEGORIES.notifications)) {
                    categorized.notifications.push(email);
                    matched = true;
                }

                // Check old emails
                if (email.date < thirtyDaysAgo) {
                    categorized.old.push(email);
                }

                if (!matched) {
                    categorized.uncategorized.push(email);
                }
            });

            return categorized;
        }

        matchesCategory(email, category) {
            const subjectMatch = category.patterns.some(p => email.subject.includes(p));
            const senderMatch = category.senderPatterns.some(p => email.senderEmail.includes(p));
            return subjectMatch || senderMatch;
        }

        getTopSenders(emails) {
            const senderCounts = {};

            emails.forEach(email => {
                const key = email.senderEmail;
                if (!senderCounts[key]) {
                    senderCounts[key] = {
                        email: email.senderEmail,
                        name: email.sender.split('<')[0].trim() || email.senderEmail,
                        count: 0
                    };
                }
                senderCounts[key].count++;
            });

            return Object.values(senderCounts)
                .sort((a, b) => b.count - a.count)
                .slice(0, 10);
        }

        async deleteEmails(categories) {
            if (!this.provider) {
                return { success: false, error: 'Provider not detected' };
            }

            try {
                const emails = this.getVisibleEmails();
                const categorized = this.categorizeEmails(emails);
                let deletedCount = 0;

                for (const category of categories) {
                    const emailsToDelete = categorized[category] || [];

                    for (const email of emailsToDelete) {
                        await this.selectAndDeleteEmail(email);
                        deletedCount++;

                        // Small delay to avoid rate limiting
                        await this.delay(100);
                    }
                }

                return { success: true, deletedCount };
            } catch (error) {
                console.error('[Email Cleaner Pro] Delete error:', error);
                return { success: false, error: error.message };
            }
        }

        async selectAndDeleteEmail(email) {
            const selectors = this.provider.selectors;

            // Click checkbox to select
            const checkbox = email.element.querySelector(selectors.checkbox);
            if (checkbox) {
                checkbox.click();
                await this.delay(50);
            }

            // Trigger delete action based on provider
            if (this.provider.key === 'gmail') {
                // Gmail: Press # for delete
                document.dispatchEvent(new KeyboardEvent('keydown', { key: '#' }));
            } else {
                // Other providers: Look for delete button
                const deleteBtn = document.querySelector('[aria-label*="Delete"], [data-testid="delete"]');
                if (deleteBtn) deleteBtn.click();
            }
        }

        async unsubscribeFromEmails(categories) {
            const emails = this.getVisibleEmails();
            const categorized = this.categorizeEmails(emails);
            let unsubscribeCount = 0;

            for (const category of categories) {
                const emailsToUnsub = categorized[category] || [];

                for (const email of emailsToUnsub) {
                    if (email.hasUnsubscribe) {
                        unsubscribeCount++;
                        // In a real implementation, we'd open unsubscribe links
                    }
                }
            }

            return { success: true, count: unsubscribeCount };
        }

        delay(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }
    }

    // Initialize
    new EmailCleanerContent();
})();
