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

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ 升级agent_config表失败: {str(e)}")
        raise e

if __name__ == "__main__":
    upgrade_agent_config_table()