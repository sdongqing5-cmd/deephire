# DeepHire 部署与运行指南

## 📋 目录

1. [系统要求](#系统要求)
2. [快速开始](#快速开始)
3. [开发环境部署](#开发环境部署)
4. [生产环境部署](#生产环境部署)
5. [常见问题](#常见问题)

---

## 系统要求

### 基础环境
- **Python**: 3.11+
- **Node.js**: 18+
- **PostgreSQL**: 14+
- **Redis**: 6+
- **OpenSearch**: 2.x
- **Docker**: 20+ (可选)
- **Conda**: 最新版本

### 硬件要求
- **开发环境**: 8GB RAM, 20GB 磁盘
- **生产环境**: 16GB+ RAM, 100GB+ 磁盘

---

## 快速开始

### 1. 克隆项目
```bash
cd /Users/nanakio/Documents/zhaopin/DeepHire
```

### 2. 启动基础服务

#### 方式A: 使用 Docker (推荐)
```bash
# 启动 PostgreSQL, Redis, OpenSearch
cd backend
docker-compose up -d postgres redis opensearch

# 等待服务启动 (约30秒)
sleep 30
```

#### 方式B: 本地安装
```bash
# PostgreSQL
brew install postgresql@14
brew services start postgresql@14

# Redis
brew install redis
brew services start redis

# OpenSearch
brew install opensearch
brew services start opensearch
```

### 3. 配置后端环境

```bash
cd backend

# 创建 Conda 环境
conda create -n deephire python=3.11 -y
conda activate deephire

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

### 4. 初始化数据库

```bash
# 创建数据库
psql -U postgres -c "CREATE DATABASE deephire;"
psql -U postgres -c "CREATE USER deephire WITH PASSWORD 'deephire';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE deephire TO deephire;"
psql -U postgres -d deephire -c "GRANT ALL ON SCHEMA public TO deephire;"

# 初始化表和种子数据
python init_db.py

# 同步 OpenSearch 索引
python sync_opensearch.py
```

### 5. 启动后端服务

```bash
# 开发模式
uvicorn app.main:app --reload --port 8000

# 访问 API 文档
# http://localhost:8000/docs
```

### 6. 配置前端环境

```bash
cd ../frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env.local
# 编辑 .env.local
```

### 7. 启动前端服务

```bash
# 开发模式
npm run dev

# 访问应用
# http://localhost:3000
```

---

## 开发环境部署

### 完整启动流程

#### 1. 启动基础服务
```bash
# 终端 1: 启动 Docker 服务
cd backend
docker-compose up -d

# 检查服务状态
docker-compose ps
```

#### 2. 启动后端
```bash
# 终端 2: 后端服务
cd backend
conda activate deephire
uvicorn app.main:app --reload --port 8000 --log-level info
```

#### 3. 启动前端
```bash
# 终端 3: 前端服务
cd frontend
npm run dev
```

### 验证部署

```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 检查 API 文档
open http://localhost:8000/docs

# 检查前端
open http://localhost:3000
```

### Demo 账号

登录测试账号：

| 角色 | 邮箱 | 密码 |
|------|------|------|
| HR | hr@deephire.com | password |
| Recruiter | recruiter@deephire.com | password |
| Interviewer | interviewer@deephire.com | password |

---

## 生产环境部署

### 方式1: Docker Compose (推荐)

#### 1. 准备生产配置

```bash
# 创建生产环境配置
cd backend
cp .env.example .env.production

# 编辑 .env.production
# 修改以下关键配置：
# - SECRET_KEY: 生成强密钥
# - DATABASE_URL: 生产数据库地址
# - OPENAI_API_KEY: 你的 OpenAI API Key
# - CORS_ORIGINS: 生产域名
```

#### 2. 构建镜像

```bash
# 构建后端镜像
cd backend
docker build -t deephire-backend:latest .

# 构建前端镜像
cd ../frontend
docker build -t deephire-frontend:latest .
```

#### 3. 启动生产服务

```bash
# 使用 docker-compose
cd backend
docker-compose -f docker-compose.prod.yml up -d

# 检查服务状态
docker-compose -f docker-compose.prod.yml ps
```

#### 4. 初始化生产数据库

```bash
# 进入后端容器
docker exec -it deephire-backend bash

# 运行初始化脚本
python init_db.py
python sync_opensearch.py

exit
```

### 方式2: 云服务部署

#### AWS 部署示例

```bash
# 1. 准备 EC2 实例
# - 类型: t3.medium 或更高
# - 系统: Ubuntu 22.04
# - 安全组: 开放 80, 443, 8000, 3000

# 2. 安装 Docker
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker

# 3. 克隆代码
git clone <your-repo-url>
cd DeepHire

# 4. 配置环境变量
cd backend
cp .env.example .env.production
nano .env.production

# 5. 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 6. 配置 Nginx 反向代理
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/deephire
```

Nginx 配置示例：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # 后端 API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

#### 配置 SSL (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### 方式3: Kubernetes 部署

```bash
# 1. 准备 K8s 配置文件
cd k8s

# 2. 创建命名空间
kubectl create namespace deephire

# 3. 创建 ConfigMap 和 Secret
kubectl create configmap deephire-config --from-env-file=.env.production -n deephire
kubectl create secret generic deephire-secrets --from-literal=openai-key=<your-key> -n deephire

# 4. 部署服务
kubectl apply -f postgres.yaml -n deephire
kubectl apply -f redis.yaml -n deephire
kubectl apply -f opensearch.yaml -n deephire
kubectl apply -f backend.yaml -n deephire
kubectl apply -f frontend.yaml -n deephire

# 5. 检查部署状态
kubectl get pods -n deephire
kubectl get services -n deephire
```

---

## 环境变量配置

### 后端 (.env)

```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@host:5432/deephire
DATABASE_ECHO=False

# Redis 配置
REDIS_URL=redis://host:6379/0

# OpenSearch 配置
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=admin

# JWT 配置
SECRET_KEY=<生成强密钥>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI 配置
OPENAI_API_KEY=<your-api-key>
OPENAI_BASE_URL=https://api.openai.com/v1

# CORS 配置
CORS_ORIGINS=http://localhost:3000,https://your-domain.com

# 环境
ENVIRONMENT=production
```

### 前端 (.env.local)

```bash
# API 地址
NEXT_PUBLIC_API_URL=http://localhost:8000

# 其他配置
NEXT_PUBLIC_APP_NAME=DeepHire
NEXT_PUBLIC_APP_VERSION=1.0.0
```

---

## 数据备份与恢复

### 备份数据库

```bash
# 备份 PostgreSQL
pg_dump -U deephire -h localhost deephire > backup_$(date +%Y%m%d).sql

# 备份 OpenSearch 索引
curl -X POST "localhost:9200/_snapshot/my_backup/snapshot_$(date +%Y%m%d)?wait_for_completion=true"
```

### 恢复数据库

```bash
# 恢复 PostgreSQL
psql -U deephire -h localhost deephire < backup_20260524.sql

# 重新同步 OpenSearch
cd backend
python sync_opensearch.py
```

---

## 监控与日志

### 查看日志

```bash
# 后端日志
tail -f backend/logs/app.log

# Docker 日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 前端日志
cd frontend
npm run dev 2>&1 | tee logs/frontend.log
```

### 性能监控

```bash
# 检查 PostgreSQL 连接
psql -U deephire -c "SELECT count(*) FROM pg_stat_activity;"

# 检查 Redis 状态
redis-cli INFO stats

# 检查 OpenSearch 健康
curl -X GET "localhost:9200/_cluster/health?pretty"
```

---

## 常见问题

### 1. 数据库连接失败

**问题**: `FATAL: password authentication failed`

**解决**:
```bash
# 检查 PostgreSQL 是否运行
brew services list | grep postgresql

# 重置密码
psql -U postgres
ALTER USER deephire WITH PASSWORD 'deephire';
GRANT ALL ON SCHEMA public TO deephire;
```

### 2. OpenSearch 启动失败

**问题**: `max virtual memory areas vm.max_map_count [65530] is too low`

**解决**:
```bash
# macOS
sudo sysctl -w vm.max_map_count=262144

# Linux
sudo sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

### 3. 前端无法连接后端

**问题**: CORS 错误

**解决**:
```bash
# 检查后端 .env 中的 CORS_ORIGINS
CORS_ORIGINS=http://localhost:3000

# 重启后端服务
```

### 4. 简历解析失败

**问题**: OpenAI API 调用失败

**解决**:
```bash
# 检查 API Key
echo $OPENAI_API_KEY

# 测试 API 连接
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### 5. 搜索功能不工作

**问题**: OpenSearch 索引未创建

**解决**:
```bash
cd backend
python sync_opensearch.py

# 检查索引
curl -X GET "localhost:9200/_cat/indices?v"
```

---

## 性能优化

### 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_candidates_email ON candidates(email);
CREATE INDEX idx_candidates_status ON candidates(status);
CREATE INDEX idx_interviews_date ON interviews(scheduled_at);

-- 分析查询性能
EXPLAIN ANALYZE SELECT * FROM candidates WHERE status = 'new';
```

### OpenSearch 优化

```bash
# 调整分片数量
curl -X PUT "localhost:9200/candidates/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "number_of_replicas": 1
  }
}'

# 刷新索引
curl -X POST "localhost:9200/candidates/_refresh"
```

### 应用优化

```bash
# 使用 Gunicorn 运行后端 (生产环境)
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120

# 前端构建优化
cd frontend
npm run build
npm run start
```

---

## 扩展性建议

### 水平扩展

1. **后端**: 使用负载均衡器 (Nginx/HAProxy) + 多个后端实例
2. **数据库**: PostgreSQL 主从复制
3. **缓存**: Redis Cluster
4. **搜索**: OpenSearch 集群

### 垂直扩展

1. **增加服务器资源**: CPU, RAM, 磁盘
2. **优化数据库连接池**: 调整 SQLAlchemy pool_size
3. **启用缓存**: Redis 缓存热点数据

---

## 安全建议

1. **更改默认密码**: 所有服务的默认密码
2. **使用强密钥**: SECRET_KEY 至少 32 字符
3. **启用 HTTPS**: 生产环境必须使用 SSL
4. **限制 CORS**: 只允许可信域名
5. **定期备份**: 每日自动备份数据库
6. **更新依赖**: 定期更新安全补丁

---

## 技术支持

如遇到问题，请检查：

1. **日志文件**: `backend/logs/` 和 `frontend/.next/`
2. **服务状态**: `docker-compose ps` 或 `brew services list`
3. **网络连接**: 防火墙和端口配置
4. **环境变量**: `.env` 文件配置是否正确

---

**部署完成后，访问 http://localhost:3000 开始使用 DeepHire！**
