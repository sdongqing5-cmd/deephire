'use client';

import { useTranslations } from 'next-intl';
import { MainLayout } from '@/components/layout/main-layout';
import { Card, CardContent } from '@/components/ui/card';
import { Calendar, Clock, FileText } from 'lucide-react';

export default function InterviewerDashboardPage() {
  const t = useTranslations();

  return (
    <MainLayout requiredPath="/dashboard/interviewer">
      <div className="space-y-6">
        {/* Page Title */}
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t('dashboard.interviewerDashboard')}</h1>
          <p className="text-muted-foreground mt-2">
            {t('dashboard.interviewerOverview')}
          </p>
        </div>

        {/* Statistics Cards */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">
                    {t('dashboard.todaysInterviews')}
                  </p>
                  <p className="mt-2 text-2xl font-bold">0</p>
                </div>
                <div className="rounded-full bg-blue-100 p-3">
                  <Calendar className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">
                    {t('dashboard.upcomingThisWeek')}
                  </p>
                  <p className="mt-2 text-2xl font-bold">0</p>
                </div>
                <div className="rounded-full bg-orange-100 p-3">
                  <Clock className="h-6 w-6 text-orange-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">
                    {t('dashboard.pendingFeedback')}
                  </p>
                  <p className="mt-2 text-2xl font-bold">0</p>
                </div>
                <div className="rounded-full bg-green-100 p-3">
                  <FileText className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* No Interviews Message */}
        <Card>
          <CardContent className="p-12">
            <div className="flex flex-col items-center justify-center text-center">
              <Calendar className="h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-base font-semibold text-gray-900 mb-2">
                {t('dashboard.noInterviewsToday')}
              </h3>
              <p className="text-sm text-muted-foreground max-w-sm">
                {t('dashboard.noInterviewsDescription')}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
