'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { ArrowLeft, Edit, Trash2, Play, Pause, Square } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
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

interface JobDetail {
  id: string;
  title: string;
  department_id: string;
  location: string;
  category: string;
  recruitment_type: string;
  level?: string;
  description?: string;
  requirements?: string;
  responsibilities?: string;
  notes?: string;
  salary_min?: number;
  salary_max?: number;
  openings: number;
  is_urgent: boolean;
  status: string;
  view_count: number;
  application_count: number;
  created_at: string;
  updated_at?: string;
  published_at?: string;
}

const jobCategories = [
  { value: 'technology', label: '技术类' },
  { value: 'product', label: '产品类' },
  { value: 'sales', label: '销售类' },
  { value: 'marketing', label: '市场类' },
  { value: 'operations', label: '运营类' },
  { value: 'admin', label: '行政类' },
  { value: 'hr', label: '人事类' },
  { value: 'finance', label: '财务类' },
  { value: 'design', label: '设计类' },
  { value: 'other', label: '其他' },
];

const jobLevels = [
  { value: 'junior', label: '初级' },
  { value: 'intermediate', label: '中级' },
  { value: 'senior', label: '高级' },
  { value: 'expert', label: '专家' },
  { value: 'manager', label: '经理' },
  { value: 'director', label: '总监' },
  { value: 'vp', label: 'VP' },
  { value: 'c_level', label: 'C-Level' },
];

const departments = [
  { value: 'dept_tech', label: '技术部' },
  { value: 'dept_product', label: '产品部' },
  { value: 'dept_sales', label: '销售部' },
];

const statusLabels: Record<string, { label: string; color: string }> = {
  draft: { label: '草稿', color: 'gray' },
  recruiting: { label: '招聘中', color: 'green' },
  paused: { label: '已暂停', color: 'yellow' },
  closed: { label: '已结束', color: 'blue' },
  cancelled: { label: '已取消', color: 'red' },
};

const toEditForm = (job: JobDetail) => ({
  title: job.title,
  department_id: job.department_id,
  location: job.location,
  category: job.category,
  recruitment_type: job.recruitment_type,
  level: job.level || '',
  description: job.description || '',
  requirements: job.requirements || '',
  responsibilities: job.responsibilities || '',
  notes: job.notes || '',
  salary_min: job.salary_min ? String(job.salary_min) : '',
  salary_max: job.salary_max ? String(job.salary_max) : '',
  openings: String(job.openings),
  is_urgent: job.is_urgent,
});

export default function JobDetailPage() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const jobId = params.id;
  const [job, setJob] = useState<JobDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [editOpen, setEditOpen] = useState(searchParams.get('edit') === '1');
  const [saving, setSaving] = useState(false);
  const [editForm, setEditForm] = useState({
    title: '',
    department_id: 'dept_tech',
    location: '',
    category: 'technology',
    recruitment_type: 'social',
    level: '',
    description: '',
    requirements: '',
    responsibilities: '',
    notes: '',
    salary_min: '',
    salary_max: '',
    openings: '1',
    is_urgent: false,
  });

  const fetchJob = useCallback(async () => {
    try {
      if (!jobId) return;

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs/${jobId}`);
      if (response.ok) {
        const data = await response.json();
        setJob(data);
        setEditForm(toEditForm(data));
      }
    } catch (error) {
      console.error('Failed to fetch job:', error);
    } finally {
      setLoading(false);
    }
  }, [jobId]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchJob();
  }, [fetchJob]);

  const updateStatus = async (newStatus: string) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs/${jobId}/status`,
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: newStatus }),
        }
      );

      if (response.ok) {
        alert('状态更新成功');
        fetchJob();
      }
    } catch {
      alert('状态更新失败');
    }
  };

  const deleteJob = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs/${jobId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        alert('职位已删除');
        router.push('/jobs');
      }
    } catch {
      alert('删除失败');
    }
  };

  const updateJob = async () => {
    setSaving(true);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs/${jobId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...editForm,
          level: editForm.level || null,
          salary_min: editForm.salary_min ? parseInt(editForm.salary_min) : null,
          salary_max: editForm.salary_max ? parseInt(editForm.salary_max) : null,
          openings: parseInt(editForm.openings),
        }),
      });

      if (response.ok) {
        setEditOpen(false);
        await fetchJob();
      } else {
        const error = await response.json();
        alert(`更新失败: ${JSON.stringify(error.detail || error)}`);
      }
    } catch {
      alert('更新失败');
    } finally {
      setSaving(false);
    }
  };

  const handleEditChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setEditForm((current) => ({
      ...current,
      [name]: value,
    }));
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

  if (!job) {
    return (
      <div className="p-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold">职位不存在</h2>
          <Button onClick={() => router.push('/jobs')} className="mt-4">
            返回职位列表
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Button variant="ghost" onClick={() => router.back()} className="mb-4 -ml-2">
            <ArrowLeft className="h-4 w-4 mr-2" />
            返回
          </Button>

          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-bold text-gray-900">{job.title}</h1>
                {job.is_urgent && (
                  <Badge variant="destructive">加急</Badge>
                )}
                <Badge
                  variant={statusLabels[job.status]?.color === 'green' ? 'default' : 'secondary'}
                >
                  {statusLabels[job.status]?.label}
                </Badge>
              </div>
              <div className="flex items-center gap-3 text-gray-600">
                <span>{job.location}</span>
                <span>•</span>
                <span>招聘 {job.openings} 人</span>
                <span>•</span>
                <span>{job.application_count} 人应聘</span>
                <span>•</span>
                <span>浏览 {job.view_count} 次</span>
              </div>
            </div>

            <div className="flex gap-2">
              {job.status === 'draft' && (
                <Button onClick={() => updateStatus('recruiting')} className="gap-2">
                  <Play className="h-4 w-4" />
                  发布招聘
                </Button>
              )}
              {job.status === 'recruiting' && (
                <Button onClick={() => updateStatus('paused')} variant="outline" className="gap-2">
                  <Pause className="h-4 w-4" />
                  暂停招聘
                </Button>
              )}
              {job.status === 'paused' && (
                <Button onClick={() => updateStatus('recruiting')} className="gap-2">
                  <Play className="h-4 w-4" />
                  恢复招聘
                </Button>
              )}
              {(job.status === 'recruiting' || job.status === 'paused') && (
                <Button onClick={() => updateStatus('closed')} variant="outline" className="gap-2">
                  <Square className="h-4 w-4" />
                  结束招聘
                </Button>
              )}
              <Button variant="outline" className="gap-2" onClick={() => setEditOpen(true)}>
                <Edit className="h-4 w-4" />
                编辑
              </Button>
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button variant="destructive" className="gap-2">
                    <Trash2 className="h-4 w-4" />
                    删除
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>确认删除</AlertDialogTitle>
                    <AlertDialogDescription>
                      删除后职位将被标记为已取消状态，此操作不可恢复。
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>取消</AlertDialogCancel>
                    <AlertDialogAction onClick={deleteJob}>确认删除</AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="grid gap-6">
          {/* 薪资范围 */}
          {(job.salary_min || job.salary_max) && (
            <Card className="p-6">
              <h2 className="text-lg font-semibold mb-3">薪资范围</h2>
              <p className="text-2xl font-bold text-primary">
                {job.salary_min?.toLocaleString()} - {job.salary_max?.toLocaleString()} 元/月
              </p>
            </Card>
          )}

          {/* 职位描述 */}
          {job.description && (
            <Card className="p-6">
              <h2 className="text-lg font-semibold mb-3">职位描述</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{job.description}</p>
            </Card>
          )}

          {/* 任职要求 */}
          {job.requirements && (
            <Card className="p-6">
              <h2 className="text-lg font-semibold mb-3">任职要求</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{job.requirements}</p>
            </Card>
          )}

          {/* 工作职责 */}
          {job.responsibilities && (
            <Card className="p-6">
              <h2 className="text-lg font-semibold mb-3">工作职责</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{job.responsibilities}</p>
            </Card>
          )}

          {/* 备注 */}
          {job.notes && (
            <Card className="p-6">
              <h2 className="text-lg font-semibold mb-3">备注</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{job.notes}</p>
            </Card>
          )}

          {/* 其他信息 */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold mb-3">其他信息</h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600">创建时间：</span>
                <span className="font-medium">
                  {new Date(job.created_at).toLocaleString('zh-CN')}
                </span>
              </div>
              {job.published_at && (
                <div>
                  <span className="text-gray-600">发布时间：</span>
                  <span className="font-medium">
                    {new Date(job.published_at).toLocaleString('zh-CN')}
                  </span>
                </div>
              )}
              {job.updated_at && (
                <div>
                  <span className="text-gray-600">更新时间：</span>
                  <span className="font-medium">
                    {new Date(job.updated_at).toLocaleString('zh-CN')}
                  </span>
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>

      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-3xl">
          <DialogHeader>
            <DialogTitle>编辑职位</DialogTitle>
          </DialogHeader>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="title">职位名称 *</Label>
              <Input id="title" name="title" value={editForm.title} onChange={handleEditChange} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="department_id">部门 *</Label>
              <select id="department_id" name="department_id" value={editForm.department_id} onChange={handleEditChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                {departments.map((department) => (
                  <option key={department.value} value={department.value}>{department.label}</option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="location">工作地点 *</Label>
              <Input id="location" name="location" value={editForm.location} onChange={handleEditChange} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="category">岗位类别 *</Label>
              <select id="category" name="category" value={editForm.category} onChange={handleEditChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                {jobCategories.map((category) => (
                  <option key={category.value} value={category.value}>{category.label}</option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="recruitment_type">招聘类别 *</Label>
              <select id="recruitment_type" name="recruitment_type" value={editForm.recruitment_type} onChange={handleEditChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                <option value="social">社会招聘</option>
                <option value="campus">校园招聘</option>
                <option value="internship">实习生招聘</option>
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="level">职位级别</Label>
              <select id="level" name="level" value={editForm.level} onChange={handleEditChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                <option value="">未指定</option>
                {jobLevels.map((level) => (
                  <option key={level.value} value={level.value}>{level.label}</option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="salary_min">最低薪资</Label>
              <Input id="salary_min" name="salary_min" type="number" value={editForm.salary_min} onChange={handleEditChange} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="salary_max">最高薪资</Label>
              <Input id="salary_max" name="salary_max" type="number" value={editForm.salary_max} onChange={handleEditChange} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="openings">招聘人数 *</Label>
              <Input id="openings" name="openings" type="number" min="1" value={editForm.openings} onChange={handleEditChange} />
            </div>

            <Label className="flex items-center gap-2 pt-8">
              <input
                type="checkbox"
                checked={editForm.is_urgent}
                onChange={(e) => setEditForm((current) => ({ ...current, is_urgent: e.target.checked }))}
                className="h-4 w-4"
              />
              加急职位
            </Label>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">职位描述</Label>
            <Textarea id="description" name="description" value={editForm.description} onChange={handleEditChange} rows={4} />
          </div>

          <div className="space-y-2">
            <Label htmlFor="requirements">任职要求</Label>
            <Textarea id="requirements" name="requirements" value={editForm.requirements} onChange={handleEditChange} rows={4} />
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setEditOpen(false)} disabled={saving}>取消</Button>
            <Button onClick={updateJob} disabled={saving}>{saving ? '保存中...' : '保存修改'}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
