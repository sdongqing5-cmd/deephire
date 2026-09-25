'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Languages } from 'lucide-react';
import { useSyncExternalStore } from 'react';

const languages = [
  { code: 'en', name: 'English' },
  { code: 'zh', name: '中文' },
];

function getLocaleFromCookie() {
  if (typeof document === 'undefined') return 'en';

  const cookieLocale = document.cookie
      .split('; ')
      .find((row) => row.startsWith('locale='))
      ?.split('=')[1];

  return cookieLocale === 'zh' ? 'zh' : 'en';
}

function subscribeToLocaleChange(callback: () => void) {
  window.addEventListener('localechange', callback);
  return () => window.removeEventListener('localechange', callback);
}

export function LanguageSwitcher() {
  const router = useRouter();
  const currentLocale = useSyncExternalStore(subscribeToLocaleChange, getLocaleFromCookie, () => 'en');

  const handleLanguageToggle = () => {
    const newLocale = currentLocale === 'en' ? 'zh' : 'en';
    document.cookie = `locale=${newLocale}; path=/; max-age=31536000`;
    window.dispatchEvent(new Event('localechange'));
    router.refresh();
  };

  const currentLanguage = languages.find((lang) => lang.code === currentLocale);

  return (
    <Button variant="ghost" size="sm" className="gap-2" onClick={handleLanguageToggle}>
      <Languages className="h-4 w-4" />
      <span className="hidden sm:inline">{currentLanguage?.name}</span>
    </Button>
  );
}
