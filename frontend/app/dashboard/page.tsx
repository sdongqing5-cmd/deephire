'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';

export default function DashboardPage() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    // Redirect to role-specific dashboard
    if (user) {
      switch (user.role) {
        case 'hr':
          router.replace('/dashboard/hr');
          break;
        case 'recruiter':
          router.replace('/dashboard/recruiter');
          break;
        case 'interviewer':
          router.replace('/dashboard/interviewer');
          break;
        default:
          router.replace('/dashboard/hr');
      }
    }
  }, [user, router]);

  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading dashboard...</p>
      </div>
    </div>
  );
}
