#!/usr/bin/env python3
"""
使用正确的API模式测试数据库查询
基于源代码中的正确实现模式
"""

import os
import sys

# 添加API路径到系统路径
sys.path.insert(0, '/ragflow')
sys.path.insert(0, '/ragflow/api')

def test_correct_api_usage():
    """使用源代码中的正确API模式测试"""
    try:
        print("=== 使用正确API模式测试 ===")

        from api.db.services.user_service import UserService
        from api.db.services.dialog_service import DialogService
        from api.db.db_models import DB

        print("\n1. 测试数据库连接:")
        try:
            # 使用装饰器模式 - 这是源代码中的正确模式
            @DB.connection_context()
            def test_connection():
                cursor = DB.execute_sql("SELECT 1 as test")
                result = cursor.fetchone()
                return result[0] == 1

            if test_connection():
                print("  ✅ 数据库连接正常")
            else:
                print("  ❌ 数据库连接测试失败")
                return False
        except Exception as e:
            print(f"  ❌ 数据库连接失败: {e}")
            return False

        print("\n2. 使用正确的UserService.query()模式:")
        try:
            # 这是源代码中的正确查询模式
            @DB.connection_context()
            def query_users():
                return UserService.query()

            users = query_users()
            if users:
                print(f"  ✅ 找到 {len(users)} 个用户:")
                for user in users:
                    print(f"    用户ID: {user.id}")
                    print(f"    Email: {user.email}")
                    print(f"    昵称: {user.nickname}")
                    print(f"    状态: {user.status}")
                    print("    ---")
            else:
                print("  ⚠️ UserService.query() 返回空结果")

                # 尝试直接SQL查询对比
                @DB.connection_context()
                def direct_query():
                    cursor = DB.execute_sql("SELECT id, email, nickname, status FROM user")
                    return cursor.fetchall()

                direct_results = direct_query()
                if direct_results:
                    print(f"  ℹ️ 直接SQL查询找到 {len(direct_results)} 个用户:")
                    for row in direct_results:
                        print(f"    ID: {row[0]}, Email: {row[1]}, 昵称: {row[2]}, 状态: {row[3]}")
                else:
                    print("  ❌ 直接SQL查询也没有结果")

        except Exception as e:
            print(f"  ❌ UserService查询失败: {e}")
            import traceback
            traceback.print_exc()

        print("\n3. 使用正确的DialogService.query()模式:")
        try:
            @DB.connection_context()
            def query_dialogs():
                return DialogService.query()

            dialogs = query_dialogs()
            if dialogs:
                print(f"  ✅ 找到 {len(dialogs)} 个Dialog:")
                for dialog in dialogs:
                    print(f"    Dialog ID: {dialog.id}")
                    print(f"    名称: {dialog.name}")
                    print(f"    Tenant ID: {dialog.tenant_id}")
                    print("    ---")
            else:
                print("  ⚠️ DialogService.query() 返回空结果")
        except Exception as e:
            print(f"  ❌ DialogService查询失败: {e}")

        print("\n4. 测试权限查询模式:")
        try:
            # 先获取用户和Dialog
            @DB.connection_context()
            def get_test_data():
                users = UserService.query()
                dialogs = DialogService.query()
                return users, dialogs

            users, dialogs = get_test_data()

            if users and dialogs:
                user = users[0]
                dialog = dialogs[0]

                # 测试tenant_id权限查询
                @DB.connection_context()
                def test_permission():
                    return DialogService.query(tenant_id=user.id)

                user_dialogs = test_permission()
                print(f"  用户 {user.email} ({user.id}) 拥有的Dialog数量: {len(user_dialogs) if user_dialogs else 0}")

                if user_dialogs:
                    for d in user_dialogs:
                        print(f"    - {d.name} (ID: {d.id}, Tenant: {d.tenant_id})")
            else:
                print("  ⚠️ 没有足够的数据进行权限测试")

        except Exception as e:
            print(f"  ❌ 权限查询测试失败: {e}")

        print("\n5. 检查Service基类实现:")
        try:
            from api.db.services.common_service import CommonService
            print(f"  UserService基类: {UserService.__bases__}")
            print(f"  CommonService位置: {CommonService.__module__}")

            # 检查是否有特殊的查询条件
            print("  检查UserService的过滤条件...")

            @DB.connection_context()
            def debug_user_query():
                # 尝试不同的查询参数
                all_users = UserService.query()
                active_users = UserService.query(status="1")
                return all_users, active_users

            all_users, active_users = debug_user_query()
            print(f"  所有用户: {len(all_users) if all_users else 0}")
            print(f"  活跃用户(status=1): {len(active_users) if active_users else 0}")

        except Exception as e:
            print(f"  ❌ 基类检查失败: {e}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_correct_api_usage()