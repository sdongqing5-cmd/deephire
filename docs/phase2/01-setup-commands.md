# Phase 2: 项目初始化命令清单

## 1. 前端初始化命令

### 1.1 创建 Next.js 15 项目

```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*" --use-npm
```

**选项说明**：
- `--typescript`: 使用 TypeScript
- `--tailwind`: 使用 Tailwind CSS
- `--app`: 使用 App Router
- `--no-src-dir`: 不使用 src 目录
- `--import-alias "@/*"`: 设置导入别名
- `--use-npm`: 使用 npm（而不是 yarn/pnpm）

---

### 1.2 安装核心依赖

```bash
cd frontend

# 状态管理
npm install @tanstack/react-query zustand

# HTTP 客户端
npm install axios

# 表单处理
npm install react-hook-form zod @hookform/resolvers

# 日期处理
npm install date-fns

# 工具库
npm install clsx tailwind-merge

# 动画
npm install framer-motion

# 图标
npm install lucide-react
```

---

### 1.3 安装 shadcn/ui

```bash
cd frontend

# 初始化 shadcn/ui
npx shadcn@latest init

# 安装常用组件
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add input
npx shadcn@latest add label
npx shadcn@latest add textarea
npx shadcn@latest add select
npx shadcn@latest add dialog
npx shadcn@latest add dropdown-menu
npx shadcn@latest add toast
npx shadcn@latest add avatar
npx shadcn@latest add badge
npx shadcn@latest add separator
npx shadcn@latest add skeleton
npx shadcn@latest add tabs
npx shadcn@latest add checkbox
npx shadcn@latest add radio-group
```

---

### 1.4 安装开发依赖

```bash
cd frontend

npm install -D @types/node @types/react @types/react-dom
npm install -D eslint eslint-config-next
npm install -D prettier prettier-plugin-tailwindcss
```

---

## 2. 后端初始化命令（稍后执行）

### 2.1 创建 Conda 环境（推荐）

```bash
cd backend

# 创建独立的 conda 环境（Python 3.12）
conda create -n deephire python=3.12 -y

# 激活环境
conda activate deephire

# 退出环境（需要时）
# conda deactivate

# 删除环境（需要时）
# conda env remove -n deephire
```

**为什么用 Conda？**
- ✅ 完全隔离，不影响其他项目
- ✅ 可以指定 Python 版本
- ✅ 管理非 Python 依赖

---

### 2.2 安装 Python 依赖

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 或者使用 pip install 逐个安装
pip install fastapi==0.115.0
pip install uvicorn[standard]==0.30.0
pip install sqlalchemy==2.0.0
pip install alembic==1.13.0
pip install asyncpg==0.29.0
pip install redis==5.0.0
pip install python-jose[cryptography]==3.3.0
pip install passlib[bcrypt]==1.7.4
pip install pydantic==2.0.0
pip install pydantic-settings==2.0.0
pip install openai==1.0.0
pip install python-dotenv==1.0.0
pip install loguru==0.7.0
```

---

## 3. Git 初始化

```bash
# 在项目根目录
git init
git add .
git commit -m "chore: initial project setup"
```

---

## 4. 启动开发服务器

### 4.1 前端

```bash
cd frontend
npm run dev
```

访问：http://localhost:3000

---

### 4.2 后端（稍后）

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

访问：http://localhost:8000/docs

---

## 5. Docker 命令（稍后）

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 执行顺序

### 现在执行（前端）：

1. ✅ 创建 Next.js 项目
2. ✅ 安装核心依赖
3. ✅ 安装 shadcn/ui
4. ✅ 安装开发依赖
5. ✅ 启动开发服务器

### 稍后执行（后端）：

6. ⏸️ 创建 Python 虚拟环境
7. ⏸️ 安装 Python 依赖
8. ⏸️ 启动后端服务器

---

## 注意事项

1. **Node.js 版本**：需要 Node.js 18.17 或更高版本
2. **Python 版本**：需要 Python 3.12
3. **网络**：某些 npm 包可能需要翻墙
4. **权限**：确保有写入权限

---

## 下一步

请按顺序执行上述命令，完成后告诉我，我会继续创建项目文件。
