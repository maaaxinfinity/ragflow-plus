#!/usr/bin/env python3
"""
手动创建agent_config表的脚本
用于解决数据库表不存在的问题
"""

from database import get_db_connection

def create_agent_config_table():
    """创建agent_config表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 创建agent_config表的SQL - 与RAGFlow Dialog模型保持一致
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS agent_config (
            id VARCHAR(32) PRIMARY KEY,
            name VARCHAR(255) NOT NULL COMMENT 'agent name',
            team_id VARCHAR(32) NOT NULL COMMENT 'tenant_id in RAGFlow',
            user_id VARCHAR(255) NULL COMMENT 'user_id',
            created_by VARCHAR(255) NULL COMMENT 'created by user',
            description TEXT NULL COMMENT 'agent description',
            icon TEXT NULL COMMENT 'icon base64 string (corresponds to avatar)',
            language VARCHAR(32) DEFAULT 'Chinese' COMMENT 'Chinese|English',
            llm_id VARCHAR(128) NOT NULL COMMENT 'default llm ID (corresponds to model_name)',
            llm_setting JSON NULL COMMENT 'llm settings object',
            prompt_type VARCHAR(16) DEFAULT 'simple' COMMENT 'simple|advanced',
            prompt_config JSON NULL COMMENT 'prompt configuration object',
            similarity_threshold FLOAT DEFAULT 0.2,
            vector_similarity_weight FLOAT DEFAULT 0.3,
            top_n INT DEFAULT 6,
            top_k INT DEFAULT 1024,
            do_refer VARCHAR(1) DEFAULT '1' COMMENT 'reference insertion flag',
            rerank_id VARCHAR(128) NULL COMMENT 'rerank model ID',
            kb_ids JSON NULL COMMENT 'knowledge base IDs',
            is_recommended BOOLEAN DEFAULT FALSE COMMENT 'recommended agent flag (extension beyond RAGFlow)',
            status VARCHAR(1) DEFAULT '1' COMMENT '1:valid, 0:invalid',
            create_time BIGINT NULL,
            create_date DATETIME NULL,
            update_time BIGINT NULL,
            update_date DATETIME NULL,
            INDEX idx_team_id (team_id),
            INDEX idx_name (name),
            INDEX idx_status (status),
            INDEX idx_is_recommended (is_recommended)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        print("创建agent_config表...")
        cursor.execute(create_table_sql)
        conn.commit()
        print("✅ agent_config表创建成功")

        # 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'agent_config'")
        result = cursor.fetchone()
        if result:
            print("✅ 表已存在于数据库中")
        else:
            print("❌ 表创建失败")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ 创建agent_config表失败: {str(e)}")
        raise e

if __name__ == "__main__":
    create_agent_config_table()