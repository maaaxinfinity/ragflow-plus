#!/usr/bin/env python3
"""
测试agent dialog API
"""

import os
import sys

# 添加API路径到系统路径
sys.path.insert(0, '/ragflow')
sys.path.insert(0, '/ragflow/api')

def test_agent_dialog_api():
    """测试agent dialog API功能"""
    try:
        print("=== 测试agent dialog API ===")

        # 首先查看现有的agent
        import mysql.connector
        from api import settings

        db_config = settings.DATABASE.copy()
        db_name = db_config.pop("name")
        conn = mysql.connector.connect(**db_config, database=db_name)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, name, team_id, status FROM agent_config WHERE status = 'active' LIMIT 3")
        agents = cursor.fetchall()

        print(f"\n1. 现有活跃的agents: {len(agents)}")
        for agent in agents:
            print(f"   ID: {agent['id']}, 名称: {agent['name']}, 团队: {agent['team_id']}")

        cursor.close()
        conn.close()

        if not agents:
            print("   没有活跃的agent，无法测试")
            return False

        test_agent = agents[0]
        agent_dialog_id = f"agent_{test_agent['id']}"

        print(f"\n2. 测试agent dialog ID: {agent_dialog_id}")

        # 测试get_agent_as_dialog函数
        from api.apps.dialog_app import get_agent_as_dialog

        agent_dialog = get_agent_as_dialog(test_agent['id'])
        if agent_dialog:
            print(f"   ✅ get_agent_as_dialog成功")
            print(f"   Dialog名称: {agent_dialog.name}")
            print(f"   租户ID: {agent_dialog.tenant_id}")
            print(f"   欢迎消息: {agent_dialog.prompt_config.get('prologue', '')}")
        else:
            print(f"   ❌ get_agent_as_dialog失败")
            return False

        # 测试权限检查
        print(f"\n3. 测试权限系统:")
        from api.db.services.user_service import UserService, UserTenantService
        from api.db.db_models import DB

        @DB.connection_context()
        def get_test_user():
            users = list(UserService.get_all())
            return users[0] if users else None

        test_user = get_test_user()
        if not test_user:
            print("   没有测试用户")
            return False

        print(f"   测试用户: {test_user.email} (ID: {test_user.id})")

        # 检查用户租户角色
        @DB.connection_context()
        def check_user_tenants():
            from api.apps.dialog_app import ensure_user_tenant_roles
            tenants = ensure_user_tenant_roles(test_user.id)
            return tenants

        user_tenants = check_user_tenants()
        print(f"   用户租户角色数量: {len(user_tenants)}")
        for tenant in user_tenants:
            print(f"     租户ID: {tenant.tenant_id}, 角色: {tenant.role}")

        # 检查用户是否有权限访问agent
        has_permission = False
        for tenant in user_tenants:
            if tenant.tenant_id == agent_dialog.tenant_id:
                has_permission = True
                break

        print(f"   用户是否有权限访问agent: {'✅' if has_permission else '❌'}")

        # 如果用户没有权限，尝试为用户添加到agent的团队
        if not has_permission:
            print("   尝试为用户添加团队权限...")
            @DB.connection_context()
            def add_team_permission():
                from api.utils import get_uuid
                from api.db import UserTenantRole

                tenant_role_data = {
                    "id": get_uuid(),
                    "user_id": test_user.id,
                    "tenant_id": agent_dialog.tenant_id,
                    "role": UserTenantRole.NORMAL,
                    "invited_by": agent_dialog.tenant_id,
                    "status": "1"
                }
                UserTenantService.save(**tenant_role_data)
                return True

            try:
                add_team_permission()
                print("   ✅ 成功添加团队权限")

                # 重新检查权限
                user_tenants = check_user_tenants()
                has_permission = any(tenant.tenant_id == agent_dialog.tenant_id for tenant in user_tenants)
                print(f"   现在用户有权限: {'✅' if has_permission else '❌'}")
            except Exception as e:
                print(f"   ❌ 添加团队权限失败: {e}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agent_dialog_api()
    if success:
        print("\n🎉 Agent Dialog API基础功能正常")
    else:
        print("\n❌ Agent Dialog API存在问题")