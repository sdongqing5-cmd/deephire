// Mock data for client jobs (客户公司发布的职位)
export interface ClientJob {
  id: string;
  clientId: string;
  title: string;
  titleKey?: string;
  description: string;
  requirements: string[];
  salary: {
    min: number;
    max: number;
    currency: string;
  };
  location: string;
  hrOwner: string; // HR负责人
  hrOwnerId: string;
  status: 'recruiting' | 'closed' | 'paused';
  type: 'social' | 'campus'; // 社招/校招
  recommendationCount: number; // 已推荐人数
  createdAt: string;
  updatedAt: string;
}

export const mockClientJobs: ClientJob[] = [
  {
    id: 'cj-1',
    clientId: '1', // Light Robotics
    title: '高级后端开发工程师',
    titleKey: 'seniorBackendEngineer',
    description: '负责公司核心业务系统的后端开发，参与架构设计和技术选型',
    requirements: [
      '5年以上后端开发经验',
      '精通Java/Go/Python中至少一种语言',
      '熟悉微服务架构',
      '有大型分布式系统经验',
    ],
    salary: {
      min: 30000,
      max: 50000,
      currency: 'CNY',
    },
    location: '北京',
    hrOwner: '徐蔚',
    hrOwnerId: 'hr-1',
    status: 'recruiting',
    type: 'social',
    recommendationCount: 22,
    createdAt: '2025-11-07T09:00:00Z',
    updatedAt: '2026-05-15T14:30:00Z',
  },
  {
    id: 'cj-2',
    clientId: '1', // Light Robotics
    title: '机器人agent开发工程师',
    titleKey: 'robotAgentEngineer',
    description: '负责机器人智能体的开发，包括感知、决策、控制等模块',
    requirements: [
      '3年以上机器人或AI相关开发经验',
      '熟悉ROS/ROS2',
      '了解强化学习、路径规划算法',
      '有实际机器人项目经验优先',
    ],
    salary: {
      min: 25000,
      max: 45000,
      currency: 'CNY',
    },
    location: '北京',
    hrOwner: '陈瑄',
    hrOwnerId: 'hr-2',
    status: 'recruiting',
    type: 'social',
    recommendationCount: 3,
    createdAt: '2026-04-17T10:00:00Z',
    updatedAt: '2026-05-20T11:20:00Z',
  },
  {
    id: 'cj-3',
    clientId: '2', // TechVision AI
    title: '算法工程师',
    titleKey: 'algorithmEngineer',
    description: '负责计算机视觉算法的研发和优化',
    requirements: [
      '硕士及以上学历，计算机或相关专业',
      '熟悉深度学习框架（PyTorch/TensorFlow）',
      '有目标检测、图像分割等项目经验',
      '发表过顶会论文优先',
    ],
    salary: {
      min: 28000,
      max: 48000,
      currency: 'CNY',
    },
    location: '上海',
    hrOwner: '李雪',
    hrOwnerId: 'hr-3',
    status: 'recruiting',
    type: 'social',
    recommendationCount: 15,
    createdAt: '2026-03-01T08:30:00Z',
    updatedAt: '2026-05-22T09:45:00Z',
  },
  {
    id: 'cj-4',
    clientId: '2', // TechVision AI
    title: '前端开发工程师',
    titleKey: 'frontendEngineer',
    description: '负责AI产品的前端界面开发',
    requirements: [
      '3年以上前端开发经验',
      '精通React/Vue',
      '熟悉TypeScript',
      '有数据可视化经验优先',
    ],
    salary: {
      min: 20000,
      max: 35000,
      currency: 'CNY',
    },
    location: '上海',
    hrOwner: '李雪',
    hrOwnerId: 'hr-3',
    status: 'recruiting',
    type: 'social',
    recommendationCount: 8,
    createdAt: '2026-04-10T09:00:00Z',
    updatedAt: '2026-05-21T15:30:00Z',
  },
  {
    id: 'cj-5',
    clientId: '3', // CloudBase Systems
    title: '云平台架构师',
    titleKey: 'cloudArchitect',
    description: '负责云平台的架构设计和技术规划',
    requirements: [
      '8年以上开发经验，5年以上架构经验',
      '精通Kubernetes、Docker',
      '熟悉AWS/阿里云/腾讯云',
      '有大规模云平台建设经验',
    ],
    salary: {
      min: 40000,
      max: 70000,
      currency: 'CNY',
    },
    location: '深圳',
    hrOwner: '王芳',
    hrOwnerId: 'hr-4',
    status: 'recruiting',
    type: 'social',
    recommendationCount: 5,
    createdAt: '2026-02-15T10:00:00Z',
    updatedAt: '2026-05-18T16:20:00Z',
  },
  {
    id: 'cj-6',
    clientId: '3', // CloudBase Systems
    title: 'DevOps工程师',
    titleKey: 'devopsEngineer',
    description: '负责CI/CD流程建设和运维自动化',
    requirements: [
      '3年以上DevOps经验',
      '熟悉Jenkins/GitLab CI',
      '熟悉Linux系统管理',
      '有监控告警系统搭建经验',
    ],
    salary: {
      min: 22000,
      max: 38000,
      currency: 'CNY',
    },
    location: '深圳',
    hrOwner: '王芳',
    hrOwnerId: 'hr-4',
    status: 'recruiting',
    type: 'social',
    recommendationCount: 12,
    createdAt: '2026-03-20T11:00:00Z',
    updatedAt: '2026-05-19T10:15:00Z',
  },
  {
    id: 'cj-7',
    clientId: '4', // DataFlow Analytics
    title: '数据分析师',
    titleKey: 'dataAnalyst',
    description: '负责业务数据分析和报表开发',
    requirements: [
      '2年以上数据分析经验',
      '熟悉SQL、Python',
      '熟悉数据可视化工具',
      '有BI工具使用经验',
    ],
    salary: {
      min: 15000,
      max: 25000,
      currency: 'CNY',
    },
    location: '杭州',
    hrOwner: '赵敏',
    hrOwnerId: 'hr-5',
    status: 'closed',
    type: 'social',
    recommendationCount: 18,
    createdAt: '2025-12-01T09:00:00Z',
    updatedAt: '2026-04-30T14:00:00Z',
  },
];
