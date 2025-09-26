-- 数据库迁移脚本：为现有的agent_config表添加权限字段
-- 此脚本用于更新已存在的数据库，添加user_id和created_by字段

USE rag_flow;

-- 检查并添加user_id字段
SET @column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'rag_flow'
    AND TABLE_NAME = 'agent_config'
    AND COLUMN_NAME = 'user_id'
);

SET @sql = IF(@column_exists = 0,
    'ALTER TABLE agent_config ADD COLUMN user_id VARCHAR(32) NULL AFTER team_id',
    'SELECT "user_id column already exists" as message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 检查并添加created_by字段
SET @column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'rag_flow'
    AND TABLE_NAME = 'agent_config'
    AND COLUMN_NAME = 'created_by'
);

SET @sql = IF(@column_exists = 0,
    'ALTER TABLE agent_config ADD COLUMN created_by VARCHAR(32) NULL AFTER user_id',
    'SELECT "created_by column already exists" as message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 检查并添加user_id索引
SET @index_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = 'rag_flow'
    AND TABLE_NAME = 'agent_config'
    AND INDEX_NAME = 'idx_user_id'
);

SET @sql = IF(@index_exists = 0,
    'ALTER TABLE agent_config ADD INDEX idx_user_id (user_id)',
    'SELECT "idx_user_id index already exists" as message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 检查并添加created_by索引
SET @index_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = 'rag_flow'
    AND TABLE_NAME = 'agent_config'
    AND INDEX_NAME = 'idx_created_by'
);

SET @sql = IF(@index_exists = 0,
    'ALTER TABLE agent_config ADD INDEX idx_created_by (created_by)',
    'SELECT "idx_created_by index already exists" as message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 更新现有agent记录的user_id和created_by（使用第一个用户作为默认创建者）
UPDATE agent_config 
SET user_id = (SELECT id FROM user ORDER BY create_time ASC LIMIT 1),
    created_by = (SELECT id FROM user ORDER BY create_time ASC LIMIT 1)
WHERE (user_id IS NULL OR user_id = '') AND EXISTS (SELECT 1 FROM user);

-- 创建权限验证视图
CREATE OR REPLACE VIEW agent_with_permissions AS
SELECT 
    a.*,
    ut.user_id as accessible_user_id,
    ut.role as user_role
FROM agent_config a
LEFT JOIN user_tenant ut ON a.team_id = ut.tenant_id
WHERE a.status = 'active';

SELECT 'Agent权限字段迁移完成' as message;