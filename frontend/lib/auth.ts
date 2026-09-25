import { User, UserRole } from '@/types/user';

export function getDashboardPath(role: UserRole): string {
  switch (role) {
    case 'hr':
      return '/dashboard/hr';
    case 'recruiter':
      return '/dashboard/recruiter';
    case 'interviewer':
      return '/dashboard/interviewer';
    case 'platform_admin':
      return '/platform-admin';
    default:
      return '/dashboard/hr';
  }
}

export function canAccessRoute(user: User | null, path: string): boolean {
  if (!user) return false;

  if (user.role === 'platform_admin') {
    return path.startsWith('/platform-admin');
  }

  // HR can access all routes
  if (user.role === 'hr') return true;

  // Recruiter can access specific routes
  if (user.role === 'recruiter') {
    const allowedPaths = [
      '/dashboard/recruiter',
      '/search',
      '/candidates',
      '/jobs',
      '/interviews',
    ];
    return allowedPaths.some((allowed) => path.startsWith(allowed)) || path.startsWith('/candidates/');
  }

  // Interviewer can only access interview-related routes
  if (user.role === 'interviewer') {
    const allowedPaths = [
      '/dashboard/interviewer',
      '/interviews',
    ];
    return allowedPaths.some((allowed) => path.startsWith(allowed));
  }

  return false;
}
