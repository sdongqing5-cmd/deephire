'use client';

import { useEffect, useMemo, useState } from 'react';
import { ArrowLeft, Mail, Save, Send } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

const defaultTemplates = [
  {
    id: 'candidate_onsite',
    name: '候选人现场面试通知',
    audience: 'candidate',
    interviewType: 'onsite',
    subject: '面试邀请：{jobTitle}',
    body: '{candidateName}您好，请于{time}到{location}参加现场面试。',
  },
  {
    id: 'candidate_video',
    name: '候选人视频面试通知',
    audience: 'candidate',
    interviewType: 'video',
    subject: '视频面试邀请：{jobTitle}',
    body: '{candidateName}您好，请于{time}通过会议链接参加视频面试：{meetingLink}',
  },
  {
    id: 'interviewer_onsite',
    name: '面试官现场面试通知',
    audience: 'interviewer',
    interviewType: 'onsite',
    subject: '面试安排：{candidateName}',
    body: '请于{time}在{location}面试候选人{candidateName}，应聘职位：{jobTitle}。',
  },
  {
    id: 'interviewer_video',
    name: '面试官视频面试通知',
    audience: 'interviewer',
    interviewType: 'video',
    subject: '视频面试安排：{candidateName}',
    body: '请于{time}通过会议链接面试候选人{candidateName}：{meetingLink}',
  },
];

type NotificationTemplate = typeof defaultTemplates[number];

export default function NotificationsPage() {
  const router = useRouter();
  const [templates, setTemplates] = useState<NotificationTemplate[]>(defaultTemplates);
  const [sendDialogOpen, setSendDialogOpen] = useState(false);
  const [selectedCandidateTemplate, setSelectedCandidateTemplate] = useState('candidate_onsite');
  const [selectedInterviewerTemplate, setSelectedInterviewerTemplate] = useState('interviewer_onsite');
  const [mailbox, setMailbox] = useState({
    provider: '163',
    email: '',
    authCode: '',
  });
  const [draft, setDraft] = useState({
    candidateName: '',
    candidateEmail: '',
    interviewerName: '',
    interviewerEmail: '',
    jobTitle: '',
    interviewType: 'onsite',
    time: '',
    location: '',
    meetingLink: '',
  });

  const filteredTemplates = useMemo(
    () => templates.filter((template) => template.interviewType === draft.interviewType),
    [draft.interviewType, templates]
  );

  useEffect(() => {
    const loadData = async () => {
      try {
        const [templateResponse, mailboxResponse] = await Promise.all([
          fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/notifications/templates`),
          fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/notifications/mailbox`),
        ]);
        if (templateResponse.ok) {
          const payload = await templateResponse.json();
          setTemplates(payload.data || defaultTemplates);
        }
        if (mailboxResponse.ok) {
          const payload = await mailboxResponse.json();
          if (payload.data) {
            setMailbox((current) => ({
              ...current,
              provider: payload.data.provider,
              email: payload.data.email,
            }));
          }
        }
      } catch (error) {
        console.error('Failed to load notification settings:', error);
      }
    };

    loadData();
  }, []);

  const saveTemplate = (id: string, subject: string, body: string) => {
    setTemplates((current) =>
      current.map((template) => template.id === id ? { ...template, subject, body } : template)
    );
  };

  const persistTemplate = async (template: NotificationTemplate) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/notifications/templates`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: template.id,
        name: template.name,
        audience: template.audience,
        interview_type: template.interviewType,
        subject: template.subject,
        body: template.body,
      }),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => null);
      throw new Error(error?.detail || '模板保存失败');
    }
  };

  const saveMailbox = async () => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/notifications/mailbox`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(mailbox),
    });
    if (response.ok) {
      alert('邮箱绑定已保存');
    } else {
      const error = await response.json().catch(() => null);
      alert(`邮箱绑定失败: ${error?.detail || '请检查配置'}`);
    }
  };

  const handleSaveAndSend = () => {
    setSelectedCandidateTemplate(filteredTemplates.find((template) => template.audience === 'candidate')?.id || '');
    setSelectedInterviewerTemplate(filteredTemplates.find((template) => template.audience === 'interviewer')?.id || '');
    setSendDialogOpen(true);
  };

  const sendNotification = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/notifications/send-interview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          candidate_template_id: selectedCandidateTemplate,
          interviewer_template_id: selectedInterviewerTemplate,
          context: {
            ...draft,
            interviewType: draft.interviewType,
          },
        }),
      });
      const payload = await response.json().catch(() => null);
      if (response.ok && payload?.data?.status === 'sent') {
        alert('邮件已发送给候选人和面试官');
        setSendDialogOpen(false);
      } else {
        alert(`发送失败: ${payload?.message || payload?.detail || '请检查邮箱配置和收件人'}`);
      }
    } catch {
      alert('发送失败，请稍后重试');
    }
  };

  return (
    <div className="p-8">
      <Button variant="ghost" onClick={() => router.push('/dashboard')} className="mb-4 -ml-2 gap-2">
        <ArrowLeft className="h-4 w-4" />
        返回首页
      </Button>

      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">通知管理</h1>
        <p className="mt-2 text-gray-600">维护面试通知模板，绑定邮箱，并同时通知候选人和面试官</p>
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <Card className="p-5 xl:col-span-1">
          <h2 className="mb-4 text-lg font-semibold">绑定邮箱</h2>
          <div className="grid gap-4">
            <div className="grid gap-2">
              <Label>邮箱服务</Label>
              <select
                className="h-10 rounded-md border border-input bg-background px-3 text-sm"
                value={mailbox.provider}
                onChange={(event) => setMailbox({ ...mailbox, provider: event.target.value })}
              >
                <option value="163">163邮箱</option>
                <option value="qq">QQ邮箱</option>
                <option value="gmail">Gmail</option>
              </select>
            </div>
            <div className="grid gap-2">
              <Label>发件邮箱</Label>
              <Input value={mailbox.email} onChange={(event) => setMailbox({ ...mailbox, email: event.target.value })} />
            </div>
            <div className="grid gap-2">
              <Label>授权码</Label>
              <Input type="password" value={mailbox.authCode} onChange={(event) => setMailbox({ ...mailbox, authCode: event.target.value })} />
            </div>
            <Button onClick={saveMailbox}>保存邮箱</Button>
          </div>
        </Card>

        <Card className="p-5 xl:col-span-2">
          <h2 className="mb-4 text-lg font-semibold">面试通知</h2>
          <div className="grid gap-4 md:grid-cols-2">
            <Input placeholder="候选人姓名" value={draft.candidateName} onChange={(event) => setDraft({ ...draft, candidateName: event.target.value })} />
            <Input placeholder="候选人邮箱" value={draft.candidateEmail} onChange={(event) => setDraft({ ...draft, candidateEmail: event.target.value })} />
            <Input placeholder="面试官姓名" value={draft.interviewerName} onChange={(event) => setDraft({ ...draft, interviewerName: event.target.value })} />
            <Input placeholder="面试官邮箱" value={draft.interviewerEmail} onChange={(event) => setDraft({ ...draft, interviewerEmail: event.target.value })} />
            <Input placeholder="职位名称" value={draft.jobTitle} onChange={(event) => setDraft({ ...draft, jobTitle: event.target.value })} />
            <select
              className="h-10 rounded-md border border-input bg-background px-3 text-sm"
              value={draft.interviewType}
              onChange={(event) => setDraft({ ...draft, interviewType: event.target.value })}
            >
              <option value="onsite">现场面试</option>
              <option value="video">视频面试</option>
            </select>
            <Input type="datetime-local" value={draft.time} onChange={(event) => setDraft({ ...draft, time: event.target.value })} />
            <Input placeholder="地点" value={draft.location} onChange={(event) => setDraft({ ...draft, location: event.target.value })} />
            <Input className="md:col-span-2" placeholder="视频会议链接" value={draft.meetingLink} onChange={(event) => setDraft({ ...draft, meetingLink: event.target.value })} />
          </div>
          <div className="mt-4 flex justify-end">
            <Button onClick={handleSaveAndSend} className="gap-2">
              <Save className="h-4 w-4" />
              保存并发送
            </Button>
          </div>
        </Card>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        {templates.map((template) => (
          <Card key={template.id} className="p-5">
            <div className="mb-3 flex items-center gap-2">
              <Mail className="h-4 w-4 text-gray-500" />
              <h3 className="font-semibold">{template.name}</h3>
            </div>
            <Input
              className="mb-3"
              value={template.subject}
              onChange={(event) => saveTemplate(template.id, event.target.value, template.body)}
            />
            <Textarea
              rows={5}
              value={template.body}
              onChange={(event) => saveTemplate(template.id, template.subject, event.target.value)}
            />
            <div className="mt-3 flex justify-end">
              <Button
                variant="outline"
                size="sm"
                onClick={async () => {
                  try {
                    await persistTemplate(template);
                    alert('模板已保存');
                  } catch (error) {
                    alert(error instanceof Error ? error.message : '模板保存失败');
                  }
                }}
              >
                保存模板
              </Button>
            </div>
          </Card>
        ))}
      </div>

      <Dialog open={sendDialogOpen} onOpenChange={setSendDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>选择模板并发送邮件</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-2">
            <div className="grid gap-2">
              <Label>候选人模板</Label>
              <select className="h-10 rounded-md border border-input bg-background px-3 text-sm" value={selectedCandidateTemplate} onChange={(event) => setSelectedCandidateTemplate(event.target.value)}>
                {filteredTemplates.filter((template) => template.audience === 'candidate').map((template) => (
                  <option key={template.id} value={template.id}>{template.name}</option>
                ))}
              </select>
            </div>
            <div className="grid gap-2">
              <Label>面试官模板</Label>
              <select className="h-10 rounded-md border border-input bg-background px-3 text-sm" value={selectedInterviewerTemplate} onChange={(event) => setSelectedInterviewerTemplate(event.target.value)}>
                {filteredTemplates.filter((template) => template.audience === 'interviewer').map((template) => (
                  <option key={template.id} value={template.id}>{template.name}</option>
                ))}
              </select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setSendDialogOpen(false)}>取消</Button>
            <Button onClick={sendNotification} className="gap-2">
              <Send className="h-4 w-4" />
              发送邮件
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
