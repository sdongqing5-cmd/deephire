'use client';

import { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { MainLayout } from '@/components/layout/main-layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { ArrowDown, ArrowLeft, ArrowUp, Check, ChevronDown, GripVertical, Plus, Search, Trash2, X } from 'lucide-react';

const jobCategories = [['technology', '技术类'], ['product', '产品类'], ['sales', '销售类'], ['marketing', '市场类'], ['operations', '运营类'], ['admin', '行政类'], ['hr', '人事类'], ['finance', '财务类'], ['design', '设计类'], ['other', '其他类']];
const jobLevels = [['junior', '初级'], ['intermediate', '中级'], ['senior', '高级'], ['expert', '专家'], ['manager', '经理'], ['director', '总监'], ['vp', 'VP'], ['c_level', 'C-Level']];
const departments = [['dept_tech', '技术部'], ['dept_product', '产品部'], ['dept_sales', '销售部']];
const stageTypes = [['hr', 'HR面试'], ['technical', '专业面试'], ['assessment', '测评'], ['business', '业务面试'], ['final', '终面']];

type DirectoryUser = { id: string; name: string; title: string; department: string; email: string };
type InterviewStage = { id: string; name: string; type: string; duration: string; interviewers: DirectoryUser[] };

// 目录数据层：后续可直接替换为 GET /users/directory，字段已与组织架构表保持一致。
const directoryUsers: DirectoryUser[] = [
  { id: '1', name: 'Sarah Chen', title: 'HRBP', department: '人力资源部', email: 'hr@deephire.com' },
  { id: '2', name: 'Mike Johnson', title: '招聘专员', department: '人力资源部', email: 'recruiter@deephire.com' },
  { id: '3', name: 'Emily Wang', title: '技术负责人', department: '技术部', email: 'interviewer@deephire.com' },
  { id: '4', name: 'Alex Li', title: '前端技术经理', department: '技术部', email: 'alex.li@deephire.com' },
  { id: '5', name: 'Jessica Zhang', title: '产品总监', department: '产品部', email: 'jessica.zhang@deephire.com' },
  { id: '6', name: 'David Wu', title: '销售总监', department: '销售部', email: 'david.wu@deephire.com' },
];

function newStage(index: number): InterviewStage {
  return { id: `stage-${Date.now()}-${index}`, name: `第${index + 1}轮面试`, type: 'technical', duration: '60', interviewers: [] };
}

function InterviewerPicker({ value, onChange }: { value: DirectoryUser[]; onChange: (users: DirectoryUser[]) => void }) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const results = useMemo(() => directoryUsers.filter((user) => `${user.name} ${user.title} ${user.department}`.toLowerCase().includes(query.toLowerCase())), [query]);
  const toggle = (user: DirectoryUser) => onChange(value.some((item) => item.id === user.id) ? value.filter((item) => item.id !== user.id) : [...value, user]);
  return <div className="relative">
    <button type="button" onClick={() => setOpen(!open)} className="flex min-h-10 w-full items-center justify-between rounded-md border bg-background px-3 py-2 text-left text-sm hover:border-primary">
      <span className={value.length ? 'flex flex-wrap gap-1' : 'text-muted-foreground'}>{value.length ? value.map((user) => <span key={user.id} className="inline-flex items-center gap-1 rounded bg-primary/10 px-2 py-0.5 text-xs text-primary">{user.name}<X className="h-3 w-3" onClick={(event) => { event.stopPropagation(); toggle(user); }} /></span>) : '请选择面试人，可多选'}</span><ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" />
    </button>
    {open && <div className="absolute z-30 mt-1 w-full rounded-md border bg-popover p-2 shadow-lg"><div className="flex items-center border-b px-2 pb-2"><Search className="mr-2 h-4 w-4 text-muted-foreground" /><input autoFocus value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索姓名、职位或部门" className="h-8 flex-1 bg-transparent text-sm outline-none" /></div><div className="max-h-56 overflow-y-auto py-1">{results.map((user) => { const selected = value.some((item) => item.id === user.id); return <button type="button" key={user.id} onClick={() => toggle(user)} className="flex w-full items-center gap-3 rounded px-2 py-2 text-left hover:bg-muted"><span className={`flex h-4 w-4 items-center justify-center rounded border ${selected ? 'border-primary bg-primary text-primary-foreground' : 'border-muted-foreground'}`}>{selected && <Check className="h-3 w-3" />}</span><span className="min-w-0"><span className="block text-sm font-medium">{user.name} <span className="font-normal text-muted-foreground">· {user.title}</span></span><span className="block truncate text-xs text-muted-foreground">{user.department}</span></span></button>; })}{!results.length && <p className="px-2 py-4 text-center text-sm text-muted-foreground">没有找到匹配的员工</p>}</div><div className="border-t pt-2 text-right"><Button type="button" size="sm" variant="ghost" onClick={() => setOpen(false)}>完成</Button></div></div>}
  </div>;
}

export default function NewJobPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [stages, setStages] = useState<InterviewStage[]>([
    { ...newStage(0), name: 'HR初筛', type: 'hr', duration: '30' },
    { ...newStage(1), name: '部门面试', type: 'technical', duration: '60', interviewers: [directoryUsers[2]] },
    { ...newStage(2), name: 'HR复试', type: 'hr', duration: '45', interviewers: [directoryUsers[0]] },
    { ...newStage(3), name: '终面', type: 'final', duration: '60' },
  ]);
  const [formData, setFormData] = useState({ title: '', department_id: 'dept_tech', location: '', category: 'technology', recruitment_type: 'social', level: '', description: '', requirements: '', responsibilities: '', notes: '', salary_min: '', salary_max: '', openings: '1', is_urgent: false, is_third_party_headhunter_enabled: false, valid_until: '', hiring_manager_id: '1', department_manager_id: '' });
  const updateField = (name: string, value: string | boolean) => setFormData((current) => ({ ...current, [name]: value }));
  const updateStage = (id: string, patch: Partial<InterviewStage>) => setStages((current) => current.map((stage) => stage.id === id ? { ...stage, ...patch } : stage));
  const moveStage = (index: number, direction: -1 | 1) => setStages((current) => { const next = [...current]; const target = index + direction; if (target < 0 || target >= next.length) return current; [next[index], next[target]] = [next[target], next[index]]; return next; });
  const removeStage = (id: string) => setStages((current) => current.filter((stage) => stage.id !== id));

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!stages.length) { alert('请至少保留一个面试环节'); return; }
    setLoading(true);
    const payload = { ...formData, level: formData.level || null, department_manager_id: formData.department_manager_id || null, salary_min: formData.salary_min ? parseInt(formData.salary_min, 10) : null, salary_max: formData.salary_max ? parseInt(formData.salary_max, 10) : null, openings: parseInt(formData.openings, 10), valid_until: formData.valid_until || null, interview_flow_config: JSON.stringify({ version: 2, stages: stages.map((stage, index) => ({ ...stage, order: index + 1, interviewer_ids: stage.interviewers.map((user) => user.id), interviewers: stage.interviewers.map(({ id, name, title, department }) => ({ id, name, title, department })) })) }) };
    try { const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }); if (!response.ok) { const error = await response.json(); throw new Error(error.detail || '请检查表单信息'); } alert('职位创建成功！'); router.push('/jobs'); } catch (error) { console.error(error); alert(`创建失败：${error instanceof Error ? error.message : '网络错误，请稍后重试'}`); } finally { setLoading(false); }
  };

  return <MainLayout requiredPath="/jobs"><div className="container mx-auto max-w-6xl py-6"><div className="mb-6"><Button variant="ghost" onClick={() => router.back()} className="mb-4"><ArrowLeft className="mr-2 h-4 w-4" />返回</Button><h1 className="text-3xl font-bold">创建新职位</h1><p className="mt-2 text-muted-foreground">填写职位信息、面试流程和每个环节的面试人</p></div><form onSubmit={handleSubmit} className="space-y-6">
    <Card><CardHeader><CardTitle>职位信息</CardTitle><CardDescription>请填写完整的职位信息</CardDescription></CardHeader><CardContent className="space-y-6"><div className="grid grid-cols-1 gap-6 md:grid-cols-2">
      {([['title', '职位名称 *', '例如：高级前端工程师'], ['location', '工作地点 *', '例如：北京'], ['salary_min', '最低薪资（元/月）', '例如：15000'], ['salary_max', '最高薪资（元/月）', '例如：25000']] as const).map(([name, label, placeholder]) => <div key={name} className="space-y-2"><Label htmlFor={name}>{label}</Label><Input id={name} name={name} type={name.includes('salary') ? 'number' : 'text'} value={formData[name]} onChange={(event) => updateField(name, event.target.value)} placeholder={placeholder} required={name === 'title' || name === 'location'} /></div>)}
      <div className="space-y-2"><Label>部门 *</Label><select value={formData.department_id} onChange={(event) => updateField('department_id', event.target.value)} className="h-10 w-full rounded-md border bg-background px-3 text-sm">{departments.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div><div className="space-y-2"><Label>岗位类别 *</Label><select value={formData.category} onChange={(event) => updateField('category', event.target.value)} className="h-10 w-full rounded-md border bg-background px-3 text-sm">{jobCategories.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div><div className="space-y-2"><Label>招聘类别 *</Label><select value={formData.recruitment_type} onChange={(event) => updateField('recruitment_type', event.target.value)} className="h-10 w-full rounded-md border bg-background px-3 text-sm"><option value="social">社会招聘</option><option value="campus">校园招聘</option><option value="internship">实习生招聘</option></select></div><div className="space-y-2"><Label>职位级别</Label><select value={formData.level} onChange={(event) => updateField('level', event.target.value)} className="h-10 w-full rounded-md border bg-background px-3 text-sm"><option value="">未指定</option>{jobLevels.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div>
    </div><div className="space-y-2"><Label>职位描述 *</Label><Textarea value={formData.description} onChange={(event) => updateField('description', event.target.value)} placeholder="描述职位的主要职责和工作内容..." rows={5} required /></div><div className="space-y-2"><Label>任职要求 *</Label><Textarea value={formData.requirements} onChange={(event) => updateField('requirements', event.target.value)} placeholder="列出候选人需要具备的技能和经验..." rows={5} required /></div></CardContent></Card>
    <Card><CardHeader className="flex flex-row items-start justify-between space-y-0"><div><CardTitle>面试工作流</CardTitle><CardDescription>按顺序配置面试环节，并为每个环节指定面试人</CardDescription></div><Button type="button" onClick={() => setStages((current) => [...current, newStage(current.length)])}><Plus className="mr-2 h-4 w-4" />添加环节</Button></CardHeader><CardContent className="space-y-3">{stages.map((stage, index) => <div key={stage.id} className="rounded-lg border bg-card p-4 shadow-sm"><div className="flex items-start gap-3"><div className="mt-2 text-muted-foreground"><GripVertical className="h-5 w-5" /></div><div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground">{index + 1}</div><div className="grid flex-1 gap-4 md:grid-cols-[1.2fr_1fr_110px_1.7fr] md:items-end"><div className="space-y-2"><Label>环节名称</Label><Input value={stage.name} onChange={(event) => updateStage(stage.id, { name: event.target.value })} placeholder="例如：部门面试" /></div><div className="space-y-2"><Label>环节类型</Label><select value={stage.type} onChange={(event) => updateStage(stage.id, { type: event.target.value })} className="h-10 w-full rounded-md border bg-background px-3 text-sm">{stageTypes.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div><div className="space-y-2"><Label>时长（分钟）</Label><Input type="number" min="15" step="15" value={stage.duration} onChange={(event) => updateStage(stage.id, { duration: event.target.value })} /></div><div className="space-y-2"><Label>面试人</Label><InterviewerPicker value={stage.interviewers} onChange={(interviewers) => updateStage(stage.id, { interviewers })} /></div></div><div className="flex gap-1"><Button type="button" variant="ghost" size="icon" aria-label="上移" disabled={index === 0} onClick={() => moveStage(index, -1)}><ArrowUp className="h-4 w-4" /></Button><Button type="button" variant="ghost" size="icon" aria-label="下移" disabled={index === stages.length - 1} onClick={() => moveStage(index, 1)}><ArrowDown className="h-4 w-4" /></Button><Button type="button" variant="ghost" size="icon" aria-label="删除" onClick={() => removeStage(stage.id)} className="text-destructive hover:text-destructive"><Trash2 className="h-4 w-4" /></Button></div></div></div>)}{!stages.length && <div className="rounded-lg border border-dashed p-10 text-center"><p className="text-sm text-muted-foreground">还没有面试环节</p><Button type="button" variant="link" onClick={() => setStages([newStage(0)])}>添加第一个环节</Button></div>}<p className="pt-2 text-xs text-muted-foreground">面试人来自公司组织架构，可按姓名、职位或部门搜索；一个环节支持配置多位面试人。</p></CardContent></Card>
    <Card><CardHeader><CardTitle>其他设置</CardTitle></CardHeader><CardContent><label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={formData.is_third_party_headhunter_enabled} onChange={(event) => updateField('is_third_party_headhunter_enabled', event.target.checked)} />开启第三方猎头协作</label></CardContent></Card><div className="flex justify-end gap-4"><Button type="button" variant="outline" onClick={() => router.back()} disabled={loading}>取消</Button><Button type="submit" disabled={loading}>{loading ? '创建中...' : '创建职位'}</Button></div>
  </form></div></MainLayout>;
}
