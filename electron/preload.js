const { contextBridge, ipcRenderer } = require('electron');

// Expose safe desktop integration APIs to the renderer
contextBridge.exposeInMainWorld('electronAPI', {
  isElectron: true,
  platform: process.platform,
  version: process.env.npm_package_version || '1.0.0',
  
  // App actions
  openExternal: (url) => ipcRenderer.send('open-external', url),
  openLogsFolder: () => ipcRenderer.send('open-logs-folder'),
  openConfigFolder: () => ipcRenderer.send('open-config-folder'),
  restartBackend: () => ipcRenderer.send('restart-backend'),
  
  // Window controls (if needed for custom headers)
  minimizeWindow: () => ipcRenderer.send('window-minimize'),
  maximizeWindow: () => ipcRenderer.send('window-maximize'),
  closeWindow: () => ipcRenderer.send('window-close'),
  
  // Event listeners
  onBackendStatus: (callback) => {
    ipcRenderer.on('backend-status', (_event, value) => callback(value));
  }
});

// Auto-tag HTML element with platform CSS classes
window.addEventListener('DOMContentLoaded', () => {
  if (document.documentElement) {
    document.documentElement.classList.add('is-electron');
    document.documentElement.classList.add(`is-electron-${process.platform}`);
  }
});

