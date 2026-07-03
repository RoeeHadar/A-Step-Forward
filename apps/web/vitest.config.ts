import { defineConfig } from 'vitest/config';
import fs from 'node:fs';
import path from 'node:path';

const envLocal = path.resolve(__dirname, '.env.local');
if (fs.existsSync(envLocal)) {
  for (const line of fs.readFileSync(envLocal, 'utf8').split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eq = trimmed.indexOf('=');
    if (eq <= 0) continue;
    const key = trimmed.slice(0, eq).trim();
    const value = trimmed.slice(eq + 1).trim();
    if (process.env[key] == null) process.env[key] = value;
  }
}

export default defineConfig({
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      'server-only': path.resolve(__dirname, './src/test-utils/server-only-stub.ts'),
      '@asf/schemas': path.resolve(__dirname, '../../packages/schemas/ts/index.ts'),
      '@asf/schemas/agents': path.resolve(__dirname, '../../packages/schemas/ts/agents.ts'),
      '@asf/schemas/memory': path.resolve(__dirname, '../../packages/schemas/ts/memory.ts'),
      '@asf/ui': path.resolve(__dirname, '../../packages/ui/src/index.ts'),
    },
  },
});
