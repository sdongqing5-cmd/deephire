'use client';

import { useState } from 'react';
import { ArrowLeft, Search } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';

interface CandidateResult {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  current_company?: string;
  current_title?: string;
  years_of_experience?: number;
  location?: string;
  status: string;
  tags?: string[];
  score?: number;
}

export default function SearchPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<CandidateResult[]>([]);
  const [form, setForm] = useState({
    query: '',
    name: '',
    phone: '',
    email: '',
    skills: '',
    education: '',
    age: '',
    minExperience: '',
  });

  const buildQuery = () =>
    [
      form.query,
      form.name && `姓名 ${form.name}`,
      form.phone && `手机号 ${form.phone}`,
      form.email && `邮箱 ${form.email}`,
      form.skills && `技术 ${form.skills}`,
      form.education && `学历 ${form.education}`,
      form.age && `年龄 ${form.age}`,
    ].filter(Boolean).join(' ');

  const fallbackSearch = async () => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/applications?page_size=100`);
    if (!response.ok) return [];

    const payload = await response.json();
    const query = buildQuery().toLowerCase();
    return (payload.data?.items || [])
      .map((item: { candidate: CandidateResult; status: string; status_label: string; id: string }) => ({
        ...item.candidate,
        id: item.id,
        status: item.status_label || item.status,
      }))
      .filter((candidate: CandidateResult) =>
        [
          candidate.name,
          candidate.email,
          candidate.phone,
          candidate.current_company,
          candidate.current_title,
          candidate.location,
          ...(candidate.tags || []),
        ].some((value) => value?.toLowerCase().includes(query))
      );
  };

  const handleSearch = async () => {
    setLoading(true);
    try {
      const query = buildQuery();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/search/candidates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          search_type: 'hybrid',
          size: 30,
          filters: form.minExperience ? { min_experience: parseInt(form.minExperience, 10) } : undefined,
        }),
      });

      if (response.ok) {
        const payload = await response.json();
        setResults(payload.results || []);
      } else {
        setResults(await fallbackSearch());
      }
    } catch {
      setResults(await fallbackSearch());
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <Button variant="ghost" onClick={() => router.push('/dashboard')} className="mb-4 -ml-2 gap-2">
        <ArrowLeft className="h-4 w-4" />
        返回首页
      </Button>

      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">简历库搜索</h1>
        <p className="mt-2 text-gray-600">按关键词、技术名词、学历、年龄、姓名、手机号和邮箱搜索候选人</p>
      </div>

      <Card className="p-5">
        <div className="grid gap-4 md:grid-cols-3">
          <div className="grid gap-2 md:col-span-3">
            <Label>关键词</Label>
            <Input value={form.query} onChange={(event) => setForm({ ...form, query: event.target.value })} placeholder="如 Python 后端 微服务" />
          </div>
          <Input placeholder="姓名" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
          <Input placeholder="手机号" value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} />
          <Input placeholder="邮箱" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} />
          <Input placeholder="技术类名词" value={form.skills} onChange={(event) => setForm({ ...form, skills: event.target.value })} />
          <Input placeholder="学历" value={form.education} onChange={(event) => setForm({ ...form, education: event.target.value })} />
          <Input placeholder="年龄" value={form.age} onChange={(event) => setForm({ ...form, age: event.target.value })} />
          <Input type="number" placeholder="最低工作年限" value={form.minExperience} onChange={(event) => setForm({ ...form, minExperience: event.target.value })} />
        </div>
        <div className="mt-4 flex justify-end">
          <Button onClick={handleSearch} disabled={loading} className="gap-2">
            <Search className="h-4 w-4" />
            {loading ? '搜索中...' : '搜索'}
          </Button>
        </div>
      </Card>

      <div className="mt-6 grid gap-4">
        {results.map((candidate) => (
          <Card key={candidate.id} className="p-5">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-semibold">{candidate.name}</h3>
                  <Badge variant="secondary">{candidate.status}</Badge>
                </div>
                <div className="mt-2 text-sm text-gray-600">
                  {candidate.current_title || '职位未知'} · {candidate.current_company || '公司未知'} · {candidate.years_of_experience ?? 0} 年经验
                </div>
                <div className="mt-2 text-sm text-gray-500">
                  {candidate.phone || '手机号未知'} · {candidate.email || '邮箱未知'} · {candidate.location || '地点未知'}
                </div>
              </div>
              {typeof candidate.score === 'number' && (
                <Badge>匹配度 {candidate.score.toFixed(2)}</Badge>
              )}
            </div>
          </Card>
        ))}
        {!loading && results.length === 0 && (
          <Card className="p-12 text-center text-gray-500">暂无搜索结果</Card>
        )}
      </div>
    </div>
  );
}
