#!/usr/bin/env python3
"""
调试 Dialog 权限问题的脚本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

def debug_dialog_permissions():
    """调试 Dialog 权限问题"""
    try:
        # 导入必要的模块
        from api.db.services.dialog_service import DialogService
        from api.db.services.user_service import UserService

        print("=== 调试 Dialog 权限问题 ===")

        # 查看所有用户
        print("\n1. 用户列表:")
        users = UserService.query()
        for user in users:
            print(f"  用户ID: {user.id}, 用户名: {user.nickname}, Email: {user.email}")

        # 查看所有Dialog
        print("\n2. Dialog列表:")
        dialogs = DialogService.query()
        for dialog in dialogs:
            print(f"  Dialog ID: {dialog.id}, 名称: {dialog.name}, Tenant ID: {dialog.tenant_id}")

        # 检查特定Dialog的权限问题
        print("\n3. 权限检查:")
        if dialogs and users:
            dialog = dialogs[0]
            user = users[0]
            print(f"检查用户 {user.id} 对 Dialog {dialog.id} 的权限...")

            # 模拟权限检查逻辑
            has_permission = DialogService.query(tenant_id=user.id, id=dialog.id)
            if has_permission:
                print("✅ 权限检查通过")
            else:
                print("❌ 权限检查失败")
                print(f"Dialog的tenant_id: {dialog.tenant_id}")
                print(f"用户的ID: {user.id}")

        return True

    except Exception as e:
        print(f"❌ 调试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_dialog_permissions()