// Setup modal logic for first-run model configuration

(function() {
    const setupModal = document.getElementById('setupModal');
    const setupDownload = document.getElementById('setupDownload');
    const setupFolder = document.getElementById('setupFolder');
    const setupRemote = document.getElementById('setupRemote');
    const setupContinue = document.getElementById('setupContinue');
    const setupDownloadProgress = document.getElementById('setupDownloadProgress');
    const setupProgressFill = document.getElementById('setupProgressFill');
    const setupProgressStatus = document.getElementById('setupProgressStatus');
    const setupRemoteInput = document.getElementById('setupRemoteInput');
    const remoteUrlInput = document.getElementById('remoteUrlInput');
    const remoteConnectBtn = document.getElementById('remoteConnectBtn');

    const bridge = window.IrisAndroidBridge;

    function showSetup() {
        setupModal.style.display = 'flex';
    }

    function hideSetup() {
        setupModal.style.display = 'none';
    }

    function isAndroid() {
        return bridge && typeof bridge.hasModels === 'function';
    }

    // Check on load if models exist
    function checkModelsAndShowSetup() {
        if (!isAndroid()) return;

        try {
            const hasModels = bridge.hasModels();
            if (!hasModels) {
                showSetup();
            }
        } catch (e) {
            console.log('Setup check skipped:', e);
        }
    }

    // Option 1: Download models
    if (setupDownload) {
        setupDownload.addEventListener('click', function() {
            setupDownloadProgress.style.display = 'block';
            setupDownload.style.display = 'none';
            setupFolder.style.display = 'none';
            setupRemote.style.display = 'none';
            setupContinue.style.display = 'none';

            try {
                bridge.downloadModels();
            } catch (e) {
                console.error('Download failed:', e);
                setupProgressStatus.textContent = 'Error: ' + e.message;
                return;
            }

            const pollInterval = setInterval(function() {
                try {
                    const statusStr = bridge.getDownloadProgress();
                    const status = JSON.parse(statusStr);

                    if (status.status === 'downloading') {
                        const progress = status.progress || 0;
                        setupProgressFill.style.width = progress + '%';
                        setupProgressStatus.textContent = (status.modelName || 'Downloading...') + ' - ' + progress + '%';
                    } else if (status.status === 'completed') {
                        clearInterval(pollInterval);
                        setupProgressFill.style.width = '100%';
                        setupProgressStatus.textContent = 'Download complete!';
                        setTimeout(hideSetup, 1500);
                    } else if (status.status === 'error') {
                        clearInterval(pollInterval);
                        setupProgressStatus.textContent = 'Error: ' + (status.error || 'Unknown error');
                    }
                } catch (e) {
                    console.log('Poll error:', e);
                }
            }, 500);
        });
    }

    // Option 2: Load from folder
    if (setupFolder) {
        setupFolder.addEventListener('click', function() {
            try {
                bridge.selectModelsDir();
            } catch (e) {
                console.error('Folder select failed:', e);
            }
        });
    }

    // Listen for folder selection callback
    window.onModelsDirSelected = function(path) {
        hideSetup();
        // Reload to pick up new models
        window.location.reload();
    };

    // Option 3: Remote access
    if (setupRemote) {
        setupRemote.addEventListener('click', function() {
            setupDownloadProgress.style.display = 'none';
            setupDownload.style.display = 'none';
            setupFolder.style.display = 'none';
            setupRemote.style.display = 'none';
            setupContinue.style.display = 'none';
            setupRemoteInput.style.display = 'flex';

            // Pre-fill with existing remote URL
            try {
                const existingUrl = bridge.getRemoteServerUrl();
                if (existingUrl) {
                    remoteUrlInput.value = existingUrl;
                }
            } catch (e) {}
        });
    }

    if (remoteConnectBtn) {
        remoteConnectBtn.addEventListener('click', function() {
            const url = remoteUrlInput.value.trim();
            if (!url) {
                remoteUrlInput.style.borderColor = '#ff4444';
                return;
            }

            try {
                bridge.setRemoteServerUrl(url);
                bridge.setRemoteMode(true);
                hideSetup();
                // Reload to use remote mode
                window.location.reload();
            } catch (e) {
                console.error('Remote connect failed:', e);
                remoteUrlInput.style.borderColor = '#ff4444';
            }
        });
    }

    // Option 4: Continue anyway
    if (setupContinue) {
        setupContinue.addEventListener('click', function() {
            hideSetup();
        });
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', checkModelsAndShowSetup);
    } else {
        checkModelsAndShowSetup();
    }

    // Expose for manual trigger
    window.showSetup = showSetup;
})();
