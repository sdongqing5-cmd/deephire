'use client';

import { useState, useEffect, useCallback } from 'react';
import { ArrowLeft, Plus, Search, Briefcase, Edit, Trash2, Play, Pause, Square } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';

interface Job {
  id: string;
  title: string;
  department_id: string;
  location: string;
  category: string;
  recruitment_type: string;
  status: string;
  openings: number;
  is_urgent: boolean;
  application_count: number;
  created_at: string;
}

const statusLabels: Record<string, { label: string; color: string }> = {
  draft: { label: '草稿', color: 'gray' },
  recruiting: { label: '招聘中', color: 'green' },
  paused: { label: '已暂停', color: 'yellow' },
  closed: { label: '已结束', color: 'blue' },
  cancelled: { label: '已取消', color: 'red' },
};

const categoryLabels: Record<string, string> = {
  technology: '技术类',
  product: '产品类',
  sales: '销售类',
  marketing: '市场类',
  operations: '运营类',
  admin: '行政类',
  hr: '人事类',
  finance: '财务类',
  design: '设计类',
  other: '其他',
};

const recruitmentTypeLabels: Record<string, string> = {
  social: '社会招聘',
  campus: '校园招聘',
  internship: '实习生招聘',
};

export default function JobsPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  const fetchJobs = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (categoryFilter !== 'all') params.append('category', categoryFilter);

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs?${params}`);
      if (response.ok) {
        const data = await response.json();
        setJobs(data.filter((job: Job) => job.status !== 'cancelled'));
      }
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
    } finally {
      setLoading(false);
    }
  }, [categoryFilter, statusFilter]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchJobs();
  }, [fetchJobs]);

  const updateStatus = async (jobId: string, status: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs/${jobId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      });

      if (response.ok) {
        await fetchJobs();
      } else {
        const error = await response.json();
        alert(`状态更新失败: ${JSON.stringify(error.detail || error)}`);
      }
    } catch {
      alert('状态更新失败');
    }
  };

  const deleteJob = async (jobId: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs/${jobId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        await fetchJobs();
      } else {
        const error = await response.json();
        alert(`删除失败: ${JSON.stringify(error.detail || error)}`);
      }
    } catch {
      alert('删除失败');
    }
  };

  const filteredJobs = jobs.filter((job) =>
    job.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
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
          <h1 className="text-3xl font-bold text-gray-900">职位管理</h1>
          <p className="text-gray-600 mt-2">管理招聘职位和岗位信息</p>
        </div>
        <Button onClick={() => router.push('/jobs/new')} className="gap-2">
          <Plus className="h-4 w-4" />
          创建职位
        </Button>
      </div>

      {/* Filters */}
      <Card className="p-4 mb-6">
        <div className="flex gap-4 items-center">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="搜索职位名称..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="职位状态" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部状态</SelectItem>
              <SelectItem value="recruiting">招聘中</SelectItem>
              <SelectItem value="paused">已暂停</SelectItem>
              <SelectItem value="closed">已结束</SelectItem>
              <SelectItem value="draft">草稿</SelectItem>
            </SelectContent>
          </Select>

          <Select value={categoryFilter} onValueChange={setCategoryFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="岗位类别" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部类别</SelectItem>
              {Object.entries(categoryLabels).map(([value, label]) => (
                <SelectItem key={value} value={value}>
                  {label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </Card>

      {/* Jobs List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      ) : filteredJobs.length === 0 ? (
        <Card className="p-12">
          <div className="text-center">
            <Briefcase className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-4 text-lg font-medium text-gray-900">暂无职位</h3>
            <p className="mt-2 text-gray-500">创建第一个招聘职位</p>
            <Button onClick={() => router.push('/jobs/new')} className="mt-4">
              创建职位
            </Button>
          </div>
        </Card>
      ) : (
        <div className="grid gap-4">
          {filteredJobs.map((job) => (
            <Card
              key={job.id}
              className="p-6 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => router.push(`/jobs/${job.id}`)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{job.title}</h3>
                    {job.is_urgent && (
                      <Badge variant="destructive" className="text-xs">
                        加急
                      </Badge>
                    )}
                    <Badge
                      variant={statusLabels[job.status]?.color === 'green' ? 'default' : 'secondary'}
                    >
                      {statusLabels[job.status]?.label || job.status}
                    </Badge>
                  </div>

                  <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                    <span>{categoryLabels[job.category] || job.category}</span>
                    <span>•</span>
                    <span>{job.location}</span>
                    <span>•</span>
                    <span>{recruitmentTypeLabels[job.recruitment_type] || job.recruitment_type}</span>
                    <span>•</span>
                    <span>招聘 {job.openings} 人</span>
                  </div>

                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>{job.application_count} 人应聘</span>
                    <span>•</span>
                    <span>发布于 {new Date(job.created_at).toLocaleDateString('zh-CN')}</span>
                  </div>
                </div>

                <div className="flex flex-wrap justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                  {job.status === 'draft' && (
                    <Button size="sm" onClick={() => updateStatus(job.id, 'recruiting')} className="gap-1">
                      <Play className="h-3.5 w-3.5" />
                      发布
                    </Button>
                  )}
                  {job.status === 'recruiting' && (
                    <>
                      <Button size="sm" variant="outline" onClick={() => updateStatus(job.id, 'paused')} className="gap-1">
                        <Pause className="h-3.5 w-3.5" />
                        暂停
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => updateStatus(job.id, 'closed')} className="gap-1">
                        <Square className="h-3.5 w-3.5" />
                        结束
                      </Button>
                    </>
                  )}
                  {job.status === 'paused' && (
                    <>
                      <Button size="sm" onClick={() => updateStatus(job.id, 'recruiting')} className="gap-1">
                        <Play className="h-3.5 w-3.5" />
                        恢复
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => updateStatus(job.id, 'closed')} className="gap-1">
                        <Square className="h-3.5 w-3.5" />
                        结束
                      </Button>
                    </>
                  )}
                  <Button size="sm" variant="outline" onClick={() => router.push(`/jobs/${job.id}?edit=1`)} className="gap-1">
                    <Edit className="h-3.5 w-3.5" />
                    编辑
                  </Button>
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button size="sm" variant="destructive" className="gap-1">
                        <Trash2 className="h-3.5 w-3.5" />
                        删除
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>确认删除</AlertDialogTitle>
                        <AlertDialogDescription>
                          删除后职位将被标记为已取消状态。
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>取消</AlertDialogCancel>
                        <AlertDialogAction onClick={() => deleteJob(job.id)}>确认删除</AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
