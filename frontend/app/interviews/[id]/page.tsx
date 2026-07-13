'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Calendar, Clock, MapPin, User, CheckCircle, XCircle, Star } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';

interface InterviewDetail {
  interview: {
    id: string;
    application_id: string;
    job_id: string;
    candidate_id: string;
    interview_type: string;
    title?: string;
    interviewer_name: string;
    scheduled_at: string;
    duration: number;
    location?: string;
    meeting_link?: string;
    status: string;
    result?: string;
    feedback?: string;
    score?: number;
  };
  candidate: {
    id: string;
    name: string;
    phone?: string;
    email?: string;
    current_company?: string;
    current_title?: string;
    years_of_experience?: number;
  };
  job: {
    id: string;
    title: string;
    location: string;
    category: string;
  };
  application_status: string;
}

const statusLabels: Record<string, string> = {
  scheduled: '已安排',
  confirmed: '已确认',
  in_progress: '进行中',
  completed: '已完成',
  cancelled: '已取消',
  no_show: '未到场',
};

const typeLabels: Record<string, string> = {
  hr_initial: 'HR初筛',
  department: '部门面试',
  hr_reinterview: 'HR复试',
  final: '终面',
};

export default function InterviewDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [interview, setInterview] = useState<InterviewDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [evaluationDialogOpen, setEvaluationDialogOpen] = useState(false);
  const [evaluationForm, setEvaluationForm] = useState({
    result: 'pass',
    score: 7,
    feedback: '',
  });

  useEffect(() => {
    fetchInterview();
  }, [params.id]);

  const fetchInterview = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/interview-management/${params.id}`
      );
      if (response.ok) {
        const result = await response.json();
        setInterview(result.data);
      }
    } catch (error) {
      console.error('Failed to fetch interview:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitEvaluation = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/interview-management/${params.id}/evaluate`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(evaluationForm),
        }
      );

      if (response.ok) {
        alert('评价提交成功！');
        setEvaluationDialogOpen(false);
        fetchInterview();
      } else {
        alert('评价提交失败');
      }
    } catch (error) {
      alert('评价提交失败');
    }
  };

  const handleCancelInterview = async () => {
    const reason = prompt('请输入取消原因：');
    if (reason === null) return;

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/interview-management/${params.id}/cancel?reason=${encodeURIComponent(reason)}`,
        { method: 'POST' }
      );

      if (response.ok) {
        alert('面试已取消');
        fetchInterview();
      } else {
        alert('取消失败');
      }
    } catch (error) {
      alert('取消失败');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  if (!interview) {
    return (
      <div className="p-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold">面试不存在</h2>
          <Button onClick={() => router.back()} className="mt-4">
            返回
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Button variant="ghost" onClick={() => router.back()} className="mb-4 -ml-2">
            <ArrowLeft className="h-4 w-4 mr-2" />
            返回
          </Button>

          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-bold text-gray-900">
                  {interview.candidate.name} - {interview.job.title}
                </h1>
                <Badge variant="outline">
                  {typeLabels[interview.interview.interview_type]}
                </Badge>
                <Badge variant="default">
                  {statusLabels[interview.interview.status]}
                </Badge>
              </div>
              <div className="flex items-center gap-4 text-gray-600">
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  <span>
                    {new Date(interview.interview.scheduled_at).toLocaleDateString('zh-CN')}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  <span>
                    {new Date(interview.interview.scheduled_at).toLocaleTimeString('zh-CN', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                    {' '}({interview.interview.duration} 分钟)
                  </span>
                </div>
              </div>
            </div>

            <div className="flex gap-2">
              {interview.interview.status === 'scheduled' && (
                <>
                  <Dialog open={evaluationDialogOpen} onOpenChange={setEvaluationDialogOpen}>
                    <DialogTrigger asChild>
                      <Button className="gap-2">
                        <Star className="h-4 w-4" />
                        提交评价
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>面试评价</DialogTitle>
                        <DialogDescription>
                          请对候选人的面试表现进行评价
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4 py-4">
                        <div>
                          <Label>评价结果</Label>
                          <div className="flex gap-2 mt-2">
                            <Button
                              type="button"
                              variant={evaluationForm.result === 'pass' ? 'default' : 'outline'}
                              onClick={() => setEvaluationForm({ ...evaluationForm, result: 'pass' })}
                              className="flex-1"
                            >
                              <CheckCircle className="h-4 w-4 mr-2" />
                              通过
                            </Button>
                            <Button
                              type="button"
                              variant={evaluationForm.result === 'fail' ? 'destructive' : 'outline'}
                              onClick={() => setEvaluationForm({ ...evaluationForm, result: 'fail' })}
                              className="flex-1"
                            >
                              <XCircle className="h-4 w-4 mr-2" />
                              淘汰
                            </Button>
                          </div>
                        </div>

                        <div>
                          <Label>评分 ({evaluationForm.score}/10)</Label>
                          <Slider
                            min={1}
                            max={10}
                            step={1}
                            value={[evaluationForm.score]}
                            onValueChange={(value) =>
                              setEvaluationForm({ ...evaluationForm, score: value[0] })
                            }
                            className="mt-2"
                          />
                        </div>

                        <div>
                          <Label htmlFor="feedback">面试反馈</Label>
                          <Textarea
                            id="feedback"
                            rows={6}
                            value={evaluationForm.feedback}
                            onChange={(e) =>
                              setEvaluationForm({ ...evaluationForm, feedback: e.target.value })
                            }
                            placeholder="请输入面试反馈..."
                            className="mt-2"
                          />
                        </div>
                      </div>
                      <DialogFooter>
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => setEvaluationDialogOpen(false)}
                        >
                          取消
                        </Button>
                        <Button type="button" onClick={handleSubmitEvaluation}>
                          提交评价
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>

                  <Button variant="destructive" onClick={handleCancelInterview}>
                    取消面试
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="grid grid-cols-3 gap-6">
          {/* Left Column */}
          <div className="col-span-1 space-y-6">
            {/* 候选人信息 */}
            <Card className="p-6">
              <div className="flex items-center gap-2 mb-4">
                <User className="h-5 w-5 text-gray-400" />
                <h2 className="text-lg font-semibold">候选人信息</h2>
              </div>
              <div className="space-y-3 text-sm">
                <div>
                  <span className="text-gray-600">姓名：</span>
                  <span
                    className="font-medium cursor-pointer text-blue-600 hover:underline"
                    onClick={() => router.push(`/candidates/${interview.candidate.id}`)}
                  >
                    {interview.candidate.name}
                  </span>
                </div>
                {interview.candidate.phone && (
                  <div>
                    <span className="text-gray-600">电话：</span>
                    <span>{interview.candidate.phone}</span>
                  </div>
                )}
                {interview.candidate.email && (
                  <div>
                    <span className="text-gray-600">邮箱：</span>
                    <span>{interview.candidate.email}</span>
                  </div>
                )}
                {interview.candidate.current_company && (
                  <div>
                    <span className="text-gray-600">公司：</span>
                    <span>{interview.candidate.current_company}</span>
                  </div>
                )}
                {interview.candidate.current_title && (
                  <div>
                    <span className="text-gray-600">职位：</span>
                    <span>{interview.candidate.current_title}</span>
                  </div>
                )}
              </div>
            </Card>

            {/* 面试信息 */}
            <Card className="p-6">
              <h2 className="text-lg font-semibold mb-4">面试信息</h2>
              <div className="space-y-3 text-sm">
                <div>
                  <span className="text-gray-600">面试官：</span>
                  <span>{interview.interview.interviewer_name}</span>
                </div>
                {interview.interview.location && (
                  <div className="flex items-start gap-2">
                    <MapPin className="h-4 w-4 text-gray-400 mt-0.5" />
                    <span>{interview.interview.location}</span>
                  </div>
                )}
                {interview.interview.meeting_link && (
                  <div>
                    <span className="text-gray-600">会议链接：</span>
                    <a
                      href={interview.interview.meeting_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      点击加入
                    </a>
                  </div>
                )}
              </div>
            </Card>
          </div>

          {/* Right Column */}
          <div className="col-span-2">
            {/* 面试评价 */}
            {interview.interview.feedback && (
              <Card className="p-6 mb-6">
                <h2 className="text-lg font-semibold mb-4">面试评价</h2>
                <div className="space-y-4">
                  {interview.interview.score && (
                    <div>
                      <span className="text-gray-600">评分：</span>
                      <span className="text-2xl font-bold text-primary ml-2">
                        {interview.interview.score}/10
                      </span>
                    </div>
                  )}
                  {interview.interview.result && (
                    <div>
                      <span className="text-gray-600">结果：</span>
                      <Badge
                        variant={interview.interview.result === 'pass' ? 'default' : 'secondary'}
                        className="ml-2"
                      >
                        {interview.interview.result === 'pass' ? '通过' : '淘汰'}
                      </Badge>
                    </div>
                  )}
                  <div>
                    <p className="text-gray-600 mb-2">反馈：</p>
                    <p className="text-gray-700 whitespace-pre-wrap">
                      {interview.interview.feedback}
                    </p>
                  </div>
                </div>
              </Card>
            )}

            {/* 职位信息 */}
            <Card className="p-6">
              <h2 className="text-lg font-semibold mb-4">职位信息</h2>
              <div className="space-y-3 text-sm">
                <div>
                  <span className="text-gray-600">职位：</span>
                  <span
                    className="font-medium cursor-pointer text-blue-600 hover:underline ml-2"
                    onClick={() => router.push(`/jobs/${interview.job.id}`)}
                  >
                    {interview.job.title}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">地点：</span>
                  <span className="ml-2">{interview.job.location}</span>
                </div>
                <div>
                  <span className="text-gray-600">类别：</span>
                  <span className="ml-2">{interview.job.category}</span>
                </div>
                <div>
                  <span className="text-gray-600">应聘状态：</span>
                  <Badge className="ml-2">{interview.application_status}</Badge>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
