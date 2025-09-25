CREATE DATABASE IF NOT EXISTS rag_flow;
USE rag_flow;

-- 创建agent_config表用于存储管理系统的Agent配置
CREATE TABLE IF NOT EXISTS agent_config (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    team_id VARCHAR(36) NOT NULL,
    description TEXT,
    model_name VARCHAR(255),
    kb_ids JSON,
    system_prompt TEXT,
    welcome_message TEXT,
    language VARCHAR(10) DEFAULT 'zh-CN',
    empty_response TEXT,
    similarity_threshold DECIMAL(3,2) DEFAULT 0.2,
    vector_similarity_weight DECIMAL(3,2) DEFAULT 0.3,
    vector_keywords_weight DECIMAL(3,2) DEFAULT 0.7,
    top_n INT DEFAULT 8,
    rerank_enabled BOOLEAN DEFAULT FALSE,
    rerank_model VARCHAR(255),
    temperature DECIMAL(3,2) DEFAULT 0.1,
    max_tokens INT DEFAULT 512,
    top_p DECIMAL(3,2) DEFAULT 0.3,
    frequency_penalty DECIMAL(3,2) DEFAULT 0.7,
    presence_penalty DECIMAL(3,2) DEFAULT 0.4,
    stream BOOLEAN DEFAULT FALSE,
    is_default BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'active',
    create_time BIGINT,
    create_date DATETIME,
    update_time BIGINT,
    update_date DATETIME,
    INDEX idx_team_id (team_id),
    INDEX idx_name (name),
    INDEX idx_status (status),
    INDEX idx_is_default (is_default)
);