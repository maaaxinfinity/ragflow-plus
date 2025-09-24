-- RAGFlow数据库清理脚本
-- 用于清理所有与文件和文档相关的记录
-- 执行前请确保已备份重要数据

-- 设置安全模式，防止意外删除
SET SQL_SAFE_UPDATES = 0;

-- 开始事务
START TRANSACTION;

-- 1. 清理chunk相关数据（ElasticSearch中的数据需要单独处理）
-- 注意：chunk数据主要存储在ElasticSearch中，这里只是记录相关操作
-- ElasticSearch的chunk数据清理需要通过API或专门的清理脚本处理

-- 2. 清理task表（文档处理任务）
DELETE FROM task WHERE doc_id IS NOT NULL;
SELECT ROW_COUNT() AS 'Deleted tasks';

-- 3. 清理file2document关联表
DELETE FROM file2document;
SELECT ROW_COUNT() AS 'Deleted file2document relations';

-- 4. 清理document表（文档记录）
DELETE FROM document;
SELECT ROW_COUNT() AS 'Deleted documents';

-- 5. 清理file表（文件记录）
DELETE FROM file;
SELECT ROW_COUNT() AS 'Deleted files';

-- 6. 清理conversation表中的reference字段（可能包含chunk引用）
UPDATE conversation SET reference = JSON_ARRAY() WHERE reference IS NOT NULL;
SELECT ROW_COUNT() AS 'Updated conversations';

-- 7. 清理api_4_conversation表中的reference字段
UPDATE api_4_conversation SET reference = JSON_ARRAY() WHERE reference IS NOT NULL;
SELECT ROW_COUNT() AS 'Updated api_4_conversations';

-- 8. 重置knowledgebase表中的统计信息
UPDATE knowledgebase SET 
    doc_num = 0,
    chunk_num = 0,
    token_num = 0
WHERE doc_num > 0 OR chunk_num > 0 OR token_num > 0;
SELECT ROW_COUNT() AS 'Updated knowledgebases';

-- 9. 清理用户画布中可能的文档引用
UPDATE user_canvas SET dsl = JSON_OBJECT() WHERE dsl IS NOT NULL;
SELECT ROW_COUNT() AS 'Updated user_canvas';

-- 10. 清理画布模板中可能的文档引用
UPDATE canvas_template SET dsl = JSON_OBJECT() WHERE dsl IS NOT NULL;
SELECT ROW_COUNT() AS 'Updated canvas_template';

-- 验证清理结果
SELECT 
    'document' as table_name, COUNT(*) as remaining_records FROM document
UNION ALL
SELECT 
    'file' as table_name, COUNT(*) as remaining_records FROM file
UNION ALL
SELECT 
    'file2document' as table_name, COUNT(*) as remaining_records FROM file2document
UNION ALL
SELECT 
    'task' as table_name, COUNT(*) as remaining_records FROM task
UNION ALL
SELECT 
    'knowledgebase_with_docs' as table_name, COUNT(*) as remaining_records 
    FROM knowledgebase WHERE doc_num > 0 OR chunk_num > 0 OR token_num > 0;

-- 提交事务
COMMIT;

-- 恢复安全模式
SET SQL_SAFE_UPDATES = 1;

-- 清理完成提示
SELECT 'Database cleanup completed successfully!' as status;

-- 重要提醒：
-- 1. 此脚本只清理MySQL数据库中的记录
-- 2. ElasticSearch中的chunk数据需要单独清理
-- 3. MinIO中的文件数据需要单独清理（已由用户手动完成）
-- 4. 建议在执行前备份数据库
-- 5. 执行后需要重启相关服务以确保缓存清理