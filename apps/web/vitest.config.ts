import { defineConfig } from 'vitest/config';
import path from 'node:path';

export default defineConfig({
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@asf/schemas': path.resolve(__dirname, '../../packages/schemas/ts/index.ts'),
      '@asf/schemas/agents': path.resolve(__dirname, '../../packages/schemas/ts/agents.ts'),
      '@asf/schemas/memory': path.resolve(__dirname, '../../packages/schemas/ts/memory.ts'),
      '@asf/ui': path.resolve(__dirname, '../../packages/ui/src/index.ts'),
    },
  },
});
