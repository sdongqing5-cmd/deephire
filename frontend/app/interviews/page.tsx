'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ArrowLeft, Bell, Calendar, Clock, MapPin, MessageSquareWarning, Plus, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Checkbox } from '@/components/ui/checkbox';
import { useAuthStore } from '@/stores/auth-store';
import { MainLayout } from '@/components/layout/main-layout';

interface Interview {
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

const statusLabels: Record<string, { label: string; color: string }> = {
  scheduled: { label: '已安排', color: 'blue' },
  confirmed: { label: '已确认', color: 'green' },
  in_progress: { label: '进行中', color: 'yellow' },
  completed: { label: '已完成', color: 'gray' },
  cancelled: { label: '已取消', color: 'red' },
  no_show: { label: '未到场', color: 'red' },
};

const typeLabels: Record<string, string> = {
  hr_initial: 'HR初筛',
  department: '部门面试',
  hr_reinterview: 'HR复试',
  final: '终面',
};

const resultLabels: Record<string, { label: string; color: string }> = {
  pass: { label: '通过', color: 'green' },
  fail: { label: '淘汰', color: 'red' },
  pending: { label: '待定', color: 'yellow' },
};

export default function InterviewsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const user = useAuthStore((state) => state.user);
  const [todayInterviews, setTodayInterviews] = useState<Interview[]>([]);
  const [upcomingInterviews, setUpcomingInterviews] = useState<Interview[]>([]);
  const [allInterviews, setAllInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const activeTab = searchParams.get('tab') || 'today';
  const resultFilter = searchParams.get('result');

  const fetchInterviews = useCallback(async () => {
    setLoading(true);
    try {
      if (activeTab === 'today') {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/interview-management/today`
        );
        if (response.ok) {
          const result = await response.json();
          setTodayInterviews(result.data || []);
        }
      } else if (activeTab === 'upcoming') {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/interview-management/upcoming?days=7`
        );
        if (response.ok) {
          const result = await response.json();
          setUpcomingInterviews(result.data || []);
        }
      } else {
        const params = new URLSearchParams({ limit: '50' });
        if (user?.role === 'interviewer' && user.id) {
          params.set('interviewer_id', user.id);
        }
        if (resultFilter) {
          params.set('result', resultFilter);
        }

        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/interview-management?${params.toString()}`
        );
        if (response.ok) {
          const result = await response.json();
          setAllInterviews(result.data || []);
        }
      }
    } catch (error) {
      console.error('Failed to fetch interviews:', error);
    } finally {
      setLoading(false);
    }
  }, [activeTab, resultFilter, user]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchInterviews();
    setSelectedIds([]);
  }, [fetchInterviews]);

  const toggleSelected = (interviewId: string) => {
    setSelectedIds((current) =>
      current.includes(interviewId)
        ? current.filter((id) => id !== interviewId)
        : [...current, interviewId]
    );
  };

  const runBatchAction = async (action: 'notify' | 'urge-candidate' | 'urge-interviewer') => {
    if (selectedIds.length === 0) {
      alert('请先选择面试安排');
      return;
    }

    const endpoint = action === 'notify' ? 'batch-notify' : 'batch-urge';
    const body =
      action === 'notify'
        ? { interview_ids: selectedIds }
        : {
            interview_ids: selectedIds,
            target: action === 'urge-candidate' ? 'candidate' : 'interviewer',
          };

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/interview-management/${endpoint}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        }
      );

      if (response.ok) {
        alert('操作成功');
        await fetchInterviews();
        setSelectedIds([]);
      } else {
        const error = await response.json();
        alert(`操作失败: ${error.detail || '未知错误'}`);
      }
    } catch {
      alert('操作失败，请稍后重试');
    }
  };

  const renderInterviewCard = (interview: Interview) => (
    <Card
      key={interview.id}
      className="p-6 hover:shadow-md transition-shadow cursor-pointer"
      onClick={() => router.push(`/interviews/${interview.id}`)}
    >
      <div className="flex items-start justify-between mb-4">
        <div
          className="mr-3 pt-1"
          onClick={(event) => {
            event.stopPropagation();
          }}
        >
          <Checkbox
            checked={selectedIds.includes(interview.id)}
            onCheckedChange={() => toggleSelected(interview.id)}
            aria-label={`选择${interview.candidate_name}的面试`}
          />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-semibold text-gray-900">
              {interview.candidate_name}
            </h3>
            <Badge variant="outline">
              {typeLabels[interview.interview_type] || interview.interview_type}
            </Badge>
            <Badge
              variant={
                statusLabels[interview.status]?.color === 'green' ? 'default' : 'secondary'
              }
            >
              {statusLabels[interview.status]?.label || interview.status}
            </Badge>
            {interview.result && (
              <Badge
                variant={
                  resultLabels[interview.result]?.color === 'green' ? 'default' : 'secondary'
                }
              >
                {resultLabels[interview.result]?.label || interview.result}
              </Badge>
            )}
          </div>
          <p className="text-gray-600 mb-3">{interview.job_title}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 text-sm text-gray-600">
        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4" />
          <span>{new Date(interview.scheduled_at).toLocaleDateString('zh-CN')}</span>
        </div>
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4" />
          <span>
            {new Date(interview.scheduled_at).toLocaleTimeString('zh-CN', {
              hour: '2-digit',
              minute: '2-digit',
            })}{' '}
            ({interview.duration} 分钟)
          </span>
        </div>
        <div className="flex items-center gap-2">
          <User className="h-4 w-4" />
          <span>面试官: {interview.interviewer_name}</span>
        </div>
        {interview.location && (
          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4" />
            <span>{interview.location}</span>
          </div>
        )}
      </div>
    </Card>
  );

  return (
    <MainLayout requiredPath="/interviews">
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <Button
            variant="ghost"
            onClick={() => router.push('/dashboard')}
            className="mb-4 -ml-2 gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            返回首页
          </Button>
          <h1 className="text-3xl font-bold text-gray-900">面试管理</h1>
          <p className="text-gray-600 mt-2">管理面试安排和面试评价</p>
        </div>
        <Button className="gap-2" onClick={() => router.push('/interviews/new')}>
          <Plus className="h-4 w-4" />
          安排面试
        </Button>
      </div>

      {/* Tabs */}
      <Tabs
        value={activeTab}
        onValueChange={(value) => {
          const params = new URLSearchParams(searchParams.toString());
          params.set('tab', value);
          if (value !== 'all') {
            params.delete('result');
          }
          router.push(`/interviews?${params.toString()}`);
        }}
      >
        <div className="flex flex-wrap items-center justify-between gap-3">
          <TabsList>
            <TabsTrigger value="today">今日面试</TabsTrigger>
            <TabsTrigger value="upcoming">未来7天</TabsTrigger>
            <TabsTrigger value="all">全部面试</TabsTrigger>
          </TabsList>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" disabled={selectedIds.length === 0} onClick={() => runBatchAction('notify')} className="gap-2">
              <Bell className="h-4 w-4" />
              通知双方
            </Button>
            <Button variant="outline" disabled={selectedIds.length === 0} onClick={() => runBatchAction('urge-candidate')} className="gap-2">
              <MessageSquareWarning className="h-4 w-4" />
              催促答复
            </Button>
            <Button variant="outline" disabled={selectedIds.length === 0} onClick={() => runBatchAction('urge-interviewer')} className="gap-2">
              <MessageSquareWarning className="h-4 w-4" />
              催促反馈
            </Button>
          </div>
        </div>

        <TabsContent value="today" className="mt-6">
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
              <p className="mt-4 text-gray-600">加载中...</p>
            </div>
          ) : todayInterviews.length === 0 ? (
            <Card className="p-12">
              <div className="text-center">
                <Calendar className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-4 text-lg font-medium text-gray-900">今日无面试</h3>
                <p className="mt-2 text-gray-500">查看未来的面试安排</p>
              </div>
            </Card>
          ) : (
            <div className="grid gap-4">
              {todayInterviews.map(renderInterviewCard)}
            </div>
          )}
        </TabsContent>

        <TabsContent value="upcoming" className="mt-6">
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
              <p className="mt-4 text-gray-600">加载中...</p>
            </div>
          ) : upcomingInterviews.length === 0 ? (
            <Card className="p-12">
              <div className="text-center">
                <Calendar className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-4 text-lg font-medium text-gray-900">暂无面试</h3>
                <p className="mt-2 text-gray-500">未来7天无面试安排</p>
              </div>
            </Card>
          ) : (
            <div className="grid gap-4">
              {upcomingInterviews.map(renderInterviewCard)}
            </div>
          )}
        </TabsContent>

        <TabsContent value="all" className="mt-6">
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
              <p className="mt-4 text-gray-600">加载中...</p>
            </div>
          ) : allInterviews.length === 0 ? (
            <Card className="p-12">
              <div className="text-center">
                <Calendar className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-4 text-lg font-medium text-gray-900">暂无面试</h3>
                <p className="mt-2 text-gray-500">开始安排第一场面试</p>
              </div>
            </Card>
          ) : (
            <div className="grid gap-4">
              {allInterviews.map(renderInterviewCard)}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
    </MainLayout>
  );
}
