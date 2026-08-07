

(function () {
    const settingsBtn        = document.getElementById('settingsBtn');
    const settingsPanel      = document.getElementById('settingsPanel');
    const settingsOverlay    = document.getElementById('settingsOverlay');
    const closeSettingsBtn   = document.getElementById('closeSettingsBtn');

    const stabBtns           = document.querySelectorAll('.stab-btn');
    const tabContents        = document.querySelectorAll('.settings-tab-content');

    const msFields = {
        roleSelect        : document.getElementById('modelRoleSelect'),
        temperature       : document.getElementById('ms_temperature'),
        top_p             : document.getElementById('ms_top_p'),
        top_k             : document.getElementById('ms_top_k'),
        repetition_penalty: document.getElementById('ms_repetition_penalty'),
        frequency_penalty : document.getElementById('ms_frequency_penalty'),
        presence_penalty  : document.getElementById('ms_presence_penalty')
    };

    const saveModelSettingsBtn = document.getElementById('saveModelSettingsBtn');
    let currentServerConfig = {};

    const csFields = {
        max_new_tokens    : document.getElementById('cs_max_new_tokens'),
        temperature       : document.getElementById('cs_temperature'),
        top_p             : document.getElementById('cs_top_p'),
        top_k             : document.getElementById('cs_top_k'),
        repetition_penalty: document.getElementById('cs_repetition_penalty'),
        n_ctx_allocation  : document.getElementById('cs_n_ctx_allocation'),
        compacting_profile: document.getElementById('cs_compacting_profile'),
        performance_profile: document.getElementById('cs_performance_profile'),
        code_review       : document.getElementById('cs_code_review'),
        keep_triage_loaded: document.getElementById('cs_keep_triage_loaded'),
    };

    const saveChatSettingsBtn = document.getElementById('saveChatSettingsBtn');



    function openSettings() {
        const s = window.getChatSettings ? window.getChatSettings() : {};
        if (csFields.max_new_tokens)     { csFields.max_new_tokens.value     = s.max_new_tokens     ?? 200; document.getElementById('val_max_new_tokens').innerText = csFields.max_new_tokens.value; }
        if (csFields.temperature)        { csFields.temperature.value        = s.temperature        ?? 0.6; document.getElementById('val_temperature').innerText = csFields.temperature.value; }
        if (csFields.top_p)              { csFields.top_p.value              = s.top_p              ?? 0.9; document.getElementById('val_top_p').innerText = csFields.top_p.value; }
        if (csFields.top_k)              { csFields.top_k.value              = s.top_k              ?? 40; document.getElementById('val_top_k').innerText = csFields.top_k.value; }
        if (csFields.repetition_penalty) { csFields.repetition_penalty.value = s.repetition_penalty ?? 1.3; document.getElementById('val_repetition_penalty').innerText = csFields.repetition_penalty.value; }

        if (csFields.n_ctx_allocation) { 
            const ctx_vals = ['auto','4096','8192','16384','32768'];
            let idx = ctx_vals.indexOf(String(s.n_ctx_allocation || 'auto').toLowerCase());
            if (idx === -1) {
                idx = ctx_vals.indexOf(String(s.n_ctx_allocation));
                if (idx === -1) idx = 0;
            }
            csFields.n_ctx_allocation.value = idx; 
            const display_vals = ['Auto','4096','8192','16384','32768'];
            document.getElementById('val_n_ctx_allocation').innerText = display_vals[idx]; 
        }
        if (csFields.compacting_profile) { 
            const cp_vals = ['low','medium','aggressive'];
            let idx = cp_vals.indexOf(String(s.compacting_profile || 'medium').toLowerCase());
            if (idx === -1) idx = 1;
            csFields.compacting_profile.value = idx; 
            const display_vals = ['Low','Medium','Aggressive'];
            document.getElementById('val_compacting_profile').innerText = display_vals[idx]; 
        }

        if (csFields.performance_profile) {
            const pp_vals = ['low', 'balanced', 'high'];
            let idx = pp_vals.indexOf(String(s.performance_profile || 'balanced').toLowerCase());
            if (idx === -1) idx = 1;
            csFields.performance_profile.value = idx;
            const display_vals = ['Low', 'Balanced', 'High'];
            const valEl = document.getElementById('val_performance_profile');
            if (valEl) valEl.innerText = display_vals[idx];
        }

        if (csFields.code_review) {
            csFields.code_review.checked = s.code_review === true;
        }
        if (csFields.keep_triage_loaded) {
            csFields.keep_triage_loaded.checked = s.keep_triage_loaded === true;
        }

        settingsPanel.classList.add('open');
        settingsOverlay.classList.add('visible');
        
        fetchServerConfig();
    }

    function closeSettings() {
        settingsPanel.classList.remove('open');
        settingsOverlay.classList.remove('visible');
    }

    settingsBtn?.addEventListener('click', openSettings);
    closeSettingsBtn?.addEventListener('click', closeSettings);
    settingsOverlay?.addEventListener('click', closeSettings);

    stabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            stabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(`stab-content-${tab}`)?.classList.add('active');

            if (tab === 'models') {
                fetchServerConfig();
            }
        });
    });

    async function fetchServerConfig() {
        try {
            const res = await fetch('/get_config');
            if (!res.ok) return;
            currentServerConfig = await res.json();
            populateModelSettings();
        } catch (e) {
            console.error("Failed to fetch server config", e);
        }
    }

    function populateModelSettings() {
        const role = msFields.roleSelect?.value;
        if (!role || !currentServerConfig.model_settings) return;

        const roleSettings = currentServerConfig.model_settings[role] || {};

        msFields.temperature.value = roleSettings.temperature !== undefined ? roleSettings.temperature : -0.01;
        document.getElementById('val_ms_temperature').innerText = msFields.temperature.value < 0 ? 'Global' : msFields.temperature.value;

        msFields.top_p.value = roleSettings.top_p !== undefined ? roleSettings.top_p : -0.05;
        document.getElementById('val_ms_top_p').innerText = msFields.top_p.value < 0 ? 'Global' : msFields.top_p.value;

        msFields.top_k.value = roleSettings.top_k !== undefined ? roleSettings.top_k : 0;
        document.getElementById('val_ms_top_k').innerText = msFields.top_k.value == 0 ? 'Global' : msFields.top_k.value;

        msFields.repetition_penalty.value = roleSettings.repetition_penalty !== undefined ? roleSettings.repetition_penalty : 0.95;
        document.getElementById('val_ms_repetition_penalty').innerText = msFields.repetition_penalty.value < 1.0 ? 'Global' : msFields.repetition_penalty.value;

        msFields.frequency_penalty.value = roleSettings.frequency_penalty !== undefined ? roleSettings.frequency_penalty : -0.05;
        document.getElementById('val_ms_frequency_penalty').innerText = msFields.frequency_penalty.value < 0 ? 'Global' : msFields.frequency_penalty.value;

        msFields.presence_penalty.value = roleSettings.presence_penalty !== undefined ? roleSettings.presence_penalty : -0.05;
        document.getElementById('val_ms_presence_penalty').innerText = msFields.presence_penalty.value < 0 ? 'Global' : msFields.presence_penalty.value;
    }

    msFields.roleSelect?.addEventListener('change', populateModelSettings);

    // ── Save Chat Settings ──
    saveChatSettingsBtn?.addEventListener('click', () => {
        const s = window.getChatSettings ? window.getChatSettings() : {};

        s.max_new_tokens     = parseInt(csFields.max_new_tokens?.value) || 512;
        s.temperature        = parseFloat(csFields.temperature?.value) || 0.6;
        s.top_p              = parseFloat(csFields.top_p?.value) || 0.9;
        s.top_k              = parseInt(csFields.top_k?.value) || 40;
        s.repetition_penalty = parseFloat(csFields.repetition_penalty?.value) || 1.3;
        s.code_review        = csFields.code_review?.checked || false;
        s.keep_triage_loaded = csFields.keep_triage_loaded?.checked || false;

        const n_ctx_map = ['auto','4096','8192','16384','32768'];
        s.n_ctx_allocation = n_ctx_map[parseInt(csFields.n_ctx_allocation?.value) || 0] || 'auto';

        const cp_map = ['low','medium','aggressive'];
        s.compacting_profile = cp_map[parseInt(csFields.compacting_profile?.value) || 1] || 'medium';

        const pp_map = ['low', 'balanced', 'high'];
        s.performance_profile = pp_map[parseInt(csFields.performance_profile?.value) || 1] || 'balanced';

        localStorage.setItem('iris_chat_settings', JSON.stringify(s));
        if (window.setChatSettings) window.setChatSettings(s);

        // Persist to server
        fetch('/save_settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                code_review: s.code_review,
                keep_triage_loaded: s.keep_triage_loaded,
                n_ctx_allocation: s.n_ctx_allocation,
                compacting_profile: s.compacting_profile,
                performance_profile: s.performance_profile
            })
        }).catch(() => {});

        showToast('Chat settings saved');
    });

    saveModelSettingsBtn?.addEventListener('click', async () => {
        const role = msFields.roleSelect?.value;
        if (!role) return;

        const newSettings = {};
        if (parseFloat(msFields.temperature.value) >= 0) newSettings.temperature = parseFloat(msFields.temperature.value);
        if (parseFloat(msFields.top_p.value) >= 0) newSettings.top_p = parseFloat(msFields.top_p.value);
        if (parseInt(msFields.top_k.value) > 0) newSettings.top_k = parseInt(msFields.top_k.value);
        if (parseFloat(msFields.repetition_penalty.value) >= 1.0) newSettings.repetition_penalty = parseFloat(msFields.repetition_penalty.value);
        if (parseFloat(msFields.frequency_penalty.value) >= 0) newSettings.frequency_penalty = parseFloat(msFields.frequency_penalty.value);
        if (parseFloat(msFields.presence_penalty.value) >= 0) newSettings.presence_penalty = parseFloat(msFields.presence_penalty.value);

        try {
            await fetch('/save_model_settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role: role, settings: newSettings })
            });
            // Update local config cache
            if (!currentServerConfig.model_settings) currentServerConfig.model_settings = {};
            currentServerConfig.model_settings[role] = newSettings;
            showToast('Model settings saved');
        } catch (e) {
            console.error("Failed to save model settings to server:", e);
        }
    });

    function showToast(message) {
        const existing = document.getElementById('saveToast');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.id = 'saveToast';
        toast.className = 'save-toast';
        toast.innerHTML = `<span class="save-toast-dot"></span>${message}`;
        document.body.appendChild(toast);

        requestAnimationFrame(() => {
            requestAnimationFrame(() => toast.classList.add('visible'));
        });

        setTimeout(() => {
            toast.classList.remove('visible');
            setTimeout(() => toast.remove(), 300);
        }, 2200);
    }
})();

// Theme Switcher Logic
(function () {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;

    // Load theme from localStorage
    const currentTheme = localStorage.getItem('theme') ? localStorage.getItem('theme') : null;
    if (currentTheme) {
        document.documentElement.setAttribute('data-theme', currentTheme);
        if (currentTheme === 'light') {
            themeToggle.checked = true;
        }
    }

    // Listen for toggle
    themeToggle.addEventListener('change', function (e) {
        if (e.target.checked) {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
        } else {
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('theme', 'dark');
        }
    });
})();
