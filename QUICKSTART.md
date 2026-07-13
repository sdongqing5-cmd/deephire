# DeepHire 快速启动指南

## 🚀 5分钟快速启动

### 前置条件

确保已安装：
- Docker Desktop (推荐) 或 Docker + Docker Compose
- Python 3.11+ 和 Conda
- Node.js 18+

---

## 方式1: Docker 一键启动 (最简单)

```bash
# 1. 进入项目目录
cd /Users/nanakio/Documents/zhaopin/DeepHire

# 2. 配置环境变量
cd backend
cp .env.example .env
# 编辑 .env，填入你的 OPENAI_API_KEY

# 3. 启动所有服务
docker-compose up -d

# 4. 等待服务启动 (约1分钟)
docker-compose ps

# 5. 初始化数据库
docker exec -it deephire-backend python init_db.py
docker exec -it deephire-backend python sync_opensearch.py

# 6. 访问应用
# 前端: http://localhost:3000
# 后端API: http://localhost:8000/docs
```

**完成！** 使用 `hr@deephire.com / password` 登录

---

## 方式2: 本地开发模式 (推荐开发使用)

### Step 1: 启动基础服务

```bash
cd /Users/nanakio/Documents/zhaopin/DeepHire

# 只启动数据库服务
docker-compose up -d postgres redis opensearch

# 等待服务就绪
sleep 30
```

### Step 2: 配置后端

```bash
cd backend

# 创建 Conda 环境
conda create -n deephire python=3.11 -y
conda activate deephire

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env  # 填入你的 OPENAI_API_KEY
```

### Step 3: 初始化数据

```bash
# 初始化数据库和种子数据
python init_db.py

# 同步 OpenSearch 索引
python sync_opensearch.py
```

### Step 4: 启动后端

```bash
# 启动 FastAPI 服务
uvicorn app.main:app --reload --port 8000

# 访问 API 文档: http://localhost:8000/docs
```

### Step 5: 启动前端

```bash
# 新开一个终端
cd /Users/nanakio/Documents/zhaopin/DeepHire/frontend

# 安装依赖
npm install

# 配置环境变量
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# 启动开发服务器
npm run dev

# 访问应用: http://localhost:3000
```

---

## 验证部署

### 1. 检查服务状态

```bash
# 检查 Docker 服务
docker-compose ps

# 检查后端健康
curl http://localhost:8000/health

# 检查 OpenSearch
curl http://localhost:9200/_cluster/health
```

### 2. 测试登录

访问 http://localhost:3000

使用以下账号登录：

| 角色 | 邮箱 | 密码 |
|------|------|------|
| HR | hr@deephire.com | password |
| Recruiter | recruiter@deephire.com | password |
| Interviewer | interviewer@deephire.com | password |

### 3. 测试核心功能

1. **候选人管理**: 查看预置的5个候选人
2. **简历上传**: 上传一份PDF简历测试解析
3. **智能搜索**: 搜索 "Python 开发工程师"
4. **面试管理**: 查看预置的面试安排

---

## 常用命令

### Docker 管理

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 重启服务
docker-compose restart backend

# 清理数据 (谨慎使用)
docker-compose down -v
```

### 后端管理

```bash
cd backend
conda activate deephire

# 启动开发服务器
uvicorn app.main:app --reload --port 8000

# 重新初始化数据库
python init_db.py

# 重新同步搜索索引
python sync_opensearch.py

# 查看数据库
psql -U deephire -h localhost -d deephire
```

### 前端管理

```bash
cd frontend

# 开发模式
npm run dev

# 生产构建
npm run build
npm run start

# 代码检查
npm run lint

# 清理缓存
rm -rf .next node_modules
npm install
```

---

## 环境变量配置

### 后端 (.env)

**必填项：**
```bash
# OpenAI API Key (必须)
OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# 数据库 (Docker 默认配置)
DATABASE_URL=postgresql://deephire:deephire@localhost:5432/deephire

# JWT 密钥 (生产环境必须修改)
SECRET_KEY=your-secret-key-change-this-in-production
```

**可选项：**
```bash
# OpenAI Base URL (使用代理时修改)
OPENAI_BASE_URL=https://api.openai.com/v1

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenSearch
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200

# CORS (添加你的前端域名)
CORS_ORIGINS=http://localhost:3000
```

### 前端 (.env.local)

```bash
# 后端 API 地址
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 故障排查

### 问题1: Docker 服务启动失败

```bash
# 检查 Docker 是否运行
docker ps

# 查看错误日志
docker-compose logs

# 重启 Docker Desktop
# macOS: 重启 Docker Desktop 应用
```

### 问题2: 数据库连接失败

```bash
# 检查 PostgreSQL 是否运行
docker-compose ps postgres

# 检查端口占用
lsof -i :5432

# 重启数据库
docker-compose restart postgres
```

### 问题3: OpenSearch 内存不足

```bash
# macOS 增加虚拟内存
sudo sysctl -w vm.max_map_count=262144

# 或修改 docker-compose.yml 降低内存
# OPENSEARCH_JAVA_OPTS=-Xms256m -Xmx256m
```

### 问题4: 前端无法连接后端

```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 检查 CORS 配置
# backend/.env 中的 CORS_ORIGINS 必须包含 http://localhost:3000

# 检查前端环境变量
cat frontend/.env.local
```

### 问题5: 简历解析失败

```bash
# 检查 OpenAI API Key
echo $OPENAI_API_KEY

# 测试 API 连接
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# 查看后端日志
docker-compose logs backend | grep -i error
```

---

## 开发工作流

### 日常开发

```bash
# 1. 启动基础服务 (只需一次)
docker-compose up -d postgres redis opensearch

# 2. 启动后端 (终端1)
cd backend
conda activate deephire
uvicorn app.main:app --reload --port 8000

# 3. 启动前端 (终端2)
cd frontend
npm run dev

# 4. 开始开发
# 后端代码修改会自动重载
# 前端代码修改会自动刷新
```

### 数据重置

```bash
# 重置数据库
cd backend
python init_db.py

# 重置搜索索引
python sync_opensearch.py
```

### 添加测试数据

```bash
# 编辑 backend/init_db.py
# 添加更多候选人、职位、面试数据

# 重新运行初始化
python init_db.py
```

---

## 生产部署

详细部署指南请查看: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

快速生产部署：

```bash
# 1. 配置生产环境变量
cp backend/.env.example backend/.env.production
nano backend/.env.production

# 2. 构建生产镜像
docker-compose -f docker-compose.prod.yml build

# 3. 启动生产服务
docker-compose -f docker-compose.prod.yml up -d

# 4. 初始化数据
docker exec -it deephire-backend python init_db.py
```

---

## 下一步

- 📖 阅读 [PROJECT_BRIEF.md](./PROJECT_BRIEF.md) 了解产品设计
- 🚀 阅读 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) 了解部署细节
- 📝 查看 [API 文档](http://localhost:8000/docs) 了解接口
- 🎨 查看前端页面了解 UI 设计

---

**需要帮助？** 检查日志文件或查看 [常见问题](#故障排查)
