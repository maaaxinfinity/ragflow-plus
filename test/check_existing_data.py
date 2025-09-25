#!/usr/bin/env python3
"""
检查现有数据的脚本
运行方式: docker exec ragflowplus-server python /ragflow/test/check_existing_data.py
"""

import os
import sys

# 添加API路径到系统路径
sys.path.insert(0, '/ragflow')
sys.path.insert(0, '/ragflow/api')

def check_existing_data():
    """检查现有的用户和Dialog数据"""
    try:
        print("=== 检查现有数据 ===")

        from api.db.services.user_service import UserService
        from api.db.services.dialog_service import DialogService
        from api.db.services.conversation_service import ConversationService
        from api.db.db_models import DB

        print("\n1. 数据库连接状态:")
        try:
            # 测试数据库连接
            with DB.connection_context():
                print("  数据库连接正常")
        except Exception as e:
            print(f"  数据库连接失败: {e}")
            return False

        # 查看所有用户 - 不使用事务上下文，直接查询
        print("\n2. 用户列表:")
        try:
            users = UserService.query()
            if users:
                print(f"  找到 {len(users)} 个用户:")
                for user in users:
                    print(f"    用户ID: {user.id}")
                    print(f"    Email: {user.email}")
                    print(f"    昵称: {user.nickname}")
                    print(f"    状态: {user.status}")
                    print("    ---")
            else:
                print("  没有找到任何用户")
        except Exception as e:
            print(f"  查询用户失败: {e}")
            import traceback
            traceback.print_exc()

        # 查看所有Dialog
        print("\n3. Dialog列表:")
        try:
            dialogs = DialogService.query()
            if dialogs:
                print(f"  找到 {len(dialogs)} 个Dialog:")
                for dialog in dialogs:
                    print(f"    Dialog ID: {dialog.id}")
                    print(f"    名称: {dialog.name}")
                    print(f"    Tenant ID: {dialog.tenant_id}")
                    print("    ---")
            else:
                print("  没有找到任何Dialog")
        except Exception as e:
            print(f"  查询Dialog失败: {e}")
            import traceback
            traceback.print_exc()

        # 查看会话列表
        print("\n4. 会话列表:")
        try:
            conversations = ConversationService.query()
            if conversations:
                print(f"  找到 {len(conversations)} 个会话:")
                for conv in conversations[:5]:  # 只显示前5个
                    print(f"    会话ID: {conv.id}")
                    print(f"    名称: {conv.name}")
                    print(f"    Dialog ID: {conv.dialog_id}")
                    print("    ---")
            else:
                print("  没有找到任何会话")
        except Exception as e:
            print(f"  查询会话失败: {e}")

        # 权限检查测试
        print("\n5. 权限检查测试:")
        try:
            users = UserService.query()
            dialogs = DialogService.query()

            if users and dialogs:
                print("  测试每个用户对每个Dialog的权限:")
                for user in users:
                    print(f"  用户 {user.email} ({user.id}):")
                    user_dialogs = DialogService.query(tenant_id=user.id)
                    if user_dialogs:
                        print(f"    拥有 {len(user_dialogs)} 个Dialog:")
                        for dialog in user_dialogs:
                            print(f"      - {dialog.name} (ID: {dialog.id})")
                    else:
                        print("    没有拥有的Dialog")
            else:
                print("  没有足够的数据进行权限测试")
        except Exception as e:
            print(f"  权限检查测试失败: {e}")

        return True

    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_existing_data()