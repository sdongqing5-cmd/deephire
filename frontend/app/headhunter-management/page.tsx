'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { ArrowLeft, CheckCircle, ClipboardList, Send, UserRoundSearch, XCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { MainLayout } from '@/components/layout/main-layout';

interface JobItem {
  id: string;
  title: string;
  location: string;
  openings: number;
  status: string;
  is_third_party_headhunter_enabled?: boolean;
}

interface RecommendationItem {
  id: string;
  job_id: string;
  job_title: string;
  candidate_name: string;
  phone?: string;
  email?: string;
  resume_url?: string;
  headhunter_name?: string;
  notes?: string;
  status: string;
  hr_feedback?: string;
  created_at?: string;
}

export default function HeadhunterManagementPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<JobItem[]>([]);
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [note, setNote] = useState('');
  const [recommendationForm, setRecommendationForm] = useState({
    job_id: '',
    candidate_name: '',
    phone: '',
    email: '',
    resume_url: '',
    headhunter_name: '',
    notes: '',
  });

  const fetchJobs = useCallback(async () => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/headhunters/jobs`);
    if (response.ok) {
      const payload = await response.json();
      setJobs(payload.data || []);
    }
  }, []);

  const fetchRecommendations = useCallback(async () => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/headhunters/recommendations`);
    if (response.ok) {
      const payload = await response.json();
      setRecommendations(payload.data || []);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchJobs();
    fetchRecommendations();
  }, [fetchJobs, fetchRecommendations]);

  const headhunterJobs = useMemo(
    () => jobs.filter((job) => job.is_third_party_headhunter_enabled),
    [jobs]
  );

  const submitRecommendation = async () => {
    if (!recommendationForm.job_id || !recommendationForm.candidate_name) {
      alert('请选择职位并填写候选人姓名');
      return;
    }

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/headhunters/recommendations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(recommendationForm),
    });
    if (response.ok) {
      setRecommendationForm({
        job_id: '',
        candidate_name: '',
        phone: '',
        email: '',
        resume_url: '',
        headhunter_name: '',
        notes: '',
      });
      await fetchRecommendations();
    } else {
      const error = await response.json().catch(() => null);
      alert(`推荐失败: ${error?.detail || '请稍后重试'}`);
    }
  };

  const updateRecommendation = async (id: string, status: string) => {
    const feedback = window.prompt(status === 'approved' ? '请输入通过意见：' : '请输入拒绝原因：', '');
    if (feedback === null) return;

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/headhunters/recommendations/${id}/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, feedback }),
    });
    if (response.ok) {
      await fetchRecommendations();
    } else {
      const error = await response.json().catch(() => null);
      alert(`审核失败: ${error?.detail || '请稍后重试'}`);
    }
  };

  return (
    <MainLayout requiredPath="/headhunter-management">
    <div className="p-8">
      <Button variant="ghost" onClick={() => router.push('/dashboard')} className="mb-4 -ml-2 gap-2">
        <ArrowLeft className="h-4 w-4" />
        返回首页
      </Button>

      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">猎头管理</h1>
        <p className="mt-2 text-gray-600">管理开放给第三方猎头的职位，并处理猎头推荐</p>
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <Card className="p-5 xl:col-span-1">
          <div className="mb-4 flex items-center gap-2">
            <ClipboardList className="h-5 w-5 text-gray-500" />
            <h2 className="text-lg font-semibold">Todo 功能列表</h2>
          </div>
          <div className="space-y-3 text-sm text-gray-700">
            <div>1. HR 创建职位并开启第三方猎头</div>
            <div>2. 职位进入猎头职位池</div>
            <div>3. 猎头提交候选人推荐</div>
            <div>4. HR 审核推荐，通过或拒绝</div>
          </div>
          <Textarea
            className="mt-4"
            rows={4}
            value={note}
            onChange={(event) => setNote(event.target.value)}
            placeholder="内部协作备注"
          />
        </Card>

        <Card className="p-5 xl:col-span-2">
          <div className="mb-4 flex items-center gap-2">
            <UserRoundSearch className="h-5 w-5 text-gray-500" />
            <h2 className="text-lg font-semibold">猎头职位池</h2>
          </div>
          {headhunterJobs.length === 0 ? (
            <div className="py-10 text-center text-gray-500">暂无开启第三方猎头的职位</div>
          ) : (
            <div className="grid gap-3">
              {headhunterJobs.map((job) => (
                <div key={job.id} className="rounded-md border p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="font-semibold">{job.title}</div>
                      <div className="mt-1 text-sm text-gray-500">{job.location} · HC {job.openings}</div>
                    </div>
                    <Badge>已开放猎头</Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      <Card className="mt-6 p-5">
        <h2 className="mb-4 text-lg font-semibold">猎头推荐</h2>
        <div className="grid gap-4 md:grid-cols-3">
          <select
            className="h-10 rounded-md border border-input bg-background px-3 text-sm"
            value={recommendationForm.job_id}
            onChange={(event) => setRecommendationForm({ ...recommendationForm, job_id: event.target.value })}
          >
            <option value="">选择开放职位</option>
            {headhunterJobs.map((job) => (
              <option key={job.id} value={job.id}>{job.title}</option>
            ))}
          </select>
          <Input placeholder="候选人姓名" value={recommendationForm.candidate_name} onChange={(event) => setRecommendationForm({ ...recommendationForm, candidate_name: event.target.value })} />
          <Input placeholder="猎头名称" value={recommendationForm.headhunter_name} onChange={(event) => setRecommendationForm({ ...recommendationForm, headhunter_name: event.target.value })} />
          <Input placeholder="手机号" value={recommendationForm.phone} onChange={(event) => setRecommendationForm({ ...recommendationForm, phone: event.target.value })} />
          <Input placeholder="邮箱" value={recommendationForm.email} onChange={(event) => setRecommendationForm({ ...recommendationForm, email: event.target.value })} />
          <Input placeholder="简历附件地址" value={recommendationForm.resume_url} onChange={(event) => setRecommendationForm({ ...recommendationForm, resume_url: event.target.value })} />
          <Textarea className="md:col-span-3" rows={3} placeholder="推荐理由" value={recommendationForm.notes} onChange={(event) => setRecommendationForm({ ...recommendationForm, notes: event.target.value })} />
        </div>
        <div className="mt-4 flex justify-end">
          <Button onClick={submitRecommendation} className="gap-2">
            <Send className="h-4 w-4" />
            提交推荐
          </Button>
        </div>
      </Card>

      <Card className="mt-6 p-5">
        <h2 className="mb-4 text-lg font-semibold">推荐待处理</h2>
        <div className="grid gap-3">
          {recommendations.map((item) => (
            <div key={item.id} className="rounded-md border p-4">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <div className="font-semibold">{item.candidate_name}</div>
                    <Badge variant={item.status === 'pending' ? 'secondary' : 'outline'}>
                      {item.status === 'pending' ? 'HR待处理' : item.status === 'approved' ? '已通过' : '已拒绝'}
                    </Badge>
                  </div>
                  <div className="mt-1 text-sm text-gray-500">{item.job_title} · {item.headhunter_name || '第三方猎头'}</div>
                  <div className="mt-1 text-sm text-gray-500">{item.phone} · {item.email}</div>
                  {item.hr_feedback && <div className="mt-1 text-sm text-gray-500">HR反馈：{item.hr_feedback}</div>}
                </div>
                {item.status === 'pending' && (
                  <div className="flex gap-2">
                    <Button size="sm" onClick={() => updateRecommendation(item.id, 'approved')} className="gap-2">
                      <CheckCircle className="h-4 w-4" />
                      通过
                    </Button>
                    <Button size="sm" variant="destructive" onClick={() => updateRecommendation(item.id, 'rejected')} className="gap-2">
                      <XCircle className="h-4 w-4" />
                      拒绝
                    </Button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
    </MainLayout>
  );
}
