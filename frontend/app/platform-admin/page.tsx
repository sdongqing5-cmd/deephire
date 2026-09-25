'use client';

import { useMemo, useState } from 'react';
import { MainLayout } from '@/components/layout/main-layout';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import {
  Activity,
  Building2,
  CheckCircle2,
  ChevronRight,
  CreditCard,
  Database,
  Download,
  Eye,
  MoreHorizontal,
  Plus,
  Search,
  ShieldCheck,
  Users,
  UserRound,
} from 'lucide-react';

type Section = 'overview' | 'tenants' | 'users' | 'billing' | 'audit';

const tenants = [
  { name: '星河科技', owner: '王敏', plan: '专业版', users: 38, jobs: 24, renewal: '2026-10-12', status: '正常', color: 'bg-emerald-50 text-emerald-700' },
  { name: '远景智能', owner: '李思远', plan: '企业版', users: 126, jobs: 67, renewal: '2026-11-03', status: '正常', color: 'bg-emerald-50 text-emerald-700' },
  { name: '云杉网络', owner: '赵琳', plan: '基础版', users: 12, jobs: 8, renewal: '2026-09-28', status: '即将到期', color: 'bg-amber-50 text-amber-700' },
  { name: '沐光咨询', owner: '陈凯', plan: '专业版', users: 54, jobs: 31, renewal: '2026-08-19', status: '已停用', color: 'bg-slate-100 text-slate-600' },
];

const platformUsers = [
  { name: '张晓岚', email: 'zhangxl@deephire.com', role: '超级管理员', lastSeen: '刚刚', status: '在线' },
  { name: '陈默', email: 'chenmo@deephire.com', role: '运营管理员', lastSeen: '10分钟前', status: '在线' },
  { name: '林夏', email: 'linxia@deephire.com', role: '客服管理员', lastSeen: '昨天 18:20', status: '离线' },
];

const auditLogs = [
  { action: '停用租户', detail: '沐光咨询（tenant_1042）', operator: '张晓岚', time: '2026-09-25 14:32', type: 'warning' },
  { action: '创建平台用户', detail: '林夏 / 客服管理员', operator: '陈默', time: '2026-09-25 11:08', type: 'info' },
  { action: '调整套餐', detail: '远景智能：专业版 → 企业版', operator: '张晓岚', time: '2026-09-24 17:46', type: 'success' },
  { action: '修改系统配置', detail: '开启候选人数据脱敏', operator: '张晓岚', time: '2026-09-24 15:20', type: 'info' },
];

function StatCard({ title, value, hint, icon: Icon, tone }: { title: string; value: string; hint: string; icon: React.ElementType; tone: string }) {
  return (
    <Card className="shadow-sm">
      <CardContent className="flex items-start justify-between p-5">
        <div>
          <p className="text-sm text-slate-500">{title}</p>
          <p className="mt-2 text-2xl font-semibold tracking-tight text-slate-900">{value}</p>
          <p className="mt-1 text-xs text-slate-500">{hint}</p>
        </div>
        <div className={`rounded-xl p-3 ${tone}`}><Icon className="h-5 w-5" /></div>
      </CardContent>
    </Card>
  );
}

function StatusBadge({ children, tone = 'green' }: { children: React.ReactNode; tone?: 'green' | 'amber' | 'gray' | 'blue' }) {
  const styles = { green: 'bg-emerald-50 text-emerald-700', amber: 'bg-amber-50 text-amber-700', gray: 'bg-slate-100 text-slate-600', blue: 'bg-blue-50 text-blue-700' };
  return <Badge className={`border-0 ${styles[tone]}`}>{children}</Badge>;
}

function Overview({ onNavigate }: { onNavigate: (section: Section) => void }) {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard title="活跃租户" value="128" hint="较上月 +12.4%" icon={Building2} tone="bg-blue-50 text-blue-600" />
        <StatCard title="平台用户" value="1,846" hint="本月新增 96 人" icon={Users} tone="bg-violet-50 text-violet-600" />
        <StatCard title="本月活跃职位" value="2,394" hint="较上月 +8.6%" icon={Activity} tone="bg-emerald-50 text-emerald-600" />
        <StatCard title="本月订阅收入" value="¥286,400" hint="较上月 +16.2%" icon={CreditCard} tone="bg-orange-50 text-orange-600" />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.4fr_1fr]">
        <Card className="shadow-sm">
          <CardHeader className="flex-row items-center justify-between pb-3"><div><CardTitle>租户概览</CardTitle><p className="mt-1 text-sm text-slate-500">最近活跃的企业客户</p></div><Button variant="ghost" size="sm" onClick={() => onNavigate('tenants')}>查看全部 <ChevronRight className="ml-1 h-4 w-4" /></Button></CardHeader>
          <CardContent><Table><TableHeader><TableRow><TableHead>企业</TableHead><TableHead>套餐</TableHead><TableHead>用户数</TableHead><TableHead>状态</TableHead></TableRow></TableHeader><TableBody>{tenants.slice(0, 3).map((tenant) => <TableRow key={tenant.name}><TableCell><div className="font-medium text-slate-900">{tenant.name}</div><div className="text-xs text-slate-500">负责人：{tenant.owner}</div></TableCell><TableCell>{tenant.plan}</TableCell><TableCell>{tenant.users}</TableCell><TableCell><StatusBadge tone={tenant.status === '正常' ? 'green' : 'amber'}>{tenant.status}</StatusBadge></TableCell></TableRow>)}</TableBody></Table></CardContent>
        </Card>
        <Card className="shadow-sm"><CardHeader><CardTitle>系统运行状态</CardTitle><p className="mt-1 text-sm text-slate-500">核心服务实时状态</p></CardHeader><CardContent className="space-y-4">{[['API 服务', '99.99%', '稳定'], ['数据库', '42%', '负载正常'], ['任务队列', '12 个', '运行中'], ['文件存储', '68%', '空间充足']].map(([label, value, status]) => <div key={label} className="flex items-center justify-between"><div className="flex items-center gap-3"><span className="h-2.5 w-2.5 rounded-full bg-emerald-500" /><div><p className="text-sm font-medium text-slate-800">{label}</p><p className="text-xs text-slate-500">{value}</p></div></div><span className="text-xs text-emerald-600">{status}</span></div>)}</CardContent></Card>
      </div>
      <Card className="shadow-sm"><CardHeader className="flex-row items-center justify-between pb-3"><div><CardTitle>最近平台操作</CardTitle><p className="mt-1 text-sm text-slate-500">平台管理员的关键操作记录</p></div><Button variant="ghost" size="sm" onClick={() => onNavigate('audit')}>查看审计日志 <ChevronRight className="ml-1 h-4 w-4" /></Button></CardHeader><CardContent><div className="divide-y">{auditLogs.slice(0, 3).map((log) => <div key={log.time} className="flex items-center justify-between py-3"><div className="flex items-center gap-3"><div className="rounded-full bg-slate-100 p-2"><ShieldCheck className="h-4 w-4 text-slate-500" /></div><div><p className="text-sm font-medium text-slate-800">{log.action}</p><p className="text-xs text-slate-500">{log.detail} · {log.operator}</p></div></div><span className="text-xs text-slate-400">{log.time}</span></div>)}</div></CardContent></Card>
    </div>
  );
}

function Tenants() {
  const [query, setQuery] = useState('');
  const filtered = useMemo(() => tenants.filter((tenant) => `${tenant.name}${tenant.owner}`.includes(query)), [query]);
  return <Card className="shadow-sm"><CardHeader className="flex-row items-center justify-between"><div><CardTitle>租户管理</CardTitle><p className="mt-1 text-sm text-slate-500">管理平台内所有企业客户及其订阅状态</p></div><Button><Plus className="mr-2 h-4 w-4" />创建租户</Button></CardHeader><CardContent><div className="mb-4 flex items-center gap-3"><div className="relative max-w-sm flex-1"><Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" /><Input className="pl-9" placeholder="搜索企业名称或负责人" value={query} onChange={(e) => setQuery(e.target.value)} /></div><Button variant="outline"><Download className="mr-2 h-4 w-4" />导出</Button></div><Table><TableHeader><TableRow><TableHead>企业</TableHead><TableHead>套餐</TableHead><TableHead>用户/职位</TableHead><TableHead>续费日期</TableHead><TableHead>状态</TableHead><TableHead className="text-right">操作</TableHead></TableRow></TableHeader><TableBody>{filtered.map((tenant) => <TableRow key={tenant.name}><TableCell><div className="font-medium">{tenant.name}</div><div className="text-xs text-slate-500">{tenant.owner}</div></TableCell><TableCell>{tenant.plan}</TableCell><TableCell>{tenant.users} / {tenant.jobs}</TableCell><TableCell>{tenant.renewal}</TableCell><TableCell><StatusBadge tone={tenant.status === '正常' ? 'green' : tenant.status === '即将到期' ? 'amber' : 'gray'}>{tenant.status}</StatusBadge></TableCell><TableCell className="text-right"><Button variant="ghost" size="sm"><Eye className="mr-1 h-4 w-4" />详情</Button><Button variant="ghost" size="icon"><MoreHorizontal className="h-4 w-4" /></Button></TableCell></TableRow>)}</TableBody></Table></CardContent></Card>;
}

function UsersPanel() { return <Card className="shadow-sm"><CardHeader className="flex-row items-center justify-between"><div><CardTitle>平台用户与权限</CardTitle><p className="mt-1 text-sm text-slate-500">管理能够访问平台管理后台的内部账号</p></div><Button><Plus className="mr-2 h-4 w-4" />邀请管理员</Button></CardHeader><CardContent><Table><TableHeader><TableRow><TableHead>用户</TableHead><TableHead>角色</TableHead><TableHead>最近登录</TableHead><TableHead>状态</TableHead><TableHead className="text-right">操作</TableHead></TableRow></TableHeader><TableBody>{platformUsers.map((user) => <TableRow key={user.email}><TableCell><div className="flex items-center gap-3"><div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-100 text-sm font-medium text-slate-600">{user.name.slice(0, 1)}</div><div><div className="font-medium">{user.name}</div><div className="text-xs text-slate-500">{user.email}</div></div></div></TableCell><TableCell>{user.role}</TableCell><TableCell>{user.lastSeen}</TableCell><TableCell><StatusBadge tone={user.status === '在线' ? 'green' : 'gray'}>{user.status}</StatusBadge></TableCell><TableCell className="text-right"><Button variant="ghost" size="sm">编辑</Button></TableCell></TableRow>)}</TableBody></Table></CardContent></Card>; }

function Billing() { return <div className="space-y-6"><div className="grid gap-4 md:grid-cols-3"><StatCard title="月度经常性收入" value="¥286,400" hint="128 个活跃订阅" icon={CreditCard} tone="bg-orange-50 text-orange-600" /><StatCard title="待续费租户" value="7" hint="未来 30 天内到期" icon={Activity} tone="bg-amber-50 text-amber-600" /><StatCard title="本月续费率" value="94.2%" hint="较上月 +2.1%" icon={CheckCircle2} tone="bg-emerald-50 text-emerald-600" /></div><Card className="shadow-sm"><CardHeader className="flex-row items-center justify-between"><div><CardTitle>套餐与订阅</CardTitle><p className="mt-1 text-sm text-slate-500">配置平台产品套餐和企业订阅</p></div><Button><Plus className="mr-2 h-4 w-4" />新增套餐</Button></CardHeader><CardContent><div className="grid gap-4 md:grid-cols-3">{[['基础版', '¥1,999/月', '42 个租户', '适合小型团队'], ['专业版', '¥4,999/月', '68 个租户', '适合成长型企业'], ['企业版', '定制报价', '18 个租户', '支持私有化与 SSO']].map(([name, price, count, desc]) => <div key={name} className="rounded-xl border p-5"><div className="flex items-center justify-between"><h3 className="font-semibold">{name}</h3><StatusBadge tone="blue">在售</StatusBadge></div><p className="mt-4 text-2xl font-semibold">{price}</p><p className="mt-2 text-sm text-slate-500">{count} · {desc}</p><Button variant="outline" className="mt-5 w-full">编辑套餐</Button></div>)}</div></CardContent></Card></div>; }

function Audit() { return <Card className="shadow-sm"><CardHeader className="flex-row items-center justify-between"><div><CardTitle>审计日志</CardTitle><p className="mt-1 text-sm text-slate-500">记录平台侧敏感操作，支持追溯与合规审查</p></div><Button variant="outline"><Download className="mr-2 h-4 w-4" />导出日志</Button></CardHeader><CardContent><Table><TableHeader><TableRow><TableHead>操作</TableHead><TableHead>详情</TableHead><TableHead>操作者</TableHead><TableHead>时间</TableHead><TableHead>结果</TableHead></TableRow></TableHeader><TableBody>{auditLogs.map((log) => <TableRow key={log.time}><TableCell className="font-medium">{log.action}</TableCell><TableCell>{log.detail}</TableCell><TableCell>{log.operator}</TableCell><TableCell>{log.time}</TableCell><TableCell><StatusBadge tone={log.type === 'warning' ? 'amber' : log.type === 'success' ? 'green' : 'blue'}>成功</StatusBadge></TableCell></TableRow>)}</TableBody></Table></CardContent></Card>; }

export default function PlatformAdminPage() {
  const [section, setSection] = useState<Section>('overview');
  const tabs: { key: Section; label: string; icon: React.ElementType }[] = [
    { key: 'overview', label: '总览', icon: Activity }, { key: 'tenants', label: '租户管理', icon: Building2 }, { key: 'users', label: '平台用户', icon: UserRound }, { key: 'billing', label: '套餐与订阅', icon: CreditCard }, { key: 'audit', label: '审计日志', icon: ShieldCheck },
  ];
  return <MainLayout requiredPath="/platform-admin"><div className="mx-auto max-w-[1440px] space-y-6"><div><div className="flex items-center justify-between"><div><div className="flex items-center gap-2 text-sm text-slate-500"><span>平台中心</span><ChevronRight className="h-4 w-4" /><span className="text-slate-900">管理后台</span></div><h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-900">平台管理后台</h1><p className="mt-1 text-slate-500">管理企业客户、平台账号、订阅产品与系统运行状态</p></div><div className="hidden items-center gap-2 rounded-lg border bg-white px-3 py-2 text-sm text-slate-600 shadow-sm md:flex"><Database className="h-4 w-4 text-emerald-500" />所有系统正常</div></div></div><div className="flex flex-wrap gap-2 border-b">{tabs.map(({ key, label, icon: Icon }) => <button key={key} onClick={() => setSection(key)} className={`flex items-center gap-2 border-b-2 px-3 py-3 text-sm font-medium transition-colors ${section === key ? 'border-slate-900 text-slate-900' : 'border-transparent text-slate-500 hover:text-slate-900'}`}><Icon className="h-4 w-4" />{label}</button>)}</div>{section === 'overview' && <Overview onNavigate={setSection} />}{section === 'tenants' && <Tenants />}{section === 'users' && <UsersPanel />}{section === 'billing' && <Billing />}{section === 'audit' && <Audit />}</div></MainLayout>;
}
