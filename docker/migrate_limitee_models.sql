-- 数据迁移脚本：将Limitee用户的模型配置迁移到全局模型表
-- 执行前请确保已经创建了global_llm和user_llm_usage表

-- 1. 查询Limitee用户的租户ID
SET @limitee_tenant_id = (
    SELECT id FROM tenant WHERE name = 'Limitee' LIMIT 1
);

-- 如果找不到Limitee租户，使用第一个租户的ID作为默认值
SET @limitee_tenant_id = IFNULL(@limitee_tenant_id, (
    SELECT id FROM tenant LIMIT 1
));

-- 显示将要迁移的数据
SELECT
    CONCAT('将迁移租户ID: ', @limitee_tenant_id, ' 的模型配置') as migration_info;

-- 2. 迁移TenantLLM中Limitee用户的数据到global_llm表
INSERT IGNORE INTO global_llm (
    fid,
    llm_factory,
    llm_name,
    model_type,
    api_key,
    api_base,
    max_tokens,
    provider_config,
    available,
    status,
    tags,
    description,
    total_usage_count,
    active_users_count,
    created_by,
    create_time,
    create_date,
    update_time,
    update_date
)
SELECT
    CONCAT(llm_factory, '_', llm_name, '_', IFNULL(model_type, 'chat')) as fid,
    llm_factory,
    llm_name,
    IFNULL(model_type, 'chat') as model_type,
    api_key,
    api_base,
    max_tokens,
    NULL as provider_config, -- 初始为空，后续可以通过management面板配置
    TRUE as available,
    'active' as status,
    '' as tags,
    CONCAT('从Limitee用户迁移: ', llm_factory, '/', llm_name) as description,
    used_tokens as total_usage_count,
    1 as active_users_count, -- 至少有Limitee用户在使用
    'migration_script' as created_by,
    UNIX_TIMESTAMP(NOW()) * 1000 as create_time,
    NOW() as create_date,
    UNIX_TIMESTAMP(NOW()) * 1000 as update_time,
    NOW() as update_date
FROM tenant_llm
WHERE tenant_id = @limitee_tenant_id
    AND api_key IS NOT NULL
    AND api_key != ''
    AND llm_name IS NOT NULL
    AND llm_name != '';

-- 3. 为迁移的模型创建用户使用统计记录
INSERT IGNORE INTO user_llm_usage (
    user_id,
    tenant_id,
    global_llm_id,
    llm_factory,
    llm_name,
    model_type,
    usage_count,
    token_usage,
    last_used_time,
    last_used_date,
    first_used_time,
    first_used_date,
    create_time,
    create_date,
    update_time,
    update_date
)
SELECT
    u.id as user_id,
    tl.tenant_id,
    gl.id as global_llm_id,
    tl.llm_factory,
    tl.llm_name,
    IFNULL(tl.model_type, 'chat') as model_type,
    tl.used_tokens as usage_count,
    tl.used_tokens as token_usage,
    UNIX_TIMESTAMP(tl.update_date) * 1000 as last_used_time,
    tl.update_date as last_used_date,
    UNIX_TIMESTAMP(tl.create_date) * 1000 as first_used_time,
    tl.create_date as first_used_date,
    UNIX_TIMESTAMP(NOW()) * 1000 as create_time,
    NOW() as create_date,
    UNIX_TIMESTAMP(NOW()) * 1000 as update_time,
    NOW() as update_date
FROM tenant_llm tl
INNER JOIN global_llm gl ON (
    gl.llm_factory = tl.llm_factory
    AND gl.llm_name = tl.llm_name
    AND gl.model_type = IFNULL(tl.model_type, 'chat')
)
INNER JOIN user u ON u.tenant_id = tl.tenant_id
WHERE tl.tenant_id = @limitee_tenant_id
    AND tl.api_key IS NOT NULL
    AND tl.api_key != ''
    AND tl.llm_name IS NOT NULL
    AND tl.llm_name != '';

-- 4. 更新global_llm表中的活跃用户数统计
UPDATE global_llm gl
SET active_users_count = (
    SELECT COUNT(DISTINCT user_id)
    FROM user_llm_usage ulu
    WHERE ulu.global_llm_id = gl.id
),
update_time = UNIX_TIMESTAMP(NOW()) * 1000,
update_date = NOW();

-- 5. 显示迁移结果
SELECT
    COUNT(*) as migrated_models_count,
    'global_llm表中的迁移模型数量' as description
FROM global_llm
WHERE created_by = 'migration_script';

SELECT
    COUNT(*) as migrated_usage_records,
    '用户使用统计记录数量' as description
FROM user_llm_usage;

SELECT
    llm_factory,
    llm_name,
    model_type,
    active_users_count,
    total_usage_count,
    status
FROM global_llm
WHERE created_by = 'migration_script'
ORDER BY llm_factory, model_type, llm_name;

-- 6. 可选：备份原始数据后删除已迁移的TenantLLM记录
-- 注意：请在确认迁移成功后再执行以下删除操作
/*
-- 创建备份表
CREATE TABLE tenant_llm_backup_limitee AS
SELECT * FROM tenant_llm WHERE tenant_id = @limitee_tenant_id;

-- 删除已迁移的记录
DELETE FROM tenant_llm WHERE tenant_id = @limitee_tenant_id;
*/

-- 验证查询：显示当前数据库中的全局模型
SELECT
    '=== 迁移完成，当前全局模型列表 ===' as info;

SELECT
    id,
    llm_factory,
    llm_name,
    model_type,
    active_users_count,
    total_usage_count,
    available,
    status,
    description
FROM global_llm
ORDER BY llm_factory, model_type, llm_name;