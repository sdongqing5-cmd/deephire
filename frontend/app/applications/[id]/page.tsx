'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, FileText, User, Briefcase, Clock, CheckCircle, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface ApplicationDetail {
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
    location: string;
    category: string;
  };
  status: string;
  status_label: string;
  resume_url?: string;
  source?: string;
  hr_name?: string;
  recruiter_name?: string;
  applied_at: string;
  last_status_change_at?: string;
  status_history?: Array<{
    from_status?: string;
    to_status: string;
    reason?: string;
    operator_name?: string;
    created_at: string;
  }>;
}

export default function ApplicationDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [application, setApplication] = useState<ApplicationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    fetchApplication();
  }, [params.id]);

  const fetchApplication = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/application-actions/${params.id}`
      );
      if (response.ok) {
        const result = await response.json();
        setApplication(result.data);
      }
    } catch (error) {
      console.error('Failed to fetch application:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePass = async () => {
    if (!confirm('确认通过该候选人并进入下一阶段？')) return;

    setActionLoading(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/application-actions/${params.id}/pass`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ notes: '通过' }),
        }
      );

      if (response.ok) {
        alert('操作成功！');
        fetchApplication();
      } else {
        const error = await response.json();
        alert(`操作失败: ${error.detail}`);
      }
    } catch (error) {
      alert('操作失败');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    const reason = prompt('请输入淘汰原因（可选）：');
    if (reason === null) return;

    setActionLoading(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/application-actions/${params.id}/reject`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ reason: reason || '不符合要求' }),
        }
      );

      if (response.ok) {
        alert('已淘汰！');
        fetchApplication();
      } else {
        const error = await response.json();
        alert(`操作失败: ${error.detail}`);
      }
    } catch (error) {
      alert('操作失败');
    } finally {
      setActionLoading(false);
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

  if (!application) {
    return (
      <div className="p-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold">应聘记录不存在</h2>
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
                  {application.candidate.name} - {application.job.title}
                </h1>
                <Badge variant="default">{application.status_label}</Badge>
              </div>
              <div className="flex items-center gap-4 text-gray-600">
                <span>应聘时间: {new Date(application.applied_at).toLocaleDateString('zh-CN')}</span>
                {application.source && (
                  <>
                    <span>•</span>
                    <span>来源: {application.source}</span>
                  </>
                )}
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                className="gap-2"
                onClick={handlePass}
                disabled={actionLoading}
              >
                <CheckCircle className="h-4 w-4" />
                通过
              </Button>
              <Button
                variant="destructive"
                className="gap-2"
                onClick={handleReject}
                disabled={actionLoading}
              >
                <XCircle className="h-4 w-4" />
                淘汰
              </Button>
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
                    onClick={() => router.push(`/candidates/${application.candidate.id}`)}
                  >
                    {application.candidate.name}
                  </span>
                </div>
                {application.candidate.phone && (
                  <div>
                    <span className="text-gray-600">电话：</span>
                    <span>{application.candidate.phone}</span>
                  </div>
                )}
                {application.candidate.email && (
                  <div>
                    <span className="text-gray-600">邮箱：</span>
                    <span>{application.candidate.email}</span>
                  </div>
                )}
                {application.candidate.current_company && (
                  <div>
                    <span className="text-gray-600">公司：</span>
                    <span>{application.candidate.current_company}</span>
                  </div>
                )}
                {application.candidate.current_title && (
                  <div>
                    <span className="text-gray-600">职位：</span>
                    <span>{application.candidate.current_title}</span>
                  </div>
                )}
                {application.candidate.years_of_experience !== undefined && (
                  <div>
                    <span className="text-gray-600">经验：</span>
                    <span>{application.candidate.years_of_experience} 年</span>
                  </div>
                )}
              </div>
            </Card>

            {/* 职位信息 */}
            <Card className="p-6">
              <div className="flex items-center gap-2 mb-4">
                <Briefcase className="h-5 w-5 text-gray-400" />
                <h2 className="text-lg font-semibold">职位信息</h2>
              </div>
              <div className="space-y-3 text-sm">
                <div>
                  <span className="text-gray-600">职位：</span>
                  <span
                    className="font-medium cursor-pointer text-blue-600 hover:underline"
                    onClick={() => router.push(`/jobs/${application.job.id}`)}
                  >
                    {application.job.title}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">地点：</span>
                  <span>{application.job.location}</span>
                </div>
                <div>
                  <span className="text-gray-600">类别：</span>
                  <span>{application.job.category}</span>
                </div>
              </div>
            </Card>

            {/* 简历文件 */}
            {application.resume_url && (
              <Card className="p-6">
                <div className="flex items-center gap-2 mb-4">
                  <FileText className="h-5 w-5 text-gray-400" />
                  <h2 className="text-lg font-semibold">简历文件</h2>
                </div>
                <Button variant="outline" className="w-full gap-2">
                  <FileText className="h-4 w-4" />
                  查看简历
                </Button>
              </Card>
            )}
          </div>

          {/* Right Column */}
          <div className="col-span-2 space-y-6">
            {/* 状态历史 */}
            <Card className="p-6">
              <div className="flex items-center gap-2 mb-4">
                <Clock className="h-5 w-5 text-gray-400" />
                <h2 className="text-lg font-semibold">状态历史</h2>
              </div>

              {application.status_history && application.status_history.length > 0 ? (
                <div className="space-y-4">
                  {application.status_history.map((history, index) => (
                    <div key={index} className="flex gap-4">
                      <div className="flex flex-col items-center">
                        <div className="w-3 h-3 rounded-full bg-primary"></div>
                        {index < application.status_history!.length - 1 && (
                          <div className="w-0.5 h-full bg-gray-300 mt-2"></div>
                        )}
                      </div>
                      <div className="flex-1 pb-4">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant="secondary">{history.to_status}</Badge>
                          <span className="text-sm text-gray-500">
                            {new Date(history.created_at).toLocaleString('zh-CN')}
                          </span>
                        </div>
                        {history.reason && (
                          <p className="text-sm text-gray-600 mt-1">原因: {history.reason}</p>
                        )}
                        {history.operator_name && (
                          <p className="text-sm text-gray-500 mt-1">
                            操作人: {history.operator_name}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 py-8">暂无状态历史</p>
              )}
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
