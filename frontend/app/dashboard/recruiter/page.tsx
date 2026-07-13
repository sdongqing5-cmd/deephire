'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';
import { MainLayout } from '@/components/layout/main-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { RecommendDialog } from '@/components/recruiter/recommend-dialog';
import { CommunicationDialog } from '@/components/recruiter/communication-dialog';
import { mockClients } from '@/lib/mock/clients';
import { mockClientJobs, type ClientJob } from '@/lib/mock/client-jobs';
import { mockRecommendations, getRecommendationStats, getRecommendationsByClient, type Recommendation } from '@/lib/mock/recommendations';
import { mockCandidates } from '@/lib/mock/candidates';
import {
  Building2,
  Briefcase,
  TrendingUp,
  DollarSign,
  Users,
  Calendar,
  Download,
  RefreshCw,
  MessageSquare,
  Search,
} from 'lucide-react';

export default function RecruiterDashboardPage() {
  const t = useTranslations();
  const router = useRouter();
  const [selectedClientId, setSelectedClientId] = useState(mockClients[0].id);
  const [recommendDialogOpen, setRecommendDialogOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState<ClientJob | null>(null);
  const [localRecommendations, setLocalRecommendations] = useState(mockRecommendations);
  const [communicationDialogOpen, setCommunicationDialogOpen] = useState(false);
  const [selectedRecommendation, setSelectedRecommendation] = useState<Recommendation | null>(null);

  // Get selected client
  const selectedClient = mockClients.find(c => c.id === selectedClientId);

  // Get client's jobs
  const clientJobs = mockClientJobs.filter(job => job.clientId === selectedClientId);
  const recruitingJobs = clientJobs.filter(job => job.status === 'recruiting');
  const closedJobs = clientJobs.filter(job => job.status === 'closed');

  // Get client's recommendations (use local state)
  const clientRecommendations = localRecommendations.filter(r => r.clientId === selectedClientId);
  const stats = getRecommendationStats(clientRecommendations);

  // Overall stats (use local state)
  const activeClients = mockClients.filter(c => c.status === 'active').length;
  const ongoingRecommendations = localRecommendations.filter(
    r => r.status === 'pending' || r.status === 'hr_reviewing' || r.status === 'interview_scheduled'
  ).length;
  const successfulThisMonth = localRecommendations.filter(r => {
    if (r.status !== 'accepted') return false;
    const date = new Date(r.updatedAt);
    const now = new Date();
    return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear();
  }).length;
  const totalCommission = localRecommendations
    .filter(r => r.commission && r.commission.status === 'paid')
    .reduce((sum, r) => sum + (r.commission?.amount || 0), 0);

  // Handle recommendation submission
  const handleRecommendClick = (job: ClientJob) => {
    setSelectedJob(job);
    setRecommendDialogOpen(true);
  };

  const handleSubmitRecommendation = async (candidateId: string, notes: string) => {
    // Create new recommendation
    const newRecommendation = {
      id: `rec-new-${Date.now()}`,
      recruiterId: 'recruiter-1',
      recruiterName: '张猎头',
      clientId: selectedClientId,
      jobId: selectedJob!.id,
      candidateId,
      status: 'pending' as const,
      hrStatus: 'pending' as const,
      hunterType: 'headhunter' as const,
      notes,
      timeline: [
        {
          id: `evt-${Date.now()}`,
          type: 'submitted' as const,
          actor: '张猎头',
          actorRole: 'recruiter' as const,
          notes: '提交推荐',
          timestamp: new Date().toISOString(),
        },
      ],
      resumeUrl: `/resumes/candidate-${candidateId}.pdf`,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    // Add to local state
    setLocalRecommendations([newRecommendation, ...localRecommendations]);
  };

  // Handle communication
  const handleCommunicationClick = (recommendation: Recommendation) => {
    setSelectedRecommendation(recommendation);
    setCommunicationDialogOpen(true);
  };

  const handleSendMessage = async (message: string) => {
    if (!selectedRecommendation) return;

    // Create new event
    const newEvent = {
      id: `evt-msg-${Date.now()}`,
      type: 'submitted' as const,
      actor: '张猎头',
      actorRole: 'recruiter' as const,
      notes: message,
      timestamp: new Date().toISOString(),
    };

    // Update recommendation timeline
    const updatedRecommendations = localRecommendations.map((rec) => {
      if (rec.id === selectedRecommendation.id) {
        return {
          ...rec,
          timeline: [...rec.timeline, newEvent],
          updatedAt: new Date().toISOString(),
        };
      }
      return rec;
    });

    setLocalRecommendations(updatedRecommendations);

    // Update selected recommendation for dialog
    const updatedRec = updatedRecommendations.find(r => r.id === selectedRecommendation.id);
    if (updatedRec) {
      setSelectedRecommendation(updatedRec);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'recruiting':
        return <Badge className="bg-blue-100 text-blue-800">{t('headhunter.recruiting')}</Badge>;
      case 'closed':
        return <Badge className="bg-gray-100 text-gray-800">{t('headhunter.closed')}</Badge>;
      case 'paused':
        return <Badge className="bg-yellow-100 text-yellow-800">{t('headhunter.paused')}</Badge>;
      default:
        return null;
    }
  };

  const getHrStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge variant="outline">{t('headhunter.notResponded')}</Badge>;
      case 'viewed':
        return <Badge className="bg-blue-100 text-blue-800">{t('headhunter.hrViewed')}</Badge>;
      case 'approved':
        return <Badge className="bg-green-100 text-green-800">{t('headhunter.hrApproved')}</Badge>;
      case 'rejected':
        return <Badge className="bg-red-100 text-red-800">{t('headhunter.hrRejected')}</Badge>;
      default:
        return null;
    }
  };

  return (
    <MainLayout requiredPath="/dashboard/recruiter">
      <div className="space-y-6">
        {/* Page Title */}
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t('dashboard.recruiterDashboard')}</h1>
        </div>

        {/* Overall Statistics */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">
                    {t('headhunter.activeClients')}
                  </p>
                  <p className="mt-2 text-2xl font-bold">{activeClients}</p>
                </div>
                <div className="rounded-full bg-blue-100 p-3">
                  <Building2 className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">
                    {t('headhunter.ongoingRecommendations')}
                  </p>
                  <p className="mt-2 text-2xl font-bold">{ongoingRecommendations}</p>
                </div>
                <div className="rounded-full bg-orange-100 p-3">
                  <TrendingUp className="h-6 w-6 text-orange-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">
                    {t('headhunter.successfulThisMonth')}
                  </p>
                  <p className="mt-2 text-2xl font-bold">{successfulThisMonth}</p>
                </div>
                <div className="rounded-full bg-green-100 p-3">
                  <Users className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">
                    {t('headhunter.totalCommission')}
                  </p>
                  <p className="mt-2 text-2xl font-bold">¥{(totalCommission / 10000).toFixed(1)}万</p>
                </div>
                <div className="rounded-full bg-purple-100 p-3">
                  <DollarSign className="h-6 w-6 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Client Selector */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-semibold">{t('headhunter.selectClient')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              {mockClients.map((client) => (
                <Button
                  key={client.id}
                  variant={selectedClientId === client.id ? 'default' : 'outline'}
                  onClick={() => setSelectedClientId(client.id)}
                  className="h-auto py-3"
                >
                  <div className="flex items-center gap-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-sm font-semibold">
                      {client.logo}
                    </div>
                    <span>{client.name}</span>
                  </div>
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Client Info */}
        {selectedClient && (
          <Card>
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <div className="flex h-16 w-16 items-center justify-center rounded-lg bg-gray-100 text-2xl font-bold">
                    {selectedClient.logo}
                  </div>
                  <div>
                    <h2 className="text-xl font-bold">{selectedClient.name}</h2>
                    <p className="text-sm text-muted-foreground mt-1">
                      {t('headhunter.announcement')}: {selectedClient.announcement || t('headhunter.noAnnouncement')}
                    </p>
                  </div>
                </div>
                <div className="flex gap-8">
                  <div className="text-center">
                    <p className="text-2xl font-bold">{clientJobs.length}</p>
                    <p className="text-sm text-muted-foreground">{t('headhunter.recruitingPositions')}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold">{clientRecommendations.length}</p>
                    <p className="text-sm text-muted-foreground">{t('headhunter.recommendationRecords')}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Tabs: Positions and Recommendations */}
        <Tabs defaultValue="positions" className="w-full">
          <TabsList>
            <TabsTrigger value="positions">{t('headhunter.positions')}</TabsTrigger>
            <TabsTrigger value="recommendations">{t('headhunter.recommendations')}</TabsTrigger>
          </TabsList>

          {/* Positions Tab */}
          <TabsContent value="positions" className="mt-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base font-semibold">{t('headhunter.recruitingPositions')}</CardTitle>
                  <div className="flex gap-2">
                    <Badge className="bg-blue-100 text-blue-800">
                      {t('headhunter.recruiting')} {recruitingJobs.length}
                    </Badge>
                    <Badge className="bg-gray-100 text-gray-800">
                      {t('headhunter.closed')} {closedJobs.length}
                    </Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {clientJobs.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-12 text-center">
                    <Briefcase className="h-12 w-12 text-gray-400 mb-4" />
                    <p className="text-sm font-medium text-gray-900">{t('headhunter.noPositions')}</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-3 px-4 text-sm font-semibold">{t('headhunter.positionName')}</th>
                          <th className="text-left py-3 px-4 text-sm font-semibold">{t('headhunter.positionOwner')}</th>
                          <th className="text-left py-3 px-4 text-sm font-semibold">{t('headhunter.recommendedCount')}</th>
                          <th className="text-left py-3 px-4 text-sm font-semibold">{t('headhunter.updateTime')}</th>
                          <th className="text-left py-3 px-4 text-sm font-semibold">{t('headhunter.recruitmentType')}</th>
                          <th className="text-left py-3 px-4 text-sm font-semibold">{t('headhunter.operations')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {clientJobs.map((job) => (
                          <tr key={job.id} className="border-b hover:bg-gray-50">
                            <td className="py-3 px-4">
                              <button className="text-sm font-medium text-blue-600 hover:underline">
                                {job.titleKey ? t(`jobs.${job.titleKey}`) : job.title}
                              </button>
                            </td>
                            <td className="py-3 px-4 text-sm">{job.hrOwner}</td>
                            <td className="py-3 px-4">
                              <span className="text-sm text-blue-600 font-medium">{job.recommendationCount}</span>
                            </td>
                            <td className="py-3 px-4 text-sm text-muted-foreground">
                              {new Date(job.updatedAt).toLocaleDateString()}
                            </td>
                            <td className="py-3 px-4">
                              {getStatusBadge(job.status)}
                            </td>
                            <td className="py-3 px-4">
                              <div className="flex gap-2">
                                <Button
                                  size="sm"
                                  variant="link"
                                  className="text-blue-600 h-auto p-0"
                                  onClick={() => handleRecommendClick(job)}
                                >
                                  {t('headhunter.recommendCandidate')}
                                </Button>
                                <Button size="sm" variant="link" className="text-gray-600 h-auto p-0">
                                  {t('headhunter.follow')}
                                </Button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Recommendations Tab */}
          <TabsContent value="recommendations" className="mt-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base font-semibold">{t('headhunter.recommendationRecords')}</CardTitle>
                  <div className="flex gap-2">
                    <Badge className="bg-blue-100 text-blue-800">
                      {t('headhunter.pending')} {stats.pending}
                    </Badge>
                    <Badge className="bg-green-100 text-green-800">
                      {t('headhunter.success')} {stats.success}
                    </Badge>
                    <Badge className="bg-red-100 text-red-800">
                      {t('headhunter.failed')} {stats.failed}
                    </Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {/* Filters */}
                <div className="mb-4 flex flex-wrap gap-3">
                  <div className="relative flex-1 min-w-[200px]">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      placeholder={t('headhunter.searchCandidateName')}
                      className="w-full rounded-md border border-gray-300 py-2 pl-10 pr-4 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                </div>

                {clientRecommendations.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-12 text-center">
                    <Calendar className="h-12 w-12 text-gray-400 mb-4" />
                    <p className="text-sm font-medium text-gray-900">{t('headhunter.noRecommendations')}</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-3 px-4 text-sm font-semibold">{t('headhunter.candidateName')}</th>
                          <th className="text-left py-3 px-4 text-sm font-semibold">{t('headhunter.email')}</th>
                          <th className="text-left py-3 px-4 text-sm font-semibold">{t('headhunter.position')}</th>
                          <th className="text-left py-3 px-4 text-sm font-semibold">{t('headhunter.recruitmentType')}</th>
                          <th className="text-left py-3 px-4 text-sm font-semibold">{t('headhunter.companyStatus')}</th>
                          <th className="text-left py-3 px-4 text-sm font-semibold">{t('headhunter.recommendTime')}</th>
                          <th className="text-left py-3 px-4 text-sm font-semibold">{t('headhunter.operations')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {clientRecommendations.map((rec) => {
                          const candidate = mockCandidates.find(c => c.id === rec.candidateId);
                          const job = mockClientJobs.find(j => j.id === rec.jobId);

                          return (
                            <tr key={rec.id} className="border-b hover:bg-gray-50">
                              <td className="py-3 px-4 text-sm font-medium">{candidate?.name}</td>
                              <td className="py-3 px-4 text-sm text-muted-foreground">{candidate?.email}</td>
                              <td className="py-3 px-4 text-sm">
                                {job?.titleKey ? t(`jobs.${job.titleKey}`) : job?.title}
                              </td>
                              <td className="py-3 px-4">
                                <Badge variant="outline">{t('headhunter.socialRecruitment')}</Badge>
                              </td>
                              <td className="py-3 px-4">
                                {getHrStatusBadge(rec.hrStatus)}
                              </td>
                              <td className="py-3 px-4 text-sm text-muted-foreground">
                                {new Date(rec.createdAt).toLocaleDateString()}
                              </td>
                              <td className="py-3 px-4">
                                <div className="flex gap-2">
                                  <Button size="sm" variant="link" className="text-blue-600 h-auto p-0">
                                    <Download className="h-3 w-3 mr-1" />
                                    {t('headhunter.downloadResume')}
                                  </Button>
                                  <Button size="sm" variant="link" className="text-blue-600 h-auto p-0">
                                    <RefreshCw className="h-3 w-3 mr-1" />
                                    {t('headhunter.updateResume')}
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="link"
                                    className="text-blue-600 h-auto p-0"
                                    onClick={() => handleCommunicationClick(rec)}
                                  >
                                    <MessageSquare className="h-3 w-3 mr-1" />
                                    {t('headhunter.contactHR')}
                                  </Button>
                                </div>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Recommend Dialog */}
        <RecommendDialog
          open={recommendDialogOpen}
          onOpenChange={setRecommendDialogOpen}
          job={selectedJob}
          onSubmit={handleSubmitRecommendation}
        />

        {/* Communication Dialog */}
        <CommunicationDialog
          open={communicationDialogOpen}
          onOpenChange={setCommunicationDialogOpen}
          recommendation={selectedRecommendation}
          onSendMessage={handleSendMessage}
        />
      </div>
    </MainLayout>
  );
}
