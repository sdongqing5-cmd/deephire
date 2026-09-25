'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';
import { formatDistanceToNow } from 'date-fns';
import { zhCN, enUS } from 'date-fns/locale';
import { MainLayout } from '@/components/layout/main-layout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { mockCandidates } from '@/lib/mock/candidates';
import { mockJobs } from '@/lib/mock/jobs';
import { mockInterviews } from '@/lib/mock/interviews';
import { mockActivities } from '@/lib/mock/activities';
import {
  Users,
  Briefcase,
  Calendar,
  ClipboardList,
  Plus,
  Search,
  CalendarPlus,
  Clock,
  TrendingUp
} from 'lucide-react';

export default function HRDashboardPage() {
  const t = useTranslations();
  const router = useRouter();

  // Get current locale for date formatting
  const currentLocale = typeof document !== 'undefined'
    ? document.cookie.split('; ').find((row) => row.startsWith('locale='))?.split('=')[1] || 'en'
    : 'en';
  const dateLocale = currentLocale === 'zh' ? zhCN : enUS;

  const [totalCandidates, setTotalCandidates] = useState(0);
  const [activeJobs, setActiveJobs] = useState(0);
  const [pendingReviews, setPendingReviews] = useState(0);

  useEffect(() => {
    const fetchDashboardStats = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL;
        const [jobsResponse, applicationsResponse, pendingResponse] = await Promise.all([
          fetch(`${apiUrl}/api/v1/jobs?status=recruiting&limit=100`),
          fetch(`${apiUrl}/api/v1/applications?page=1&page_size=1`),
          fetch(`${apiUrl}/api/v1/applications?status=new&page=1&page_size=1`),
        ]);

        if (jobsResponse.ok) {
          const jobs = await jobsResponse.json();
          setActiveJobs(Array.isArray(jobs) ? jobs.length : 0);
        }

        if (applicationsResponse.ok) {
          const result = await applicationsResponse.json();
          setTotalCandidates(result.data?.total || 0);
        }

        if (pendingResponse.ok) {
          const result = await pendingResponse.json();
          setPendingReviews(result.data?.total || 0);
        }
      } catch (error) {
        console.error('Failed to fetch HR dashboard stats:', error);
      }
    };

    fetchDashboardStats();
  }, []);

  const todayInterviews = mockInterviews.filter(interview => {
    const interviewDate = new Date(interview.scheduledAt);
    const today = new Date();
    return interviewDate.toDateString() === today.toDateString();
  }).length;

  // Get today's interviews
  const todaysInterviewsList = mockInterviews
    .filter(interview => {
      const interviewDate = new Date(interview.scheduledAt);
      const today = new Date();
      return interviewDate.toDateString() === today.toDateString();
    })
    .slice(0, 5);

  // Get recent activities
  const recentActivities = mockActivities.slice(0, 8);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'candidate_added':
        return <Users className="h-4 w-4" />;
      case 'interview_scheduled':
        return <Calendar className="h-4 w-4" />;
      case 'status_changed':
        return <TrendingUp className="h-4 w-4" />;
      case 'offer_sent':
        return <ClipboardList className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  return (
    <MainLayout requiredPath="/dashboard/hr">
      <div className="space-y-8">
        {/* Page Title */}
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t('dashboard.hrDashboard')}</h1>
        </div>

        {/* Statistics Cards */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <Card
            className="cursor-pointer transition-all hover:shadow-lg hover:-translate-y-1"
            onClick={() => router.push('/candidates')}
          >
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">
                    {t('dashboard.totalCandidates')}
                  </p>
                  <p className="mt-2 text-2xl font-bold">{totalCandidates}</p>
                </div>
                <div className="rounded-full bg-blue-100 p-3">
                  <Users className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card
            className="cursor-pointer transition-all hover:shadow-lg hover:-translate-y-1"
            onClick={() => router.push('/jobs')}
          >
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">
                    {t('dashboard.activeJobs')}
                  </p>
                  <p className="mt-2 text-2xl font-bold">{activeJobs}</p>
                </div>
                <div className="rounded-full bg-green-100 p-3">
                  <Briefcase className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card
            className="cursor-pointer transition-all hover:shadow-lg hover:-translate-y-1"
            onClick={() => router.push('/interviews')}
          >
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">
                    {t('dashboard.interviewsToday')}
                  </p>
                  <p className="mt-2 text-2xl font-bold">{todayInterviews}</p>
                </div>
                <div className="rounded-full bg-purple-100 p-3">
                  <Calendar className="h-6 w-6 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card
            className="cursor-pointer transition-all hover:shadow-lg hover:-translate-y-1"
            onClick={() => router.push('/candidates?view=pending-view')}
          >
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">
                    {t('dashboard.pendingReviews')}
                  </p>
                  <p className="mt-2 text-2xl font-bold">{pendingReviews}</p>
                </div>
                <div className="rounded-full bg-orange-100 p-3">
                  <ClipboardList className="h-6 w-6 text-orange-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-semibold">{t('dashboard.quickActions')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              <Button onClick={() => router.push('/jobs/new')} size="default">
                <Plus className="mr-2 h-4 w-4" />
                {t('dashboard.createJob')}
              </Button>
              <Button variant="secondary" onClick={() => router.push('/search')} size="default">
                <Search className="mr-2 h-4 w-4" />
                {t('dashboard.searchTalent')}
              </Button>
              <Button variant="secondary" onClick={() => router.push('/interviews/new')} size="default">
                <CalendarPlus className="mr-2 h-4 w-4" />
                {t('dashboard.scheduleInterview')}
              </Button>
            </div>
          </CardContent>
        </Card>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Today's Interviews */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base font-semibold">{t('dashboard.todaysInterviews')}</CardTitle>
            </CardHeader>
            <CardContent>
              {todaysInterviewsList.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-8 text-center">
                  <div className="rounded-full bg-gray-100 p-4 mb-4">
                    <Calendar className="h-8 w-8 text-gray-400" />
                  </div>
                  <p className="text-sm font-medium text-gray-900">{t('dashboard.noInterviewsToday')}</p>
                  <p className="text-xs text-muted-foreground mt-1">{t('dashboard.noInterviewsDescription')}</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {todaysInterviewsList.map((interview) => {
                    const candidate = mockCandidates.find(c => c.id === interview.candidateId);
                    const job = mockJobs.find(j => j.id === interview.jobId);
                    const time = new Date(interview.scheduledAt).toLocaleTimeString('en-US', {
                      hour: '2-digit',
                      minute: '2-digit'
                    });

                    return (
                      <div
                        key={interview.id}
                        className="flex items-center justify-between border-b pb-3 last:border-0 hover:bg-gray-50 -mx-2 px-2 py-2 rounded transition-colors cursor-pointer"
                      >
                        <div className="flex-1">
                          <p className="font-medium">{candidate?.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {job?.titleKey ? t(`jobs.${job.titleKey}`) : job?.title}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">
                            {time} • {interview.duration} min
                          </p>
                        </div>
                        <Badge className={getStatusColor(interview.status)}>
                          {t(`status.${interview.status}`)}
                        </Badge>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recent Activities */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base font-semibold">{t('dashboard.recentActivities')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentActivities.map((activity) => {
                  const timeAgo = formatDistanceToNow(new Date(activity.timestamp), {
                    addSuffix: true,
                    locale: dateLocale
                  });
                  const candidate = mockCandidates.find(c => c.id === activity.candidateId);
                  const job = mockJobs.find(j => j.id === activity.jobId);

                  // Generate translated title and description
                  const title = t(`activities.${activity.type}`);
                  let description = '';

                  switch (activity.type) {
                    case 'candidate_added':
                      description = t('activities.candidate_applied', {
                        name: candidate?.name || '',
                        job: job?.titleKey ? t(`jobs.${job.titleKey}`) : job?.title || ''
                      });
                      break;
                    case 'interview_scheduled':
                      const interview = mockInterviews.find(i => i.id === activity.interviewId);
                      description = t('activities.interview_scheduled_with', {
                        type: interview?.type ? t(`interviewTypes.${interview.type}`) : '',
                        name: candidate?.name || ''
                      });
                      break;
                    case 'interview_completed':
                      const completedInterview = mockInterviews.find(i => i.id === activity.interviewId);
                      description = t('activities.interview_completed_for', {
                        type: completedInterview?.type ? t(`interviewTypes.${completedInterview.type}`) : '',
                        name: candidate?.name || ''
                      });
                      break;
                    case 'interview_cancelled':
                      const cancelledInterview = mockInterviews.find(i => i.id === activity.interviewId);
                      description = t('activities.interview_cancelled_for', {
                        type: cancelledInterview?.type ? t(`interviewTypes.${cancelledInterview.type}`) : '',
                        name: candidate?.name || ''
                      });
                      break;
                    case 'status_changed':
                      description = t('activities.candidate_moved_to', {
                        name: candidate?.name || '',
                        stage: candidate?.status || ''
                      });
                      break;
                    case 'offer_sent':
                      description = t('activities.offer_sent_to', {
                        name: candidate?.name || ''
                      });
                      break;
                    case 'job_created':
                      description = t('activities.job_position_opened', {
                        job: job?.titleKey ? t(`jobs.${job.titleKey}`) : job?.title || ''
                      });
                      break;
                    default:
                      description = activity.description;
                  }

                  return (
                    <div key={activity.id} className="flex gap-3 border-b pb-3 last:border-0 hover:bg-gray-50 -mx-2 px-2 py-2 rounded transition-colors cursor-pointer">
                      <div className="mt-1 rounded-full bg-gray-100 p-2">
                        {getActivityIcon(activity.type)}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">{title}</p>
                        <p className="text-xs text-muted-foreground">{description}</p>
                        <p className="text-xs text-muted-foreground mt-1">{timeAgo}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}
