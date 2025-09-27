#!/usr/bin/env python3

"""
数据库迁移脚本：为conversation表添加is_bookmarked字段
运行方式：python migrate_conversation_bookmark.py
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.db.db_models import DB, Conversation
from peewee import BooleanField


def migrate_conversation_bookmark():
    """为conversation表添加is_bookmarked字段"""
    try:
        with DB.connection_context():
            # 检查字段是否已存在 (MySQL语法)
            cursor = DB.execute_sql("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'conversation'
                AND COLUMN_NAME = 'is_bookmarked'
            """)
            column_exists = cursor.fetchone()[0] > 0

            if not column_exists:
                print("添加is_bookmarked字段到conversation表...")

                # 添加新字段 (MySQL语法)
                DB.execute_sql(
                    "ALTER TABLE conversation ADD COLUMN is_bookmarked BOOLEAN DEFAULT FALSE"
                )

                print("✓ 成功添加is_bookmarked字段")
                print("✓ 字段默认值：FALSE")

                # 创建索引
                try:
                    DB.execute_sql(
                        "CREATE INDEX idx_conversation_is_bookmarked ON conversation(is_bookmarked)"
                    )
                    print("✓ 创建索引：idx_conversation_is_bookmarked")
                except Exception as e:
                    print(f"索引创建失败（可能已存在）: {e}")

                print("✓ 数据库迁移完成")
            else:
                print("✓ is_bookmarked字段已存在，跳过迁移")

    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        raise


if __name__ == "__main__":
    migrate_conversation_bookmark()