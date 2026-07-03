#!/usr/bin/env node
/**
 * Windows-safe MCP launcher for obsidian-vault.
 * Prefer scripts/mcp-obsidian-vault.cmd on Windows (quoted paths for OneDrive folders with spaces).
 */
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const vault = path.join(root, 'obsidian-vault');
const server = path.join(root, 'node_modules', '@bitbonsai', 'mcpvault', 'dist', 'server.js');
const logPath = path.join(vault, '.mcp-startup.log');

function log(line) {
  try {
    fs.appendFileSync(logPath, `${new Date().toISOString()} ${line}\n`, 'utf8');
  } catch {
    // ignore logging failures
  }
}

log(`start cwd=${process.cwd()} execPath=${process.execPath}`);

if (!fs.existsSync(vault)) {
  log(`ERROR vault missing: ${vault}`);
  console.error(`mcp-obsidian-vault: vault not found at ${vault}`);
  process.exit(1);
}

if (!fs.existsSync(server)) {
  log(`ERROR mcpvault missing: ${server}`);
  console.error('mcp-obsidian-vault: @bitbonsai/mcpvault not installed. Run: pnpm install');
  process.exit(1);
}

log(`spawn ${server} ${vault}`);

const child = spawn(process.execPath, [server, vault], {
  stdio: 'inherit',
  env: process.env,
  windowsHide: true,
});

child.on('error', (err) => {
  log(`ERROR spawn failed: ${err.message}`);
  console.error(`mcp-obsidian-vault: failed to start: ${err.message}`);
  process.exit(1);
});

child.on('exit', (code, signal) => {
  log(`exit code=${code ?? 'null'} signal=${signal ?? 'null'}`);
  if (signal) process.kill(process.pid, signal);
  else process.exit(code ?? 0);
});
