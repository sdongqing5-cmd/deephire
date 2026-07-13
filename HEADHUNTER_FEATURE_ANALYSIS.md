# 猎头功能分析与设计方案

## 一、Moka 猎头功能提取

### 1. 核心功能模块

#### 1.1 公司/客户管理
- **公司信息展示**
  - 公司名称、Logo
  - 公司公告（猎头公司公告）
  - 统计数据：招聘职位数、推荐记录数

#### 1.2 招聘职位管理
- **职位列表**
  - 职位筛选（按职位、职位负责人）
  - 职位状态：招聘中、已关闭
  - 职位详情查看
  
#### 1.3 推荐记录管理（核心功能）
- **推荐状态追踪**
  - 推荐中
  - 推荐成功
  - 推荐失败
  
- **多维度筛选**
  - HR待处理状态
  - 候选人姓名搜索
  - 推荐职位筛选
  - 猎头类型筛选
  - 显示已离职候选人（开关）
  - 职位负责人筛选

- **推荐历史**
  - 推荐记录列表
  - 推荐时间线
  - 推荐结果追踪

### 2. 功能调用关系

```
猎头登录
    ↓
选择客户公司（Light Robotics）
    ↓
    ├─→ 查看招聘职位
    │       ↓
    │   筛选职位（按状态、负责人）
    │       ↓
    │   查看职位详情
    │       ↓
    │   推荐候选人 ──────┐
    │                     │
    └─→ 查看推荐记录 ←────┘
            ↓
        筛选推荐记录
            ↓
        追踪推荐状态
            ↓
        查看推荐结果
```

## 二、DeepHire 当前状态

### 现有功能
- 基础 Dashboard 框架
- 简单统计卡片：
  - 我的候选人：0
  - 已安排面试：0
  - 待处理事项：0

### 缺失功能
1. ❌ 客户公司管理
2. ❌ 客户职位列表
3. ❌ 推荐记录管理
4. ❌ 推荐状态追踪
5. ❌ 多维度筛选系统
6. ❌ 推荐历史时间线
7. ❌ 候选人推荐流程
8. ❌ 推荐成功率统计

## 三、功能设计方案

### 3.1 数据模型设计

#### Client（客户公司）
```typescript
interface Client {
  id: string;
  name: string;
  logo?: string;
  announcement?: string;
  contactPerson: string;
  contactEmail: string;
  contactPhone: string;
  status: 'active' | 'inactive';
  createdAt: Date;
  updatedAt: Date;
}
```

#### ClientJob（客户职位）
```typescript
interface ClientJob {
  id: string;
  clientId: string;
  title: string;
  description: string;
  requirements: string[];
  salary: {
    min: number;
    max: number;
    currency: string;
  };
  location: string;
  hrOwner: string; // HR负责人
  status: 'recruiting' | 'closed' | 'paused';
  createdAt: Date;
  updatedAt: Date;
}
```

#### Recommendation（推荐记录）
```typescript
interface Recommendation {
  id: string;
  recruiterId: string; // 猎头ID
  clientId: string;
  jobId: string;
  candidateId: string;
  status: 'pending' | 'hr_reviewing' | 'interview_scheduled' | 
          'offer_sent' | 'accepted' | 'rejected' | 'withdrawn';
  hrStatus: 'pending' | 'approved' | 'rejected';
  hunterType: 'internal' | 'external' | 'partner';
  commission?: {
    amount: number;
    currency: string;
    status: 'pending' | 'paid';
  };
  notes: string;
  timeline: RecommendationEvent[];
  createdAt: Date;
  updatedAt: Date;
}

interface RecommendationEvent {
  id: string;
  type: 'submitted' | 'hr_reviewed' | 'interview_scheduled' | 
        'interview_completed' | 'offer_sent' | 'accepted' | 'rejected';
  actor: string;
  notes?: string;
  timestamp: Date;
}
```

### 3.2 页面结构设计

#### 猎头 Dashboard 页面结构
```
/dashboard/recruiter
├── 统计概览
│   ├── 活跃客户数
│   ├── 进行中的推荐
│   ├── 本月成功推荐
│   └── 待处理事项
├── 客户列表（快速切换）
├── 当前客户详情
│   ├── 客户信息
│   ├── 招聘职位 Tab
│   │   ├── 职位筛选
│   │   ├── 职位列表
│   │   └── 推荐候选人按钮
│   └── 推荐记录 Tab
│       ├── 状态统计（推荐中/成功/失败）
│       ├── 多维度筛选
│       └── 推荐记录列表
└── 快速操作
    ├── 推荐候选人
    ├── 搜索人才
    └── 查看佣金
```

### 3.3 核心功能实现

#### 功能1：客户管理
- 客户列表展示
- 客户切换（下拉选择或侧边栏）
- 客户详情查看
- 客户统计数据

#### 功能2：职位管理
- 查看客户发布的职位
- 职位筛选（状态、负责人）
- 职位详情查看
- 从职位发起推荐

#### 功能3：推荐管理（核心）
- **推荐提交**
  - 选择客户
  - 选择职位
  - 选择候选人
  - 填写推荐理由
  - 提交推荐

- **推荐追踪**
  - 推荐状态实时更新
  - HR审核状态
  - 面试安排状态
  - Offer状态
  - 最终结果

- **推荐筛选**
  - 按HR处理状态
  - 按候选人姓名
  - 按推荐职位
  - 按猎头类型
  - 按时间范围
  - 显示/隐藏已离职候选人

#### 功能4：统计分析
- 推荐成功率
- 各阶段转化率
- 佣金统计
- 客户满意度

### 3.4 UI/UX 设计要点

#### 布局设计
1. **顶部区域**
   - 客户选择器（突出显示当前客户）
   - 客户基本信息和公告
   - 关键统计数据

2. **主内容区**
   - Tab切换（招聘职位 / 推荐记录）
   - 筛选器区域（固定在顶部）
   - 列表/卡片展示区

3. **快速操作**
   - 浮动操作按钮
   - 快速推荐入口

#### 交互设计
1. **推荐流程**
   - 步骤1：选择客户和职位
   - 步骤2：搜索/选择候选人
   - 步骤3：填写推荐信息
   - 步骤4：确认提交

2. **状态可视化**
   - 使用颜色区分不同状态
   - 进度条显示推荐进度
   - 时间线展示推荐历程

3. **筛选体验**
   - 筛选条件持久化
   - 快速清除筛选
   - 筛选结果计数

## 四、实施优先级

### P0（核心功能）
1. 客户管理基础功能
2. 客户职位列表
3. 推荐记录管理
4. 推荐状态追踪

### P1（重要功能）
1. 多维度筛选系统
2. 推荐历史时间线
3. 统计数据展示
4. 推荐流程优化

### P2（增强功能）
1. 佣金管理
2. 客户满意度
3. 推荐成功率分析
4. 批量操作

## 五、技术实现要点

### 5.1 状态管理
- 使用 React Context 或 Zustand 管理客户选择状态
- 推荐记录的实时更新（WebSocket 或轮询）

### 5.2 数据获取
- 客户列表：一次性加载
- 职位列表：按客户懒加载
- 推荐记录：分页加载 + 虚拟滚动

### 5.3 性能优化
- 列表虚拟化（react-window）
- 筛选防抖
- 数据缓存策略

### 5.4 国际化
- 所有文案支持中英文
- 状态标签翻译
- 日期格式本地化

## 六、Mock 数据结构

需要创建以下 Mock 数据：
1. `mockClients.ts` - 客户公司数据
2. `mockClientJobs.ts` - 客户职位数据
3. `mockRecommendations.ts` - 推荐记录数据
4. 扩展现有的 `mockCandidates.ts` - 添加猎头相关字段

## 七、API 接口设计

### 客户相关
- `GET /api/recruiter/clients` - 获取客户列表
- `GET /api/recruiter/clients/:id` - 获取客户详情
- `GET /api/recruiter/clients/:id/jobs` - 获取客户职位

### 推荐相关
- `POST /api/recruiter/recommendations` - 提交推荐
- `GET /api/recruiter/recommendations` - 获取推荐列表
- `GET /api/recruiter/recommendations/:id` - 获取推荐详情
- `PATCH /api/recruiter/recommendations/:id` - 更新推荐状态
- `DELETE /api/recruiter/recommendations/:id` - 撤回推荐

### 统计相关
- `GET /api/recruiter/stats` - 获取统计数据
- `GET /api/recruiter/commission` - 获取佣金信息
