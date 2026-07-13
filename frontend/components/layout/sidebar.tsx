'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { useAuthStore } from '@/stores/auth-store';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  Users,
  Briefcase,
  Calendar,
  Search,
  Settings,
} from 'lucide-react';

interface NavItem {
  labelKey: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  roles?: string[];
}

const navItems: NavItem[] = [
  {
    labelKey: 'nav.dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    labelKey: 'nav.candidates',
    href: '/candidates',
    icon: Users,
    roles: ['hr', 'recruiter'],
  },
  {
    labelKey: 'nav.positions',
    href: '/jobs',
    icon: Briefcase,
    roles: ['hr', 'recruiter'],
  },
  {
    labelKey: 'nav.interviews',
    href: '/interviews',
    icon: Calendar,
  },
  {
    labelKey: 'nav.search',
    href: '/search',
    icon: Search,
    roles: ['hr', 'recruiter'],
  },
  {
    labelKey: 'common.settings',
    href: '/settings',
    icon: Settings,
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const t = useTranslations();
  const user = useAuthStore((state) => state.user);

  const filteredNavItems = navItems.filter((item) => {
    if (!item.roles) return true;
    return user && item.roles.includes(user.role);
  });

  return (
    <aside className="w-64 border-r bg-gray-50/40 flex flex-col">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-gray-900">{t('common.appName')}</h1>
      </div>

      <nav className="flex-1 px-4 space-y-1">
        {filteredNavItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-gray-700 hover:bg-gray-100'
              )}
            >
              <Icon className="h-5 w-5" />
              {t(item.labelKey)}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
