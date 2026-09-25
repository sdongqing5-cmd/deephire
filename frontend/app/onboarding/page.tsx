'use client';

import { useCallback, useEffect, useState } from 'react';
import { ArrowLeft, CalendarClock, CheckCircle, ClipboardList, UserX } from 'lucide-react';
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
import { Textarea } from '@/components/ui/textarea';

interface OnboardingItem {
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
  updated_at?: string;
}

export default function OnboardingPage() {
  const router = useRouter();
  const [items, setItems] = useState<OnboardingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<OnboardingItem | null>(null);
  const [dialogMode, setDialogMode] = useState<'prepare' | 'notify' | 'reschedule' | 'cancel' | 'complete' | 'attachment' | null>(null);
  const [attachmentFile, setAttachmentFile] = useState<File | null>(null);
  const [form, setForm] = useState({
    expected_start_date: '',
    actual_start_date: '',
    due_date: '',
    reason: '',
    notes: '',
    attachment_name: '',
    attachment_url: '',
  });

  const fetchItems = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/offers/onboarding?limit=100`);
      if (response.ok) {
        const result = await response.json();
        setItems(result.data?.items || []);
      }
    } catch (error) {
      console.error('Failed to fetch onboarding items:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchItems();
  }, [fetchItems]);

  const openDialog = (item: OnboardingItem, mode: typeof dialogMode) => {
    setSelected(item);
    setDialogMode(mode);
    if (mode === 'attachment') {
      setAttachmentFile(null);
    }
  };

  const runAction = async (item: OnboardingItem, path: string, body: Record<string, unknown>) => {
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
      if (dialogMode === 'prepare') {
        await runAction(selected, 'prepare-onboarding', {
          expected_start_date: new Date(form.expected_start_date).toISOString(),
        });
      } else if (dialogMode === 'notify') {
        await runAction(selected, 'notify-info-collection', {
          due_date: form.due_date ? new Date(form.due_date).toISOString() : undefined,
          notes: form.notes || undefined,
        });
      } else if (dialogMode === 'reschedule') {
        await runAction(selected, 'reschedule-onboarding', {
          expected_start_date: new Date(form.expected_start_date).toISOString(),
          reason: form.reason || undefined,
        });
      } else if (dialogMode === 'cancel') {
        await runAction(selected, 'cancel-onboarding', {
          reason: form.reason || '取消入职',
        });
      } else if (dialogMode === 'attachment') {
        if (attachmentFile) {
          const uploadForm = new FormData();
          uploadForm.append('name', form.attachment_name || attachmentFile.name);
          uploadForm.append('attachment_file', attachmentFile);
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/offers/applications/${selected.id}/onboarding-attachment-upload`, {
            method: 'POST',
            body: uploadForm,
          });
          if (!response.ok) {
            const error = await response.json().catch(() => null);
            throw new Error(error?.detail || '附件上传失败');
          }
        } else {
          await runAction(selected, 'onboarding-attachment', {
            name: form.attachment_name || '入职附件',
            url: form.attachment_url,
          });
        }
      } else {
        await runAction(selected, 'complete-onboarding', {
          actual_start_date: new Date(form.actual_start_date).toISOString(),
        });
      }

      setDialogMode(null);
      setSelected(null);
      setAttachmentFile(null);
      await fetchItems();
    } catch (error) {
      alert(`操作失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  };

  const renderActions = (item: OnboardingItem) => (
    <div className="flex flex-wrap justify-end gap-2">
      {item.status === 'offer_accepted' && (
        <Button size="sm" onClick={() => openDialog(item, 'prepare')} className="gap-2">
          <ClipboardList className="h-4 w-4" />
          转入待入职
        </Button>
      )}
      {item.status === 'pending_onboard' && (
        <>
          <Button size="sm" variant="outline" onClick={() => openDialog(item, 'notify')} className="gap-2">
            <ClipboardList className="h-4 w-4" />
            通知采集信息
          </Button>
          <Button size="sm" variant="outline" onClick={() => openDialog(item, 'reschedule')} className="gap-2">
            <CalendarClock className="h-4 w-4" />
            改期入职
          </Button>
          <Button size="sm" variant="outline" onClick={() => openDialog(item, 'attachment')} className="gap-2">
            <ClipboardList className="h-4 w-4" />
            上传附件
          </Button>
          <Button size="sm" variant="destructive" onClick={() => openDialog(item, 'cancel')} className="gap-2">
            <UserX className="h-4 w-4" />
            取消入职
          </Button>
          <Button size="sm" onClick={() => openDialog(item, 'complete')} className="gap-2">
            <CheckCircle className="h-4 w-4" />
            已入职
          </Button>
        </>
      )}
    </div>
  );

  return (
    <div className="p-8">
      <Button variant="ghost" onClick={() => router.push('/dashboard')} className="mb-4 -ml-2 gap-2">
        <ArrowLeft className="h-4 w-4" />
        返回首页
      </Button>

      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">入职管理</h1>
        <p className="mt-2 text-gray-600">跟进已接受Offer候选人的信息采集、入职改期、取消和入职确认</p>
      </div>

      <Card className="mb-4 border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
        Offer发出后如薪资变动，请删除旧Offer和待入职记录后，从应聘者重新转移到“接受口头Offer”，重新审批、编辑并发送Offer，确保数据同步给组织人事与薪酬模块。
      </Card>

      {loading ? (
        <Card className="p-12 text-center text-gray-500">加载中...</Card>
      ) : items.length === 0 ? (
        <Card className="p-12 text-center text-gray-500">暂无待入职记录</Card>
      ) : (
        <div className="grid gap-4">
          {items.map((item) => (
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

      <Dialog open={dialogMode !== null} onOpenChange={(open) => !open && setDialogMode(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {dialogMode === 'prepare'
                ? '转入待入职'
                : dialogMode === 'notify'
                  ? '通知采集信息'
                  : dialogMode === 'reschedule'
                    ? '改期入职'
                    : dialogMode === 'cancel'
                      ? '取消入职'
                      : dialogMode === 'attachment'
                        ? '上传入职附件'
                        : '确认已入职'}
            </DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-2">
            {['prepare', 'reschedule'].includes(dialogMode || '') && (
              <div className="grid gap-2">
                <Label>预计入职日期</Label>
                <Input
                  type="datetime-local"
                  value={form.expected_start_date}
                  onChange={(event) => setForm({ ...form, expected_start_date: event.target.value })}
                />
              </div>
            )}
            {dialogMode === 'complete' && (
              <div className="grid gap-2">
                <Label>实际入职日期</Label>
                <Input
                  type="datetime-local"
                  value={form.actual_start_date}
                  onChange={(event) => setForm({ ...form, actual_start_date: event.target.value })}
                />
              </div>
            )}
            {dialogMode === 'notify' && (
              <>
                <div className="grid gap-2">
                  <Label>信息采集截止时间</Label>
                  <Input
                    type="datetime-local"
                    value={form.due_date}
                    onChange={(event) => setForm({ ...form, due_date: event.target.value })}
                  />
                </div>
                <div className="grid gap-2">
                  <Label>通知备注</Label>
                  <Textarea rows={4} value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} />
                </div>
              </>
            )}
            {dialogMode === 'attachment' && (
              <>
                <div className="grid gap-2">
                  <Label>附件名称</Label>
                  <Input
                    value={form.attachment_name}
                    onChange={(event) => setForm({ ...form, attachment_name: event.target.value })}
                    placeholder="如 身份证扫描件"
                  />
                </div>
                <div className="grid gap-2">
                  <Label>选择附件</Label>
                  <Input
                    type="file"
                    onChange={(event) => setAttachmentFile(event.target.files?.[0] || null)}
                  />
                </div>
                <div className="grid gap-2">
                  <Label>附件地址</Label>
                  <Input
                    value={form.attachment_url}
                    onChange={(event) => setForm({ ...form, attachment_url: event.target.value })}
                    placeholder="上传后的文件地址"
                  />
                </div>
              </>
            )}
            {['reschedule', 'cancel'].includes(dialogMode || '') && (
              <div className="grid gap-2">
                <Label>原因</Label>
                <Textarea rows={4} value={form.reason} onChange={(event) => setForm({ ...form, reason: event.target.value })} />
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogMode(null)}>取消</Button>
            <Button onClick={submitDialog}>确认</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
