'use client';

import { useCallback, useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { AlertTriangle, ArrowLeft, Briefcase, CheckCircle, Clock, History, RotateCcw, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { useAuthStore } from '@/stores/auth-store';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';

interface ApplicationDetail {
  id: string;
  candidate: {
    id: string;
    name: string;
    phone?: string;
    email?: string;
    current_company?: string;
    current_position?: string;
    work_years?: number;
  };
  job: {
    id: string;
    title: string;
    department?: string;
  };
  status: string;
  status_label: string;
  rejection_reason?: string;
  interviewer_evaluation?: string;
  available_transitions: Array<{ status: string; label: string }>;
  resume_url?: string;
  resume_parsed_data?: Record<string, unknown>;
  source?: string;
  applied_at: string;
  last_status_change_at?: string;
}

interface JobOption {
  id: string;
  title: string;
}

interface StatusHistoryItem {
  id: string;
  from_status?: string;
  to_status: string;
  to_status_label: string;
  reason?: string;
  operator_name?: string;
  created_at?: string;
}

const nextStatusByCurrent: Record<string, { status: string; label: string; reason: string }> = {
  new: { status: 'sent_to_interviewer', label: 'HR筛选通过，推送用人部门', reason: 'HR筛选通过' },
  sent_to_interviewer: { status: 'interview_intention_communication', label: '面试官筛选通过，进入意向沟通', reason: '面试官筛选通过' },
  interviewer_hold: { status: 'interview_intention_communication', label: '面试官筛选通过，进入意向沟通', reason: '面试官筛选通过' },
  interview_intention_communication: { status: 'interview_time_confirming', label: '候选人同意面试', reason: '候选人同意面试' },
  interview_time_confirming: { status: 'department_interview_scheduled', label: '已约定面试时间', reason: '已约定面试时间' },
  department_interview_scheduled: { status: 'department_interviewing', label: '进入面试', reason: '进入面试' },
  department_interviewing: { status: 'department_interview_completed', label: '部门面试通过', reason: '部门面试通过' },
  offer_accepted: { status: 'pending_onboard', label: '待入职', reason: '候选人接受Offer' },
  pending_onboard: { status: 'onboarded', label: '已入职', reason: '已入职' },
};

const rejectStatusByCurrent: Record<string, { status: string; label: string; reason: string }> = {
  new: { status: 'hr_rejected', label: '淘汰：HR筛选未通过', reason: 'HR筛选未通过' },
  sent_to_interviewer: { status: 'interviewer_rejected', label: '淘汰：面试官筛选未通过', reason: '面试官筛选未通过' },
  interviewer_hold: { status: 'interviewer_rejected', label: '淘汰：面试官筛选未通过', reason: '面试官筛选未通过' },
  interview_intention_communication: { status: 'candidate_declined_interview', label: '候选人放弃面试', reason: '候选人放弃面试' },
  interview_time_confirming: { status: 'candidate_declined_interview', label: '候选人放弃面试', reason: '候选人放弃面试' },
  department_interview_scheduled: { status: 'department_interview_rejected', label: '淘汰：面试失败', reason: '面试失败' },
  department_interviewing: { status: 'department_interview_rejected', label: '淘汰：面试失败', reason: '面试失败' },
};

function getResumeText(parsedData?: Record<string, unknown>) {
  const text = parsedData?.resume_text;
  return typeof text === 'string' ? text : '';
}

function getResumeFileUrl(resumeUrl?: string) {
  if (!resumeUrl) return null;
  if (resumeUrl.startsWith('http')) return resumeUrl;

  const normalizedPath = resumeUrl.startsWith('/') ? resumeUrl : `/${resumeUrl}`;
  return `${process.env.NEXT_PUBLIC_API_URL}${normalizedPath}`;
}

export default function CandidateDetailPage() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const applicationId = params.id;
  const user = useAuthStore((state) => state.user);
  const [application, setApplication] = useState<ApplicationDetail | null>(null);
  const [history, setHistory] = useState<StatusHistoryItem[]>([]);
  const [jobs, setJobs] = useState<JobOption[]>([]);
  const [transferJobId, setTransferJobId] = useState('');
  const [transferReason, setTransferReason] = useState('');
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState('');

  const fetchApplication = useCallback(async () => {
    try {
      if (!applicationId) return;

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/applications/${applicationId}`);
      if (response.ok) {
        const result = await response.json();
        setApplication(result.data);
      }
    } catch (error) {
      console.error('Failed to fetch application:', error);
    } finally {
      setLoading(false);
    }
  }, [applicationId]);

  const fetchHistory = useCallback(async () => {
    if (!applicationId) return;

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/applications/${applicationId}/status-history`);
    if (response.ok) {
      const result = await response.json();
      setHistory(result.data.items || []);
    }
  }, [applicationId]);

  const fetchJobs = useCallback(async () => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs?status=recruiting&limit=100`);
    if (response.ok) {
      const result = await response.json();
      setJobs(result.filter((job: JobOption) => job.id !== application?.job.id));
    }
  }, [application?.job.id]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchApplication();
    fetchHistory();
  }, [fetchApplication, fetchHistory]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchJobs();
  }, [fetchJobs]);

  const nextAction = application ? nextStatusByCurrent[application.status] : undefined;
  const rejectAction = application ? rejectStatusByCurrent[application.status] : undefined;
  const canUndo = application
    ? [
        'new',
        'sent_to_interviewer',
        'interviewer_hold',
        'interviewer_rejected',
        'interview_intention_communication',
      ].includes(application.status)
    : false;
  const canTransfer = user?.role === 'hr' || user?.role === 'recruiter';

  const resumeText = getResumeText(application?.resume_parsed_data);
  const resumeFileUrl = getResumeFileUrl(application?.resume_url);

  const transitionTo = async (status: string, reason: string, interviewerEvaluation?: string) => {
    setActionLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/applications/${applicationId}/transition-status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ to_status: status, reason, interviewer_evaluation: interviewerEvaluation }),
      });

      if (response.ok) {
        await fetchApplication();
        await fetchHistory();
      } else {
        const error = await response.json();
        alert(`操作失败: ${error.detail || '未知错误'}`);
      }
    } catch {
      alert('操作失败，请稍后重试');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!rejectAction) return;
    setRejectReason(application?.rejection_reason || rejectAction.reason);
    setRejectDialogOpen(true);
  };

  const confirmReject = async () => {
    if (!rejectAction) return;
    await transitionTo(rejectAction.status, rejectReason.trim() || rejectAction.reason);
    setRejectDialogOpen(false);
  };

  const handleInterviewerPass = async () => {
    const evaluation = window.prompt('请输入候选人评价：', application?.interviewer_evaluation || '');
    if (evaluation === null) return;
    await transitionTo('interview_intention_communication', '面试官筛选通过', evaluation);
  };

  const handleInterviewerHold = async () => {
    const evaluation = application?.interviewer_evaluation || '';
    await transitionTo('interviewer_hold', evaluation || '面试官待定', evaluation);
  };

  const transferToJob = async () => {
    if (!transferJobId) {
      alert('请选择目标职位');
      return;
    }
    setActionLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/applications/${applicationId}/transfer-job`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_job_id: transferJobId, reason: transferReason }),
      });
      if (response.ok) {
        const result = await response.json();
        alert('转推成功');
        router.push(`/candidates/${result.data.application_id}`);
      } else {
        const error = await response.json();
        alert(`转推失败: ${error.detail || '未知错误'}`);
      }
    } catch {
      alert('转推失败，请稍后重试');
    } finally {
      setActionLoading(false);
    }
  };

  const undoLastAction = async () => {
    setActionLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/applications/${applicationId}/undo`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: '操作失误，撤销上一步' }),
      });

      if (response.ok) {
        await fetchApplication();
        await fetchHistory();
      } else {
        const error = await response.json();
        alert(`撤销失败: ${error.detail || '没有可撤销的操作'}`);
      }
    } catch {
      alert('撤销失败，请稍后重试');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-b-2 border-primary"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  if (!application) {
    return (
      <div className="p-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold">简历记录不存在</h2>
          <Button onClick={() => router.push('/candidates')} className="mt-4">
            返回候选人列表
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6">
          <Button variant="ghost" onClick={() => router.back()} className="mb-4 -ml-2">
            <ArrowLeft className="mr-2 h-4 w-4" />
            返回
          </Button>

          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="mb-2 flex items-center gap-3">
                <h1 className="text-3xl font-bold text-gray-900">{application.candidate.name}</h1>
                <Badge>{application.status_label}</Badge>
              </div>
              <div className="text-sm text-gray-600">
                应聘职位：{application.job.title} · 上传时间：{new Date(application.applied_at).toLocaleString('zh-CN')}
              </div>
            </div>

            <div className="flex flex-wrap justify-end gap-2">
              {application.status === 'sent_to_interviewer' ? (
                <>
                  <Button disabled={actionLoading} onClick={handleInterviewerPass} className="gap-2">
                    <CheckCircle className="h-4 w-4" />
                    通过
                  </Button>
                  <Button disabled={actionLoading} variant="outline" onClick={handleInterviewerHold} className="gap-2">
                    <Clock className="h-4 w-4" />
                    待定
                  </Button>
                </>
              ) : nextAction && (
                <Button disabled={actionLoading} onClick={() => transitionTo(nextAction.status, nextAction.reason)} className="gap-2">
                  <CheckCircle className="h-4 w-4" />
                  通过
                </Button>
              )}
              {rejectAction && (
                <Button disabled={actionLoading} variant="destructive" onClick={handleReject} className="gap-2">
                  <XCircle className="h-4 w-4" />
                  淘汰
                </Button>
              )}
              <Dialog
                open={rejectDialogOpen}
                onOpenChange={(open) => {
                  setRejectDialogOpen(open);
                  if (!open) setRejectReason('');
                }}
              >
                <DialogContent className="overflow-hidden p-0 sm:max-w-[460px]">
                  <DialogHeader className="border-b bg-white px-6 pb-5 pr-12 pt-6 text-left">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-red-50 text-red-600">
                        <AlertTriangle className="h-5 w-5" />
                      </div>
                      <div className="space-y-1">
                        <DialogTitle className="text-base font-semibold text-slate-900">确认淘汰候选人</DialogTitle>
                        <DialogDescription className="text-sm leading-5 text-slate-500">
                          淘汰后将离开当前筛选流程，可通过撤销恢复。
                        </DialogDescription>
                      </div>
                    </div>
                  </DialogHeader>
                  <div className="space-y-5 bg-white px-6 py-6">
                    <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
                      <div className="mb-1 text-xs font-medium text-slate-500">当前候选人</div>
                      <div className="flex items-center gap-2 text-sm">
                        <span className="font-semibold text-slate-900">{application.candidate.name}</span>
                        <span className="text-slate-300">/</span>
                        <span className="truncate text-slate-600">{application.job.title}</span>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label htmlFor="reject-reason" className="text-sm font-medium text-slate-900">
                        淘汰原因
                      </label>
                      <Textarea
                        id="reject-reason"
                        value={rejectReason}
                        onChange={(event) => setRejectReason(event.target.value)}
                        placeholder="请输入具体原因，便于后续复盘"
                        rows={4}
                        autoFocus
                        className="resize-none border-slate-300 bg-white leading-6 focus-visible:ring-red-500"
                      />
                    </div>
                  </div>
                  <DialogFooter className="border-t bg-slate-50 px-6 py-4 sm:space-x-3">
                    <Button
                      type="button"
                      variant="outline"
                      disabled={actionLoading}
                      onClick={() => setRejectDialogOpen(false)}
                    >
                      取消
                    </Button>
                    <Button
                      type="button"
                      variant="destructive"
                      disabled={actionLoading}
                      onClick={confirmReject}
                    >
                      {actionLoading ? '提交中...' : '确认淘汰'}
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
              {canTransfer && (
                <Dialog>
                  <DialogTrigger asChild>
                    <Button variant="outline" className="gap-2">
                      <Briefcase className="h-4 w-4" />
                      转推职位
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-xl">
                    <DialogHeader>
                      <DialogTitle>转推到其他职位</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4">
                      <select
                        className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
                        value={transferJobId}
                        onChange={(event) => setTransferJobId(event.target.value)}
                      >
                        <option value="">选择目标职位</option>
                        {jobs.map((job) => (
                          <option key={job.id} value={job.id}>{job.title}</option>
                        ))}
                      </select>
                      <Textarea
                        rows={4}
                        value={transferReason}
                        onChange={(event) => setTransferReason(event.target.value)}
                        placeholder="转推原因"
                      />
                      <div className="flex justify-end">
                        <Button disabled={actionLoading} onClick={transferToJob}>确认转推</Button>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
              )}
              <Button disabled={!canUndo || actionLoading || history.length === 0} variant="outline" onClick={undoLastAction} className="gap-2">
                <RotateCcw className="h-4 w-4" />
                撤销
              </Button>
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="outline" className="gap-2">
                    <History className="h-4 w-4" />
                    操作记录
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-2xl">
                  <DialogHeader>
                    <DialogTitle>操作记录</DialogTitle>
                  </DialogHeader>
                  {history.length === 0 ? (
                    <div className="py-8 text-center text-gray-500">暂无操作记录</div>
                  ) : (
                    <div className="max-h-[60vh] space-y-3 overflow-auto">
                      {history.map((item) => (
                        <div key={item.id} className="rounded-md border p-4">
                          <div className="font-medium">{item.to_status_label}</div>
                          <div className="mt-1 text-sm text-gray-500">
                            {item.reason || '-'} · {item.operator_name || '系统'} · {item.created_at ? new Date(item.created_at).toLocaleString('zh-CN') : '-'}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-4 space-y-6">
            <Card className="p-6">
              <h2 className="mb-4 text-lg font-semibold">基本信息</h2>
              <div className="space-y-3 text-sm">
                <div><span className="text-gray-500">手机号：</span>{application.candidate.phone || '-'}</div>
                <div><span className="text-gray-500">邮箱：</span>{application.candidate.email || '-'}</div>
                <div><span className="text-gray-500">当前职位：</span>{application.candidate.current_position || '无'}</div>
                <div><span className="text-gray-500">工作年限：</span>{application.candidate.work_years ?? 0}年</div>
              </div>
            </Card>

            <Card className="p-6">
              <h2 className="mb-4 text-lg font-semibold">流程状态</h2>
              <div className="space-y-2 text-sm">
                <div><span className="text-gray-500">当前状态：</span>{application.status_label}</div>
                {nextAction && <div><span className="text-gray-500">下一阶段：</span>{nextAction.label}</div>}
                {application.interviewer_evaluation && (
                  <div><span className="text-gray-500">候选人评价：</span>{application.interviewer_evaluation}</div>
                )}
                {application.rejection_reason && (
                  <div><span className="text-gray-500">原因：</span>{application.rejection_reason}</div>
                )}
              </div>
            </Card>
          </div>

          <div className="col-span-8">
            <div className="h-[78vh] overflow-hidden bg-white">
              {resumeFileUrl ? (
                <iframe
                  src={resumeFileUrl}
                  title="简历文件"
                  className="h-full w-full border-0"
                />
              ) : resumeText ? (
                <pre className="h-full overflow-auto whitespace-pre-wrap bg-gray-50 p-4 text-sm leading-6 text-gray-900">
                  {resumeText}
                </pre>
              ) : (
                <div className="flex h-full items-center justify-center text-gray-500">
                  暂无简历文件
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
