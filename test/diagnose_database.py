#!/usr/bin/env python3
"""
深度诊断数据库连接问题
"""

import os
import sys

# 添加API路径到系统路径
sys.path.insert(0, '/ragflow')
sys.path.insert(0, '/ragflow/api')

def diagnose_database():
    """深度诊断数据库连接"""
    try:
        print("=== 深度数据库诊断 ===")

        from api.db.db_models import DB
        from api import settings
        import mysql.connector

        print("\n1. 应用配置:")
        print(f"  数据库类型: {getattr(settings, 'DATABASE_TYPE', 'N/A')}")
        print(f"  数据库配置: {getattr(settings, 'DATABASE', {})}")

        print("\n2. 直接MySQL连接测试:")
        try:
            # 直接使用配置连接MySQL
            db_config = settings.DATABASE.copy()
            db_name = db_config.pop("name")

            print(f"  连接参数: host={db_config['host']}, port={db_config['port']}, user={db_config['user']}, database={db_name}")

            # 直接连接MySQL
            conn = mysql.connector.connect(**db_config, database=db_name)
            cursor = conn.cursor()

            # 显示当前数据库
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()[0]
            print(f"  当前数据库: {current_db}")

            # 显示所有表
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"  数据库中的表: {tables}")

            # 检查user表
            if 'user' in tables:
                cursor.execute("SELECT COUNT(*) FROM user")
                user_count = cursor.fetchone()[0]
                print(f"  user表记录数: {user_count}")

                if user_count > 0:
                    cursor.execute("SELECT id, email, nickname FROM user LIMIT 3")
                    users = cursor.fetchall()
                    print("  前3个用户:")
                    for user in users:
                        print(f"    ID: {user[0]}, Email: {user[1]}, 昵称: {user[2]}")
            else:
                print("  ❌ user表不存在！")

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"  直接MySQL连接失败: {e}")
            import traceback
            traceback.print_exc()

        print("\n3. 应用DB对象测试:")
        try:
            print(f"  DB对象类型: {type(DB)}")
            print(f"  DB数据库名: {DB.database}")

            # 通过应用DB对象执行查询
            with DB.connection_context():
                cursor = DB.execute_sql("SELECT DATABASE()")
                current_db = cursor.fetchone()[0]
                print(f"  应用DB连接的数据库: {current_db}")

                cursor = DB.execute_sql("SHOW TABLES")
                tables = [row[0] for row in cursor.fetchall()]
                print(f"  应用DB看到的表: {tables}")

                if 'user' in tables:
                    cursor = DB.execute_sql("SELECT COUNT(*) FROM user")
                    user_count = cursor.fetchone()[0]
                    print(f"  应用DB查询的user表记录数: {user_count}")
                else:
                    print("  ❌ 应用DB看不到user表！")

        except Exception as e:
            print(f"  应用DB测试失败: {e}")
            import traceback
            traceback.print_exc()

        print("\n4. UserService测试:")
        try:
            from api.db.services.user_service import UserService

            # 不使用with语句，直接调用
            users = UserService.query()
            print(f"  UserService.query()返回: {len(users) if users else 0} 个用户")

            if users:
                for i, user in enumerate(users[:3]):
                    print(f"    用户{i+1}: {user.email} (ID: {user.id})")

        except Exception as e:
            print(f"  UserService测试失败: {e}")
            import traceback
            traceback.print_exc()

        return True

    except Exception as e:
        print(f"❌ 诊断失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    diagnose_database()