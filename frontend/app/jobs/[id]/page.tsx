'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { ArrowDown, ArrowLeft, ArrowUp, Check, ChevronDown, Edit, GripVertical, Plus, Search, Trash2, Play, Pause, Square, X } from 'lucide-react';
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
  is_third_party_headhunter_enabled: boolean;
  interview_flow_config?: string;
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

type DirectoryUser = { id: string; name: string; title: string; department: string };
type EditableStage = { id: string; name: string; type: string; duration: string; interviewers: DirectoryUser[]; order?: number };
const stageTypes = [['hr', 'HR面试'], ['technical', '专业面试'], ['assessment', '测评'], ['business', '业务面试'], ['final', '终面']];
const directoryUsers: DirectoryUser[] = [
  { id: '1', name: 'Sarah Chen', title: 'HRBP', department: '人力资源部' },
  { id: '2', name: 'Mike Johnson', title: '招聘专员', department: '人力资源部' },
  { id: '3', name: 'Emily Wang', title: '技术负责人', department: '技术部' },
  { id: '4', name: 'Alex Li', title: '前端技术经理', department: '技术部' },
  { id: '5', name: 'Jessica Zhang', title: '产品总监', department: '产品部' },
  { id: '6', name: 'David Wu', title: '销售总监', department: '销售部' },
];
const defaultStages: EditableStage[] = [
  { id: 'stage-hr', name: 'HR初筛', type: 'hr', duration: '30', interviewers: [] },
  { id: 'stage-department', name: '部门面试', type: 'technical', duration: '60', interviewers: [] },
  { id: 'stage-final', name: '终面', type: 'final', duration: '60', interviewers: [] },
];

function InterviewerPicker({ value, onChange }: { value: DirectoryUser[]; onChange: (users: DirectoryUser[]) => void }) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const results = directoryUsers.filter((user) => `${user.name} ${user.title} ${user.department}`.toLowerCase().includes(query.toLowerCase()));
  const toggle = (user: DirectoryUser) => onChange(value.some((item) => item.id === user.id) ? value.filter((item) => item.id !== user.id) : [...value, user]);
  return <div className="relative"><button type="button" onClick={() => setOpen(!open)} className="flex min-h-10 w-full items-center justify-between rounded-md border bg-background px-3 py-2 text-left text-sm hover:border-primary"><span className={value.length ? 'flex flex-wrap gap-1' : 'text-muted-foreground'}>{value.length ? value.map((user) => <span key={user.id} className="inline-flex items-center gap-1 rounded bg-primary/10 px-2 py-0.5 text-xs text-primary">{user.name}<X className="h-3 w-3" onClick={(event) => { event.stopPropagation(); toggle(user); }} /></span>) : '请选择面试人，可多选'}</span><ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" /></button>{open && <div className="absolute z-30 mt-1 w-full rounded-md border bg-popover p-2 shadow-lg"><div className="flex items-center border-b px-2 pb-2"><Search className="mr-2 h-4 w-4 text-muted-foreground" /><input autoFocus value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索姓名、职位或部门" className="h-8 flex-1 bg-transparent text-sm outline-none" /></div><div className="max-h-56 overflow-y-auto py-1">{results.map((user) => { const selected = value.some((item) => item.id === user.id); return <button type="button" key={user.id} onClick={() => toggle(user)} className="flex w-full items-center gap-3 rounded px-2 py-2 text-left hover:bg-muted"><span className={`flex h-4 w-4 items-center justify-center rounded border ${selected ? 'border-primary bg-primary text-primary-foreground' : 'border-muted-foreground'}`}>{selected && <Check className="h-3 w-3" />}</span><span><span className="block text-sm font-medium">{user.name} <span className="font-normal text-muted-foreground">· {user.title}</span></span><span className="block text-xs text-muted-foreground">{user.department}</span></span></button>; })}</div><div className="border-t pt-2 text-right"><Button type="button" size="sm" variant="ghost" onClick={() => setOpen(false)}>完成</Button></div></div>}</div>;
}

const statusLabels: Record<string, { label: string; color: string }> = {
  draft: { label: '草稿', color: 'gray' },
  recruiting: { label: '招聘中', color: 'green' },
  paused: { label: '已暂停', color: 'yellow' },
  closed: { label: '已结束', color: 'blue' },
  cancelled: { label: '已取消', color: 'red' },
};

const toEditForm = (job: JobDetail) => ({
  ...parseWorkflowConfig(job.interview_flow_config),
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
  is_third_party_headhunter_enabled: job.is_third_party_headhunter_enabled || false,
});

function parseWorkflowConfig(config?: string) {
  const defaults = {
    workflow_hr_initial: false,
    workflow_department: true,
    workflow_assessment: false,
    workflow_hr_reinterview: false,
    workflow_final: false,
  };
  if (!config) return { ...defaults, stages: defaultStages };
  try {
    const stages = JSON.parse(config).stages || [];
    const editableStages: EditableStage[] = stages.length && typeof stages[0] === 'object'
      ? stages.map((stage: { id?: string; name?: string; type?: string; duration?: string | number; interviewers?: DirectoryUser[]; order?: number }, index: number) => ({ id: stage.id || `stage-${index}`, name: stage.name || `第${index + 1}轮面试`, type: stage.type || 'technical', duration: String(stage.duration || 60), interviewers: stage.interviewers || [], order: stage.order || index + 1 }))
      : stages.map((stage: string, index: number) => ({ ...defaultStages.find((item) => (stage === 'hr_initial' && item.type === 'hr') || (stage === 'department' && item.type === 'technical') || stage === item.type) || defaultStages[0], id: `stage-${index}` }));
    // 新版工作流保存的是环节对象；编辑页仍兼容旧版字符串数组。
    const stageKeys = stages.map((stage: string | { type?: string; name?: string }) =>
      typeof stage === 'string' ? stage : stage.type,
    );
    return {
      workflow_hr_initial: stageKeys.includes('hr_initial') || stageKeys.includes('hr'),
      workflow_department: stageKeys.includes('department') || stageKeys.includes('technical') || stageKeys.includes('business'),
      workflow_assessment: stageKeys.includes('assessment'),
      workflow_hr_reinterview: stageKeys.includes('hr_reinterview'),
      workflow_final: stageKeys.includes('final'),
      stages: editableStages.length ? editableStages : defaultStages,
    };
  } catch {
    return { ...defaults, stages: defaultStages };
  }
}

function getWorkflowStages(config?: string): EditableStage[] {
  if (!config) return [];
  try {
    const stages = JSON.parse(config).stages || [];
    if (stages.length && typeof stages[0] === 'object') {
      return stages
        .sort((a: { order?: number }, b: { order?: number }) => (a.order || 0) - (b.order || 0))
        .map((stage: { id?: string; name?: string; type?: string; duration?: string | number; interviewers?: DirectoryUser[]; order?: number }, index: number) => ({
          id: stage.id || `stage-${index}`,
          name: stage.name || `第${index + 1}轮面试`,
          type: stage.type || 'technical',
          duration: String(stage.duration || 60),
          interviewers: stage.interviewers || [],
          order: stage.order || index + 1,
        }));
    }
    return stages.map((stage: string, index: number) => ({
      id: `stage-${index}`,
      name: stage === 'hr_initial' ? 'HR初筛' : stage === 'department' ? '部门面试' : stage === 'assessment' ? '测评' : stage === 'hr_reinterview' ? 'HR复试' : stage === 'final' ? '终面' : stage,
      type: stage,
      duration: '未设置',
      interviewers: [],
      order: index + 1,
    }));
  } catch {
    return [];
  }
}

function stageTypeLabel(type: string) {
  return stageTypes.find(([value]) => value === type)?.[1] || type || '未设置';
}

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
    is_third_party_headhunter_enabled: false,
    workflow_hr_initial: false,
    workflow_department: true,
    workflow_assessment: false,
    workflow_hr_reinterview: false,
    workflow_final: false,
    stages: defaultStages,
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
          interview_flow_config: JSON.stringify({
            version: 2,
            stages: editForm.stages.map((stage, index) => ({
              ...stage,
              order: index + 1,
              interviewer_ids: stage.interviewers.map((user) => user.id),
              interviewers: stage.interviewers.map(({ id, name, title, department }) => ({ id, name, title, department })),
            })),
          }),
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

  const handleEditCheckboxChange = (name: string, checked: boolean) => {
    setEditForm((current) => ({
      ...current,
      [name]: checked,
    }));
  };

  const updateEditStage = (id: string, patch: Partial<EditableStage>) => {
    setEditForm((current) => ({ ...current, stages: current.stages.map((stage) => stage.id === id ? { ...stage, ...patch } : stage) }));
  };

  const moveEditStage = (index: number, direction: -1 | 1) => {
    setEditForm((current) => {
      const stages = [...current.stages];
      const target = index + direction;
      if (target < 0 || target >= stages.length) return current;
      [stages[index], stages[target]] = [stages[target], stages[index]];
      return { ...current, stages };
    });
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
                {job.is_third_party_headhunter_enabled && (
                  <>
                    <span>•</span>
                    <span>已开放猎头</span>
                  </>
                )}
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

          {/* 面试流程 */}
          <Card className="p-6">
            <div className="mb-5 flex items-center justify-between">
              <div><h2 className="text-lg font-semibold">面试流程</h2><p className="mt-1 text-sm text-muted-foreground">查看每个环节的顺序、面试人和预计时长</p></div>
              <Badge variant="secondary">{getWorkflowStages(job.interview_flow_config).length} 个环节</Badge>
            </div>
            {getWorkflowStages(job.interview_flow_config).length ? <div className="space-y-3">{getWorkflowStages(job.interview_flow_config).map((stage, index) => <div key={stage.id} className="flex items-start gap-4 rounded-lg border bg-muted/20 p-4"><div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground">{index + 1}</div><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center gap-2"><h3 className="font-semibold">{stage.name}</h3><Badge variant="outline">{stageTypeLabel(stage.type)}</Badge><span className="text-sm text-muted-foreground">{stage.duration === '未设置' ? stage.duration : `${stage.duration} 分钟`}</span></div><div className="mt-2 flex flex-wrap items-center gap-2 text-sm"><span className="text-muted-foreground">面试人：</span>{stage.interviewers.length ? stage.interviewers.map((user) => <span key={user.id} className="rounded bg-primary/10 px-2 py-1 text-primary">{user.name}<span className="ml-1 text-xs text-muted-foreground">· {user.department}</span></span>) : <span className="text-muted-foreground">未指定</span>}</div></div></div>)}</div> : <div className="rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground">暂未配置面试流程</div>}
          </Card>

          {/* 其他信息 */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold mb-3">其他信息</h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600">第三方猎头：</span>
                <span className="font-medium">{job.is_third_party_headhunter_enabled ? '开启' : '关闭'}</span>
              </div>
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
                onChange={(e) => handleEditCheckboxChange('is_urgent', e.target.checked)}
                className="h-4 w-4"
              />
              加急职位
            </Label>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <Card className="p-4 md:col-span-2">
              <div className="mb-3 flex items-start justify-between gap-4">
                <div><h3 className="text-sm font-semibold">面试工作流</h3><p className="mt-1 text-xs text-muted-foreground">按顺序编辑环节，并为每个环节指定面试人</p></div>
                <Button type="button" size="sm" onClick={() => setEditForm((current) => ({ ...current, stages: [...current.stages, { id: `stage-${Date.now()}`, name: `第${current.stages.length + 1}轮面试`, type: 'technical', duration: '60', interviewers: [] }] }))}><Plus className="mr-1 h-4 w-4" />添加环节</Button>
              </div>
              <div className="space-y-3">
                {editForm.stages.map((stage, index) => <div key={stage.id} className="rounded-lg border p-3"><div className="flex items-start gap-2"><GripVertical className="mt-2 h-4 w-4 text-muted-foreground" /><div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary text-xs text-primary-foreground">{index + 1}</div><div className="grid flex-1 gap-3 md:grid-cols-[1.2fr_1fr_90px_1.7fr] md:items-end"><div className="space-y-1"><Label>环节名称</Label><Input value={stage.name} onChange={(event) => updateEditStage(stage.id, { name: event.target.value })} /></div><div className="space-y-1"><Label>环节类型</Label><select value={stage.type} onChange={(event) => updateEditStage(stage.id, { type: event.target.value })} className="h-10 w-full rounded-md border bg-background px-3 text-sm">{stageTypes.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div><div className="space-y-1"><Label>时长</Label><Input type="number" min="15" step="15" value={stage.duration} onChange={(event) => updateEditStage(stage.id, { duration: event.target.value })} /></div><div className="space-y-1"><Label>面试人</Label><InterviewerPicker value={stage.interviewers} onChange={(interviewers) => updateEditStage(stage.id, { interviewers })} /></div></div><div className="flex gap-0"><Button type="button" variant="ghost" size="icon" aria-label="上移" disabled={index === 0} onClick={() => moveEditStage(index, -1)}><ArrowUp className="h-4 w-4" /></Button><Button type="button" variant="ghost" size="icon" aria-label="下移" disabled={index === editForm.stages.length - 1} onClick={() => moveEditStage(index, 1)}><ArrowDown className="h-4 w-4" /></Button><Button type="button" variant="ghost" size="icon" aria-label="删除" className="text-destructive" onClick={() => setEditForm((current) => ({ ...current, stages: current.stages.filter((item) => item.id !== stage.id) }))}><Trash2 className="h-4 w-4" /></Button></div></div></div>)}
                {!editForm.stages.length && <div className="rounded-md border border-dashed p-4 text-center text-sm text-muted-foreground">暂无环节，请添加面试环节</div>}
              </div>
            </Card>

            <Card className="p-4">
              <h3 className="mb-3 text-sm font-semibold">猎头协作</h3>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={editForm.is_third_party_headhunter_enabled}
                  onChange={(event) => handleEditCheckboxChange('is_third_party_headhunter_enabled', event.target.checked)}
                />
                开启第三方猎头
              </label>
            </Card>
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
