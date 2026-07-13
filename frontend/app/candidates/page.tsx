'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Search, Trash2, Upload, Users } from 'lucide-react';
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
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

interface ApplicationItem {
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
    tags?: string[];
  };
  job: {
    id: string;
    title: string;
  };
  status: string;
  status_label: string;
  applied_at: string;
}

interface JobOption {
  id: string;
  title: string;
}

const statusGroups = [
  { value: 'all', label: '全部状态' },
  { value: 'new', label: 'HR待查看' },
  { value: 'sent_to_interviewer', label: 'HR筛选通过' },
  { value: 'hr_rejected', label: 'HR筛选未通过' },
  { value: 'interview_intention_communication', label: '面试意向沟通中' },
  { value: 'interview_time_confirming', label: '候选人同意面试' },
  { value: 'candidate_declined_interview', label: '候选人放弃面试' },
  { value: 'department_interviewing', label: '面试中' },
  { value: 'department_interview_rejected', label: '面试失败' },
  { value: 'department_interview_completed', label: '面试通过' },
  { value: 'onboarded', label: '已入职' },
];

export default function CandidatesPage() {
  const router = useRouter();
  const [applications, setApplications] = useState<ApplicationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [jobs, setJobs] = useState<JobOption[]>([]);

  const fetchApplications = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (statusFilter !== 'all') params.append('status', statusFilter);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/applications?${params}`
      );
      if (response.ok) {
        const result = await response.json();
        setApplications(result.data.items || []);
      }
    } catch (error) {
      console.error('Failed to fetch candidates:', error);
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  const fetchJobs = useCallback(async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs?status=recruiting`
      );
      if (response.ok) {
        const data = await response.json();
        setJobs(data);
      }
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchApplications();
    fetchJobs();
  }, [fetchApplications, fetchJobs]);

  const handleSearch = () => {
    fetchApplications();
  };

  const filteredApplications = applications.filter((application) => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) return true;

    return [
      application.candidate.name,
      application.candidate.email,
      application.candidate.phone,
      application.candidate.current_company,
      application.job.title,
    ].some((value) => value?.toLowerCase().includes(query));
  });

  const handleUploadResume = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    for (const field of ['candidate_name', 'candidate_phone', 'candidate_email']) {
      if (formData.get(field) === '') {
        formData.delete(field);
      }
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/candidates/upload-resume`,
        {
          method: 'POST',
          body: formData,
        }
      );

      if (response.ok) {
        const result = await response.json();
        if (result.is_duplicate) {
          alert(`简历重复: ${result.duplicate_reason}`);
        } else {
          alert('简历上传成功！');
          setUploadDialogOpen(false);
          fetchApplications();
        }
      } else {
        const error = await response.json().catch(() => null);
        alert(`上传失败: ${error?.detail || '请稍后重试'}`);
      }
    } catch {
      alert('上传失败');
    }
  };

  const deleteCandidate = async (candidateId: string) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/candidates/${candidateId}`,
        { method: 'DELETE' }
      );

      if (response.ok) {
        await fetchApplications();
      } else {
        const error = await response.json().catch(() => null);
        alert(`删除失败: ${error?.detail || '请稍后重试'}`);
      }
    } catch {
      alert('删除失败');
    }
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">候选人管理</h1>
          <p className="text-gray-600 mt-2">管理简历解析结果、筛选流程和面试推进</p>
        </div>
        <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2">
              <Upload className="h-4 w-4" />
              上传简历
            </Button>
          </DialogTrigger>
          <DialogContent>
            <form onSubmit={handleUploadResume}>
              <DialogHeader>
                <DialogTitle>上传简历</DialogTitle>
                <DialogDescription>
                  上传候选人简历到指定职位
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div>
                  <Label htmlFor="job_id">选择职位 *</Label>
                  <Select name="job_id" required>
                    <SelectTrigger>
                      <SelectValue placeholder="选择职位" />
                    </SelectTrigger>
                    <SelectContent>
                      {jobs.map((job) => (
                        <SelectItem key={job.id} value={job.id}>
                          {job.title}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="candidate_name">候选人姓名</Label>
                  <Input id="candidate_name" name="candidate_name" />
                </div>

                <div>
                  <Label htmlFor="candidate_phone">手机号</Label>
                  <Input id="candidate_phone" name="candidate_phone" />
                </div>

                <div>
                  <Label htmlFor="candidate_email">邮箱</Label>
                  <Input
                    id="candidate_email"
                    name="candidate_email"
                    type="email"
                  />
                </div>

                <div>
                  <Label htmlFor="resume_file">简历文件 *</Label>
                  <Input
                    id="resume_file"
                    name="resume_file"
                    type="file"
                    accept=".pdf,.docx"
                    required
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    支持 PDF 和 DOCX 格式
                  </p>
                </div>
              </div>
              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setUploadDialogOpen(false)}
                >
                  取消
                </Button>
                <Button type="submit">上传</Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <Card className="p-4 mb-6">
        <div className="flex gap-4 items-center">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="搜索姓名、邮箱、电话、公司..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="pl-10"
            />
          </div>

          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="简历状态" />
            </SelectTrigger>
            <SelectContent>
              {statusGroups.map((status) => (
                <SelectItem key={status.value} value={status.value}>
                  {status.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Button onClick={handleSearch}>搜索</Button>
        </div>
      </Card>

      {/* Candidates List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      ) : filteredApplications.length === 0 ? (
        <Card className="p-12">
          <div className="text-center">
            <Users className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-4 text-lg font-medium text-gray-900">
              暂无简历
            </h3>
            <p className="mt-2 text-gray-500">上传第一份简历</p>
          </div>
        </Card>
      ) : (
        <div className="grid gap-4">
          {filteredApplications.map((application) => (
            <Card
              key={application.id}
              className="p-6 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => router.push(`/candidates/${application.id}`)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {application.candidate.name}
                    </h3>
                    <Badge variant="secondary">
                      {application.status_label || application.status}
                    </Badge>
                  </div>

                  <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                    <span>应聘职位：{application.job.title}</span>
                    {application.candidate.current_title && (
                      <>
                        <span>•</span>
                        <span>{application.candidate.current_title}</span>
                      </>
                    )}
                    {application.candidate.current_company && (
                      <>
                        <span>•</span>
                        <span>{application.candidate.current_company}</span>
                      </>
                    )}
                    {application.candidate.years_of_experience && (
                      <>
                        <span>•</span>
                        <span>{application.candidate.years_of_experience} 年经验</span>
                      </>
                    )}
                    {application.candidate.location && (
                      <>
                        <span>•</span>
                        <span>{application.candidate.location}</span>
                      </>
                    )}
                  </div>

                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    {application.candidate.phone && <span>{application.candidate.phone}</span>}
                    {application.candidate.email && (
                      <>
                        {application.candidate.phone && <span>•</span>}
                        <span>{application.candidate.email}</span>
                      </>
                    )}
                    <span>•</span>
                    <span>
                      {new Date(application.applied_at).toLocaleDateString(
                        'zh-CN'
                      )}
                    </span>
                  </div>

                  {application.candidate.tags && application.candidate.tags.length > 0 && (
                    <div className="flex gap-2 mt-3">
                      {application.candidate.tags.map((tag, index) => (
                        <Badge key={index} variant="outline">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
                <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                  <Button variant="outline" onClick={() => router.push(`/candidates/${application.id}`)}>
                    查看简历
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
                        <AlertDialogTitle>确认删除候选人</AlertDialogTitle>
                        <AlertDialogDescription>
                          删除后会同时删除该候选人的所有简历和应聘记录。之后可以重新上传该简历。
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>取消</AlertDialogCancel>
                        <AlertDialogAction onClick={() => deleteCandidate(application.candidate.id)}>
                          确认删除
                        </AlertDialogAction>
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
