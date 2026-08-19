#!/usr/bin/env node
/**
 * Compile Electron JavaScript source files into V8 binary bytecode (.jsc)
 * using Electron's embedded V8 engine via Bytenode.
 *
 * This strips all plain-text JavaScript source code from the final distribution
 * package so that extracting app.asar yields only compiled binary bytecode.
 */

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT_DIR = path.resolve(__dirname, '..');
const SRC_DIR = path.join(ROOT_DIR, 'electron');
const OUT_DIR = path.join(ROOT_DIR, 'dist-electron');

// Check if running inside Electron runtime
const isRunningInElectron = typeof process !== 'undefined' && Boolean(process.versions && process.versions.electron);

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function writeBootstrapLoader(outJsPath, jscFilename) {
  const content = `'use strict';
// Protected V8 Bytecode Loader
const bytenode = require('bytenode');
require('./${jscFilename}');
`;
  fs.writeFileSync(outJsPath, content, 'utf8');
  console.log(`[Bytecode Compiler] Generated bootstrap loader: ${path.basename(outJsPath)}`);
}

async function runCompilation() {
  const bytenode = require('bytenode');
  console.log(`[Bytecode Compiler] Running with V8 v${process.versions.v8} (Electron: ${process.versions.electron || 'Node'})...`);
  ensureDir(OUT_DIR);

  // 1. Compile main.js -> main.jsc
  const srcMain = path.join(SRC_DIR, 'main.js');
  const outMainJsc = path.join(OUT_DIR, 'main.jsc');
  const outMainJs = path.join(OUT_DIR, 'main.js');
  console.log(`[Bytecode Compiler] Compiling main.js -> main.jsc...`);
  await bytenode.compileFile({
    filename: srcMain,
    output: outMainJsc,
    compileAsModule: true
  });
  writeBootstrapLoader(outMainJs, 'main.jsc');

  // 2. Compile preload.js -> preload.jsc
  const srcPreload = path.join(SRC_DIR, 'preload.js');
  const outPreloadJsc = path.join(OUT_DIR, 'preload.jsc');
  const outPreloadJs = path.join(OUT_DIR, 'preload.js');
  console.log(`[Bytecode Compiler] Compiling preload.js -> preload.jsc...`);
  await bytenode.compileFile({
    filename: srcPreload,
    output: outPreloadJsc,
    compileAsModule: true
  });
  writeBootstrapLoader(outPreloadJs, 'preload.jsc');

  // 3. Copy UI assets (splash.html)
  const srcSplash = path.join(SRC_DIR, 'splash.html');
  const outSplash = path.join(OUT_DIR, 'splash.html');
  if (fs.existsSync(srcSplash)) {
    fs.copyFileSync(srcSplash, outSplash);
    console.log('[Bytecode Compiler] Copied splash.html');
  }

  console.log('[Bytecode Compiler] Bytecode compilation complete!');
  process.exit(0);
}

function main() {
  if (isRunningInElectron) {
    // Already running inside Electron's V8 engine -> execute compilation
    runCompilation().catch((err) => {
      console.error('[Bytecode Compiler] Error:', err);
      process.exit(1);
    });
  } else {
    // Running from Node.js CLI -> delegate to Electron binary to match V8 engine version exactly
    console.log('[Bytecode Compiler] Delegating to Electron runtime to match target V8 version...');
    const electronBin = path.join(ROOT_DIR, 'node_modules', '.bin', 'electron');
    const result = spawnSync(electronBin, [__filename], {
      cwd: ROOT_DIR,
      stdio: 'inherit',
      env: Object.assign({}, process.env, { ELECTRON_ENABLE_LOGGING: '1' })
    });

    if (result.status !== 0) {
      console.error(`[Bytecode Compiler] Electron compilation failed with exit code ${result.status}`);
      process.exit(result.status || 1);
    }
  }
}

main();
