'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';
import { canAccessRoute } from '@/lib/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPath?: string;
}

export function ProtectedRoute({ children, requiredPath }: ProtectedRouteProps) {
  const router = useRouter();
  const { user, isAuthenticated, hasHydrated } = useAuthStore();

  useEffect(() => {
    if (!hasHydrated) {
      return;
    }

    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (requiredPath && !canAccessRoute(user, requiredPath)) {
      // Redirect to user's dashboard if they don't have access
      router.push('/login');
    }
  }, [hasHydrated, isAuthenticated, user, requiredPath, router]);

  if (!hasHydrated) {
    return null;
  }

  if (!isAuthenticated) {
    return null;
  }

  if (requiredPath && !canAccessRoute(user, requiredPath)) {
    return null;
  }

  return <>{children}</>;
}
