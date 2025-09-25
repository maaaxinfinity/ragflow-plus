#!/usr/bin/env python3
"""
修复缺失的用户租户角色数据
"""

import os
import sys

# 添加API路径到系统路径
sys.path.insert(0, '/ragflow')
sys.path.insert(0, '/ragflow/api')

def fix_missing_tenant_roles():
    """修复缺失的用户租户角色数据"""
    try:
        print("=== 修复缺失的用户租户角色数据 ===")

        from api.db.services.user_service import UserService, UserTenantService
        from api.db.services.dialog_service import DialogService
        from api.db.db_models import DB
        from api.utils import get_uuid
        from api.db import UserTenantRole

        print("\n1. 检查现有用户和租户角色:")
        @DB.connection_context()
        def check_current_state():
            users = list(UserService.get_all())
            user_tenants = list(UserTenantService.get_all())
            dialogs = list(DialogService.get_all())
            return users, user_tenants, dialogs

        users, user_tenants, dialogs = check_current_state()
        print(f"  用户总数: {len(users)}")
        print(f"  用户租户关系总数: {len(user_tenants)}")
        print(f"  Dialog总数: {len(dialogs)}")

        # 分析哪些用户缺少租户角色
        users_with_tenants = set()
        for ut in user_tenants:
            users_with_tenants.add(ut.user_id)

        users_without_tenants = []
        for user in users:
            if user.id not in users_with_tenants:
                users_without_tenants.append(user)

        print(f"\n2. 缺少租户角色的用户: {len(users_without_tenants)}")
        for user in users_without_tenants:
            print(f"    - {user.email} (ID: {user.id})")

        if not users_without_tenants:
            print("  ✅ 所有用户都有租户角色")
            return True

        # 检查这些用户是否有Dialog
        print("\n3. 检查无租户角色用户的Dialog:")
        users_with_dialogs = []
        users_without_dialogs = []

        for user in users_without_tenants:
            user_dialogs = []
            for dialog in dialogs:
                if dialog.tenant_id == user.id:
                    user_dialogs.append(dialog)

            if user_dialogs:
                users_with_dialogs.append((user, user_dialogs))
                print(f"    用户 {user.email} 有 {len(user_dialogs)} 个Dialog")
            else:
                users_without_dialogs.append(user)

        print(f"    有Dialog但无租户角色的用户: {len(users_with_dialogs)}")
        print(f"    既无Dialog也无租户角色的用户: {len(users_without_dialogs)}")

        print("\n4. 为用户创建租户角色:")

        @DB.connection_context()
        def create_tenant_roles():
            fixed_count = 0

            # 为所有用户创建owner角色（以自己为租户）
            for user in users_without_tenants:
                try:
                    tenant_role_data = {
                        "id": get_uuid(),
                        "user_id": user.id,
                        "tenant_id": user.id,  # 用户自己就是租户
                        "role": UserTenantRole.OWNER,
                        "invited_by": user.id,
                        "status": "1"
                    }

                    result = UserTenantService.save(**tenant_role_data)
                    if result:
                        print(f"    ✅ 为用户 {user.email} 创建owner角色成功")
                        fixed_count += 1
                    else:
                        print(f"    ❌ 为用户 {user.email} 创建owner角色失败")

                except Exception as e:
                    print(f"    ❌ 为用户 {user.email} 创建租户角色时出错: {e}")

            return fixed_count

        fixed_count = create_tenant_roles()
        print(f"\n5. 修复结果: 成功为 {fixed_count} 个用户创建租户角色")

        print("\n6. 验证修复结果:")
        @DB.connection_context()
        def verify_fix():
            all_users = list(UserService.get_all())
            success_count = 0

            for user in all_users:
                tenants = UserTenantService.query(user_id=user.id)
                dialogs = DialogService.query(tenant_id=user.id, status="1")

                print(f"    用户 {user.email}:")
                print(f"      租户角色数: {len(tenants) if tenants else 0}")
                print(f"      拥有Dialog数: {len(dialogs) if dialogs else 0}")

                if tenants:
                    success_count += 1

            return success_count

        success_count = verify_fix()
        print(f"\n✅ 修复完成: {success_count}/{len(users)} 个用户现在有租户角色")

        # 测试修复后的Dialog列表功能
        print("\n7. 测试修复后的功能:")
        if users:
            test_user = users[0]

            @DB.connection_context()
            def test_dialog_list():
                tenants = UserTenantService.query(user_id=test_user.id)
                all_dialogs = []
                for tenant in tenants:
                    tenant_dialogs = DialogService.query(tenant_id=tenant.tenant_id, status="1")
                    all_dialogs.extend(tenant_dialogs)
                return all_dialogs

            user_dialogs = test_dialog_list()
            print(f"    测试用户 {test_user.email} 现在可以看到 {len(user_dialogs)} 个Dialog")

        return True

    except Exception as e:
        print(f"❌ 修复失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_missing_tenant_roles()
    if success:
        print("\n🎉 用户租户角色数据修复完成！")
        print("现在所有用户都应该能正常访问他们的Dialog了。")
    else:
        print("\n❌ 修复过程中出现问题，需要进一步检查。")