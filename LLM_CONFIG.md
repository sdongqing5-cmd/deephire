# LLM 配置说明

DeepHire 支持两种 LLM 提供商：**OpenAI** 和 **Anthropic**，并支持使用中转 API。

---

## 配置方式

编辑 `backend/.env` 文件，配置以下参数：

### 1. 选择 LLM 提供商

```bash
# 可选值: openai 或 anthropic
LLM_PROVIDER=anthropic
```

### 2. OpenAI 配置

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# OpenAI Base URL (支持中转 API)
OPENAI_BASE_URL=https://api.openai.com/v1

# OpenAI 模型
OPENAI_MODEL=gpt-4o-mini
```

**支持的模型：**
- `gpt-4o` - 最强大
- `gpt-4o-mini` - 性价比高（推荐）
- `gpt-4-turbo`
- `gpt-3.5-turbo`

### 3. Anthropic 配置

```bash
# Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# Anthropic Base URL (支持中转 API)
ANTHROPIC_BASE_URL=https://api.anthropic.com

# Anthropic 模型
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

**支持的模型：**
- `claude-3-5-sonnet-20241022` - 最新最强（推荐）
- `claude-3-5-haiku-20241022` - 速度快
- `claude-3-opus-20240229` - 最强推理能力

---

## 使用中转 API

### OpenAI 中转示例

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your-relay-api-key
OPENAI_BASE_URL=https://your-relay-domain.com/v1
OPENAI_MODEL=gpt-4o-mini
```

### Anthropic 中转示例

```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-26f5b07980c820577a9beb2728ad8c554b6697f8ab9a6141e25caae4291a47e8
ANTHROPIC_BASE_URL=https://realm-token.com
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

---

## 功能说明

### 简历解析

使用配置的 LLM 自动解析上传的简历（PDF/DOCX），提取：
- 姓名、电话、邮箱
- 当前公司和职位
- 工作年限
- 技能标签
- 教育背景
- 个人简介

### 切换 LLM

只需修改 `LLM_PROVIDER` 参数，无需修改代码：

```bash
# 使用 OpenAI
LLM_PROVIDER=openai

# 使用 Anthropic
LLM_PROVIDER=anthropic
```

重启后端服务即可生效。

---

## 架构设计

### 统一接口

所有 LLM 调用通过统一的 `BaseLLMClient` 接口：

```python
from app.services.llm_client import get_llm_client

llm_client = get_llm_client()
response = llm_client.chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0,
    max_tokens=1000
)
```

### 自动适配

- **OpenAI 格式**: 直接使用 OpenAI SDK
- **Anthropic 格式**: 自动转换消息格式（system message 单独处理）

### 工厂模式

使用 `LLMClientFactory` 根据配置自动创建对应的客户端：

```python
class LLMClientFactory:
    @classmethod
    def get_client(cls) -> BaseLLMClient:
        provider = settings.LLM_PROVIDER.lower()
        
        if provider == "openai":
            return OpenAIClient()
        elif provider == "anthropic":
            return AnthropicClient()
```

---

## 成本对比

### OpenAI 定价（2024）

| 模型 | 输入 | 输出 |
|-----|------|------|
| gpt-4o | $2.50/1M tokens | $10.00/1M tokens |
| gpt-4o-mini | $0.15/1M tokens | $0.60/1M tokens |
| gpt-3.5-turbo | $0.50/1M tokens | $1.50/1M tokens |

### Anthropic 定价（2024）

| 模型 | 输入 | 输出 |
|-----|------|------|
| Claude 3.5 Sonnet | $3.00/1M tokens | $15.00/1M tokens |
| Claude 3.5 Haiku | $0.80/1M tokens | $4.00/1M tokens |
| Claude 3 Opus | $15.00/1M tokens | $75.00/1M tokens |

### 推荐配置

**开发环境：**
- OpenAI: `gpt-4o-mini` (性价比最高)
- Anthropic: `claude-3-5-haiku-20241022` (速度快)

**生产环境：**
- OpenAI: `gpt-4o` (质量稳定)
- Anthropic: `claude-3-5-sonnet-20241022` (推理能力强)

---

## 故障排查

### 1. API Key 无效

**错误信息：**
```
ValueError: OpenAI API call failed: Invalid API key
```

**解决方案：**
- 检查 `.env` 文件中的 API Key 是否正确
- 确认 API Key 有足够的额度

### 2. 中转 API 连接失败

**错误信息：**
```
ValueError: Anthropic API call failed: Connection timeout
```

**解决方案：**
- 检查 `BASE_URL` 是否正确
- 确认网络可以访问中转域名
- 检查中转 API 是否正常运行

### 3. 模型不支持

**错误信息：**
```
ValueError: Model not found: gpt-5
```

**解决方案：**
- 使用支持的模型名称
- 检查中转 API 是否支持该模型

### 4. 消息格式错误

**错误信息：**
```
ValueError: Invalid message format
```

**解决方案：**
- 确保消息格式正确：`[{"role": "user", "content": "..."}]`
- Anthropic 会自动处理 system message

---

## 测试配置

### 测试 OpenAI 配置

```bash
cd backend
python -c "
from app.services.llm_client import get_llm_client
from app.core.config import settings

settings.LLM_PROVIDER = 'openai'
client = get_llm_client()
response = client.chat_completion(
    messages=[{'role': 'user', 'content': 'Hello!'}],
    temperature=0
)
print(response)
"
```

### 测试 Anthropic 配置

```bash
cd backend
python -c "
from app.services.llm_client import get_llm_client
from app.core.config import settings

settings.LLM_PROVIDER = 'anthropic'
client = get_llm_client()
response = client.chat_completion(
    messages=[{'role': 'user', 'content': 'Hello!'}],
    temperature=0
)
print(response)
"
```

---

## 扩展支持

如需添加其他 LLM 提供商（如 Google Gemini、Azure OpenAI），只需：

1. 在 `llm_client.py` 中创建新的客户端类
2. 继承 `BaseLLMClient` 接口
3. 实现 `chat_completion` 方法
4. 在 `LLMClientFactory` 中注册

示例：

```python
class GeminiClient(BaseLLMClient):
    def __init__(self):
        # 初始化 Gemini 客户端
        pass
    
    def chat_completion(self, messages, temperature=0, max_tokens=None):
        # 实现 Gemini API 调用
        pass
```

---

## 总结

✅ **支持双 LLM**：OpenAI 和 Anthropic  
✅ **支持中转 API**：自定义 Base URL  
✅ **一键切换**：修改配置即可  
✅ **统一接口**：代码无需修改  
✅ **易于扩展**：可添加更多 LLM  

**当前配置（推荐）：**
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-26f5b07980c820577a9beb2728ad8c554b6697f8ab9a6141e25caae4291a47e8
ANTHROPIC_BASE_URL=https://realm-token.com
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```
