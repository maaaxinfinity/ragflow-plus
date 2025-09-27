# Management Panel API Specification

## 概述
Management后台的模型管理API，支持全局模型配置和统一下发给所有用户。

## API接口规范

### 1. 获取全局模型列表
```
GET /v1/management/llm/list
```

**Response:**
```json
{
  "code": 0,
  "data": [
    {
      "id": 1,
      "fid": "model_id_123",
      "llm_factory": "openai",
      "llm_name": "gpt-4",
      "model_type": "chat",
      "max_tokens": 4096,
      "api_key": "sk-xxx...xxx",
      "api_base": "https://api.openai.com/v1",
      "available": true,
      "status": "active",
      "tags": "LLM,OpenAI",
      "create_date": "2024-01-01",
      "create_time": 1704067200,
      "update_date": "2024-01-01",
      "update_time": 1704067200,
      "total_users": 150,
      "is_global": true
    }
  ],
  "message": "success"
}
```

### 2. 添加全局模型
```
POST /v1/management/llm/add
```

**Request Body:**
```json
{
  "llm_factory": "openai",
  "llm_name": "gpt-4",
  "model_type": "chat",
  "api_key": "sk-xxx...xxx",
  "api_base": "https://api.openai.com/v1",
  "max_tokens": 4096,
  "is_global": true
}
```

**Response:**
```json
{
  "code": 0,
  "message": "模型添加成功"
}
```

### 3. 删除全局模型
```
POST /v1/management/llm/delete
```

**Request Body:**
```json
{
  "llm_factory": "openai",
  "llm_name": "gpt-4"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "模型删除成功"
}
```

### 4. 删除模型工厂
```
POST /v1/management/llm/delete_factory
```

**Request Body:**
```json
{
  "llm_factory": "openai"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "模型工厂删除成功"
}
```

### 5. 获取模型工厂列表
```
GET /v1/llm/factories
```

**Response:**
```json
{
  "code": 0,
  "data": [
    {
      "name": "OpenAI",
      "tags": "LLM,Chat,Embedding",
      "description": "OpenAI GPT models",
      "supported_types": ["chat", "embedding", "image2text"],
      "available": true
    }
  ],
  "message": "success"
}
```

### 6. 获取用户模型使用统计
```
GET /v1/management/llm/usage_stats
```

**Response:**
```json
{
  "code": 0,
  "data": [
    {
      "user_id": "user_123",
      "user_name": "张三",
      "tenant_id": "tenant_456",
      "tenant_name": "科技公司",
      "llm_factory": "openai",
      "llm_name": "gpt-4",
      "used_token": 15000,
      "last_used": "2024-01-01 12:00:00"
    }
  ],
  "message": "success"
}
```

## 全局模型管理特性

### 1. 权限说明
- Management后台创建的模型具有全局权限
- 无需用户级别鉴权，agent和rag已做鉴权
- 统一下发给所有用户使用

### 2. 数据流向
```
Management面板 → 全局模型配置 → 自动下发 → 所有用户可用
```

### 3. 与Web端的区别
- Web端: 用户个人模型配置 (已移除)
- Management: 全局模型管理，统一配置下发

### 4. 兼容性
- 支持所有原有的17+个模型供应商
- 保持原有的字段结构和验证逻辑
- 条件显示逻辑与原始React组件完全一致

## 错误码说明

- `0`: 成功
- `1001`: 参数错误
- `1002`: 模型已存在
- `1003`: 模型不存在
- `1004`: 权限不足
- `1005`: 内部服务错误