const toggleBtn       = document.getElementById('toggleBtn');
const mobileToggleBtn = document.getElementById('mobileToggleBtn');
const sidebar         = document.getElementById('sidebar');
const mainContent     = document.getElementById('mainContent');

if (sidebar) {
    const toggleSidebar = () => sidebar.classList.toggle('expanded');
    if (toggleBtn) toggleBtn.addEventListener('click', toggleSidebar);
    if (mobileToggleBtn) mobileToggleBtn.addEventListener('click', toggleSidebar);
}

function handleInput() {
    const input = document.getElementById('chatInput');
    const wave  = document.getElementById('waveIcon');
    const send  = document.getElementById('sendIcon');
    if (!input) return;
    const hasText = input.value.trim() !== '';
    if (wave) wave.style.display = hasText ? 'none'  : 'block';
    if (send) send.style.display = hasText ? 'block' : 'none';
}
window.handleInput = handleInput;
const chatInputEl = document.getElementById('chatInput');
if (chatInputEl) {
    chatInputEl.addEventListener('input', handleInput);
    handleInput();
}

const attachBtn = document.getElementById('attachBtn');
if (attachBtn) {
    attachBtn.addEventListener('click', (event) => {
        event.stopPropagation();
        const menu = document.getElementById('attachMenu');
        if (menu) menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
    });
}
document.addEventListener('click', (e) => {
    // Close attach menu if clicking outside
    const menu = document.getElementById('attachMenu');
    if (menu && menu.style.display === 'block') {
        if (!menu.contains(e.target) && !attachBtn.contains(e.target)) {
            menu.style.display = 'none';
        }
    }
    
    // Close sidebar if clicking outside
    if (sidebar && sidebar.classList.contains('expanded')) {
        if (e.target.closest('#settingsPanel, #settingsOverlay, .chat-context-menu')) {
            return; // Don't close if clicking inside a modal or dialog
        }
        if (!sidebar.contains(e.target) && 
            (!mobileToggleBtn || !mobileToggleBtn.contains(e.target)) && 
            (!toggleBtn || !toggleBtn.contains(e.target))) {
            sidebar.classList.remove('expanded');
        }
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const customDropdownBtn = document.getElementById('customModelDropdownBtn');
    const customModelMenu = document.getElementById('customModelMenu');
    const customModelSelectedText = document.getElementById('customModelSelectedText');
    const hiddenSelect = document.getElementById('cs_performance_profile');
    
    if (customDropdownBtn && customModelMenu) {
        customDropdownBtn.addEventListener('click', (e) => {
            if (e.target.closest('.custom-model-menu')) return;
            customModelMenu.style.display = customModelMenu.style.display === 'none' ? 'flex' : 'none';
        });
        
        document.addEventListener('click', (e) => {
            if (!customDropdownBtn.contains(e.target)) {
                customModelMenu.style.display = 'none';
            }
        });
        
        const options = customModelMenu.querySelectorAll('.custom-model-option');
        options.forEach(opt => {
            opt.addEventListener('click', () => {
                const val = opt.getAttribute('data-value');
                options.forEach(o => o.classList.remove('selected'));
                opt.classList.add('selected');
                hiddenSelect.value = val;
                
                if (val === '0') customModelSelectedText.textContent = 'Low';
                else if (val === '1') customModelSelectedText.textContent = 'Balanced';
                else if (val === '2') customModelSelectedText.textContent = 'High';
                
                customModelMenu.style.display = 'none';
                
                // Trigger any potential change listeners
                hiddenSelect.dispatchEvent(new Event('change'));
            });
        });
        
        // Ensure initial sync
        const initialVal = hiddenSelect.value;
        options.forEach(o => o.classList.remove('selected'));
        const initialOpt = customModelMenu.querySelector(`.custom-model-option[data-value="${initialVal}"]`);
        if (initialOpt) initialOpt.classList.add('selected');
    }
});