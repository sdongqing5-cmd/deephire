'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { useAuthStore } from '@/stores/auth-store';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Bell, LogOut, User } from 'lucide-react';
import { LanguageSwitcher } from '@/components/language-switcher';

interface NotificationItem {
  id: string;
  candidate: {
    name: string;
    current_title?: string;
  };
  job: {
    title: string;
  };
  status_label: string;
}

export function Navbar() {
  const router = useRouter();
  const t = useTranslations();
  const { user, logout } = useAuthStore();
  const [notificationOpen, setNotificationOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);

  useEffect(() => {
    const loadNotifications = async () => {
      if (!notificationOpen || user?.role !== 'interviewer') return;

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/applications?status=sent_to_interviewer&page=1&page_size=5`
      );
      if (response.ok) {
        const result = await response.json();
        setNotifications(result.data.items || []);
      }
    };

    loadNotifications();
  }, [notificationOpen, user?.role]);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase();
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'hr':
        return t('roles.hr');
      case 'recruiter':
        return t('roles.recruiter');
      case 'interviewer':
        return t('roles.interviewer');
      case 'platform_admin':
        return t('roles.platformAdmin');
      default:
        return role;
    }
  };

  return (
    <header className="border-b bg-white">
      <div className="flex h-16 items-center justify-between px-6">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-semibold text-gray-900">
            {t('common.welcomeBack', { name: user?.name || 'User' })}
          </h2>
        </div>

        <div className="flex items-center gap-4">
          <LanguageSwitcher />

          <DropdownMenu open={notificationOpen} onOpenChange={setNotificationOpen}>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-5 w-5" />
                {user?.role === 'interviewer' && notifications.length > 0 && (
                  <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-red-500" />
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80">
              <DropdownMenuLabel>消息通知</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {user?.role !== 'interviewer' ? (
                <DropdownMenuItem disabled>
                  当前角色暂无通知中心
                </DropdownMenuItem>
              ) : notifications.length === 0 ? (
                <DropdownMenuItem disabled>
                  暂无待处理简历
                </DropdownMenuItem>
              ) : (
                notifications.map((item) => (
                  <DropdownMenuItem
                    key={item.id}
                    onSelect={() => router.push(`/dashboard/interviewer?tab=screening&app=${item.id}`)}
                    className="cursor-pointer"
                  >
                    <div className="flex w-full flex-col items-start gap-1">
                      <div className="text-sm font-medium text-gray-900">{item.candidate.name}</div>
                      <div className="text-xs text-muted-foreground">
                        {item.job.title}
                        {item.candidate.current_title ? ` · ${item.candidate.current_title}` : ''}
                      </div>
                      <div className="text-xs text-primary">{item.status_label}</div>
                    </div>
                  </DropdownMenuItem>
                ))
              )}
            </DropdownMenuContent>
          </DropdownMenu>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                <Avatar>
                  <AvatarFallback>
                    {user ? getInitials(user.name) : 'U'}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium">{user?.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {user ? getRoleLabel(user.role) : ''}
                  </p>
                  <p className="text-xs text-muted-foreground">{user?.email}</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <User className="mr-2 h-4 w-4" />
                {t('common.profile')}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout}>
                <LogOut className="mr-2 h-4 w-4" />
                {t('common.logout')}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
