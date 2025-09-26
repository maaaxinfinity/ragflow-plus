#!/usr/bin/env python3
"""
添加is_recommended字段到agent_config表的迁移脚本
解决Unknown column 'is_recommended' in 'field list'错误
"""

from database import get_db_connection

def migrate_agent_table():
    """添加is_recommended字段到现有的agent_config表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查is_recommended字段是否已存在
        cursor.execute("DESCRIBE agent_config")
        columns = [row[0] for row in cursor.fetchall()]

        if 'is_recommended' not in columns:
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
        else:
            print("✅ is_recommended字段已存在")

        # 检查是否有旧的is_default字段需要迁移
        if 'is_default' in columns:
            print("迁移is_default数据到is_recommended...")
            # 将is_default的数据迁移到is_recommended
            migrate_sql = "UPDATE agent_config SET is_recommended = is_default WHERE is_default = 1"
            cursor.execute(migrate_sql)

            # 删除旧的is_default字段（可选）
            # cursor.execute("ALTER TABLE agent_config DROP COLUMN is_default")

            conn.commit()
            print("✅ 数据迁移完成")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ 迁移agent_config表失败: {str(e)}")
        raise e

if __name__ == "__main__":
    migrate_agent_table()