'use client';

import { useEffect } from 'react';
import { writeFrontendLog } from '@/lib/logger';

export function FrontendLogProvider() {
  useEffect(() => {
    const onError = (event: ErrorEvent) => {
      writeFrontendLog('error', 'uncaught frontend error', {
        message: event.message,
        source: event.filename,
        line: event.lineno,
        column: event.colno,
      });
    };
    const onRejection = (event: PromiseRejectionEvent) => {
      writeFrontendLog('error', 'unhandled promise rejection', {
        reason: event.reason instanceof Error ? event.reason.message : String(event.reason),
      });
    };
    window.addEventListener('error', onError);
    window.addEventListener('unhandledrejection', onRejection);
    return () => {
      window.removeEventListener('error', onError);
      window.removeEventListener('unhandledrejection', onRejection);
    };
  }, []);

  return null;
}
