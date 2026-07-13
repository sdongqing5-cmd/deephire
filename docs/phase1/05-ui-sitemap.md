# Phase 1: UI Sitemap 与页面结构

## 1. 整体导航结构

### 1.1 登录后的主导航

```
┌─────────────────────────────────────────────────────────┐
│  DeepHire Logo    [Search]    [Notifications]  [Avatar] │
└─────────────────────────────────────────────────────────┘
│                                                           │
│  Sidebar                    Main Content Area            │
│  ┌──────────┐              ┌─────────────────────────┐  │
│  │ 🏠 Home  │              │                         │  │
│  │ 👥 Jobs  │              │                         │  │
│  │ 🔍 Search│              │      Page Content       │  │
│  │ 📋 Candidates            │                         │  │
│  │ 📅 Interviews            │                         │  │
│  │ 📊 Analytics             │                         │  │
│  └──────────┘              └─────────────────────────┘  │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

**为什么这样设计？**
- **侧边栏导航**：现代 SaaS 标准布局
- **全局搜索**：快速访问任何候选人
- **通知中心**：实时提醒
- **用户头像**：快速访问设置

---

## 2. 角色导航差异

### 2.1 HR 导航

```
🏠 Dashboard
👥 Jobs
   ├─ All Jobs
   ├─ Create Job
   └─ Archived Jobs
🔍 Search
📋 Candidates
   ├─ All Candidates
   ├─ By Status
   └─ By Owner
📅 Interviews
   ├─ Calendar View
   ├─ Today
   └─ Upcoming
📊 Analytics
   ├─ Hiring Funnel
   ├─ Time to Hire
   └─ Source Analysis
⚙️ Settings
   ├─ Team
   ├─ Integrations
   └─ Profile
```

### 2.2 Recruiter 导航

```
🏠 Dashboard
👥 My Jobs
🔍 Search (重点)
📋 My Candidates
   ├─ To Contact Today
   ├─ In Progress
   └─ All
📅 My Interviews
📤 Upload Resume
⚙️ Settings
```

**为什么更简单？**
- Recruiter 只关心自己的数据
- 减少干扰，提升效率

### 2.3 Interviewer 导航

```
🏠 Today's Interviews
📋 Pending Feedback
📅 Interview History
⚙️ Settings
```

**为什么极简？**
- Interviewer 只需要完成面试
- 不需要复杂功能

---

## 3. 页面 Sitemap

### 3.1 认证页面

```
/login
/forgot-password
/reset-password
```

### 3.2 HR 页面

```
/dashboard                    # HR Dashboard
/jobs                         # 职位列表
/jobs/new                     # 创建职位
/jobs/:id                     # 职位详情
/jobs/:id/edit                # 编辑职位
/jobs/:id/candidates          # 职位候选人

/search                       # 搜索页面（核心）

/candidates                   # 候选人列表
/candidates/:id               # 候选人详情
/candidates/:id/edit          # 编辑候选人

/interviews                   # 面试列表
/interviews/calendar          # 面试日历
/interviews/:id               # 面试详情
/interviews/:id/feedback      # 面试反馈

/analytics                    # 数据分析
/analytics/funnel             # 招聘漏斗
/analytics/sources            # 来源分析

/settings                     # 设置
/settings/team                # 团队管理
/settings/profile             # 个人资料
```

### 3.3 Recruiter 页面

```
/dashboard                    # Recruiter Dashboard
/my-jobs                      # 我的职位
/search                       # 搜索页面（核心）
/my-candidates                # 我的候选人
/candidates/:id               # 候选人详情
/upload                       # 上传简历
/my-interviews                # 我的面试
/settings/profile             # 个人资料
```

### 3.4 Interviewer 页面

```
/dashboard                    # Today's Interviews
/interviews/:id               # 面试详情
/interviews/:id/feedback      # 提交反馈
/history                      # 面试历史
/settings/profile             # 个人资料
```

---

## 4. 核心页面详细设计

### 4.1 登录页面 (`/login`)

**布局**：
```
┌─────────────────────────────────────────┐
│                                         │
│              DeepHire Logo              │
│                                         │
│         AI-Powered Recruiting           │
│                                         │
│    ┌─────────────────────────────┐     │
│    │  Email                      │     │
│    │  [input]                    │     │
│    │                             │     │
│    │  Password                   │     │
│    │  [input]                    │     │
│    │                             │     │
│    │  [Login Button]             │     │
│    │                             │     │
│    │  Forgot password?           │     │
│    └─────────────────────────────┘     │
│                                         │
└─────────────────────────────────────────┘
```

**特点**：
- 极简设计
- 居中布局
- 品牌感强

---

### 4.2 HR Dashboard (`/dashboard`)

**布局**：
```
┌─────────────────────────────────────────────────────────┐
│  Welcome back, HR Admin                    [Create Job] │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Stats Cards (4 cards in a row)                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ 15       │ │ 10,000   │ │ 500      │ │ 8        │  │
│  │ Open Jobs│ │ Candidates│ │ Active   │ │ Today    │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                                                           │
│  Quick Actions                                           │
│  [Search Candidates] [Upload Resume] [Schedule Interview]│
│                                                           │
│  ┌─────────────────────┐  ┌─────────────────────────┐  │
│  │ Today's Interviews  │  │ Recent Activities       │  │
│  │                     │  │                         │  │
│  │ 10:00 张三          │  │ • 李四 status changed   │  │
│  │ 14:00 李四          │  │ • 王五 resume uploaded  │  │
│  │ 16:00 王五          │  │ • 赵六 interview done   │  │
│  │                     │  │                         │  │
│  └─────────────────────┘  └─────────────────────────┘  │
│                                                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Recent Candidate Activations                      │  │
│  │                                                   │  │
│  │ [Card] [Card] [Card] [Card]                      │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

**特点**：
- 信息密度高
- 快速操作
- 卡片式布局

---

### 4.3 搜索页面 (`/search`) - 核心页面

**布局**：
```
┌─────────────────────────────────────────────────────────┐
│  Search Candidates                                       │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │  🔍  找做过医疗器械销售，负责东南亚市场的人      │    │
│  └─────────────────────────────────────────────────┘    │
│                                                           │
│  Filters:                                                │
│  [5-10 years] [Shanghai] [Medical Device] [×]           │
│  + Add Filter                                            │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │ Search Mode: ● Hybrid  ○ Keyword  ○ Semantic   │    │
│  └─────────────────────────────────────────────────┘    │
│                                                           │
│  Found 50 candidates · 150ms                            │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 张三                              Match: 95%    │    │
│  │ Senior Sales Manager @ MedTech Inc              │    │
│  │ 📍 Shanghai  💼 8 years  🏷️ Medical Device      │    │
│  │                                                 │    │
│  │ Match Reasons:                                  │    │
│  │ • 8年医疗器械销售经验                           │    │
│  │ • 负责东南亚市场                                │    │
│  │ • B2B销售背景                                   │    │
│  │                                                 │    │
│  │ [View Profile] [Contact]                        │    │
│  └─────────────────────────────────────────────────┘    │
│                                                           │
│  [More results...]                                       │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

**为什么这样设计？**

1. **超大搜索框**：
   - 视觉焦点
   - 支持自然语言
   - 降低使用门槛

2. **Filter Chips**：
   - 快速添加/移除
   - 视觉清晰
   - 不占空间

3. **Match Score**：
   - 直观展示匹配度
   - 帮助快速筛选

4. **Match Reasons**：
   - 解释为什么匹配
   - 提升信任度
   - AI 可解释性

5. **卡片式结果**：
   - 信息密度高
   - 易于扫描
   - 支持快速操作

---

### 4.4 候选人详情页 (`/candidates/:id`)

**布局**：
```
┌─────────────────────────────────────────────────────────┐
│  ← Back to Search                    [Edit] [Contact]   │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────┐  ┌─────────────────────────────────────┐ │
│  │          │  │ 张三                                 │ │
│  │  Avatar  │  │ Senior Sales Manager @ MedTech Inc  │ │
│  │          │  │ 📍 Shanghai  💼 8 years             │ │
│  └──────────┘  │ 📧 zhang@example.com                │ │
│                │ 📱 +86 138 0000 0000                │ │
│                │                                     │ │
│                │ Status: [New ▼]                     │ │
│                │ Tags: [医疗器械] [东南亚] [+]       │ │
│                └─────────────────────────────────────┘ │
│                                                           │
│  ┌─────────────────────┐  ┌─────────────────────────┐  │
│  │ Resume Summary      │  │ Timeline                │  │
│  │                     │  │                         │  │
│  │ 8年医疗器械销售经验  │  │ • 2026-05-23 10:00     │  │
│  │ 负责东南亚市场       │  │   Resume uploaded      │  │
│  │ 年销售额$5M         │  │                         │  │
│  │ 团队管理10人        │  │ • 2026-05-23 10:05     │  │
│  │                     │  │   Status changed       │  │
│  │ [View Full Resume]  │  │                         │  │
│  │                     │  │ • 2026-05-23 10:10     │  │
│  └─────────────────────┘  │   Note added           │  │
│                            │                         │  │
│  ┌─────────────────────┐  │ [Load More]            │  │
│  │ Experience          │  └─────────────────────────┘  │
│  │                     │                                │
│  │ MedTech Inc         │  ┌─────────────────────────┐  │
│  │ Senior Sales Mgr    │  │ Notes                   │  │
│  │ 2018-01 - Present   │  │                         │  │
│  │                     │  │ [Add Note]              │  │
│  │ • 负责东南亚市场     │  │                         │  │
│  │ • 年销售额$5M       │  │ 候选人对薪资要求较高     │  │
│  │ • 团队管理10人      │  │ - by Recruiter          │  │
│  │                     │  │   2026-05-23 10:10      │  │
│  └─────────────────────┘  └─────────────────────────┘  │
│                                                           │
│  ┌─────────────────────┐                                │
│  │ Education           │                                │
│  │                     │                                │
│  │ 复旦大学             │                                │
│  │ Bachelor - 市场营销  │                                │
│  │ 2010-09 - 2014-06   │                                │
│  └─────────────────────┘                                │
│                                                           │
│  ┌─────────────────────┐                                │
│  │ Skills              │                                │
│  │                     │                                │
│  │ [B2B销售] [医疗器械] [东南亚市场] [团队管理]         │
│  └─────────────────────┘                                │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

**为什么这样设计？**

1. **三栏布局**：
   - 左侧：基础信息 + 简历内容
   - 右侧：Timeline + Notes
   - 信息层级清晰

2. **Timeline**：
   - 完整的活动记录
   - 时间倒序
   - 支持快速回顾

3. **Notes**：
   - 团队协作
   - 记录沟通细节
   - 支持私有备注

4. **快速操作**：
   - 状态更新
   - 添加标签
   - 联系候选人

---

### 4.5 Recruiter Dashboard (`/dashboard`)

**布局**：
```
┌─────────────────────────────────────────────────────────┐
│  Good morning, Recruiter                [Upload Resume] │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Stats Cards                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ 5        │ │ 50       │ │ 10       │ │ 25       │  │
│  │ My Jobs  │ │ Candidates│ │ To Contact│ │ This Week│  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                                                           │
│  Quick Actions                                           │
│  [🔍 Search Candidates] [📤 Upload Resume] [📞 Contact] │
│                                                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │ To Contact Today (10)                             │  │
│  │                                                   │  │
│  │ [Card] 张三 - Medical Device Sales                │  │
│  │ [Card] 李四 - Backend Engineer                    │  │
│  │ [Card] 王五 - Product Manager                     │  │
│  │                                                   │  │
│  │ [View All]                                        │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Recent Contacts                                   │  │
│  │                                                   │  │
│  │ • 张三 - Interested (2 hours ago)                 │  │
│  │ • 李四 - Follow up later (Yesterday)              │  │
│  │ • 王五 - Not interested (2 days ago)              │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

**为什么这样设计？**

1. **工作效率优先**：
   - 今日待办清晰
   - 快速操作按钮
   - 减少点击路径

2. **To Contact Today**：
   - 自动提醒
   - 优先级排序
   - 一键联系

---

### 4.6 Interviewer Dashboard (`/dashboard`)

**布局**：
```
┌─────────────────────────────────────────────────────────┐
│  Today's Interviews - May 23, 2026                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 10:00 - 11:00                                     │  │
│  │                                                   │  │
│  │ 张三                                              │  │
│  │ Senior Sales Manager                              │  │
│  │ Position: Medical Device Sales Manager           │  │
│  │ Round: 1st Interview (Technical)                 │  │
│  │                                                   │  │
│  │ 📍 Office Room 301                                │  │
│  │                                                   │  │
│  │ [View Profile] [Start Interview]                 │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 14:00 - 15:00                                     │  │
│  │                                                   │  │
│  │ 李四                                              │  │
│  │ Backend Engineer                                  │  │
│  │ Position: Senior Backend Engineer                │  │
│  │ Round: 2nd Interview (Behavioral)                │  │
│  │                                                   │  │
│  │ 🔗 Zoom Meeting                                   │  │
│  │                                                   │  │
│  │ [View Profile] [Join Meeting]                    │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Pending Feedback (2)                              │  │
│  │                                                   │  │
│  │ • 王五 - Interviewed yesterday                    │  │
│  │ • 赵六 - Interviewed 2 days ago                   │  │
│  │                                                   │  │
│  │ [Submit Feedback]                                 │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

**为什么这样设计？**

1. **极简设计**：
   - 只显示今天的面试
   - 时间清晰
   - 一键进入

2. **Pending Feedback**：
   - 提醒未完成的反馈
   - 避免遗漏

---

### 4.7 面试反馈页面 (`/interviews/:id/feedback`)

**布局**：
```
┌─────────────────────────────────────────────────────────┐
│  Interview Feedback - 张三                               │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Position: Medical Device Sales Manager                 │
│  Date: May 23, 2026 10:00                               │
│  Duration: 60 minutes                                    │
│                                                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Overall Score                                     │  │
│  │                                                   │  │
│  │ ⭐ ⭐ ⭐ ⭐ ☆  (4/5)                                │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Dimensions                                        │  │
│  │                                                   │  │
│  │ Technical Skills      ⭐⭐⭐⭐☆ (4/5)              │  │
│  │ Communication         ⭐⭐⭐⭐⭐ (5/5)              │  │
│  │ Team Fit              ⭐⭐⭐⭐☆ (4/5)              │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Feedback                                          │  │
│  │                                                   │  │
│  │ [Textarea]                                        │  │
│  │ 候选人技术能力强，沟通清晰，团队协作意识好。       │  │
│  │ 对医疗器械行业有深入理解，东南亚市场经验丰富。     │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Result                                            │  │
│  │                                                   │  │
│  │ ● Pass    ○ Pending    ○ Reject                  │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
│  [Cancel] [Submit Feedback]                             │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

**为什么这样设计？**

1. **结构化评分**：
   - 多维度评分
   - 量化评估
   - 便于对比

2. **简单明了**：
   - 不要复杂表单
   - 快速完成
   - 降低负担

---

## 5. 移动端适配

### 5.1 响应式设计

所有页面必须支持：
- Desktop: 1920px+
- Laptop: 1366px
- Tablet: 768px
- Mobile: 375px

### 5.2 移动端优先页面

1. **搜索页面**：移动端也要好用
2. **候选人详情**：支持快速查看
3. **面试列表**：Interviewer 移动端查看

---

## 6. 交互设计原则

### 6.1 减少点击

❌ **不好**：
```
Dashboard → Candidates → Search → Input → Filter → Results → Detail
```

✅ **好**：
```
Dashboard → Search (with filters) → Results → Detail
```

### 6.2 快捷操作

每个页面都要有：
- 快捷键支持（Cmd+K 搜索）
- 快速操作按钮
- 右键菜单

### 6.3 即时反馈

- Loading skeleton
- Optimistic updates
- Toast notifications
- Progress indicators

---

## 7. 空状态设计

每个列表页面都要有：

```
┌─────────────────────────────────────┐
│                                     │
│           [Empty Icon]              │
│                                     │
│      No candidates yet              │
│                                     │
│   Upload a resume to get started   │
│                                     │
│      [Upload Resume Button]         │
│                                     │
└─────────────────────────────────────┘
```

---

## 总结

这套 UI Sitemap：

✅ **角色差异化**：不同角色不同体验
✅ **效率优先**：减少点击，快速操作
✅ **信息密度**：高信息密度，不拥挤
✅ **现代设计**：卡片式，留白合理
✅ **搜索核心**：搜索体验是重点
✅ **移动友好**：响应式设计

下一步：页面 Wireframes
