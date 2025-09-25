#!/usr/bin/env python3
"""
调试权限验证逻辑
"""

import os
import sys

# 添加API路径到系统路径
sys.path.insert(0, '/ragflow')
sys.path.insert(0, '/ragflow/api')

def debug_permission_logic():
    """调试权限验证逻辑"""
    try:
        print("=== 调试权限验证逻辑 ===")

        from api.db.services.user_service import UserService
        from api.db.services.dialog_service import DialogService
        from api.db.services.user_service import UserTenantService
        from api.db.db_models import DB

        print("\n1. 获取用户和Dialog数据:")
        @DB.connection_context()
        def get_test_data():
            users = list(UserService.get_all())
            dialogs = list(DialogService.get_all())
            return users, dialogs

        users, dialogs = get_test_data()
        print(f"  用户数量: {len(users)}")
        print(f"  Dialog数量: {len(dialogs)}")

        if not users or not dialogs:
            print("  ❌ 没有足够的测试数据")
            return False

        # 选择一个有Dialog的用户进行测试
        test_user = None
        test_dialog = None

        for dialog in dialogs:
            for user in users:
                if user.id == dialog.tenant_id:
                    test_user = user
                    test_dialog = dialog
                    break
            if test_user:
                break

        if not test_user or not test_dialog:
            print("  ❌ 找不到有权限的用户-Dialog匹配")
            return False

        print(f"\n2. 测试用户: {test_user.email} (ID: {test_user.id})")
        print(f"   测试Dialog: {test_dialog.name} (ID: {test_dialog.id}, tenant_id: {test_dialog.tenant_id})")

        print("\n3. 测试DialogService.query权限检查:")

        @DB.connection_context()
        def test_dialog_query():
            # 测试正确的权限查询
            result1 = DialogService.query(tenant_id=test_user.id, id=test_dialog.id)
            result2 = DialogService.query(tenant_id=test_user.id)
            result3 = DialogService.query(id=test_dialog.id)
            return result1, result2, result3

        result1, result2, result3 = test_dialog_query()

        print(f"  DialogService.query(tenant_id={test_user.id}, id={test_dialog.id}): {len(result1) if result1 else 0} 个结果")
        print(f"  DialogService.query(tenant_id={test_user.id}): {len(result2) if result2 else 0} 个结果")
        print(f"  DialogService.query(id={test_dialog.id}): {len(result3) if result3 else 0} 个结果")

        print("\n4. 测试UserTenantService权限逻辑:")

        @DB.connection_context()
        def test_user_tenant():
            # 模拟dialog_app.py中的权限检查逻辑
            tenants = UserTenantService.query(user_id=test_user.id)
            return tenants

        try:
            tenants = test_user_tenant()
            print(f"  UserTenantService.query(user_id={test_user.id}): {len(tenants) if tenants else 0} 个结果")

            if tenants:
                print("  租户信息:")
                for tenant in tenants:
                    print(f"    Tenant ID: {tenant.tenant_id}, Role: {tenant.role}")

                    # 测试这个tenant_id是否能找到Dialog
                    @DB.connection_context()
                    def test_tenant_dialog():
                        return DialogService.query(tenant_id=tenant.tenant_id, id=test_dialog.id)

                    tenant_dialogs = test_tenant_dialog()
                    print(f"    用此tenant_id查询Dialog: {len(tenant_dialogs) if tenant_dialogs else 0} 个结果")
            else:
                print("  ⚠️ UserTenantService没有返回任何租户信息")
                print("  这可能是权限问题的根源！")

                # 检查user表中是否有直接的tenant关系
                print("\n  检查用户是否应该作为自己的tenant:")
                @DB.connection_context()
                def check_user_as_tenant():
                    # 尝试用用户ID作为tenant_id查询
                    user_as_tenant = DialogService.query(tenant_id=test_user.id)
                    return user_as_tenant

                user_dialogs = check_user_as_tenant()
                print(f"  用用户ID作为tenant_id查询: {len(user_dialogs) if user_dialogs else 0} 个Dialog")

        except Exception as e:
            print(f"  ❌ UserTenantService测试失败: {e}")
            import traceback
            traceback.print_exc()

        print("\n5. 测试不同Dialog的权限:")
        for i, dialog in enumerate(dialogs[:3]):  # 测试前3个Dialog
            print(f"\n  Dialog {i+1}: {dialog.name} (tenant_id: {dialog.tenant_id})")

            # 找到拥有这个Dialog的用户
            owner_user = None
            for user in users:
                if user.id == dialog.tenant_id:
                    owner_user = user
                    break

            if owner_user:
                print(f"    拥有者: {owner_user.email} ({owner_user.id})")

                @DB.connection_context()
                def test_owner_access():
                    return DialogService.query(tenant_id=owner_user.id, id=dialog.id)

                owner_access = test_owner_access()
                print(f"    拥有者权限查询: {len(owner_access) if owner_access else 0} 个结果")
            else:
                print(f"    ⚠️ 找不到拥有者 (tenant_id: {dialog.tenant_id})")

        return True

    except Exception as e:
        print(f"❌ 调试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_permission_logic()