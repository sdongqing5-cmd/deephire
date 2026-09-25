"use client";

export type FrontendLogLevel = 'info' | 'warn' | 'error';

export function writeFrontendLog(level: FrontendLogLevel, message: string, details?: Record<string, unknown>) {
  const entry = {
    timestamp: new Date().toISOString(),
    level,
    message,
    path: typeof window === 'undefined' ? '-' : window.location.pathname,
    details,
  };

  if (level === 'error') console.error(message, details);
  else if (level === 'warn') console.warn(message, details);
  else console.info(message, details);

  if (typeof window !== 'undefined') {
    void fetch('/api/client-logs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(entry),
      keepalive: true,
    }).catch(() => undefined);
  }
}
