'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, CheckCircle, RotateCcw, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

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
  available_transitions: Array<{ status: string; label: string }>;
  resume_url?: string;
  resume_parsed_data?: Record<string, unknown>;
  source?: string;
  applied_at: string;
  last_status_change_at?: string;
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
  new: { status: 'sent_to_interviewer', label: '下一阶段：HR筛选通过，推送用人部门', reason: 'HR筛选通过' },
  sent_to_interviewer: { status: 'interview_intention_communication', label: '下一阶段：面试官筛选通过，进入意向沟通', reason: '面试官筛选通过' },
  interview_intention_communication: { status: 'interview_time_confirming', label: '下一阶段：候选人同意面试', reason: '候选人同意面试' },
  interview_time_confirming: { status: 'department_interview_scheduled', label: '下一阶段：已约定面试时间', reason: '已约定面试时间' },
  department_interview_scheduled: { status: 'department_interviewing', label: '下一阶段：进入面试', reason: '进入面试' },
  department_interviewing: { status: 'department_interview_completed', label: '下一阶段：面试通过', reason: '面试通过' },
  offer_accepted: { status: 'pending_onboard', label: '下一阶段：待入职', reason: '候选人接受Offer' },
  pending_onboard: { status: 'onboarded', label: '下一阶段：已入职', reason: '已入职' },
};

const rejectStatusByCurrent: Record<string, { status: string; label: string; reason: string }> = {
  new: { status: 'hr_rejected', label: '淘汰：HR筛选未通过', reason: 'HR筛选未通过' },
  sent_to_interviewer: { status: 'interviewer_rejected', label: '淘汰：面试官筛选未通过', reason: '面试官筛选未通过' },
  interview_intention_communication: { status: 'candidate_declined_interview', label: '候选人放弃面试', reason: '候选人放弃面试' },
  interview_time_confirming: { status: 'candidate_declined_interview', label: '候选人放弃面试', reason: '候选人放弃面试' },
  department_interview_scheduled: { status: 'department_interview_rejected', label: '淘汰：面试失败', reason: '面试失败' },
  department_interviewing: { status: 'department_interview_rejected', label: '淘汰：面试失败', reason: '面试失败' },
};

function formatValue(value: unknown) {
  if (Array.isArray(value)) return value.join('、');
  if (typeof value === 'object' && value !== null) return JSON.stringify(value, null, 2);
  if (value === null || value === undefined || value === '') return '-';
  return String(value);
}

export default function CandidateDetailPage() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const applicationId = params.id;
  const [application, setApplication] = useState<ApplicationDetail | null>(null);
  const [history, setHistory] = useState<StatusHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

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

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchApplication();
    fetchHistory();
  }, [fetchApplication, fetchHistory]);

  const nextAction = application ? nextStatusByCurrent[application.status] : undefined;
  const rejectAction = application ? rejectStatusByCurrent[application.status] : undefined;

  const resumeEntries = useMemo(() => {
    if (!application?.resume_parsed_data) return [];
    return Object.entries(application.resume_parsed_data).filter(([key]) => !['resume_url', 'resume_text'].includes(key));
  }, [application]);

  const transitionTo = async (status: string, reason: string) => {
    setActionLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/applications/${applicationId}/transition-status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ to_status: status, reason }),
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
                应聘职位：{application.job.title} · 投递时间：{new Date(application.applied_at).toLocaleString('zh-CN')}
              </div>
            </div>

            <div className="flex flex-wrap justify-end gap-2">
              {nextAction && (
                <Button disabled={actionLoading} onClick={() => transitionTo(nextAction.status, nextAction.reason)} className="gap-2">
                  <CheckCircle className="h-4 w-4" />
                  下一阶段
                </Button>
              )}
              {rejectAction && (
                <Button disabled={actionLoading} variant="destructive" onClick={() => transitionTo(rejectAction.status, rejectAction.reason)} className="gap-2">
                  <XCircle className="h-4 w-4" />
                  淘汰
                </Button>
              )}
              <Button disabled={actionLoading || history.length === 0} variant="outline" onClick={undoLastAction} className="gap-2">
                <RotateCcw className="h-4 w-4" />
                撤销
              </Button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-1 space-y-6">
            <Card className="p-6">
              <h2 className="mb-4 text-lg font-semibold">基本信息</h2>
              <div className="space-y-3 text-sm">
                <div><span className="text-gray-500">手机号：</span>{application.candidate.phone || '-'}</div>
                <div><span className="text-gray-500">邮箱：</span>{application.candidate.email || '-'}</div>
                <div><span className="text-gray-500">当前职位：</span>{application.candidate.current_position || '-'}</div>
                <div><span className="text-gray-500">工作年限：</span>{application.candidate.work_years ?? '-'} 年</div>
                <div><span className="text-gray-500">来源：</span>{application.source || '-'}</div>
              </div>
            </Card>

            <Card className="p-6">
              <h2 className="mb-4 text-lg font-semibold">流程状态</h2>
              <div className="space-y-2 text-sm">
                <div><span className="text-gray-500">当前状态：</span>{application.status_label}</div>
                {nextAction && <div><span className="text-gray-500">下一步：</span>{nextAction.label}</div>}
                {rejectAction && <div><span className="text-gray-500">淘汰动作：</span>{rejectAction.label}</div>}
              </div>
            </Card>
          </div>

          <div className="col-span-2">
            <Tabs defaultValue="resume" className="w-full">
              <TabsList>
                <TabsTrigger value="resume">查看简历</TabsTrigger>
                <TabsTrigger value="history">操作记录</TabsTrigger>
              </TabsList>

              <TabsContent value="resume" className="mt-6">
                <Card className="p-6">
                  <h2 className="mb-4 text-lg font-semibold">解析后的简历详情</h2>
                  {resumeEntries.length === 0 ? (
                    <div className="py-8 text-center text-gray-500">暂无解析结果</div>
                  ) : (
                    <div className="space-y-4">
                      {resumeEntries.map(([key, value]) => (
                        <div key={key} className="border-b pb-3 last:border-b-0">
                          <div className="mb-1 text-sm font-medium text-gray-500">{key}</div>
                          <div className="whitespace-pre-wrap text-sm text-gray-900">{formatValue(value)}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </Card>
              </TabsContent>

              <TabsContent value="history" className="mt-6">
                <Card className="p-6">
                  {history.length === 0 ? (
                    <div className="py-8 text-center text-gray-500">暂无操作记录</div>
                  ) : (
                    <div className="space-y-4">
                      {history.map((item) => (
                        <div key={item.id} className="rounded-lg border p-4">
                          <div className="font-medium">{item.to_status_label}</div>
                          <div className="mt-1 text-sm text-gray-500">
                            {item.reason || '-'} · {item.operator_name || '系统'} · {item.created_at ? new Date(item.created_at).toLocaleString('zh-CN') : '-'}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </div>
  );
}
