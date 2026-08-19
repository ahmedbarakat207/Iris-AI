const { app, BrowserWindow, Menu, shell, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const http = require('http');
const { spawn, execSync } = require('child_process');

let mainWindow = null;
let splashWindow = null;
let pythonProcess = null;
let isQuitting = false;

const BACKEND_HOST = '127.0.0.1';
const BACKEND_PORT = parseInt(process.env.PORT || process.env.IRIS_PORT || '5050', 10);
const BACKEND_URL = `http://${BACKEND_HOST}:${BACKEND_PORT}`;
const ROOT_DIR = path.resolve(__dirname, '..');

/**
 * Locate the most suitable Python executable on the system.
 */
function findPythonExecutable() {
  // 1. User override via environment variable
  if (process.env.IRIS_PYTHON_PATH && fs.existsSync(process.env.IRIS_PYTHON_PATH)) {
    return process.env.IRIS_PYTHON_PATH;
  }

  // 2. Look for project-local virtual environment
  const venvCandidates = [
    path.join(ROOT_DIR, '.venv', 'bin', 'python'),
    path.join(ROOT_DIR, '.venv', 'bin', 'python3'),
    path.join(ROOT_DIR, '.venv', 'Scripts', 'python.exe'),
    path.join(ROOT_DIR, 'venv', 'bin', 'python'),
    path.join(ROOT_DIR, 'venv', 'Scripts', 'python.exe'),
    path.join(ROOT_DIR, 'env', 'bin', 'python'),
    path.join(ROOT_DIR, 'env', 'Scripts', 'python.exe')
  ];

  for (const candidate of venvCandidates) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }

  // 3. System PATH fallback
  const isWin = process.platform === 'win32';
  return isWin ? 'python' : 'python3';
}

/**
 * Test whether the Flask server is already accepting HTTP connections.
 */
function pingBackend(timeoutMs = 1200) {
  return new Promise((resolve) => {
    const req = http.get(`${BACKEND_URL}/get_settings`, { timeout: timeoutMs }, (res) => {
      // 200 OK from Iris Flask endpoint
      if (res.statusCode === 200) {
        resolve(true);
      } else {
        resolve(false);
      }
      res.resume();
    });

    req.on('error', () => resolve(false));
    req.on('timeout', () => {
      req.destroy();
      resolve(false);
    });
  });
}

/**
 * Spawn the Python Flask backend service.
 */
function spawnBackend() {
  const pythonPath = findPythonExecutable();
  const appScript = path.join(ROOT_DIR, 'app.py');

  console.log(`[Electron] Using Python executable: ${pythonPath}`);
  console.log(`[Electron] Launching backend script: ${appScript}`);

  const env = Object.assign({}, process.env, {
    PYTHONUNBUFFERED: '1',
    PORT: BACKEND_PORT.toString(),
    IRIS_PORT: BACKEND_PORT.toString(),
    IRIS_BACKEND_SPAWNED_BY_ELECTRON: '1'
  });

  const rawArgs = process.argv.slice(2);
  const forwardArgs = [];

  if (rawArgs.includes('--preview-only') || rawArgs.includes('--preview')) {
    forwardArgs.push('--preview-only');
    console.log('[Electron] Mode: Preview (Mock Responses)');
  } else {
    console.log('[Electron] Mode: Full AI Engine (Live Models)');
  }

  if (rawArgs.includes('--pro')) {
    forwardArgs.push('--pro');
  }

  try {
    pythonProcess = spawn(pythonPath, [appScript, ...forwardArgs], {
      cwd: ROOT_DIR,
      env: env,
      stdio: ['ignore', 'pipe', 'pipe']
    });

    pythonProcess.stdout.on('data', (data) => {
      const line = data.toString().trim();
      if (line) console.log(`[Python stdout] ${line}`);
    });

    pythonProcess.stderr.on('data', (data) => {
      const line = data.toString().trim();
      if (line) console.warn(`[Python stderr] ${line}`);
    });

    pythonProcess.on('error', (err) => {
      console.error(`[Electron] Failed to spawn Python backend: ${err.message}`);
      if (!isQuitting) {
        dialog.showErrorBox(
          'Iris AI Backend Error',
          `Failed to launch Python engine with '${pythonPath}'.\n\nPlease ensure Python 3 is installed with all project requirements.\n\nError: ${err.message}`
        );
      }
    });

    pythonProcess.on('exit', (code, signal) => {
      console.log(`[Electron] Python backend exited with code ${code} (signal: ${signal})`);
      pythonProcess = null;
    });
  } catch (err) {
    console.error(`[Electron] Exception while starting backend: ${err.message}`);
  }
}

/**
 * Terminate the spawned Python backend process cleanly.
 */
function terminateBackend() {
  if (pythonProcess && !pythonProcess.killed) {
    console.log('[Electron] Terminating Python backend...');
    try {
      if (process.platform === 'win32') {
        execSync(`taskkill /pid ${pythonProcess.pid} /T /F`);
      } else {
        // Send SIGTERM to process group
        process.kill(-pythonProcess.pid, 'SIGTERM');
      }
    } catch (e) {
      try {
        pythonProcess.kill('SIGTERM');
      } catch (err) {
        // Process might already have exited
      }
    }
    pythonProcess = null;
  }
}

/**
 * Create the loading splash screen window.
 */
function createSplashWindow() {
  const iconPath = getAppIconPath();

  splashWindow = new BrowserWindow({
    width: 400,
    height: 460,
    resizable: false,
    frame: false,
    show: true,
    alwaysOnTop: true,
    backgroundColor: '#000000',
    icon: iconPath,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  splashWindow.loadFile(path.join(__dirname, 'splash.html'));
  splashWindow.center();
}

/**
 * Get the proper platform application icon path.
 */
function getAppIconPath() {
  if (process.platform === 'darwin') {
    const icns = path.join(ROOT_DIR, 'build', 'icon.icns');
    if (fs.existsSync(icns)) return icns;
  } else if (process.platform === 'win32') {
    const ico = path.join(ROOT_DIR, 'build', 'icon.ico');
    if (fs.existsSync(ico)) return ico;
  }
  const png = path.join(ROOT_DIR, 'build', 'icon.png');
  if (fs.existsSync(png)) return png;
  return path.join(ROOT_DIR, 'logo', 'logo3.png');
}

/**
 * Create the main application window.
 */
function createMainWindow() {
  const iconPath = getAppIconPath();

  mainWindow = new BrowserWindow({
    width: 1380,
    height: 900,
    minWidth: 980,
    minHeight: 650,
    show: false,
    backgroundColor: '#000000',
    title: 'Iris AI',
    icon: iconPath,
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    trafficLightPosition: process.platform === 'darwin' ? { x: 18, y: 18 } : undefined,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false
    }
  });

  // Load the running Flask application URL
  mainWindow.loadURL(BACKEND_URL);

  mainWindow.once('ready-to-show', () => {
    if (splashWindow && !splashWindow.isDestroyed()) {
      splashWindow.close();
      splashWindow = null;
    }
    mainWindow.show();
    mainWindow.focus();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external link navigation safely
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http:') || url.startsWith('https:')) {
      shell.openExternal(url);
      return { action: 'deny' };
    }
    return { action: 'allow' };
  });
}

/**
 * Poll the backend until ready, then transition to main window.
 */
async function waitForBackendAndLaunch() {
  const maxAttempts = 60; // 60 * 500ms = 30 seconds max
  let attempts = 0;

  while (attempts < maxAttempts) {
    if (isQuitting) return;
    const isAlive = await pingBackend();
    if (isAlive) {
      console.log('[Electron] Flask backend is online and ready!');
      createMainWindow();
      return;
    }
    attempts++;
    await new Promise((r) => setTimeout(r, 500));
  }

  // If timeout reached
  if (!isQuitting) {
    if (splashWindow && !splashWindow.isDestroyed()) {
      splashWindow.close();
      splashWindow = null;
    }
    dialog.showErrorBox(
      'Iris AI Startup Timeout',
      `The Iris AI backend service failed to respond at ${BACKEND_URL} within 30 seconds.\n\nPlease check server logs in the logs/ directory or try launching 'python3 app.py' manually.`
    );
  }
}

/**
 * Construct native desktop application menus.
 */
function buildMenu() {
  const isMac = process.platform === 'darwin';

  const template = [
    ...(isMac
      ? [
          {
            label: app.name,
            submenu: [
              { role: 'about', label: 'About Iris AI' },
              { type: 'separator' },
              { role: 'services' },
              { type: 'separator' },
              { role: 'hide', label: 'Hide Iris AI' },
              { role: 'hideOthers' },
              { role: 'unhide' },
              { type: 'separator' },
              { role: 'quit', label: 'Quit Iris AI' }
            ]
          }
        ]
      : []),
    {
      label: 'File',
      submenu: [
        {
          label: 'Open Web UI in Browser',
          click: () => shell.openExternal(BACKEND_URL)
        },
        {
          label: 'Restart Backend Engine',
          click: () => {
            terminateBackend();
            setTimeout(() => {
              spawnBackend();
              if (mainWindow) mainWindow.reload();
            }, 1000);
          }
        },
        { type: 'separator' },
        isMac ? { role: 'close' } : { role: 'quit', label: 'Exit' }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectAll' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Iris AI',
      submenu: [
        {
          label: 'Open Models Directory',
          click: () => shell.openPath(path.join(ROOT_DIR, 'models'))
        },
        {
          label: 'Open Config Directory',
          click: () => shell.openPath(path.join(ROOT_DIR, 'config'))
        },
        {
          label: 'Open Logs Directory',
          click: () => shell.openPath(path.join(ROOT_DIR, 'logs'))
        },
        {
          label: 'Open Outputs Directory',
          click: () => shell.openPath(path.join(ROOT_DIR, 'outputs'))
        }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'zoom' },
        ...(isMac
          ? [
              { type: 'separator' },
              { role: 'front' },
              { type: 'separator' },
              { role: 'window' }
            ]
          : [{ role: 'close' }])
      ]
    },
    {
      role: 'help',
      submenu: [
        {
          label: 'Iris AI Documentation',
          click: () => shell.openPath(path.join(ROOT_DIR, 'documentations'))
        },
        {
          label: 'GitHub Repository',
          click: () => shell.openExternal('https://github.com/ahmedbarakat207/Iris-AI')
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// ── IPC Handlers ─────────────────────────────────────────────────────────────
ipcMain.on('open-external', (_event, url) => {
  if (url && (url.startsWith('http://') || url.startsWith('https://'))) {
    shell.openExternal(url);
  }
});

ipcMain.on('open-logs-folder', () => {
  shell.openPath(path.join(ROOT_DIR, 'logs'));
});

ipcMain.on('open-config-folder', () => {
  shell.openPath(path.join(ROOT_DIR, 'config'));
});

ipcMain.on('restart-backend', () => {
  terminateBackend();
  setTimeout(() => {
    spawnBackend();
    if (mainWindow) mainWindow.reload();
  }, 1000);
});

ipcMain.on('window-minimize', () => {
  if (mainWindow) mainWindow.minimize();
});

ipcMain.on('window-maximize', () => {
  if (mainWindow) {
    if (mainWindow.isMaximized()) mainWindow.unmaximize();
    else mainWindow.maximize();
  }
});

ipcMain.on('window-close', () => {
  if (mainWindow) mainWindow.close();
});

// ── App Lifecycle ────────────────────────────────────────────────────────────
const singleInstanceLock = app.requestSingleInstanceLock();
if (!singleInstanceLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });

  app.whenReady().then(async () => {
    buildMenu();
    createSplashWindow();

    // Check if Flask is already running
    const alreadyAlive = await pingBackend(500);
    if (!alreadyAlive) {
      spawnBackend();
    } else {
      console.log('[Electron] Detected existing Flask instance at ' + BACKEND_URL);
    }

    waitForBackendAndLaunch();

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        createMainWindow();
      }
    });
  });
}

app.on('before-quit', () => {
  isQuitting = true;
  terminateBackend();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
