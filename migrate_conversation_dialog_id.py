#!/usr/bin/env python3
"""
数据库迁移脚本：扩展conversation表的dialog_id字段长度
"""

import sys
import os
sys.path.insert(0, '/ragflow')
sys.path.insert(0, '/ragflow/api')

def migrate_conversation_dialog_id():
    """扩展conversation表的dialog_id字段长度从32到64"""
    try:
        from api.db.db_models import DB

        with DB.connection_context():
            print("开始迁移conversation表的dialog_id字段...")

            # 修改字段长度
            cursor = DB.execute_sql("""
                ALTER TABLE conversation
                MODIFY COLUMN dialog_id VARCHAR(64) NOT NULL
            """)

            print("✅ dialog_id字段长度已从32扩展到64")

            # 验证修改
            cursor = DB.execute_sql("""
                DESCRIBE conversation
            """)

            print("\n📊 conversation表结构验证：")
            for row in cursor.fetchall():
                field_name, field_type, null_allowed, key, default, extra = row
                if field_name == 'dialog_id':
                    print(f"  dialog_id: {field_type} (应为 varchar(64))")

            # 检查被截断的记录
            cursor = DB.execute_sql("""
                SELECT id, dialog_id, name
                FROM conversation
                WHERE dialog_id LIKE %s
                AND LENGTH(dialog_id) < %s
            """, ('agent_%', 38))

            truncated_records = cursor.fetchall()
            if truncated_records:
                print(f"\n⚠️  发现 {len(truncated_records)} 条被截断的Agent conversation记录：")
                for record_id, dialog_id, name in truncated_records:
                    print(f"  ID: {record_id}, dialog_id: {dialog_id}, name: {name}")
                print("\n❌ 这些记录需要手动修复或重新创建")
            else:
                print("\n✅ 未发现被截断的记录")

            print("\n🎉 迁移完成！")

    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_conversation_dialog_id()