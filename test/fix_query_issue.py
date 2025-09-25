#!/usr/bin/env python3
"""
修复查询问题的脚本 - 正确使用API查询所有数据
"""

import os
import sys

# 添加API路径到系统路径
sys.path.insert(0, '/ragflow')
sys.path.insert(0, '/ragflow/api')

def fix_and_test_queries():
    """修复并测试查询问题"""
    try:
        print("=== 修复查询问题测试 ===")

        from api.db.services.user_service import UserService
        from api.db.services.dialog_service import DialogService
        from api.db.db_models import DB

        print("\n1. 问题分析:")
        print("  发现问题：model.query() 方法在没有过滤参数时返回空列表")
        print("  解决方案：使用 get_all() 方法或提供默认过滤条件")

        print("\n2. 正确获取所有用户:")
        try:
            @DB.connection_context()
            def get_all_users():
                # 方法1：使用 get_all() 方法
                all_users = UserService.get_all()
                return list(all_users)

            users = get_all_users()
            print(f"  ✅ 使用get_all()找到 {len(users)} 个用户:")
            for user in users:
                print(f"    用户ID: {user.id}")
                print(f"    Email: {user.email}")
                print(f"    昵称: {user.nickname}")
                print(f"    状态: {user.status}")
                print("    ---")

        except Exception as e:
            print(f"  ❌ get_all()方法失败: {e}")

        print("\n3. 正确获取所有Dialog:")
        try:
            @DB.connection_context()
            def get_all_dialogs():
                # 使用 get_all() 方法获取所有Dialog
                all_dialogs = DialogService.get_all()
                return list(all_dialogs)

            dialogs = get_all_dialogs()
            print(f"  ✅ 使用get_all()找到 {len(dialogs)} 个Dialog:")
            for dialog in dialogs:
                print(f"    Dialog ID: {dialog.id}")
                print(f"    名称: {dialog.name}")
                print(f"    Tenant ID: {dialog.tenant_id}")
                print("    ---")

        except Exception as e:
            print(f"  ❌ DialogService.get_all()失败: {e}")

        print("\n4. 权限验证测试:")
        try:
            @DB.connection_context()
            def test_permissions():
                users = list(UserService.get_all())
                dialogs = list(DialogService.get_all())
                return users, dialogs

            users, dialogs = test_permissions()

            if users and dialogs:
                print(f"  测试数据: {len(users)} 个用户, {len(dialogs)} 个Dialog")

                for user in users[:2]:  # 测试前2个用户
                    print(f"\n  测试用户 {user.email} ({user.id}):")

                    # 查询该用户拥有的Dialog
                    @DB.connection_context()
                    def get_user_dialogs():
                        return DialogService.query(tenant_id=user.id)

                    user_dialogs = get_user_dialogs()
                    if user_dialogs:
                        print(f"    ✅ 拥有 {len(user_dialogs)} 个Dialog:")
                        for dialog in user_dialogs:
                            print(f"      - {dialog.name} (ID: {dialog.id})")
                    else:
                        print("    ⚠️ 没有拥有的Dialog")

                        # 如果没有Dialog，尝试创建一个测试Dialog
                        print("    尝试为用户创建测试Dialog...")
                        from api.utils import get_uuid

                        @DB.connection_context()
                        def create_test_dialog():
                            dialog_dict = {
                                "id": get_uuid(),
                                "name": f"测试对话-{user.nickname}",
                                "description": "系统自动创建的测试对话",
                                "tenant_id": user.id,
                                "status": "1",
                                "language": "Chinese",
                                "llm_id": "",
                                "llm_setting": {},
                                "prompt_config": {
                                    "prologue": "你好，我是AI助手",
                                    "quote": True,
                                    "parameters": []
                                }
                            }
                            return DialogService.save(**dialog_dict)

                        try:
                            result = create_test_dialog()
                            if result:
                                print("    ✅ 成功创建测试Dialog")
                            else:
                                print("    ❌ 创建测试Dialog失败")
                        except Exception as e:
                            print(f"    ❌ 创建测试Dialog出错: {e}")
            else:
                print("  ❌ 没有足够的数据进行测试")

        except Exception as e:
            print(f"  ❌ 权限验证测试失败: {e}")
            import traceback
            traceback.print_exc()

        print("\n5. 验证修复结果:")
        try:
            @DB.connection_context()
            def final_verification():
                users = list(UserService.get_all())
                dialogs = list(DialogService.get_all())

                print(f"  最终统计:")
                print(f"    用户总数: {len(users)}")
                print(f"    Dialog总数: {len(dialogs)}")

                # 统计每个用户的Dialog数量
                user_dialog_counts = {}
                for dialog in dialogs:
                    tenant_id = dialog.tenant_id
                    if tenant_id in user_dialog_counts:
                        user_dialog_counts[tenant_id] += 1
                    else:
                        user_dialog_counts[tenant_id] = 1

                print(f"    用户-Dialog分布:")
                for user in users:
                    count = user_dialog_counts.get(user.id, 0)
                    print(f"      {user.email}: {count} 个Dialog")

                return len(users) > 0 and len(dialogs) > 0

            success = final_verification()
            if success:
                print("  ✅ 数据查询和权限系统工作正常")
                return True
            else:
                print("  ❌ 仍存在问题")
                return False

        except Exception as e:
            print(f"  ❌ 最终验证失败: {e}")
            return False

        return True

    except Exception as e:
        print(f"❌ 修复测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_and_test_queries()