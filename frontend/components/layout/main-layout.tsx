'use client';

import { ProtectedRoute } from '@/components/auth/protected-route';
import { Sidebar } from './sidebar';
import { Navbar } from './navbar';

interface MainLayoutProps {
  children: React.ReactNode;
  requiredPath?: string;
}

export function MainLayout({ children, requiredPath }: MainLayoutProps) {
  return (
    <ProtectedRoute requiredPath={requiredPath}>
      <div className="flex h-screen overflow-hidden">
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-hidden">
          <Navbar />
          <main className="flex-1 overflow-y-auto bg-gray-50 p-6">
            {children}
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
