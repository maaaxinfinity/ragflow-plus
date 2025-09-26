#!/usr/bin/env python3
"""
升级agent_config表的脚本
添加avatar字段
"""

from database import get_db_connection

def upgrade_agent_config_table():
    """升级agent_config表，添加avatar字段"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查avatar字段是否已存在
        cursor.execute("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'agent_config'
            AND COLUMN_NAME = 'avatar'
        """)

        result = cursor.fetchone()
        if result:
            print("✅ avatar字段已存在")
            return

        # 添加avatar字段
        alter_sql = """
        ALTER TABLE agent_config
        ADD COLUMN avatar TEXT AFTER description
        """

        print("添加avatar字段到agent_config表...")
        cursor.execute(alter_sql)
        conn.commit()
        print("✅ avatar字段添加成功")

        # 设置默认头像
        update_sql = """
        UPDATE agent_config
        SET avatar = '/assets/agent/Agent-icon.svg'
        WHERE avatar IS NULL OR avatar = ''
        """

        print("设置默认头像...")
        cursor.execute(update_sql)
        conn.commit()
        print("✅ 默认头像设置完成")

        # 检查is_recommended字段是否已存在
        cursor.execute("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'agent_config'
            AND COLUMN_NAME = 'is_recommended'
        """)

        result = cursor.fetchone()
        if not result:
            print("添加is_recommended字段...")
            # 添加is_recommended字段
            alter_sql = """
            ALTER TABLE agent_config
            ADD COLUMN is_recommended BOOLEAN DEFAULT FALSE AFTER stream
            """
            cursor.execute(alter_sql)

            # 添加索引
            index_sql = "ALTER TABLE agent_config ADD INDEX idx_is_recommended (is_recommended)"
            cursor.execute(index_sql)

            conn.commit()
            print("✅ is_recommended字段添加成功")

            # 检查是否有旧的is_default字段需要迁移
            cursor.execute("""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'agent_config'
                AND COLUMN_NAME = 'is_default'
            """)

            if cursor.fetchone():
                print("迁移is_default数据到is_recommended...")
                # 将is_default的数据迁移到is_recommended
                migrate_sql = "UPDATE agent_config SET is_recommended = is_default WHERE is_default = 1"
                cursor.execute(migrate_sql)
                conn.commit()
                print("✅ 数据迁移完成")
        else:
            print("✅ is_recommended字段已存在")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ 升级agent_config表失败: {str(e)}")
        raise e

if __name__ == "__main__":
    upgrade_agent_config_table()