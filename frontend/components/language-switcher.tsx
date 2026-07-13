'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Languages } from 'lucide-react';
import { useState, useEffect } from 'react';

const languages = [
  { code: 'en', name: 'English' },
  { code: 'zh', name: '中文' },
];

export function LanguageSwitcher() {
  const router = useRouter();
  const [currentLocale, setCurrentLocale] = useState('en');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const locale =
      document.cookie
        .split('; ')
        .find((row) => row.startsWith('locale='))
        ?.split('=')[1] || 'en';
    setCurrentLocale(locale);
  }, []);

  const handleLanguageToggle = () => {
    const newLocale = currentLocale === 'en' ? 'zh' : 'en';
    document.cookie = `locale=${newLocale}; path=/; max-age=31536000`;
    setCurrentLocale(newLocale);
    router.refresh();
  };

  const currentLanguage = languages.find((lang) => lang.code === currentLocale);

  // 避免水合错误，在客户端挂载前不显示语言名称
  if (!mounted) {
    return (
      <Button variant="ghost" size="sm" className="gap-2">
        <Languages className="h-4 w-4" />
        <span className="hidden sm:inline">English</span>
      </Button>
    );
  }

  return (
    <Button variant="ghost" size="sm" className="gap-2" onClick={handleLanguageToggle}>
      <Languages className="h-4 w-4" />
      <span className="hidden sm:inline">{currentLanguage?.name}</span>
    </Button>
  );
}
