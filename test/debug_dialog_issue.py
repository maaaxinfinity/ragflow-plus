#!/usr/bin/env python3
"""
调试 Dialog 权限问题的脚本
运行方式: docker exec ragflowplus-server python /opt/ragflow/test/debug_dialog_issue.py
"""

import os
import sys

# 添加API路径到系统路径
sys.path.insert(0, '/opt/ragflow')
sys.path.insert(0, '/opt/ragflow/api')

def debug_dialog_permissions():
    """调试 Dialog 权限问题"""
    try:
        print("=== 调试 Dialog 权限问题 ===")

        # 设置数据库连接
        from api.db.services.user_service import UserService
        from api.db.services.dialog_service import DialogService
        from api.db.services.conversation_service import ConversationService
        from api.db.db_models import DB

        # 初始化数据库连接
        if not DB.is_connected():
            DB.connect(reuse_if_open=True)

        print("\n1. 数据库连接状态:")
        print(f"  数据库已连接: {DB.is_connected()}")

        # 查看所有用户
        print("\n2. 用户列表:")
        try:
            users = UserService.query()
            if users:
                for user in users:
                    print(f"  用户ID: {user.id}, 用户名: {user.nickname or user.email}, Email: {user.email}")
            else:
                print("  没有找到任何用户")
        except Exception as e:
            print(f"  查询用户失败: {e}")

        # 查看所有租户（暂时跳过，专注于用户和Dialog）
        print("\n3. 租户列表: (跳过，专注于核心问题)")

        # 查看所有Dialog
        print("\n4. Dialog列表:")
        try:
            dialogs = DialogService.query()
            if dialogs:
                for dialog in dialogs:
                    print(f"  Dialog ID: {dialog.id}, 名称: {dialog.name}, Tenant ID: {dialog.tenant_id}")
            else:
                print("  没有找到任何Dialog")
        except Exception as e:
            print(f"  查询Dialog失败: {e}")

        # 查看会话列表
        print("\n5. 会话列表:")
        try:
            conversations = ConversationService.query()
            if conversations:
                for conv in conversations:
                    print(f"  会话ID: {conv.id}, 名称: {conv.name}, Dialog ID: {conv.dialog_id}")
            else:
                print("  没有找到任何会话")
        except Exception as e:
            print(f"  查询会话失败: {e}")

        # 权限检查测试
        print("\n6. 权限检查测试:")
        if users and dialogs:
            user = users[0]
            dialog = dialogs[0]
            print(f"  测试用户 {user.id} 对 Dialog {dialog.id} 的权限...")

            # 模拟权限检查逻辑
            has_permission = DialogService.query(tenant_id=user.id, id=dialog.id)
            if has_permission:
                print("  ✅ 权限检查通过")
            else:
                print("  ❌ 权限检查失败")
                print(f"  Dialog的tenant_id: {dialog.tenant_id}")
                print(f"  用户的ID: {user.id}")

                # 尝试查找正确的对应关系
                print("  \n  查找用户和Dialog的正确对应关系:")
                for u in users:
                    user_dialogs = DialogService.query(tenant_id=u.id)
                    if user_dialogs:
                        print(f"    用户 {u.id} ({u.nickname or u.email}) 拥有 {len(user_dialogs)} 个Dialog")
                        for d in user_dialogs:
                            print(f"      - Dialog {d.id}: {d.name}")

        return True

    except Exception as e:
        print(f"❌ 调试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 关闭数据库连接
        if DB.is_connected():
            DB.close()

if __name__ == "__main__":
    debug_dialog_permissions()