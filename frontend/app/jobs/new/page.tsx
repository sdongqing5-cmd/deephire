'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { MainLayout } from '@/components/layout/main-layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { ArrowLeft } from 'lucide-react';

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

export default function NewJobPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
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
    valid_until: '',
    hiring_manager_id: '1', // TODO: 从当前用户获取
    department_manager_id: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        ...formData,
        level: formData.level || null,
        department_manager_id: formData.department_manager_id || null,
        salary_min: formData.salary_min ? parseInt(formData.salary_min) : null,
        salary_max: formData.salary_max ? parseInt(formData.salary_max) : null,
        openings: parseInt(formData.openings),
        valid_until: formData.valid_until || null,
      };

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/jobs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        alert('职位创建成功！');
        router.push('/jobs');
      } else {
        const error = await response.json();
        alert(`创建失败: ${error.detail || '请检查表单信息'}`);
      }
    } catch (error) {
      console.error('Error creating job:', error);
      alert('网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <MainLayout>
      <div className="container mx-auto py-6">
        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={() => router.back()}
            className="mb-4"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            返回
          </Button>
          <h1 className="text-3xl font-bold">创建新职位</h1>
          <p className="text-muted-foreground mt-2">填写职位信息并发布招聘</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>职位信息</CardTitle>
            <CardDescription>请填写完整的职位信息</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="title">职位名称 *</Label>
                  <Input
                    id="title"
                    name="title"
                    value={formData.title}
                    onChange={handleChange}
                    placeholder="例如：高级前端工程师"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="department_id">部门 *</Label>
                  <select
                    id="department_id"
                    name="department_id"
                    value={formData.department_id}
                    onChange={handleChange}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    required
                  >
                    {departments.map((department) => (
                      <option key={department.value} value={department.value}>
                        {department.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="location">工作地点 *</Label>
                  <Input
                    id="location"
                    name="location"
                    value={formData.location}
                    onChange={handleChange}
                    placeholder="例如：北京"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="category">岗位类别 *</Label>
                  <select
                    id="category"
                    name="category"
                    value={formData.category}
                    onChange={handleChange}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    required
                  >
                    {jobCategories.map((category) => (
                      <option key={category.value} value={category.value}>
                        {category.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="recruitment_type">招聘类别 *</Label>
                  <select
                    id="recruitment_type"
                    name="recruitment_type"
                    value={formData.recruitment_type}
                    onChange={handleChange}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    required
                  >
                    <option value="social">社会招聘</option>
                    <option value="campus">校园招聘</option>
                    <option value="internship">实习生招聘</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="level">职位级别</Label>
                  <select
                    id="level"
                    name="level"
                    value={formData.level}
                    onChange={handleChange}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <option value="">未指定</option>
                    {jobLevels.map((level) => (
                      <option key={level.value} value={level.value}>
                        {level.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="salary_min">最低薪资（元/月）</Label>
                  <Input
                    id="salary_min"
                    name="salary_min"
                    type="number"
                    value={formData.salary_min}
                    onChange={handleChange}
                    placeholder="例如：15000"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="salary_max">最高薪资（元/月）</Label>
                  <Input
                    id="salary_max"
                    name="salary_max"
                    type="number"
                    value={formData.salary_max}
                    onChange={handleChange}
                    placeholder="例如：25000"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">职位描述 *</Label>
                <Textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  placeholder="描述职位的主要职责和工作内容..."
                  rows={6}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="requirements">任职要求 *</Label>
                <Textarea
                  id="requirements"
                  name="requirements"
                  value={formData.requirements}
                  onChange={handleChange}
                  placeholder="列出候选人需要具备的技能和经验..."
                  rows={6}
                  required
                />
              </div>

              <div className="flex justify-end gap-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.back()}
                  disabled={loading}
                >
                  取消
                </Button>
                <Button type="submit" disabled={loading}>
                  {loading ? '创建中...' : '创建职位'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
