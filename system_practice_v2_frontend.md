# DeepHire 招聘系统 - V2前端设计文档

## 📋 文档说明

本文档包含：
- 前端页面设计
- 组件设计
- 状态管理
- 交互流程

---

## 一、页面结构设计

### 1.1 HR工作台（Dashboard）

```
┌─────────────────────────────────────────────────────────┐
│  DeepHire  [职位] [简历] [面试] [Offer] [入职]  [🔔3] [HR]│
├─────────────────────────────────────────────────────────┤
│  统计卡片                                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ 招聘中   │ │ 待处理   │ │ 本月入职 │ │ 本月Offer│  │
│  │ 15个职位 │ │ 23条简历 │ │ 8人      │ │ 12个     │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
├─────────────────────────────────────────────────────────┤
│  待处理事项                                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │ • 5份简历待查看                                   │  │
│  │ • 3个HR初筛面试待安排                            │  │
│  │ • 2个面试官筛选结果待查看                        │  │
│  │ • 4个部门面试评价待查看                          │  │
│  │ • 1个Offer审批待处理                             │  │
│  └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│  最近活动                                                │
│  • 张三 - 高级前端工程师 - 部门面试通过                 │
│  • 李四 - 产品经理 - 已接受Offer                        │
│  • 王五 - 后端工程师 - HR初筛面试完成                   │
└─────────────────────────────────────────────────────────┘
```

### 1.2 简历管理页（按状态分组）

```
┌─────────────────────────────────────────────────────────┐
│  简历管理                                                │
│  [上传简历]  [批量操作▼]  [搜索____________]  [筛选▼]  │
├─────────────────────────────────────────────────────────┤
│  [新简历(5)] [HR筛选中(3)] [HR初筛面试(2)] [推送面试官(4)]│
│  [面试意向沟通(1)] [等待确认时间(2)] [部门面试(6)] ...  │
├─────────────────────────────────────────────────────────┤
│  新简历 (5)                                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │ ☐ 张伟 - 高级前端工程师                          │  │
│  │    5年经验 · 字节跳动 · React/TypeScript         │  │
│  │    2小时前投递 · 主动投递                        │  │
│  │    [查看详情] [开始筛选] [淘汰]                  │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │ ☐ 李娜 - 产品经理                                │  │
│  │    3年经验 · 腾讯 · B端产品                      │  │
│  │    1天前投递 · 内推                              │  │
│  │    [查看详情] [开始筛选] [淘汰]                  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 1.3 简历详情页（完整流程）

```
┌─────────────────────────────────────────────────────────┐
│  ← 返回  张伟 - 高级前端工程师                          │
│  当前状态: HR初筛面试已完成                             │
│  [推送面试官] [更多操作▼]                               │
├─────────────────────────────────────────────────────────┤
│  [基本信息] [简历] [面试] [评价] [时间线]              │
├─────────────────────────────────────────────────────────┤
│  基本信息                                                │
│  姓名: 张伟                                              │
│  电话: 138-1234-5678                                    │
│  邮箱: zhangwei@email.com                               │
│  当前公司: 字节跳动                                     │
│  当前职位: 高级前端工程师                               │
│  工作年限: 5年                                           │
│  期望薪资: 30-50万                                      │
│                                                          │
│  应聘信息                                                │
│  应聘职位: 高级前端工程师                               │
│  投递时间: 2026-05-30 10:00                             │
│  简历来源: 主动投递                                     │
│  负责HR: 李HR                                           │
│                                                          │
│  面试意向沟通                                            │
│  沟通方式: 人工联系                                     │
│  沟通结果: 同意面试                                     │
│  沟通时间: 2026-05-30 15:30                             │
│  备注: 候选人对职位很感兴趣，可随时面试                 │
└─────────────────────────────────────────────────────────┘
```

### 1.4 时间线组件（完整流程展示）

```
┌─────────────────────────────────────────────────────────┐
│  时间线                                                  │
├─────────────────────────────────────────────────────────┤
│  ● 简历投递                                              │
│    2026-05-30 10:00                                     │
│    来源: 主动投递                                       │
│                                                          │
│  ● HR筛选中                                              │
│    2026-05-30 10:30 · 李HR                              │
│    开始筛选简历                                         │
│                                                          │
│  ● 电话沟通                                              │
│    2026-05-30 11:00 · 李HR                              │
│    候选人确认意向，同意面试                             │
│                                                          │
│  ● HR初筛面试已安排                                     │
│    2026-05-30 14:00 · 李HR                              │
│    面试时间: 2026-05-31 10:00                           │
│                                                          │
│  ● HR初筛面试已完成 ✓                                   │
│    2026-05-31 10:30 · 李HR                              │
│    评价: 通过 · 得分: 85分                              │
│    反馈: 候选人技术基础扎实，沟通能力强                 │
│                                                          │
│  ○ 推送面试官（待处理）                                 │
│    下一步: 推送给用人部门面试官筛选简历                 │
└─────────────────────────────────────────────────────────┘
```

### 1.5 面试官筛选简历页面

```
┌─────────────────────────────────────────────────────────┐
│  待筛选简历 (3)                                          │
│  [全部] [今天推送] [本周推送]                           │
├─────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────┐  │
│  │ 张伟 - 高级前端工程师                            │  │
│  │ 5年经验 · 字节跳动 · React/TypeScript            │  │
│  │ 推送时间: 2小时前 · 推送人: 李HR                 │  │
│  │                                                   │  │
│  │ HR初筛评价:                                       │  │
│  │ 技术基础扎实，沟通能力强，对职位很感兴趣         │  │
│  │ 得分: 85分                                        │  │
│  │                                                   │  │
│  │ [查看完整简历]                                    │  │
│  │                                                   │  │
│  │ 筛选意见:                                         │  │
│  │ ┌─────────────────────────────────────────────┐  │  │
│  │ │ [简单填写筛选意见]                          │  │  │
│  │ └─────────────────────────────────────────────┘  │  │
│  │                                                   │  │
│  │ [✓ 通过] [✗ 淘汰]                                │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 1.6 面试意向沟通页面

```
┌─────────────────────────────────────────────────────────┐
│  面试意向沟通                                            │
│  候选人: 张伟 - 高级前端工程师                          │
├─────────────────────────────────────────────────────────┤
│  选择沟通方式:                                           │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │ 🤖 智能外呼     │  │ 📞 人工联系     │              │
│  │                 │  │                 │              │
│  │ 系统自动拨打    │  │ HR手动联系      │              │
│  │ 候选人电话      │  │ 候选人          │              │
│  └─────────────────┘  └─────────────────┘              │
│                                                          │
│  候选人电话: 138-1234-5678                              │
│                                                          │
│  [发起智能外呼] [我已人工联系]                          │
└─────────────────────────────────────────────────────────┘

// 人工联系后记录结果
┌─────────────────────────────────────────────────────────┐
│  记录沟通结果                                            │
├─────────────────────────────────────────────────────────┤
│  沟通结果:                                               │
│  ○ 同意面试                                              │
│  ○ 拒绝面试                                              │
│  ○ 未接听                                                │
│                                                          │
│  备注:                                                   │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 候选人对职位很感兴趣，可随时面试                │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  [取消] [确认]                                           │
└─────────────────────────────────────────────────────────┘
```

### 1.7 面试时间确认页面（HR端）

```
┌─────────────────────────────────────────────────────────┐
│  发送面试时间确认                                        │
│  候选人: 张伟 - 高级前端工程师                          │
├─────────────────────────────────────────────────────────┤
│  提供时间选项（候选人将收到邮件选择）:                  │
│                                                          │
│  选项1: [2026-06-01] [10:00] [+]                        │
│  选项2: [2026-06-01] [14:00] [+]                        │
│  选项3: [2026-06-02] [10:00] [+]                        │
│                                                          │
│  [+ 添加更多选项]                                        │
│                                                          │
│  面试官: [选择面试官▼]                                   │
│  面试地点: [会议室A___________]                          │
│  面试时长: [60] 分钟                                     │
│                                                          │
│  [取消] [发送确认邮件]                                   │
└─────────────────────────────────────────────────────────┘
```

### 1.8 面试时间确认页面（候选人端 - H5/Web）

```
┌─────────────────────────────────────────────────────────┐
│  DeepHire 招聘系统                                       │
├─────────────────────────────────────────────────────────┤
│  面试邀请                                                │
│                                                          │
│  尊敬的 张伟，                                           │
│                                                          │
│  感谢您应聘我们公司的「高级前端工程师」职位。           │
│  经过初步筛选，我们诚挚邀请您参加面试。                 │
│                                                          │
│  请选择您方便的面试时间:                                 │
│                                                          │
│  ○ 2026年6月1日 10:00-11:00                             │
│  ○ 2026年6月1日 14:00-15:00                             │
│  ○ 2026年6月2日 10:00-11:00                             │
│                                                          │
│  面试地点: 会议室A                                       │
│  面试官: 王经理                                          │
│                                                          │
│  [确认参加] [无法参加]                                   │
└─────────────────────────────────────────────────────────┘
```

### 1.9 面试管理页面

```
┌─────────────────────────────────────────────────────────┐
│  面试管理                                                │
│  [安排面试]  [批量通知]  [搜索____________]  [筛选▼]    │
├─────────────────────────────────────────────────────────┤
│  [今天(3)] [本周(12)] [全部] [待评价(5)]                │
├─────────────────────────────────────────────────────────┤
│  今天的面试 (3场)                                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 10:00 - 11:00  HR初筛面试                        │  │
│  │ 张伟 - 高级前端工程师                            │  │
│  │ 面试官: 李HR                                      │  │
│  │ 地点: 会议室A                                     │  │
│  │ 状态: 候选人已确认 ✓                             │  │
│  │ [查看详情] [改期] [取消] [填写评价]              │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 14:00 - 15:00  部门面试                          │  │
│  │ 李娜 - 产品经理                                  │  │
│  │ 面试官: 张总监                                    │  │
│  │ 地点: 会议室B                                     │  │
│  │ 状态: 待候选人确认                                │  │
│  │ [查看详情] [改期] [取消] [催促答复]              │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 1.10 面试评价表填写页面

```
┌─────────────────────────────────────────────────────────┐
│  填写面试评价                                            │
│  候选人: 张伟 - 高级前端工程师                          │
│  面试类型: HR初筛面试                                    │
│  面试时间: 2026-05-31 10:00                             │
├─────────────────────────────────────────────────────────┤
│  评价维度:                                               │
│                                                          │
│  专业能力 (40%)                                          │
│  ☆☆☆☆☆ [4分]                                            │
│                                                          │
│  沟通能力 (30%)                                          │
│  ☆☆☆☆☆ [5分]                                            │
│                                                          │
│  学习能力 (30%)                                          │
│  ☆☆☆☆☆ [4分]                                            │
│                                                          │
│  综合得分: 85分                                          │
│                                                          │
│  面试反馈:                                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 候选人技术基础扎实，对React和TypeScript有深入   │    │
│  │ 理解。沟通能力强，表达清晰。学习能力强，对新   │    │
│  │ 技术保持关注。建议进入下一轮面试。             │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  面试结果:                                               │
│  ○ 通过                                                  │
│  ○ 未通过                                                │
│  ○ 待定                                                  │
│                                                          │
│  [取消] [提交评价]                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 二、核心组件设计

### 2.1 状态流转组件

```tsx
// components/StatusFlow.tsx
interface StatusFlowProps {
  application: Application;
  onStatusChange: (newStatus: ApplicationStatus, reason?: string) => void;
}

export function StatusFlow({ application, onStatusChange }: StatusFlowProps) {
  const availableActions = getAvailableActions(application.status);
  
  return (
    <div className="flex gap-2">
      {availableActions.map(action => (
        <Button
          key={action.status}
          variant={action.variant}
          onClick={() => handleAction(action)}
        >
          {action.label}
        </Button>
      ))}
    </div>
  );
}

function getAvailableActions(status: ApplicationStatus) {
  const actionsMap = {
    [ApplicationStatus.NEW]: [
      { status: ApplicationStatus.HR_SCREENING, label: '开始筛选', variant: 'default' },
      { status: ApplicationStatus.HR_REJECTED, label: '淘汰', variant: 'destructive' },
    ],
    [ApplicationStatus.HR_SCREENING]: [
      { status: ApplicationStatus.HR_INTERVIEW_SCHEDULED, label: '安排HR初筛面试', variant: 'default' },
      { status: ApplicationStatus.HR_REJECTED, label: '淘汰', variant: 'destructive' },
    ],
    [ApplicationStatus.HR_INTERVIEW_COMPLETED]: [
      { status: ApplicationStatus.SENT_TO_INTERVIEWER, label: '推送面试官', variant: 'default' },
      { status: ApplicationStatus.HR_INTERVIEW_REJECTED, label: '淘汰', variant: 'destructive' },
    ],
    // ... 其他状态的可用操作
  };
  
  return actionsMap[status] || [];
}
```

### 2.2 时间线组件

```tsx
// components/Timeline.tsx
interface TimelineProps {
  applicationId: string;
}

export function Timeline({ applicationId }: TimelineProps) {
  const { data: history } = useQuery({
    queryKey: ['application-history', applicationId],
    queryFn: () => fetchApplicationHistory(applicationId),
  });
  
  return (
    <div className="space-y-6">
      {history?.map((event, index) => (
        <div key={event.id} className="flex gap-4">
          <div className="flex flex-col items-center">
            <div className={cn(
              "w-3 h-3 rounded-full",
              getStatusColor(event.to_status)
            )} />
            {index < history.length - 1 && (
              <div className="w-0.5 flex-1 bg-gray-200 mt-2" />
            )}
          </div>
          
          <div className="flex-1 pb-6">
            <div className="flex items-center justify-between">
              <span className="font-medium">
                {getStatusLabel(event.to_status)}
              </span>
              <span className="text-sm text-gray-500">
                {formatDateTime(event.created_at)}
              </span>
            </div>
            
            {event.reason && (
              <p className="text-sm text-gray-600 mt-1">{event.reason}</p>
            )}
            
            <p className="text-xs text-gray-400 mt-1">
              操作人: {event.operator_name}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
```

### 2.3 面试安排对话框

```tsx
// components/ScheduleInterviewDialog.tsx
interface ScheduleInterviewDialogProps {
  applicationId: string;
  interviewType: InterviewType;
  open: boolean;
  onClose: () => void;
}

export function ScheduleInterviewDialog({
  applicationId,
  interviewType,
  open,
  onClose
}: ScheduleInterviewDialogProps) {
  const form = useForm<ScheduleInterviewForm>({
    defaultValues: {
      interviewerId: '',
      scorecardTemplateId: '',
      scheduledAt: new Date(),
      duration: 60,
      location: '',
    }
  });
  
  const onSubmit = async (data: ScheduleInterviewForm) => {
    await scheduleInterview({
      applicationId,
      interviewType,
      ...data,
    });
    
    toast.success('面试安排成功');
    onClose();
  };
  
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>安排{getInterviewTypeLabel(interviewType)}</DialogTitle>
        </DialogHeader>
        
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="interviewerId"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>面试官</FormLabel>
                  <UserSelect
                    value={field.value}
                    onChange={field.onChange}
                    role="interviewer"
                  />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="scorecardTemplateId"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>评价表模板</FormLabel>
                  <ScorecardTemplateSelect
                    value={field.value}
                    onChange={field.onChange}
                    interviewType={interviewType}
                  />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="scheduledAt"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>面试时间</FormLabel>
                  <DateTimePicker
                    value={field.value}
                    onChange={field.onChange}
                  />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="location"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>面试地点</FormLabel>
                  <Input {...field} placeholder="会议室A 或 线上会议链接" />
                </FormItem>
              )}
            />
            
            <DialogFooter>
              <Button type="button" variant="outline" onClick={onClose}>
                取消
              </Button>
              <Button type="submit">
                确认安排
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
```

---

## 三、状态管理设计

### 3.1 全局状态（使用Zustand）

```typescript
// stores/useApplicationStore.ts
interface ApplicationStore {
  // 状态
  applications: Application[];
  currentApplication: Application | null;
  filters: ApplicationFilters;
  
  // 操作
  fetchApplications: (filters?: ApplicationFilters) => Promise<void>;
  fetchApplicationById: (id: string) => Promise<void>;
  updateApplicationStatus: (id: string, status: ApplicationStatus, reason?: string) => Promise<void>;
  pushToInterviewer: (id: string, interviewerId: string) => Promise<void>;
  rejectApplication: (id: string, reason: string) => Promise<void>;
}

export const useApplicationStore = create<ApplicationStore>((set, get) => ({
  applications: [],
  currentApplication: null,
  filters: {},
  
  fetchApplications: async (filters) => {
    const data = await api.getApplications(filters);
    set({ applications: data.items, filters });
  },
  
  fetchApplicationById: async (id) => {
    const data = await api.getApplication(id);
    set({ currentApplication: data });
  },
  
  updateApplicationStatus: async (id, status, reason) => {
    await api.updateApplicationStatus(id, status, reason);
    await get().fetchApplicationById(id);
  },
  
  // ... 其他操作
}));
```

---

**文档版本**: v2.0
**创建时间**: 2026-05-30
**状态**: 前端设计完成
