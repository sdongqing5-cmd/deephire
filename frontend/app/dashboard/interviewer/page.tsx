'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { formatDistanceToNow } from 'date-fns';
import { enUS, zhCN } from 'date-fns/locale';
import {
  Calendar,
  CalendarPlus,
  Clock,
  FileText,
  History,
  MessageSquareWarning,
  UserCheck,
} from 'lucide-react';
import { MainLayout } from '@/components/layout/main-layout';
import { useAuthStore } from '@/stores/auth-store';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { mockActivities } from '@/lib/mock/activities';

interface ApplicationListItem {
  id: string;
  candidate: {
    id: string;
    name: string;
    phone?: string;
    email?: string;
    current_company?: string;
    current_title?: string;
    years_of_experience?: number;
    location?: string;
  };
  job: {
    id: string;
    title: string;
  };
  status: string;
  status_label: string;
  interviewer_evaluation?: string;
  resume_url?: string;
  applied_at: string;
}

interface InterviewItem {
  id: string;
  application_id: string;
  candidate_id: string;
  candidate_name: string;
  job_id: string;
  job_title: string;
  interview_type: string;
  interviewer_name: string;
  scheduled_at: string;
  duration: number;
  location?: string;
  status: string;
  result?: string;
}

const statusLabels: Record<string, string> = {
  scheduled: '已安排',
  confirmed: '已确认',
  in_progress: '进行中',
  completed: '已完成',
  cancelled: '已取消',
  no_show: '未到场',
};

export default function InterviewerDashboardPage() {
  const t = useTranslations();
  const router = useRouter();
  const searchParams = useSearchParams();
  const user = useAuthStore((state) => state.user);
  const isScreeningView = searchParams.get('tab') === 'screening';
  const screeningTab = searchParams.get('screeningTab') === 'screened' ? 'screened' : 'pending';
  const currentLocale = typeof document !== 'undefined'
    ? document.cookie.split('; ').find((row) => row.startsWith('locale='))?.split('=')[1] || 'en'
    : 'en';
  const dateLocale = currentLocale === 'zh' ? zhCN : enUS;

  const [applications, setApplications] = useState<ApplicationListItem[]>([]);
  const [screenedApplications, setScreenedApplications] = useState<ApplicationListItem[]>([]);
  const [todayInterviews, setTodayInterviews] = useState<InterviewItem[]>([]);
  const [upcomingInterviews, setUpcomingInterviews] = useState<InterviewItem[]>([]);
  const [pendingFeedback, setPendingFeedback] = useState<InterviewItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [evaluationApplication, setEvaluationApplication] = useState<ApplicationListItem | null>(null);
  const [evaluationText, setEvaluationText] = useState('');
  const [evaluationDialogOpen, setEvaluationDialogOpen] = useState(false);
  const [evaluationSaving, setEvaluationSaving] = useState(false);

  const fetchApplications = useCallback(async () => {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/applications?page=1&page_size=200`
    );
    if (!response.ok) {
      return { pending: [], screened: [] };
    }

    const result = await response.json();
    const items: ApplicationListItem[] = result.data.items || [];
    const pending = items.filter((application) => application.status === 'sent_to_interviewer');
    const screenedStatuses = new Set([
      'interviewer_hold',
      'interviewer_rejected',
      'interview_intention_communication',
      'candidate_declined_interview',
      'interview_time_confirming',
      'department_interview_scheduled',
      'department_interviewing',
      'department_interview_hold',
      'department_interview_completed',
      'department_interview_rejected',
      'assessment_invited',
      'assessment_in_progress',
      'assessment_completed',
      'assessment_failed',
      'hr_reinterview_scheduled',
      'hr_reinterviewing',
      'hr_reinterview_completed',
      'hr_reinterview_rejected',
      'final_interview_scheduled',
      'final_interviewing',
      'final_interview_completed',
      'final_interview_rejected',
      'salary_negotiation',
      'salary_rejected',
      'verbal_offer_accepted',
      'offer_approval',
      'offer_approval_rejected',
      'offer_pending',
      'offer_sent',
      'offer_not_agreed',
      'offer_rejected',
      'offer_accepted',
      'pending_onboard',
      'onboard_cancelled',
      'onboarded',
    ]);

    return {
      pending,
      screened: items.filter((application) => screenedStatuses.has(application.status)),
    };
  }, []);

  const fetchInterviews = useCallback(async () => {
    const interviewerId = user?.id;
    const allInterviewsUrl = new URL(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/interview-management`);
    allInterviewsUrl.searchParams.set('limit', '50');
    if (interviewerId) {
      allInterviewsUrl.searchParams.set('interviewer_id', interviewerId);
      allInterviewsUrl.searchParams.set('result', 'pending');
    }

    const [todayResponse, upcomingResponse, pendingResponse] = await Promise.all([
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/interview-management/today`),
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/interview-management/upcoming?days=7`),
      fetch(allInterviewsUrl.toString()),
    ]);

    return {
      today: todayResponse.ok ? (await todayResponse.json()).data || [] : [],
      upcoming: upcomingResponse.ok ? (await upcomingResponse.json()).data || [] : [],
      pending: pendingResponse.ok ? (await pendingResponse.json()).data || [] : [],
    };
  }, [user?.id]);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        setLoading(true);
        const [applicationItems, interviewData] = await Promise.all([
          fetchApplications(),
          fetchInterviews(),
        ]);

        setApplications(applicationItems.pending);
        setScreenedApplications(applicationItems.screened);
        setTodayInterviews(interviewData.today);
        setUpcomingInterviews(interviewData.upcoming);
        setPendingFeedback(interviewData.pending);
      } catch (error) {
        console.error('Failed to load interviewer dashboard:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, [fetchApplications, fetchInterviews]);

  const recentActivities = useMemo(
    () =>
      mockActivities
        .filter((activity) => activity.userId === '3' || activity.type.startsWith('interview_'))
        .slice(0, 8),
    []
  );

  const openEvaluationDialog = (application: ApplicationListItem) => {
    setEvaluationApplication(application);
    setEvaluationText(application.interviewer_evaluation || '');
    setEvaluationDialogOpen(true);
  };

  const saveEvaluation = async () => {
    if (!evaluationApplication) return;

    setEvaluationSaving(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/applications/${evaluationApplication.id}/interviewer-evaluation`,
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ evaluation: evaluationText }),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        alert(`保存失败: ${error.detail || '未知错误'}`);
        return;
      }

      const latestApplications = await fetchApplications();
      setApplications(latestApplications.pending);
      setScreenedApplications(latestApplications.screened);
      setEvaluationDialogOpen(false);
    } catch {
      alert('保存失败，请稍后重试');
    } finally {
      setEvaluationSaving(false);
    }
  };

  const getInterviewerStatusLabel = (status: string, fallback: string) => {
    switch (status) {
      case 'sent_to_interviewer':
        return t('dashboard.interviewerWorkspace.statusSentToInterviewer');
      case 'interview_intention_communication':
        return t('dashboard.interviewerWorkspace.statusInterviewIntentionCommunication');
      case 'interviewer_rejected':
        return t('dashboard.interviewerWorkspace.statusInterviewerRejected');
      default:
        return fallback;
    }
  };

  if (isScreeningView) {
    const switchScreeningTab = (value: string) => {
      router.push(`/dashboard/interviewer?tab=screening&screeningTab=${value}`);
    };

    return (
      <MainLayout requiredPath="/dashboard/interviewer">
        <div className="space-y-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              {t('dashboard.interviewerWorkspace.candidatesTitle')}
            </h1>
            <p className="mt-2 text-sm text-muted-foreground">
              {t('dashboard.interviewerWorkspace.candidatesDescription')}
            </p>
          </div>

          <Tabs value={screeningTab} onValueChange={switchScreeningTab} className="mt-4 space-y-4">
            <TabsList>
              <TabsTrigger value="pending">
                {t('dashboard.interviewerWorkspace.pendingSection', { count: applications.length })}
              </TabsTrigger>
              <TabsTrigger value="screened">
                {t('dashboard.interviewerWorkspace.screenedSection', { count: screenedApplications.length })}
              </TabsTrigger>
            </TabsList>

            {loading ? (
              <div className="py-12 text-center">
                <div className="mx-auto h-12 w-12 animate-spin rounded-full border-b-2 border-primary"></div>
                <p className="mt-4 text-gray-600">{t('dashboard.interviewerWorkspace.loading')}</p>
              </div>
            ) : (
              <>
                <TabsContent value="pending" className="mt-0">
                  {applications.length === 0 ? (
                    <Card className="p-12">
                      <div className="text-center">
                        <FileText className="mx-auto h-12 w-12 text-gray-400" />
                        <h3 className="mt-4 text-lg font-medium text-gray-900">
                          {t('dashboard.interviewerWorkspace.noPendingResumes')}
                        </h3>
                        <p className="mt-2 text-gray-500">
                          {t('dashboard.interviewerWorkspace.noPendingResumesHint')}
                        </p>
                      </div>
                    </Card>
                  ) : (
                    <div className="grid gap-4">
                      {applications.map((application) => (
                  <Card
                    key={application.id}
                    className="cursor-pointer p-6 transition-shadow hover:shadow-md"
                    onClick={() => router.push(`/candidates/${application.id}`)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="mb-2 flex items-center gap-3">
                          <h3 className="text-lg font-semibold text-gray-900">
                            {application.candidate.name}
                          </h3>
                          <Badge variant="secondary">
                            {getInterviewerStatusLabel(application.status, application.status_label)}
                          </Badge>
                        </div>

                        <div className="mb-3 flex items-center gap-4 text-sm text-gray-600">
                          <span>
                            {t('dashboard.interviewerWorkspace.appliedJob', { title: application.job.title })}
                          </span>
                          {application.candidate.current_title && (
                            <>
                              <span>•</span>
                              <span>{application.candidate.current_title}</span>
                            </>
                          )}
                          {application.candidate.current_company && (
                            <>
                              <span>•</span>
                              <span>{application.candidate.current_company}</span>
                            </>
                          )}
                          {application.candidate.location && (
                            <>
                              <span>•</span>
                              <span>{application.candidate.location}</span>
                            </>
                          )}
                        </div>

                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          {application.candidate.phone && <span>{application.candidate.phone}</span>}
                          {application.candidate.email && (
                            <>
                              {application.candidate.phone && <span>•</span>}
                              <span>{application.candidate.email}</span>
                            </>
                          )}
                          <span>•</span>
                          <span>{new Date(application.applied_at).toLocaleDateString('zh-CN')}</span>
                        </div>
                      </div>

                      <div onClick={(event) => event.stopPropagation()}>
                        <Button variant="outline" onClick={() => router.push(`/candidates/${application.id}`)}>
                          {t('dashboard.interviewerWorkspace.viewResume')}
                        </Button>
                      </div>
                    </div>
                  </Card>
                      ))}
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="screened" className="mt-0">
                  {screenedApplications.length === 0 ? (
                    <Card className="p-12">
                      <div className="text-center">
                        <FileText className="mx-auto h-12 w-12 text-gray-400" />
                        <h3 className="mt-4 text-lg font-medium text-gray-900">
                          {t('dashboard.interviewerWorkspace.noScreenedResumes')}
                        </h3>
                        <p className="mt-2 text-gray-500">
                          {t('dashboard.interviewerWorkspace.noScreenedResumesHint')}
                        </p>
                      </div>
                    </Card>
                  ) : (
                    <div className="grid gap-4">
                      {screenedApplications.map((application) => (
                        <Card
                          key={application.id}
                          className="cursor-pointer p-6 transition-shadow hover:shadow-md"
                          onClick={() => router.push(`/candidates/${application.id}`)}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="mb-2 flex items-center gap-3">
                                <h3 className="text-lg font-semibold text-gray-900">
                                  {application.candidate.name}
                                </h3>
                                <Badge variant="outline">
                                  {getInterviewerStatusLabel(application.status, application.status_label)}
                                </Badge>
                              </div>
                              <div className="mb-3 flex items-center gap-4 text-sm text-gray-600">
                                <span>
                                  {t('dashboard.interviewerWorkspace.appliedJob', { title: application.job.title })}
                                </span>
                                {application.candidate.current_title && (
                                  <>
                                    <span>•</span>
                                    <span>{application.candidate.current_title}</span>
                                  </>
                                )}
                                {application.candidate.current_company && (
                                  <>
                                    <span>•</span>
                                    <span>{application.candidate.current_company}</span>
                                  </>
                                )}
                                {application.candidate.location && (
                                  <>
                                    <span>•</span>
                                    <span>{application.candidate.location}</span>
                                  </>
                                )}
                              </div>
                              <div className="flex items-center gap-4 text-sm text-gray-500">
                                {application.candidate.phone && <span>{application.candidate.phone}</span>}
                                {application.candidate.email && (
                                  <>
                                    {application.candidate.phone && <span>•</span>}
                                    <span>{application.candidate.email}</span>
                                  </>
                                )}
                                <span>•</span>
                                <span>{new Date(application.applied_at).toLocaleDateString('zh-CN')}</span>
                              </div>
                            </div>
                            <div onClick={(event) => event.stopPropagation()}>
                              <div className="flex gap-2">
                                <Button variant="outline" onClick={() => router.push(`/candidates/${application.id}`)}>
                                  {t('dashboard.interviewerWorkspace.viewResume')}
                                </Button>
                                <Button variant="outline" onClick={() => openEvaluationDialog(application)}>
                                  {t('dashboard.interviewerWorkspace.candidateEvaluation')}
                                </Button>
                              </div>
                            </div>
                          </div>
                          {application.interviewer_evaluation && (
                            <div className="mt-4 rounded-md bg-muted/40 px-3 py-2 text-sm text-muted-foreground">
                              <span className="font-medium text-foreground">{t('dashboard.interviewerWorkspace.evaluationLabel')}：</span>
                              {application.interviewer_evaluation}
                            </div>
                          )}
                        </Card>
                      ))}
                    </div>
                  )}
                </TabsContent>
              </>
            )}
          </Tabs>

          <Dialog
            open={evaluationDialogOpen}
            onOpenChange={(open) => {
              setEvaluationDialogOpen(open);
              if (!open) setEvaluationApplication(null);
            }}
          >
            <DialogContent className="sm:max-w-lg">
              <DialogHeader>
                <DialogTitle>{t('dashboard.interviewerWorkspace.candidateEvaluation')}</DialogTitle>
                <DialogDescription>
                  {evaluationApplication?.candidate.name} · {evaluationApplication?.job.title}
                </DialogDescription>
              </DialogHeader>
              <Textarea
                value={evaluationText}
                onChange={(event) => setEvaluationText(event.target.value)}
                placeholder={t('dashboard.interviewerWorkspace.evaluationPlaceholder')}
                rows={6}
                autoFocus
              />
              <DialogFooter>
                <Button variant="outline" disabled={evaluationSaving} onClick={() => setEvaluationDialogOpen(false)}>
                  {t('dashboard.interviewerWorkspace.cancel')}
                </Button>
                <Button disabled={evaluationSaving} onClick={saveEvaluation}>
                  {evaluationSaving ? t('dashboard.interviewerWorkspace.saving') : t('dashboard.interviewerWorkspace.saveEvaluation')}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout requiredPath="/dashboard/interviewer">
      <div className="space-y-8">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t('dashboard.interviewerDashboard')}</h1>
          <p className="mt-2 text-sm text-muted-foreground">{t('dashboard.interviewerOverview')}</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <Card className="cursor-pointer transition-all hover:-translate-y-1 hover:shadow-lg" onClick={() => router.push('/dashboard/interviewer?tab=screening')}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">{t('dashboard.pendingReviews')}</p>
                  <p className="mt-2 text-2xl font-bold">{applications.length}</p>
                </div>
                <div className="rounded-full bg-blue-100 p-3">
                  <FileText className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="cursor-pointer transition-all hover:-translate-y-1 hover:shadow-lg" onClick={() => router.push('/interviews?tab=today')}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">{t('dashboard.interviewsToday')}</p>
                  <p className="mt-2 text-2xl font-bold">{todayInterviews.length}</p>
                </div>
                <div className="rounded-full bg-purple-100 p-3">
                  <Calendar className="h-6 w-6 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="cursor-pointer transition-all hover:-translate-y-1 hover:shadow-lg" onClick={() => router.push('/interviews?tab=upcoming')}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">{t('dashboard.upcomingThisWeek')}</p>
                  <p className="mt-2 text-2xl font-bold">{upcomingInterviews.length}</p>
                </div>
                <div className="rounded-full bg-green-100 p-3">
                  <Clock className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="cursor-pointer transition-all hover:-translate-y-1 hover:shadow-lg" onClick={() => router.push('/interviews?tab=all&result=pending')}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">{t('dashboard.pendingFeedback')}</p>
                  <p className="mt-2 text-2xl font-bold">{pendingFeedback.length}</p>
                </div>
                <div className="rounded-full bg-orange-100 p-3">
                  <MessageSquareWarning className="h-6 w-6 text-orange-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-base font-semibold">{t('dashboard.quickActions')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              <Button onClick={() => router.push('/dashboard/interviewer?tab=screening')} size="default">
                <UserCheck className="mr-2 h-4 w-4" />
                {t('dashboard.interviewerWorkspace.candidatesTitle')}
              </Button>
              <Button variant="secondary" onClick={() => router.push('/interviews?tab=today')} size="default">
                <Calendar className="mr-2 h-4 w-4" />
                {t('dashboard.todaysInterviews')}
              </Button>
              <Button variant="secondary" onClick={() => router.push('/interviews/new')} size="default">
                <CalendarPlus className="mr-2 h-4 w-4" />
                {t('dashboard.scheduleInterview')}
              </Button>
            </div>
          </CardContent>
        </Card>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base font-semibold">{t('dashboard.todaysInterviews')}</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="py-8 text-center">
                  <div className="mx-auto h-12 w-12 animate-spin rounded-full border-b-2 border-primary"></div>
                </div>
              ) : todayInterviews.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-8 text-center">
                  <div className="mb-4 rounded-full bg-gray-100 p-4">
                    <Calendar className="h-8 w-8 text-gray-400" />
                  </div>
                  <p className="text-sm font-medium text-gray-900">{t('dashboard.noInterviewsToday')}</p>
                  <p className="mt-1 text-xs text-muted-foreground">{t('dashboard.noInterviewsDescription')}</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {todayInterviews.slice(0, 5).map((interview) => (
                    <div
                      key={interview.id}
                      onClick={() => router.push(`/interviews/${interview.id}`)}
                      className="-mx-2 cursor-pointer rounded border-b px-2 py-2 transition-colors hover:bg-gray-50 last:border-0"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <p className="font-medium">{interview.candidate_name}</p>
                          <p className="text-sm text-muted-foreground">{interview.job_title}</p>
                          <p className="mt-1 text-xs text-muted-foreground">
                            {new Date(interview.scheduled_at).toLocaleTimeString('zh-CN', {
                              hour: '2-digit',
                              minute: '2-digit',
                            })}{' '}
                            • {interview.duration} 分钟
                          </p>
                        </div>
                        <Badge variant="secondary">
                          {statusLabels[interview.status] || interview.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base font-semibold">{t('dashboard.recentActivities')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentActivities.map((activity) => {
                  const timeAgo = formatDistanceToNow(new Date(activity.timestamp), {
                    addSuffix: true,
                    locale: dateLocale,
                  });

                  return (
                    <div
                      key={activity.id}
                      className="-mx-2 flex cursor-pointer gap-3 rounded border-b px-2 py-2 transition-colors hover:bg-gray-50 last:border-0"
                    >
                      <div className="mt-1 rounded-full bg-gray-100 p-2">
                        <History className="h-4 w-4" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">{t(`activities.${activity.type}`)}</p>
                        <p className="text-xs text-muted-foreground">{activity.description}</p>
                        <p className="mt-1 text-xs text-muted-foreground">{timeAgo}</p>
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
