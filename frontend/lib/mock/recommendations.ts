// Mock data for recommendations (推荐记录)
export interface RecommendationEvent {
  id: string;
  type: 'submitted' | 'hr_reviewed' | 'interview_scheduled' |
        'interview_completed' | 'offer_sent' | 'accepted' | 'rejected' | 'withdrawn';
  actor: string;
  actorRole: 'recruiter' | 'hr' | 'interviewer' | 'candidate';
  notes?: string;
  timestamp: string;
}

export interface Recommendation {
  id: string;
  recruiterId: string; // 猎头ID
  recruiterName: string;
  clientId: string;
  jobId: string;
  candidateId: string;
  status: 'pending' | 'hr_reviewing' | 'interview_scheduled' |
          'offer_sent' | 'accepted' | 'rejected' | 'withdrawn';
  hrStatus: 'pending' | 'viewed' | 'approved' | 'rejected'; // 企业接收状态
  hunterType: 'internal' | 'external' | 'headhunter'; // 猎头类型
  commission?: {
    amount: number;
    currency: string;
    percentage: number;
    status: 'pending' | 'approved' | 'paid';
  };
  notes: string;
  timeline: RecommendationEvent[];
  resumeUrl?: string;
  createdAt: string;
  updatedAt: string;
}

export const mockRecommendations: Recommendation[] = [
  {
    id: 'rec-1',
    recruiterId: 'recruiter-1',
    recruiterName: '张猎头',
    clientId: '1',
    jobId: 'cj-2', // 机器人agent开发工程师
    candidateId: '1',
    status: 'pending',
    hrStatus: 'pending',
    hunterType: 'headhunter',
    notes: '候选人有丰富的ROS开发经验，曾参与多个机器人项目',
    timeline: [
      {
        id: 'evt-1',
        type: 'submitted',
        actor: '张猎头',
        actorRole: 'recruiter',
        notes: '提交推荐',
        timestamp: '2026-05-15T09:30:00Z',
      },
    ],
    resumeUrl: '/resumes/candidate-1.pdf',
    createdAt: '2026-05-15T09:30:00Z',
    updatedAt: '2026-05-15T09:30:00Z',
  },
  {
    id: 'rec-2',
    recruiterId: 'recruiter-1',
    recruiterName: '张猎头',
    clientId: '1',
    jobId: 'cj-2', // 机器人agent开发工程师
    candidateId: '2',
    status: 'pending',
    hrStatus: 'pending',
    hunterType: 'headhunter',
    notes: '候选人在AI领域有深厚积累，适合agent开发',
    timeline: [
      {
        id: 'evt-2',
        type: 'submitted',
        actor: '张猎头',
        actorRole: 'recruiter',
        notes: '提交推荐',
        timestamp: '2026-04-18T14:20:00Z',
      },
    ],
    resumeUrl: '/resumes/candidate-2.pdf',
    createdAt: '2026-04-18T14:20:00Z',
    updatedAt: '2026-04-18T14:20:00Z',
  },
  {
    id: 'rec-3',
    recruiterId: 'recruiter-1',
    recruiterName: '张猎头',
    clientId: '1',
    jobId: 'cj-1', // 高级后端开发工程师
    candidateId: '3',
    status: 'pending',
    hrStatus: 'pending',
    hunterType: 'headhunter',
    notes: '10年后端经验，有大型分布式系统架构经验',
    timeline: [
      {
        id: 'evt-3',
        type: 'submitted',
        actor: '张猎头',
        actorRole: 'recruiter',
        notes: '提交推荐',
        timestamp: '2026-04-16T10:15:00Z',
      },
    ],
    resumeUrl: '/resumes/candidate-3.pdf',
    createdAt: '2026-04-16T10:15:00Z',
    updatedAt: '2026-04-16T10:15:00Z',
  },
  {
    id: 'rec-4',
    recruiterId: 'recruiter-1',
    recruiterName: '张猎头',
    clientId: '1',
    jobId: 'cj-1', // 高级后端开发工程师
    candidateId: '4',
    status: 'pending',
    hrStatus: 'pending',
    hunterType: 'headhunter',
    notes: '精通Go语言，有微服务架构实战经验',
    timeline: [
      {
        id: 'evt-4',
        type: 'submitted',
        actor: '张猎头',
        actorRole: 'recruiter',
        notes: '提交推荐',
        timestamp: '2026-04-15T16:45:00Z',
      },
    ],
    resumeUrl: '/resumes/candidate-4.pdf',
    createdAt: '2026-04-15T16:45:00Z',
    updatedAt: '2026-04-15T16:45:00Z',
  },
  {
    id: 'rec-5',
    recruiterId: 'recruiter-1',
    recruiterName: '张猎头',
    clientId: '1',
    jobId: 'cj-1', // 高级后端开发工程师
    candidateId: '5',
    status: 'pending',
    hrStatus: 'pending',
    hunterType: 'headhunter',
    notes: '有电商平台高并发系统开发经验',
    timeline: [
      {
        id: 'evt-5',
        type: 'submitted',
        actor: '张猎头',
        actorRole: 'recruiter',
        notes: '提交推荐',
        timestamp: '2026-04-07T11:30:00Z',
      },
    ],
    resumeUrl: '/resumes/candidate-5.pdf',
    createdAt: '2026-04-07T11:30:00Z',
    updatedAt: '2026-04-07T11:30:00Z',
  },
  {
    id: 'rec-6',
    recruiterId: 'recruiter-1',
    recruiterName: '张猎头',
    clientId: '1',
    jobId: 'cj-1', // 高级后端开发工程师
    candidateId: '1',
    status: 'hr_reviewing',
    hrStatus: 'viewed',
    hunterType: 'headhunter',
    commission: {
      amount: 40000,
      currency: 'CNY',
      percentage: 20,
      status: 'pending',
    },
    notes: '候选人背景优秀，强烈推荐',
    timeline: [
      {
        id: 'evt-6',
        type: 'submitted',
        actor: '张猎头',
        actorRole: 'recruiter',
        notes: '提交推荐',
        timestamp: '2026-03-08T09:00:00Z',
      },
      {
        id: 'evt-7',
        type: 'hr_reviewed',
        actor: '徐蔚',
        actorRole: 'hr',
        notes: 'HR已查看简历',
        timestamp: '2026-03-09T14:30:00Z',
      },
    ],
    resumeUrl: '/resumes/candidate-1.pdf',
    createdAt: '2026-03-08T09:00:00Z',
    updatedAt: '2026-03-09T14:30:00Z',
  },
  {
    id: 'rec-7',
    recruiterId: 'recruiter-1',
    recruiterName: '张猎头',
    clientId: '1',
    jobId: 'cj-1', // 高级后端开发工程师
    candidateId: '2',
    status: 'interview_scheduled',
    hrStatus: 'approved',
    hunterType: 'headhunter',
    commission: {
      amount: 40000,
      currency: 'CNY',
      percentage: 20,
      status: 'pending',
    },
    notes: '技术栈匹配度高',
    timeline: [
      {
        id: 'evt-8',
        type: 'submitted',
        actor: '张猎头',
        actorRole: 'recruiter',
        notes: '提交推荐',
        timestamp: '2026-03-08T10:00:00Z',
      },
      {
        id: 'evt-9',
        type: 'hr_reviewed',
        actor: '徐蔚',
        actorRole: 'hr',
        notes: 'HR已查看并通过初筛',
        timestamp: '2026-03-09T15:00:00Z',
      },
      {
        id: 'evt-10',
        type: 'interview_scheduled',
        actor: '徐蔚',
        actorRole: 'hr',
        notes: '已安排技术面试',
        timestamp: '2026-03-12T10:30:00Z',
      },
    ],
    resumeUrl: '/resumes/candidate-2.pdf',
    createdAt: '2026-03-08T10:00:00Z',
    updatedAt: '2026-03-12T10:30:00Z',
  },
  {
    id: 'rec-8',
    recruiterId: 'recruiter-1',
    recruiterName: '张猎头',
    clientId: '1',
    jobId: 'cj-1', // 高级后端开发工程师
    candidateId: '3',
    status: 'offer_sent',
    hrStatus: 'approved',
    hunterType: 'headhunter',
    commission: {
      amount: 40000,
      currency: 'CNY',
      percentage: 20,
      status: 'approved',
    },
    notes: '资深候选人，面试表现优秀',
    timeline: [
      {
        id: 'evt-11',
        type: 'submitted',
        actor: '张猎头',
        actorRole: 'recruiter',
        notes: '提交推荐',
        timestamp: '2026-03-05T09:00:00Z',
      },
      {
        id: 'evt-12',
        type: 'hr_reviewed',
        actor: '徐蔚',
        actorRole: 'hr',
        notes: 'HR已查看并通过初筛',
        timestamp: '2026-03-06T11:00:00Z',
      },
      {
        id: 'evt-13',
        type: 'interview_scheduled',
        actor: '徐蔚',
        actorRole: 'hr',
        notes: '已安排技术面试',
        timestamp: '2026-03-08T14:00:00Z',
      },
      {
        id: 'evt-14',
        type: 'interview_completed',
        actor: '李工',
        actorRole: 'interviewer',
        notes: '技术面试通过',
        timestamp: '2026-03-15T16:30:00Z',
      },
      {
        id: 'evt-15',
        type: 'offer_sent',
        actor: '徐蔚',
        actorRole: 'hr',
        notes: '已发送Offer',
        timestamp: '2026-03-18T10:00:00Z',
      },
    ],
    resumeUrl: '/resumes/candidate-3.pdf',
    createdAt: '2026-03-05T09:00:00Z',
    updatedAt: '2026-03-18T10:00:00Z',
  },
  {
    id: 'rec-9',
    recruiterId: 'recruiter-1',
    recruiterName: '张猎头',
    clientId: '1',
    jobId: 'cj-2', // 机器人agent开发工程师
    candidateId: '4',
    status: 'accepted',
    hrStatus: 'approved',
    hunterType: 'headhunter',
    commission: {
      amount: 35000,
      currency: 'CNY',
      percentage: 20,
      status: 'paid',
    },
    notes: '候选人接受Offer，推荐成功',
    timeline: [
      {
        id: 'evt-16',
        type: 'submitted',
        actor: '张猎头',
        actorRole: 'recruiter',
        notes: '提交推荐',
        timestamp: '2026-02-10T09:00:00Z',
      },
      {
        id: 'evt-17',
        type: 'hr_reviewed',
        actor: '陈瑄',
        actorRole: 'hr',
        notes: 'HR已查看并通过初筛',
        timestamp: '2026-02-11T10:00:00Z',
      },
      {
        id: 'evt-18',
        type: 'interview_scheduled',
        actor: '陈瑄',
        actorRole: 'hr',
        notes: '已安排技术面试',
        timestamp: '2026-02-13T14:00:00Z',
      },
      {
        id: 'evt-19',
        type: 'interview_completed',
        actor: '王工',
        actorRole: 'interviewer',
        notes: '技术面试通过',
        timestamp: '2026-02-20T15:30:00Z',
      },
      {
        id: 'evt-20',
        type: 'offer_sent',
        actor: '陈瑄',
        actorRole: 'hr',
        notes: '已发送Offer',
        timestamp: '2026-02-22T09:00:00Z',
      },
      {
        id: 'evt-21',
        type: 'accepted',
        actor: '候选人',
        actorRole: 'candidate',
        notes: '候选人接受Offer',
        timestamp: '2026-02-25T16:00:00Z',
      },
    ],
    resumeUrl: '/resumes/candidate-4.pdf',
    createdAt: '2026-02-10T09:00:00Z',
    updatedAt: '2026-02-25T16:00:00Z',
  },
  {
    id: 'rec-10',
    recruiterId: 'recruiter-1',
    recruiterName: '张猎头',
    clientId: '1',
    jobId: 'cj-1', // 高级后端开发工程师
    candidateId: '5',
    status: 'rejected',
    hrStatus: 'rejected',
    hunterType: 'headhunter',
    notes: '候选人经验不足',
    timeline: [
      {
        id: 'evt-22',
        type: 'submitted',
        actor: '张猎头',
        actorRole: 'recruiter',
        notes: '提交推荐',
        timestamp: '2026-03-04T09:00:00Z',
      },
      {
        id: 'evt-23',
        type: 'hr_reviewed',
        actor: '徐蔚',
        actorRole: 'hr',
        notes: 'HR查看后认为不匹配',
        timestamp: '2026-03-05T11:00:00Z',
      },
      {
        id: 'evt-24',
        type: 'rejected',
        actor: '徐蔚',
        actorRole: 'hr',
        notes: '简历筛选未通过',
        timestamp: '2026-03-05T11:30:00Z',
      },
    ],
    resumeUrl: '/resumes/candidate-5.pdf',
    createdAt: '2026-03-04T09:00:00Z',
    updatedAt: '2026-03-05T11:30:00Z',
  },
  // 添加更多推荐记录以达到18条"推荐中"
  ...Array.from({ length: 8 }, (_, i) => ({
    id: `rec-${11 + i}`,
    recruiterId: 'recruiter-1',
    recruiterName: '张猎头',
    clientId: '1',
    jobId: i % 2 === 0 ? 'cj-1' : 'cj-2',
    candidateId: `${(i % 5) + 1}`,
    status: 'pending' as const,
    hrStatus: 'pending' as const,
    hunterType: 'headhunter' as const,
    notes: `候选人${i + 1}的推荐`,
    timeline: [
      {
        id: `evt-${25 + i}`,
        type: 'submitted' as const,
        actor: '张猎头',
        actorRole: 'recruiter' as const,
        notes: '提交推荐',
        timestamp: new Date(2026, 2, 10 + i, 9, 0, 0).toISOString(),
      },
    ],
    resumeUrl: `/resumes/candidate-${(i % 5) + 1}.pdf`,
    createdAt: new Date(2026, 2, 10 + i, 9, 0, 0).toISOString(),
    updatedAt: new Date(2026, 2, 10 + i, 9, 0, 0).toISOString(),
  })),
  // 添加更多成功案例
  ...Array.from({ length: 6 }, (_, i) => ({
    id: `rec-success-${i + 1}`,
    recruiterId: 'recruiter-1',
    recruiterName: '张猎头',
    clientId: i < 3 ? '1' : '2',
    jobId: i < 3 ? 'cj-1' : 'cj-3',
    candidateId: `${(i % 5) + 1}`,
    status: 'accepted' as const,
    hrStatus: 'approved' as const,
    hunterType: 'headhunter' as const,
    commission: {
      amount: 35000 + i * 1000,
      currency: 'CNY',
      percentage: 20,
      status: i < 3 ? ('paid' as const) : ('approved' as const),
    },
    notes: `成功推荐案例${i + 1}`,
    timeline: [
      {
        id: `evt-success-${i * 5 + 1}`,
        type: 'submitted' as const,
        actor: '张猎头',
        actorRole: 'recruiter' as const,
        notes: '提交推荐',
        timestamp: new Date(2026, 0, 10 + i * 5, 9, 0, 0).toISOString(),
      },
      {
        id: `evt-success-${i * 5 + 2}`,
        type: 'hr_reviewed' as const,
        actor: 'HR',
        actorRole: 'hr' as const,
        notes: 'HR已查看',
        timestamp: new Date(2026, 0, 11 + i * 5, 10, 0, 0).toISOString(),
      },
      {
        id: `evt-success-${i * 5 + 3}`,
        type: 'interview_completed' as const,
        actor: '面试官',
        actorRole: 'interviewer' as const,
        notes: '面试通过',
        timestamp: new Date(2026, 0, 15 + i * 5, 14, 0, 0).toISOString(),
      },
      {
        id: `evt-success-${i * 5 + 4}`,
        type: 'offer_sent' as const,
        actor: 'HR',
        actorRole: 'hr' as const,
        notes: '已发送Offer',
        timestamp: new Date(2026, 0, 18 + i * 5, 9, 0, 0).toISOString(),
      },
      {
        id: `evt-success-${i * 5 + 5}`,
        type: 'accepted' as const,
        actor: '候选人',
        actorRole: 'candidate' as const,
        notes: '候选人接受Offer',
        timestamp: new Date(2026, 0, 20 + i * 5, 16, 0, 0).toISOString(),
      },
    ],
    resumeUrl: `/resumes/candidate-${(i % 5) + 1}.pdf`,
    createdAt: new Date(2026, 0, 10 + i * 5, 9, 0, 0).toISOString(),
    updatedAt: new Date(2026, 0, 20 + i * 5, 16, 0, 0).toISOString(),
  })),
  // 添加一个失败案例
  {
    id: 'rec-fail-1',
    recruiterId: 'recruiter-1',
    recruiterName: '张猎头',
    clientId: '1',
    jobId: 'cj-2',
    candidateId: '3',
    status: 'rejected',
    hrStatus: 'rejected',
    hunterType: 'headhunter',
    notes: '候选人面试表现不佳',
    timeline: [
      {
        id: 'evt-fail-1',
        type: 'submitted',
        actor: '张猎头',
        actorRole: 'recruiter',
        notes: '提交推荐',
        timestamp: '2026-02-01T09:00:00Z',
      },
      {
        id: 'evt-fail-2',
        type: 'hr_reviewed',
        actor: '陈瑄',
        actorRole: 'hr',
        notes: 'HR已查看',
        timestamp: '2026-02-02T10:00:00Z',
      },
      {
        id: 'evt-fail-3',
        type: 'interview_scheduled',
        actor: '陈瑄',
        actorRole: 'hr',
        notes: '已安排面试',
        timestamp: '2026-02-05T14:00:00Z',
      },
      {
        id: 'evt-fail-4',
        type: 'rejected',
        actor: '面试官',
        actorRole: 'interviewer',
        notes: '面试未通过',
        timestamp: '2026-02-10T16:00:00Z',
      },
    ],
    resumeUrl: '/resumes/candidate-3.pdf',
    createdAt: '2026-02-01T09:00:00Z',
    updatedAt: '2026-02-10T16:00:00Z',
  },
];

// 辅助函数：获取推荐统计
export function getRecommendationStats(recommendations: Recommendation[]) {
  return {
    pending: recommendations.filter(r => r.status === 'pending' || r.status === 'hr_reviewing' || r.status === 'interview_scheduled' || r.status === 'offer_sent').length,
    success: recommendations.filter(r => r.status === 'accepted').length,
    failed: recommendations.filter(r => r.status === 'rejected' || r.status === 'withdrawn').length,
  };
}

// 辅助函数：按客户ID筛选推荐
export function getRecommendationsByClient(clientId: string) {
  return mockRecommendations.filter(r => r.clientId === clientId);
}

// 辅助函数：按职位ID筛选推荐
export function getRecommendationsByJob(jobId: string) {
  return mockRecommendations.filter(r => r.jobId === jobId);
}
