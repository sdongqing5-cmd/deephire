'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, CalendarPlus, Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface ApplicationItem {
  id: string;
  candidate: {
    id: string;
    name: string;
    email?: string;
    phone?: string;
  };
  job: {
    id: string;
    title: string;
  };
  status: string;
  status_label: string;
}

const interviewTypes = [
  { value: 'hr_initial', label: '初试 / HR初筛', scorecard: '社招-HR初筛评价表' },
  { value: 'department', label: '复试 / 用人部门面试', scorecard: '用人部门面试评价表' },
  { value: 'hr_reinterview', label: '复试 / HR复试', scorecard: '社招-HR初筛评价表' },
  { value: 'final', label: '终试 / 终面官面试', scorecard: '终面官面试评价表' },
];

const schedulableStatuses = [
  'interview_intention_communication',
  'interview_time_confirming',
  'hr_screening',
  'hr_interview_completed',
  'department_interview_completed',
  'assessment_completed',
  'hr_reinterview_completed',
  'final_interview_scheduled',
];

export default function NewInterviewPage() {
  const router = useRouter();
  const [applications, setApplications] = useState<ApplicationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    application_id: '',
    interview_type: 'department',
    scorecard_template_id: '用人部门面试评价表',
    interviewer_id: '3',
    interviewer_name: 'Interviewer',
    scheduled_at: '',
    duration: '60',
    location: '',
    meeting_link: '',
  });

  const selectedApplication = useMemo(
    () => applications.find((item) => item.id === form.application_id),
    [applications, form.application_id]
  );

  const fetchApplications = useCallback(async () => {
    try {
      const batches = await Promise.all(
        schedulableStatuses.map((status) =>
          fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/applications?status=${status}&page_size=50`)
        )
      );
      const results = await Promise.all(
        batches.filter((response) => response.ok).map((response) => response.json())
      );
      const items = results.flatMap((result) => result.data?.items || []);
      const uniqueItems = Array.from(new Map(items.map((item) => [item.id, item])).values()) as ApplicationItem[];
      setApplications(uniqueItems);
      if (uniqueItems.length > 0) {
        setForm((current) => ({ ...current, application_id: current.application_id || uniqueItems[0].id }));
      }
    } catch (error) {
      console.error('Failed to fetch applications:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchApplications();
  }, [fetchApplications]);

  const updateInterviewType = (value: string) => {
    const type = interviewTypes.find((item) => item.value === value);
    setForm((current) => ({
      ...current,
      interview_type: value,
      scorecard_template_id: type?.scorecard || current.scorecard_template_id,
    }));
  };

  const submitInterview = async () => {
    if (!selectedApplication || !form.scheduled_at) {
      alert('请选择候选人并填写面试时间');
      return;
    }

    setSubmitting(true);
    try {
      const typeLabel = interviewTypes.find((item) => item.value === form.interview_type)?.label || '面试';
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/interview-management/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          application_id: selectedApplication.id,
          candidate_id: selectedApplication.candidate.id,
          job_id: selectedApplication.job.id,
          interviewer_id: form.interviewer_id,
          interviewer_name: form.interviewer_name,
          interview_type: form.interview_type,
          title: `${selectedApplication.candidate.name} - ${typeLabel}`,
          scorecard_template_id: form.scorecard_template_id,
          scheduled_at: new Date(form.scheduled_at).toISOString(),
          duration: Number(form.duration),
          location: form.location || undefined,
          meeting_link: form.meeting_link || undefined,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        const interviewId = result.id || result.data?.id;
        alert('面试安排已创建，并可通知候选人与面试官');
        router.push(interviewId ? `/interviews/${interviewId}` : '/interviews');
      } else {
        const error = await response.json();
        alert(`创建失败: ${error.detail || '未知错误'}`);
      }
    } catch {
      alert('创建失败，请稍后重试');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-8">
      <div className="mx-auto max-w-4xl">
        <Button variant="ghost" onClick={() => router.back()} className="mb-4 -ml-2 gap-2">
          <ArrowLeft className="h-4 w-4" />
          返回
        </Button>

        <div className="mb-6 flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-md bg-primary text-primary-foreground">
            <CalendarPlus className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">安排面试</h1>
            <p className="mt-1 text-gray-600">选择面试环节、评价表，并通知面试双方</p>
          </div>
        </div>

        <Card className="p-6">
          {loading ? (
            <div className="py-12 text-center text-gray-500">加载中...</div>
          ) : (
            <div className="grid gap-5">
              <div className="grid gap-2">
                <Label>候选人</Label>
                <Select
                  value={form.application_id}
                  onValueChange={(value) => setForm((current) => ({ ...current, application_id: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="选择候选人" />
                  </SelectTrigger>
                  <SelectContent>
                    {applications.map((item) => (
                      <SelectItem key={item.id} value={item.id}>
                        {item.candidate.name} / {item.job.title} / {item.status_label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-5 md:grid-cols-2">
                <div className="grid gap-2">
                  <Label>面试环节</Label>
                  <Select value={form.interview_type} onValueChange={updateInterviewType}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {interviewTypes.map((item) => (
                        <SelectItem key={item.value} value={item.value}>
                          {item.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label>面试评价表</Label>
                  <Input
                    value={form.scorecard_template_id}
                    onChange={(event) => setForm((current) => ({ ...current, scorecard_template_id: event.target.value }))}
                  />
                </div>
                <div className="grid gap-2">
                  <Label>面试官姓名</Label>
                  <Input
                    value={form.interviewer_name}
                    onChange={(event) => setForm((current) => ({ ...current, interviewer_name: event.target.value }))}
                  />
                </div>
                <div className="grid gap-2">
                  <Label>面试官ID</Label>
                  <Input
                    value={form.interviewer_id}
                    onChange={(event) => setForm((current) => ({ ...current, interviewer_id: event.target.value }))}
                  />
                </div>
                <div className="grid gap-2">
                  <Label>面试时间</Label>
                  <Input
                    type="datetime-local"
                    value={form.scheduled_at}
                    onChange={(event) => setForm((current) => ({ ...current, scheduled_at: event.target.value }))}
                  />
                </div>
                <div className="grid gap-2">
                  <Label>面试时长（分钟）</Label>
                  <Input
                    type="number"
                    min="15"
                    step="15"
                    value={form.duration}
                    onChange={(event) => setForm((current) => ({ ...current, duration: event.target.value }))}
                  />
                </div>
                <div className="grid gap-2">
                  <Label>面试地点</Label>
                  <Input
                    value={form.location}
                    onChange={(event) => setForm((current) => ({ ...current, location: event.target.value }))}
                    placeholder="会议室 / 城市 / 报到地点"
                  />
                </div>
                <div className="grid gap-2">
                  <Label>线上会议链接</Label>
                  <Input
                    value={form.meeting_link}
                    onChange={(event) => setForm((current) => ({ ...current, meeting_link: event.target.value }))}
                    placeholder="https://..."
                  />
                </div>
              </div>

              <div className="flex justify-end">
                <Button onClick={submitInterview} disabled={submitting || applications.length === 0} className="gap-2">
                  <Send className="h-4 w-4" />
                  保存并生成通知
                </Button>
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
