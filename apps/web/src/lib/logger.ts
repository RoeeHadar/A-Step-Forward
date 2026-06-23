/**
 * Small structured logger for the frontend. Use this instead of console.log.
 * Sub-agent 01-frontend wires this to a real sink (Vercel logs / Sentry).
 */
type Level = 'debug' | 'info' | 'warn' | 'error';

function emit(level: Level, message: string, meta?: Record<string, unknown>) {
  const payload = { ts: new Date().toISOString(), level, message, ...meta };
  if (typeof window === 'undefined') {
    process.stdout.write(JSON.stringify(payload) + '\n');
  } else if (process.env.NODE_ENV !== 'production') {
    // eslint-disable-next-line no-console
    console[level === 'debug' ? 'log' : level](payload);
  }
}

export const logger = {
  debug: (m: string, meta?: Record<string, unknown>) => emit('debug', m, meta),
  info: (m: string, meta?: Record<string, unknown>) => emit('info', m, meta),
  warn: (m: string, meta?: Record<string, unknown>) => emit('warn', m, meta),
  error: (m: string, meta?: Record<string, unknown>) => emit('error', m, meta),
};
