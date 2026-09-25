import { appendFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { NextResponse } from 'next/server';

const allowedLevels = new Set(['info', 'warn', 'error']);

export async function POST(request: Request) {
  try {
    const payload = await request.json();
    const level = allowedLevels.has(payload?.level) ? payload.level : 'info';
    const entry = JSON.stringify({
      timestamp: typeof payload?.timestamp === 'string' ? payload.timestamp : new Date().toISOString(),
      level,
      message: typeof payload?.message === 'string' ? payload.message.slice(0, 1000) : 'frontend log',
      path: typeof payload?.path === 'string' ? payload.path.slice(0, 500) : '-',
      details: payload?.details,
    }) + '\n';
    const logDir = path.join(process.cwd(), 'logs');
    await mkdir(logDir, { recursive: true });
    await appendFile(path.join(logDir, level === 'error' ? 'error.log' : 'app.log'), entry, 'utf8');
    return NextResponse.json({ ok: true });
  } catch {
    return NextResponse.json({ ok: false }, { status: 400 });
  }
}
