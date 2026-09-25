'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { ArrowLeft, CheckCircle, FilePenLine, Mail, Send, UserX } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';

interface OfferItem {
  id: string;
  candidate: {
    id?: string;
    name: string;
    phone?: string;
    email?: string;
  };
  job: {
    id?: string;
    title: string;
    location?: string;
  };
  status: string;
  status_label: string;
  latest_action?: string;
  offer_details?: Record<string, string>;
  updated_at?: string;
}

const tabs = [
  {
    value: 'pending',
    label: '待发Offer',
    statuses: [
      'department_interview_completed',
      'assessment_completed',
      'hr_reinterview_completed',
      'final_interview_completed',
      'verbal_offer_accepted',
      'offer_pending',
    ],
  },
  { value: 'approval', label: '审批中', statuses: ['offer_approval', 'offer_approval_rejected'] },
  { value: 'sent', label: '已发Offer', statuses: ['offer_sent'] },
  { value: 'closed', label: '结果', statuses: ['offer_accepted', 'offer_rejected', 'offer_not_agreed'] },
];

type DialogMode = 'record' | 'approval' | 'edit' | 'send' | 'feedback' | 'reject';

export default function OffersPage() {
  const router = useRouter();
  const [items, setItems] = useState<OfferItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('pending');
  const [selected, setSelected] = useState<OfferItem | null>(null);
  const [dialogMode, setDialogMode] = useState<DialogMode | null>(null);
  const [form, setForm] = useState({
    salary: '',
    company: '',
    department: '',
    business: '',
    base_city: '',
    contract_entity: '',
    past_experience: '',
    personal_info: '',
    talent_type: '',
    interview_evaluation: '',
    assessment_score: '',
    start_date: '',
    offer_letter_url: '',
    valid_until: '',
    feedback_result: 'accept',
    feedback_reason: '',
    signature_url: '',
  });

  const visibleItems = useMemo(() => {
    const current = tabs.find((tab) => tab.value === activeTab);
    return items.filter((item) => current?.statuses.includes(item.status));
  }, [activeTab, items]);

  const fetchOffers = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/offers?limit=100`);
      if (response.ok) {
        const result = await response.json();
        setItems(result.data?.items || []);
      }
    } catch (error) {
      console.error('Failed to fetch offers:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchOffers();
  }, [fetchOffers]);

  const openDialog = (item: OfferItem, mode: DialogMode) => {
    setSelected(item);
    setDialogMode(mode);
    setForm((current) => ({
      ...current,
      department: current.department || item.job.title,
      base_city: current.base_city || item.job.location || '',
    }));
  };

  const runAction = async (item: OfferItem, path: string, body: Record<string, unknown>) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/offers/applications/${item.id}/${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '未知错误');
    }
  };

  const submitDialog = async () => {
    if (!selected || !dialogMode) return;

    try {
      if (dialogMode === 'record') {
        await runAction(selected, 'record-offer', {
          offer_details: {
            salary: form.salary,
            contract_entity: form.contract_entity,
            company: form.company,
            department: form.department,
            business: form.business,
            base_city: form.base_city,
            past_experience: form.past_experience,
            personal_info: form.personal_info,
            talent_type: form.talent_type,
            interview_evaluation: form.interview_evaluation,
            assessment_score: form.assessment_score,
            start_date: form.start_date,
          },
        });
      } else if (dialogMode === 'approval') {
        await runAction(selected, 'submit-offer-approval', {
          offer_details: {
            salary: form.salary,
            contract_entity: form.contract_entity,
            company: form.company,
            department: form.department,
            business: form.business,
            base_city: form.base_city,
            talent_type: form.talent_type,
            interview_evaluation: form.interview_evaluation,
            assessment_score: form.assessment_score,
          },
        });
      } else if (dialogMode === 'edit') {
        await runAction(selected, 'edit-offer', {
          offer_details: {
            salary: form.salary,
            contract_entity: form.contract_entity,
            company: form.company,
            department: form.department,
            base_city: form.base_city,
            start_date: form.start_date,
            talent_type: form.talent_type,
            past_experience: form.past_experience,
            personal_info: form.personal_info,
          },
        });
      } else if (dialogMode === 'send') {
        await runAction(selected, 'send-offer', {
          offer_letter_url: form.offer_letter_url || 'system-generated-offer.pdf',
          valid_until: new Date(form.valid_until || Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
          template_name: '社会招聘offer模板',
          cc_recipients: [],
        });
      } else if (dialogMode === 'reject') {
        await runAction(selected, 'reject-at-offer-stage', {
          reason: form.feedback_reason || 'Offer没谈拢',
        });
      } else if (form.feedback_result === 'accept') {
        await runAction(selected, 'candidate-accept-offer', {
          signature_url: form.signature_url || undefined,
        });
      } else {
        await runAction(selected, 'candidate-decline-offer', {
          reason: form.feedback_reason || '候选人拒绝',
        });
      }

      setDialogMode(null);
      setSelected(null);
      await fetchOffers();
    } catch (error) {
      alert(`操作失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  };

  const quickAction = async (item: OfferItem, path: string, body: Record<string, unknown> = {}) => {
    try {
      await runAction(item, path, body);
      await fetchOffers();
    } catch (error) {
      alert(`操作失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  };

  const renderActions = (item: OfferItem) => (
    <div className="flex flex-wrap justify-end gap-2">
      {[
        'department_interview_completed',
        'assessment_completed',
        'hr_reinterview_completed',
        'final_interview_completed',
      ].includes(item.status) && (
        <Button size="sm" variant="outline" onClick={() => openDialog(item, 'record')} className="gap-2">
          <FilePenLine className="h-4 w-4" />
          录入Offer
        </Button>
      )}
      {['verbal_offer_accepted', 'offer_pending'].includes(item.status) && (
        <Button size="sm" variant="outline" onClick={() => openDialog(item, 'approval')} className="gap-2">
          <FilePenLine className="h-4 w-4" />
          发起审批
        </Button>
      )}
      {item.status === 'offer_approval' && (
        <Button size="sm" onClick={() => quickAction(item, 'approve-offer', { comments: '审批通过' })} className="gap-2">
          <CheckCircle className="h-4 w-4" />
          审批通过
        </Button>
      )}
      {['verbal_offer_accepted', 'offer_approval', 'offer_pending', 'offer_approval_rejected'].includes(item.status) && (
        <Button size="sm" variant="outline" onClick={() => openDialog(item, 'edit')} className="gap-2">
          <FilePenLine className="h-4 w-4" />
          编辑录用信息
        </Button>
      )}
      {item.status === 'offer_pending' && (
        <Button size="sm" onClick={() => openDialog(item, 'send')} className="gap-2">
          <Mail className="h-4 w-4" />
          发送Offer
        </Button>
      )}
      {item.status === 'offer_sent' && (
        <Button size="sm" variant="outline" onClick={() => openDialog(item, 'feedback')} className="gap-2">
          <CheckCircle className="h-4 w-4" />
          记录候选人反馈
        </Button>
      )}
      {['offer_pending', 'offer_sent', 'offer_approval', 'offer_approval_rejected'].includes(item.status) && (
        <Button size="sm" variant="destructive" onClick={() => openDialog(item, 'reject')} className="gap-2">
          <UserX className="h-4 w-4" />
          Offer没谈拢
        </Button>
      )}
    </div>
  );

  const dialogTitle =
    dialogMode === 'record' ? '录入Offer' :
    dialogMode === 'approval' ? '发起Offer审批' :
    dialogMode === 'edit' ? '编辑录用信息' :
    dialogMode === 'feedback' ? '记录候选人反馈' :
    dialogMode === 'reject' ? 'Offer没谈拢' :
    '发送Offer';

  return (
    <div className="p-8">
      <Button variant="ghost" onClick={() => router.push('/dashboard')} className="mb-4 -ml-2 gap-2">
        <ArrowLeft className="h-4 w-4" />
        返回首页
      </Button>

      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Offer管理</h1>
          <p className="mt-2 text-gray-600">发起审批、编辑录用信息、发送Offer并记录候选人反馈</p>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          {tabs.map((tab) => (
            <TabsTrigger key={tab.value} value={tab.value}>
              {tab.label}
            </TabsTrigger>
          ))}
        </TabsList>

        {tabs.map((tab) => (
          <TabsContent key={tab.value} value={tab.value} className="mt-6">
            {loading ? (
              <Card className="p-12 text-center text-gray-500">加载中...</Card>
            ) : visibleItems.length === 0 ? (
              <Card className="p-12 text-center text-gray-500">暂无记录</Card>
            ) : (
              <div className="grid gap-4">
                {visibleItems.map((item) => (
                  <Card key={item.id} className="p-5">
                    <div className="flex flex-wrap items-start justify-between gap-4">
                      <div>
                        <div className="mb-2 flex flex-wrap items-center gap-2">
                          <h3 className="text-lg font-semibold text-gray-900">{item.candidate.name}</h3>
                          <Badge>{item.status_label}</Badge>
                        </div>
                        <div className="text-sm text-gray-600">{item.job.title}</div>
                        <div className="mt-2 text-sm text-gray-500">
                          {item.candidate.email || '邮箱未填写'} · {item.updated_at ? new Date(item.updated_at).toLocaleString('zh-CN') : '-'}
                        </div>
                        {item.latest_action && <div className="mt-2 text-sm text-gray-500">{item.latest_action}</div>}
                      </div>
                      {renderActions(item)}
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        ))}
      </Tabs>

      <Dialog open={dialogMode !== null} onOpenChange={(open) => !open && setDialogMode(null)}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>{dialogTitle}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-2 md:grid-cols-2">
            {dialogMode === 'send' ? (
              <>
                <div className="grid gap-2 md:col-span-2">
                  <Label>Offer附件地址</Label>
                  <Input value={form.offer_letter_url} onChange={(event) => setForm({ ...form, offer_letter_url: event.target.value })} placeholder="系统生成附件或上传附件地址" />
                </div>
                <div className="grid gap-2">
                  <Label>有效期至</Label>
                  <Input type="datetime-local" value={form.valid_until} onChange={(event) => setForm({ ...form, valid_until: event.target.value })} />
                </div>
              </>
            ) : dialogMode === 'feedback' || dialogMode === 'reject' ? (
              <>
                {dialogMode === 'feedback' && (
                <div className="grid gap-2">
                  <Label>反馈结果</Label>
                  <select
                    className="h-10 rounded-md border border-input bg-background px-3 text-sm"
                    value={form.feedback_result}
                    onChange={(event) => setForm({ ...form, feedback_result: event.target.value })}
                  >
                    <option value="accept">接受Offer</option>
                    <option value="decline">拒绝Offer</option>
                  </select>
                </div>
                )}
                {dialogMode === 'feedback' && form.feedback_result === 'accept' ? (
                  <div className="grid gap-2">
                    <Label>签署文件地址</Label>
                    <Input value={form.signature_url} onChange={(event) => setForm({ ...form, signature_url: event.target.value })} placeholder="可选" />
                  </div>
                ) : (
                  <div className="grid gap-2 md:col-span-2">
                    <Label>{dialogMode === 'reject' ? '没谈拢原因' : '拒绝原因'}</Label>
                    <Textarea rows={4} value={form.feedback_reason} onChange={(event) => setForm({ ...form, feedback_reason: event.target.value })} />
                  </div>
                )}
              </>
            ) : (
              <>
                <div className="grid gap-2">
                  <Label>录用公司</Label>
                  <Input value={form.company} onChange={(event) => setForm({ ...form, company: event.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label>劳动合同主体</Label>
                  <Input value={form.contract_entity} onChange={(event) => setForm({ ...form, contract_entity: event.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label>录用部门</Label>
                  <Input value={form.department} onChange={(event) => setForm({ ...form, department: event.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label>录用业务</Label>
                  <Input value={form.business} onChange={(event) => setForm({ ...form, business: event.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label>Base地点</Label>
                  <Input value={form.base_city} onChange={(event) => setForm({ ...form, base_city: event.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label>Offer薪资</Label>
                  <Input type="number" value={form.salary} onChange={(event) => setForm({ ...form, salary: event.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label>人才类别</Label>
                  <Input value={form.talent_type} onChange={(event) => setForm({ ...form, talent_type: event.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label>商推得分</Label>
                  <Input value={form.assessment_score} onChange={(event) => setForm({ ...form, assessment_score: event.target.value })} placeholder="如 5.5（中高）" />
                </div>
                <div className="grid gap-2">
                  <Label>预计入职日期</Label>
                  <Input type="date" value={form.start_date} onChange={(event) => setForm({ ...form, start_date: event.target.value })} />
                </div>
                <div className="grid gap-2 md:col-span-2">
                  <Label>过往履历</Label>
                  <Textarea rows={3} value={form.past_experience} onChange={(event) => setForm({ ...form, past_experience: event.target.value })} />
                </div>
                <div className="grid gap-2 md:col-span-2">
                  <Label>个人信息</Label>
                  <Textarea rows={3} value={form.personal_info} onChange={(event) => setForm({ ...form, personal_info: event.target.value })} />
                </div>
                <div className="grid gap-2 md:col-span-2">
                  <Label>面试评价汇总</Label>
                  <Textarea rows={4} value={form.interview_evaluation} onChange={(event) => setForm({ ...form, interview_evaluation: event.target.value })} />
                </div>
              </>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogMode(null)}>取消</Button>
            <Button onClick={submitDialog} className="gap-2">
              <Send className="h-4 w-4" />
              提交
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
