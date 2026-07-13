'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Calendar, Clock, MapPin, Video, User, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

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
  const [todayInterviews, setTodayInterviews] = useState<Interview[]>([]);
  const [upcomingInterviews, setUpcomingInterviews] = useState<Interview[]>([]);
  const [allInterviews, setAllInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('today');

  useEffect(() => {
    fetchInterviews();
  }, [activeTab]);

  const fetchInterviews = async () => {
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
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/interview-management?limit=50`
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
  };

  const renderInterviewCard = (interview: Interview) => (
    <Card
      key={interview.id}
      className="p-6 hover:shadow-md transition-shadow cursor-pointer"
      onClick={() => router.push(`/interviews/${interview.id}`)}
    >
      <div className="flex items-start justify-between mb-4">
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
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">面试管理</h1>
          <p className="text-gray-600 mt-2">管理面试安排和面试评价</p>
        </div>
        <Button className="gap-2" onClick={() => router.push('/interviews/new')}>
          <Plus className="h-4 w-4" />
          安排面试
        </Button>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="today">今日面试</TabsTrigger>
          <TabsTrigger value="upcoming">未来7天</TabsTrigger>
          <TabsTrigger value="all">全部面试</TabsTrigger>
        </TabsList>

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
  );
}
