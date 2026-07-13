// Mock data for client companies (猎头的客户公司)
export interface Client {
  id: string;
  name: string;
  logo?: string;
  announcement?: string;
  contactPerson: string;
  contactEmail: string;
  contactPhone: string;
  status: 'active' | 'inactive';
  industry: string;
  location: string;
  createdAt: string;
  updatedAt: string;
}

export const mockClients: Client[] = [
  {
    id: '1',
    name: 'Light Robotics',
    logo: 'Li',
    announcement: '暂无公告',
    contactPerson: '张经理',
    contactEmail: 'zhang@lightrobotics.com',
    contactPhone: '13800138000',
    status: 'active',
    industry: '人工智能/机器人',
    location: '北京',
    createdAt: '2025-01-15T08:00:00Z',
    updatedAt: '2026-05-20T10:30:00Z',
  },
  {
    id: '2',
    name: 'TechVision AI',
    logo: 'TV',
    announcement: '急招算法工程师，优先推荐',
    contactPerson: '李总',
    contactEmail: 'li@techvision.com',
    contactPhone: '13900139000',
    status: 'active',
    industry: '人工智能',
    location: '上海',
    createdAt: '2025-03-10T09:00:00Z',
    updatedAt: '2026-05-22T14:20:00Z',
  },
  {
    id: '3',
    name: 'CloudBase Systems',
    logo: 'CB',
    announcement: '',
    contactPerson: '王主管',
    contactEmail: 'wang@cloudbase.com',
    contactPhone: '13700137000',
    status: 'active',
    industry: '云计算',
    location: '深圳',
    createdAt: '2025-02-20T10:00:00Z',
    updatedAt: '2026-05-18T16:45:00Z',
  },
  {
    id: '4',
    name: 'DataFlow Analytics',
    logo: 'DF',
    announcement: '本月暂停招聘',
    contactPerson: '赵经理',
    contactEmail: 'zhao@dataflow.com',
    contactPhone: '13600136000',
    status: 'inactive',
    industry: '大数据',
    location: '杭州',
    createdAt: '2024-11-05T11:00:00Z',
    updatedAt: '2026-04-30T09:15:00Z',
  },
];
