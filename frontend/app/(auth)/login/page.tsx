'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useTranslations } from 'next-intl';
import { useAuthStore } from '@/stores/auth-store';
import { getDashboardPath } from '@/lib/auth';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { LanguageSwitcher } from '@/components/language-switcher';

export default function LoginPage() {
  const router = useRouter();
  const { toast } = useToast();
  const t = useTranslations();
  const login = useAuthStore((state) => state.login);
  const [isLoading, setIsLoading] = useState(false);

  const loginSchema = z.object({
    email: z.string().email(t('validation.invalidEmail')),
    password: z.string().min(1, t('validation.required')),
  });

  type LoginFormValues = z.infer<typeof loginSchema>;

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (data: LoginFormValues) => {
    setIsLoading(true);
    try {
      await login(data.email, data.password);
      const user = useAuthStore.getState().user;

      if (user) {
        const dashboardPath = getDashboardPath(user.role);
        router.push(dashboardPath);
      }
    } catch (error) {
      toast({
        variant: 'destructive',
        title: t('auth.loginFailed'),
        description: error instanceof Error ? error.message : t('auth.invalidCredentials'),
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="absolute right-4 top-4">
        <LanguageSwitcher />
      </div>
      <div className="w-full max-w-md space-y-8 rounded-lg bg-white p-8 shadow-lg">
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight">{t('common.appName')}</h1>
          <p className="mt-2 text-sm text-gray-600">
            {t('auth.loginTitle')}
          </p>
        </div>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t('auth.email')}</FormLabel>
                  <FormControl>
                    <Input
                      type="email"
                      placeholder={t('auth.emailPlaceholder')}
                      {...field}
                      disabled={isLoading}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t('auth.password')}</FormLabel>
                  <FormControl>
                    <Input
                      type="password"
                      placeholder={t('auth.passwordPlaceholder')}
                      {...field}
                      disabled={isLoading}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? t('auth.signingIn') : t('auth.login')}
            </Button>
          </form>
        </Form>

        <div className="mt-6 rounded-md bg-blue-50 p-4">
          <p className="text-xs font-semibold text-blue-900">{t('auth.demoAccounts')}</p>
          <div className="mt-2 space-y-1 text-xs text-blue-800">
            <p>{t('auth.hr')}: hr@deephire.com</p>
            <p>{t('auth.recruiter')}: recruiter@deephire.com</p>
            <p>{t('auth.interviewer')}: interviewer@deephire.com</p>
            <p className="mt-2 text-blue-600">{t('auth.password')}: password123</p>
          </div>
        </div>
      </div>
    </div>
  );
}
