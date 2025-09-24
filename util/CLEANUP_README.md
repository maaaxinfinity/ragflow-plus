# RAGFlow 数据清理工具

## 概述

本工具集用于清理RAGFlow系统中的所有文档和文件数据，包括MySQL数据库记录、ElasticSearch索引数据、MinIO存储桶和Redis缓存数据。适用于需要重置系统数据或解决存储异常的情况。

## 文件说明

- `complete_cleanup.py` - 综合清理脚本，整合所有清理操作
- `cleanup_database.sql` - MySQL数据库清理SQL脚本
- `run_cleanup.py` - MySQL数据库清理执行脚本
- `cleanup_elasticsearch.py` - ElasticSearch数据清理脚本
- `cleanup_minio.py` - MinIO存储桶清理脚本
- `cleanup_redis.py` - Redis缓存数据清理脚本
- `check_minio.py` - MinIO连接和存储桶检查脚本
- `config_loader.py` - 统一配置加载模块
- `CLEANUP_README.md` - 本使用说明文档

## 使用前准备

### 1. 安装依赖

```bash
pip install mysql-connector-python elasticsearch minio redis
```

### 2. 确认配置

确保 `docker/.env` 文件存在且包含正确的配置。工具会自动从 `../docker/.env` 加载以下配置:

```env
# MySQL配置
MYSQL_PASSWORD=infiniflow
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_DB=rag_flow

# ElasticSearch配置
ES_HOST=127.0.0.1
ES_PORT=9200
ELASTIC_PASSWORD=infiniflow

# MinIO配置
MINIO_HOST=127.0.0.1
MINIO_PORT=9000
MINIO_USER=minioadmin
MINIO_PASSWORD=minioadmin
```

### 3. 备份数据（重要！）

⚠️ **执行清理前务必备份重要数据**

```bash
# 备份MySQL数据库
mysqldump -u root -p rag_flow > backup_$(date +%Y%m%d_%H%M%S).sql

# 备份ElasticSearch（如需要）
# 使用ElasticSearch快照功能

# 备份MinIO数据（如需要）
# 使用MinIO客户端或控制台导出
```

## 使用方法

### 方法一：综合清理脚本（推荐）

运行主清理脚本，支持交互式和自动化两种模式：

```bash
# 交互式模式
python complete_cleanup.py

# 自动化模式（清理所有数据）
python complete_cleanup.py --auto
```

交互式模式提供以下选项：
1. 仅清理MySQL数据库
2. 仅清理ElasticSearch
3. 仅清理MinIO存储桶
4. 清理数据库和搜索引擎（MySQL + ElasticSearch）
5. 清理所有数据（MySQL + ElasticSearch + MinIO）
6. 退出

### 方法二：单独运行脚本

如果需要单独执行某个清理步骤：

```bash
# 仅清理MySQL数据库
python run_cleanup.py --auto-confirm

# 仅清理ElasticSearch
python cleanup_elasticsearch.py --auto-confirm

# 仅清理MinIO存储桶
python cleanup_minio.py --auto-confirm

# 仅清理Redis缓存
python cleanup_redis.py --auto-confirm

# 检查MinIO连接状态
python check_minio.py
```

## 清理内容详细说明

### MySQL数据库清理

清理以下表的数据：
- `document` - 文档记录
- `file` - 文件记录  
- `file2document` - 文件与文档关联
- `task` - 任务记录
- `conversation` - 对话记录
- `api_4_conversation` - API对话记录
- `chunk` - 文档块数据

同时重置以下表的统计信息：
- `knowledgebase` - 重置文档数量和块数量
- `user_canvas` - 重置对话数量
- `canvas_template` - 重置对话数量

### ElasticSearch清理

- 删除所有以 `ragflow_` 开头的索引
- 清理所有chunk向量数据
- 支持删除文档或删除整个索引两种模式
- 自动确认模式下默认删除文档但保留索引结构

### MinIO清理

- 自动连接到MinIO服务器
- 列出所有存储桶
- 清空每个存储桶中的所有对象
- 删除空的存储桶
- 支持自动确认和交互式两种模式

清理过程：
1. 连接MinIO服务器
2. 获取所有存储桶列表
3. 逐个清空存储桶中的对象
4. 删除空的存储桶
5. 验证清理结果

### Redis清理

`cleanup_redis.py` 脚本会清理以下Redis数据：

- **临时文件缓存** (`temp_file:*`) - 上传的临时文件数据
- **文档处理队列** (`doc_*`, `task_*`) - 文档处理相关的队列数据
- **任务执行器心跳** (`HEARTBEAT:*`) - 任务执行器的心跳信息
- **文件缓存数据** (`file_*`) - 文件内容缓存
- **其他应用缓存** - 系统运行时产生的其他缓存数据

清理前会显示Redis连接信息和数据库统计，清理后会显示清理结果。

## 安全注意事项

⚠️ **重要警告**：

1. **数据不可恢复**: 清理操作会永久删除数据，无法撤销
2. **备份重要数据**: 执行前请确保已备份重要数据
3. **停止服务**: 建议在清理前停止RAGFlow相关服务
4. **测试环境**: 建议先在测试环境中验证清理效果
5. **权限确认**: 确保有足够权限访问数据库、ElasticSearch和MinIO
6. **配置检查**: 工具会自动检查配置文件和服务连接状态
7. **依赖验证**: 执行前会自动检查所需的Python模块

## 执行后验证

清理完成后，建议进行以下验证：

### 1. 数据库验证
```sql
-- 检查主要表的记录数
SELECT 'document' as table_name, COUNT(*) as count FROM document
UNION ALL
SELECT 'file', COUNT(*) FROM file
UNION ALL  
SELECT 'chunk', COUNT(*) FROM chunk;
```

### 2. ElasticSearch验证
```bash
# 检查索引
curl -X GET "localhost:9200/_cat/indices?v"

# 检查文档数量
curl -X GET "localhost:9200/ragflow_*/_count"
```

### 3. MinIO验证
```bash
# 使用检查脚本
python check_minio.py

# 或手动检查
# 访问MinIO控制台: http://localhost:9001
```

### 4. 系统功能验证
- 重启RAGFlow服务
- 尝试上传新文档
- 验证文档处理流程
- 检查搜索功能
- 验证MinIO存储功能

## 故障排除

### 常见问题

1. **连接失败**
   - 检查服务是否运行
   - 验证配置文件中的连接信息
   - 确认网络连接
   - 使用 `python check_minio.py` 检查MinIO连接

2. **权限错误**
   - 检查数据库用户权限
   - 验证ElasticSearch认证信息
   - 确认MinIO访问密钥

3. **配置文件问题**
   - 确保 `../docker/.env` 文件存在
   - 检查配置文件格式
   - 验证所有必需的配置项

4. **部分清理失败**
   - 查看详细错误信息
   - 手动执行失败的步骤
   - 检查数据完整性约束

### 日志查看

脚本会输出详细的执行日志，包括：
- 配置加载状态
- 服务连接状态
- 清理进度
- 错误信息
- 操作结果

## 恢复系统

如果需要恢复系统到清理前状态：

1. **恢复数据库**
   ```bash
   mysql -u root -p rag_flow < backup.sql
   ```

2. **恢复ElasticSearch**
   - 使用ElasticSearch快照功能
   - 重新索引数据

3. **恢复MinIO**
   - 从备份恢复存储桶
   - 重新上传文件
   - 使用MinIO客户端工具恢复

4. **重启服务**
   ```bash
   docker-compose restart
   ```

5. **验证恢复**
   - 检查所有服务状态
   - 验证数据完整性
   - 测试系统功能

## 联系支持

如果在使用过程中遇到问题，请：

1. 查看详细的错误日志
2. 检查配置文件和服务状态
3. 参考故障排除部分
4. 联系技术支持团队

---

**最后提醒**: 数据清理是不可逆操作，请务必在执行前做好充分的备份和测试！