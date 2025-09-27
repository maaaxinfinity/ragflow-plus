-- 创建全局模型管理表
-- Management后台创建的模型，具有全局权限，自动对所有用户生效

CREATE TABLE IF NOT EXISTS global_llm (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fid VARCHAR(128) NOT NULL COMMENT '模型唯一标识符',
    llm_factory VARCHAR(128) NOT NULL COMMENT 'LLM factory name',
    llm_name VARCHAR(128) NOT NULL COMMENT 'LLM model name',
    model_type VARCHAR(128) NOT NULL COMMENT 'chat, embedding, image2text, tts, asr, rerank',
    api_key VARCHAR(1024) NOT NULL COMMENT 'API密钥',
    api_base VARCHAR(255) NULL COMMENT 'API基础地址',
    max_tokens INT DEFAULT 4096 COMMENT '最大令牌数',

    -- 供应商特定字段 (JSON格式存储)
    provider_config JSON NULL COMMENT '供应商特定配置字段',

    -- 状态和元数据
    available BOOLEAN DEFAULT TRUE COMMENT '是否可用',
    status VARCHAR(32) DEFAULT 'active' COMMENT '状态',
    tags VARCHAR(255) NULL COMMENT '标签',
    description TEXT NULL COMMENT '描述',

    -- 使用统计
    total_usage_count BIGINT DEFAULT 0 COMMENT '总使用次数',
    active_users_count INT DEFAULT 0 COMMENT '活跃用户数',
    last_used_time BIGINT NULL COMMENT '最后使用时间戳',

    -- 审计字段
    created_by VARCHAR(128) NULL COMMENT '创建者',
    create_time BIGINT NULL COMMENT '创建时间戳',
    create_date DATETIME NULL COMMENT '创建日期',
    update_time BIGINT NULL COMMENT '更新时间戳',
    update_date DATETIME NULL COMMENT '更新日期',

    -- 索引
    INDEX idx_llm_factory (llm_factory),
    INDEX idx_model_type (model_type),
    INDEX idx_status (status),
    INDEX idx_available (available),
    INDEX idx_create_time (create_time),
    UNIQUE KEY uk_factory_name_type (llm_factory, llm_name, model_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='全局模型配置表';

-- 创建用户模型使用统计表
CREATE TABLE IF NOT EXISTS user_llm_usage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(32) NOT NULL COMMENT '用户ID',
    tenant_id VARCHAR(32) NOT NULL COMMENT '租户ID',
    global_llm_id INT NOT NULL COMMENT '全局模型ID',
    llm_factory VARCHAR(128) NOT NULL COMMENT '模型工厂',
    llm_name VARCHAR(128) NOT NULL COMMENT '模型名称',
    model_type VARCHAR(128) NOT NULL COMMENT '模型类型',

    -- 使用统计
    usage_count BIGINT DEFAULT 0 COMMENT '使用次数',
    token_usage BIGINT DEFAULT 0 COMMENT '令牌使用量',
    last_used_time BIGINT NULL COMMENT '最后使用时间',
    last_used_date DATETIME NULL COMMENT '最后使用日期',
    first_used_time BIGINT NULL COMMENT '首次使用时间',
    first_used_date DATETIME NULL COMMENT '首次使用日期',

    -- 审计字段
    create_time BIGINT NULL,
    create_date DATETIME NULL,
    update_time BIGINT NULL,
    update_date DATETIME NULL,

    -- 索引
    INDEX idx_user_id (user_id),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_global_llm_id (global_llm_id),
    INDEX idx_llm_factory (llm_factory),
    INDEX idx_last_used (last_used_time),
    UNIQUE KEY uk_user_model (user_id, global_llm_id),

    -- 外键约束
    FOREIGN KEY fk_global_llm (global_llm_id) REFERENCES global_llm(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户模型使用统计表';