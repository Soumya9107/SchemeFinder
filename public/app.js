/**
 * SchemeFinder Assistant - Enhanced Frontend Logic
 * Multi-lingual support (EN, HI, BN) & API client
 */

let currentLang = 'en';
let cachedSchemes = [];

// Localization Dictionary
const I18N = {
    en: {
        nav_chat: "AI Assistant",
        nav_check: "Eligibility Test",
        nav_directory: "Scheme Directory",
        status_engine: "Strands Agent Ready",
        arch_laptop: "Runs on your laptop",
        heading_chat: "Government Scheme Assistant",
        subtitle_chat: "Ask questions or check eligibility in your preferred language",
        lang_title: "Language",
        chip_farmer: "PM-Kisan Farmer Eligibility",
        chip_health: "Health Insurance Cover",
        chip_loan: "Mudra Business Loan",
        chip_wb: "WB Female Student Schemes",
        welcome_msg: "Namaste! I am your <strong>SchemeFinder Assistant</strong>. I can help you search government welfare schemes, verify your eligibility with deterministic rules, and find required documents & application links.",
        welcome_hint: "Try asking a question in English, Hindi, or Bengali, or use the <strong>Eligibility Test</strong> tab for instant evaluation.",
        form_title: "Check Your Scheme Eligibility",
        form_desc: "Fill in your basic demographics to run a deterministic check against all verified government schemes.",
        label_age: "Age (Years)",
        label_income: "Annual Family Income (₹)",
        label_gender: "Gender",
        label_occupation: "Occupation",
        label_state: "State of Residence",
        label_category: "Category",
        opt_all: "All / Any",
        opt_male: "Male",
        opt_female: "Female",
        opt_other: "Other",
        occ_all: "All / General",
        occ_farmer: "Farmer / Agriculture Worker",
        occ_student: "Student",
        occ_vendor: "Street Vendor / Shopkeeper",
        occ_self: "Self-Employed / Entrepreneur",
        occ_unemployed: "Unemployed",
        state_all: "All India (Central Schemes)",
        cat_all: "General / All",
        btn_evaluate: "Evaluate Eligible Schemes",
        results_title: "Evaluation Results",
        apply_now: "Official Portal / Apply Now",
        docs_required: "Required Documents:"
    },
    hi: {
        nav_chat: "एआई सहायक",
        nav_check: "पात्रता परीक्षण",
        nav_directory: "योजना निर्देशिका",
        status_engine: "स्ट्रैंड्स एजेंट तैयार",
        arch_laptop: "आपके लैपटॉप पर चलता है",
        heading_chat: "सरकारी योजना सहायक",
        subtitle_chat: "अपनी पसंदीदा भाषा में प्रश्न पूछें या पात्रता जांचें",
        lang_title: "भाषा",
        chip_farmer: "पीएम-किसान पात्रता",
        chip_health: "स्वास्थ्य बीमा कवर (₹5 लाख)",
        chip_loan: "मुद्रा व्यापार ऋण",
        chip_wb: "पश्चिम बंगाल महिला योजनाएं",
        welcome_msg: "नमस्ते! मैं आपका <strong>SchemeFinder असिस्टेंट</strong> हूँ। मैं आपको कल्याणकारी योजनाओं की खोज करने, पात्रता जांचने और आवश्यक दस्तावेज़ व आवेदन लिंक खोजने में मदद कर सकता हूँ।",
        welcome_hint: "अंग्रेजी, हिंदी या बंगाली में प्रश्न पूछें या त्वरित मूल्यांकन के लिए <strong>पात्रता परीक्षण</strong> का उपयोग करें।",
        form_title: "अपनी योजना पात्रता जांचें",
        form_desc: "सत्यापित योजनाओं के विरुद्ध त्वरित जांच के लिए अपनी बुनियादी जानकारी भरें।",
        label_age: "आयु (वर्ष)",
        label_income: "वार्षिक पारिवारिक आय (₹)",
        label_gender: "लिंग",
        label_occupation: "व्यवसाय",
        label_state: "निवास का राज्य",
        label_category: "वर्ग / श्रेणी",
        opt_all: "सभी",
        opt_male: "पुरुष",
        opt_female: "महिला",
        opt_other: "अन्य",
        occ_all: "सभी / सामान्य",
        occ_farmer: "किसान / कृषि श्रमिक",
        occ_student: "छात्र / विद्यार्थी",
        occ_vendor: "रेहड़ी-पटरी / दुकानदार",
        occ_self: "स्वरोजगार / व्यवसायी",
        occ_unemployed: "बेरोजगार",
        state_all: "संपूर्ण भारत (केंद्रीय योजनाएं)",
        cat_all: "सामान्य / सभी",
        btn_evaluate: "योग्य योजनाओं का मूल्यांकन करें",
        results_title: "मूल्यांकन परिणाम",
        apply_now: "आधिकारिक पोर्टल / आवेदन करें",
        docs_required: "आवश्यक दस्तावेज़:"
    },
    bn: {
        nav_chat: "এআই সহকারী",
        nav_check: "যোগ্যতা পরীক্ষা",
        nav_directory: "প্রকল্প তালিকা",
        status_engine: "স্ট্র্যান্ডস এজেন্ট প্রস্তুত",
        arch_laptop: "আপনার ল্যাপটপে চলছে",
        heading_chat: "সরকারি প্রকল্প সহকারী",
        subtitle_chat: "আপনার পছন্দের ভাষায় প্রশ্ন জিজ্ঞাসা করুন বা যোগ্যতা পরীক্ষা করুন",
        lang_title: "ভাষা",
        chip_farmer: "পিএম-কিষাণ কৃষক যোগ্যতা",
        chip_health: "স্বাস্থ্য বীমা কভার (৫ লক্ষ টাকা)",
        chip_loan: "মুদ্রা ব্যবসা ঋণ",
        chip_wb: "পশ্চিমবঙ্গ মহিলা প্রকল্প",
        welcome_msg: "নমস্কার! আমি আপনার <strong>SchemeFinder সহকারী</strong>। আমি আপনাকে সরকারি কল্যাণমূলক প্রকল্প খুঁজতে, আপনার যোগ্যতা যাচাই করতে এবং প্রয়োজনীয় কাগজপত্র ও আবেদনের লিঙ্ক খুঁজে পেতে সাহায্য করতে পারি।",
        welcome_hint: "ইংরেজি, হিন্দি বা বাংলায় প্রশ্ন জিজ্ঞাসা করুন অথবা <strong>যোগ্যতা পরীক্ষা</strong> ট্যাব ব্যবহার করুন।",
        form_title: "আপনার প্রকল্পের যোগ্যতা পরীক্ষা করুন",
        form_desc: "সমস্ত যাচাইকৃত সরকারি প্রকল্পের সাথে মিলিয়ে দেখতে আপনার মৌলিক তথ্য পূরণ করুন।",
        label_age: "বয়স (বছর)",
        label_income: "বার্ষিক পারিবারিক আয় (₹)",
        label_gender: "লিঙ্গ",
        label_occupation: "পেশা",
        label_state: "বাসস্থানের রাজ্য",
        label_category: "বিভাগ / শ্রেণী",
        opt_all: "সকল",
        opt_male: "পুরুষ",
        opt_female: "মহিলা",
        opt_other: "অন্যান্য",
        occ_all: "সকল / সাধারণ",
        occ_farmer: "কৃষক / কৃষি শ্রমিক",
        occ_student: "ছাত্র / ছাত্রী",
        occ_vendor: "হকার / দোকানদার",
        occ_self: "স্বনির্ভর / ব্যবসায়ী",
        occ_unemployed: "বেকার",
        state_all: "সমগ্র ভারত (কেন্দ্রীয় প্রকল্প)",
        cat_all: "সাধারণ / সকল",
        btn_evaluate: "যোগ্য প্রকল্পসমূহ মূল্যায়ন করুন",
        results_title: "মূল্যায়নের ফলাফল",
        apply_now: "অফিসিয়াল পোর্টাল / আবেদন করুন",
        docs_required: "প্রয়োজনীয় কাগজপত্র:"
    }
};

document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initLanguageSelector();
    initChat();
    initEligibilityForm();
    initDirectory();
    initModal();
    fetchSchemes();
});

// Tab Switching Handler
function initTabs() {
    const navItems = document.querySelectorAll('.nav-item');
    const tabPanes = document.querySelectorAll('.tab-pane');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');

            navItems.forEach(n => n.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            item.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });
}

// Language Selector Handler
function initLanguageSelector() {
    const langBtns = document.querySelectorAll('.lang-btn');

    langBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            langBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            currentLang = btn.getAttribute('data-lang');
            updatePageTranslations();
        });
    });
}

function updatePageTranslations() {
    const langData = I18N[currentLang] || I18N.en;

    document.querySelectorAll('[data-i18n]').forEach(elem => {
        const key = elem.getAttribute('data-i18n');
        if (langData[key]) {
            if (elem.tagName === 'INPUT' && elem.hasAttribute('placeholder')) {
                elem.placeholder = langData[key];
            } else {
                elem.innerHTML = langData[key];
            }
        }
    });

    renderDirectory();
}

// Chat Assistant Logic
function initChat() {
    const form = document.getElementById('chat-form');
    const input = document.getElementById('chat-input');
    const chips = document.querySelectorAll('.chip');

    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const text = chip.getAttribute('data-prompt');
            input.value = text;
            form.dispatchEvent(new Event('submit'));
        });
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userMsg = input.value.trim();
        if (!userMsg) return;

        // Append User Bubble
        appendBubble('user', userMsg);
        input.value = '';

        // Show Bouncing Typing Indicator
        const typingId = appendTypingIndicator();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMsg, language: currentLang })
            });
            const data = await response.json();

            removeBubble(typingId);
            appendBubble('assistant', data.response || 'No response received.');
        } catch (err) {
            removeBubble(typingId);
            appendBubble('assistant', '❌ Network error communicating with local server. Ensure `local_server.py` is running.');
        }
    });
}

function appendTypingIndicator() {
    const log = document.getElementById('chat-log');
    const id = 'msg-typing-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.id = id;

    messageDiv.innerHTML = `
        <div class="avatar"><i class="fa-solid fa-robot"></i></div>
        <div class="msg-bubble">
            <span style="display:inline-flex; gap:4px; align-items:center;">
                <span style="width:6px; height:6px; background:#6366f1; border-radius:50%; animation: pulseGlow 1s infinite 0.1s;"></span>
                <span style="width:6px; height:6px; background:#06b6d4; border-radius:50%; animation: pulseGlow 1s infinite 0.3s;"></span>
                <span style="width:6px; height:6px; background:#d946ef; border-radius:50%; animation: pulseGlow 1s infinite 0.5s;"></span>
            </span>
        </div>
    `;

    log.appendChild(messageDiv);
    log.scrollTop = log.scrollHeight;
    return id;
}

function appendBubble(role, content) {
    const log = document.getElementById('chat-log');
    const id = 'msg-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.id = id;

    const avatarHtml = role === 'assistant' 
        ? '<div class="avatar"><i class="fa-solid fa-robot"></i></div>'
        : '<div class="avatar"><i class="fa-solid fa-user"></i></div>';

    // Format text markdown
    let formattedText = content
        .replace(/### (.*?)\n/g, '<h4 style="margin-top:8px; margin-bottom:4px; font-weight:700;">$1</h4>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" class="apply-link">$1 <i class="fa-solid fa-arrow-up-right-from-square"></i></a>');

    messageDiv.innerHTML = `
        ${avatarHtml}
        <div class="msg-bubble">
            <p>${formattedText}</p>
        </div>
    `;

    log.appendChild(messageDiv);
    log.scrollTop = log.scrollHeight;
    return id;
}

function removeBubble(id) {
    const elem = document.getElementById(id);
    if (elem) elem.remove();
}

// Eligibility Questionnaire Form
function initEligibilityForm() {
    const form = document.getElementById('eligibility-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const profile = {
            age: parseInt(document.getElementById('user-age').value),
            income: parseFloat(document.getElementById('user-income').value),
            gender: document.getElementById('user-gender').value,
            occupation: document.getElementById('user-occupation').value,
            state: document.getElementById('user-state').value,
            category: document.getElementById('user-category').value
        };

        const resultsContainer = document.getElementById('eligibility-results');
        const grid = document.getElementById('results-grid');
        const badge = document.getElementById('match-count-badge');

        grid.innerHTML = '<p style="color: var(--text-muted); grid-column:1/-1;">Evaluating profile rules...</p>';
        resultsContainer.classList.remove('hidden');

        try {
            const resp = await fetch('/check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ profile })
            });
            const data = await resp.json();

            grid.innerHTML = '';
            const eligible = data.eligible_schemes || [];
            const ineligible = data.ineligible_schemes || [];

            badge.textContent = `${eligible.length} Eligible Schemes`;

            eligible.forEach(scheme => {
                grid.appendChild(createSchemeCard(scheme, true));
            });

            ineligible.forEach(scheme => {
                grid.appendChild(createSchemeCard(scheme, false));
            });

        } catch (err) {
            grid.innerHTML = '<p style="color: var(--accent-rose); grid-column:1/-1;">Error evaluating eligibility.</p>';
        }
    });
}

function createSchemeCard(scheme, isEligible) {
    const langData = I18N[currentLang] || I18N.en;
    const card = document.createElement('div');
    card.className = 'scheme-card';

    const name = scheme.name[currentLang] || scheme.name.en;
    const obj = scheme.objective[currentLang] || scheme.objective.en;

    const badgeHtml = isEligible
        ? `<span class="badge badge-success"><i class="fa-solid fa-circle-check"></i> Eligible</span>`
        : `<span class="badge badge-danger"><i class="fa-solid fa-circle-xmark"></i> Mismatch</span>`;

    let docsList = '';
    if (scheme.documents && scheme.documents.length) {
        docsList = `<div class="docs-section">
            <strong>${langData.docs_required}</strong>
            <ul>
                ${scheme.documents.slice(0, 3).map(d => `<li><i class="fa-solid fa-check" style="color:var(--accent-cyan); font-size:10px; margin-right:4px;"></i> ${d}</li>`).join('')}
            </ul>
        </div>`;
    }

    card.innerHTML = `
        <div class="card-top">
            <div>
                <span class="category-tag">${scheme.category}</span>
                <h4 class="scheme-title" style="margin-top:6px;">${name}</h4>
            </div>
            ${badgeHtml}
        </div>
        <p class="scheme-obj">${obj}</p>
        ${docsList}
        <a href="${scheme.apply_link}" target="_blank" class="apply-btn">
            ${langData.apply_now} <i class="fa-solid fa-arrow-up-right-from-square"></i>
        </a>
    `;

    return card;
}

// Directory Page
async function fetchSchemes() {
    try {
        const res = await fetch('/schemes');
        const data = await res.json();
        cachedSchemes = data.schemes || [];
        renderDirectory();
    } catch (e) {
        console.warn('Could not fetch schemes list.');
    }
}

function initDirectory() {
    const searchInput = document.getElementById('directory-search');
    searchInput.addEventListener('input', () => {
        renderDirectory(searchInput.value.toLowerCase().trim());
    });
}

function renderDirectory(filterText = '') {
    const grid = document.getElementById('directory-grid');
    if (!grid) return;

    grid.innerHTML = '';
    const filtered = cachedSchemes.filter(s => {
        if (!filterText) return true;
        const name = (s.name[currentLang] || s.name.en).toLowerCase();
        const obj = (s.objective[currentLang] || s.objective.en).toLowerCase();
        return name.includes(filterText) || obj.includes(filterText) || s.category.toLowerCase().includes(filterText);
    });

    if (!filtered.length) {
        grid.innerHTML = '<p style="color: var(--text-muted); grid-column: 1/-1; text-align: center;">No matching schemes found.</p>';
        return;
    }

    filtered.forEach(scheme => {
        grid.appendChild(createSchemeCard(scheme, true));
    });
}

// Modal handler
function initModal() {
    const closeBtn = document.getElementById('modal-close');
    const backdrop = document.getElementById('scheme-modal');

    if (closeBtn && backdrop) {
        closeBtn.addEventListener('click', () => {
            backdrop.classList.add('hidden');
        });
        backdrop.addEventListener('click', (e) => {
            if (e.target === backdrop) backdrop.classList.add('hidden');
        });
    }
}
