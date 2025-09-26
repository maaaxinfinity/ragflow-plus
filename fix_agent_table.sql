-- 修复agent权限问题的SQL脚本
-- 为agent_config表添加user_id和created_by字段

-- 1. 添加user_id字段
ALTER TABLE agent_config 
ADD COLUMN user_id VARCHAR(32) NULL AFTER team_id,
ADD INDEX idx_user_id (user_id);

-- 2. 添加created_by字段
ALTER TABLE agent_config 
ADD COLUMN created_by VARCHAR(32) NULL AFTER user_id,
ADD INDEX idx_created_by (created_by);

-- 3. 更新现有agent记录的user_id（使用第一个用户作为默认创建者）
-- 注意：请根据实际情况修改用户ID
UPDATE agent_config 
SET user_id = (SELECT id FROM user ORDER BY create_time ASC LIMIT 1),
    created_by = (SELECT id FROM user ORDER BY create_time ASC LIMIT 1)
WHERE user_id IS NULL OR user_id = '';

-- 4. 创建权限验证视图
CREATE OR REPLACE VIEW agent_with_permissions AS
SELECT 
    a.*,
    ut.user_id as accessible_user_id,
    ut.role as user_role
FROM agent_config a
LEFT JOIN user_tenant ut ON a.team_id = ut.tenant_id
WHERE a.status = 'active';

-- 查看修改结果
SELECT 'agent_config表结构:' as info;
DESCRIBE agent_config;

SELECT 'agent记录统计:' as info;
SELECT 
    COUNT(*) as total_agents,
    COUNT(user_id) as agents_with_user_id,
    COUNT(*) - COUNT(user_id) as agents_without_user_id
FROM agent_config;