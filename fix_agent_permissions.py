#!/usr/bin/env python3
"""
修复Agent权限问题的脚本
解决用户无法访问Agent的权限问题
"""

import sys
import os
sys.path.insert(0, '/ragflow')
sys.path.insert(0, '/ragflow/api')

def fix_agent_permissions():
    """修复Agent权限问题"""
    try:
        from api.db.db_models import DB
        from api.utils import get_uuid
        from api.db import UserTenantRole

        with DB.connection_context():
            print("开始修复Agent权限问题...")

            # 1. 获取所有活跃的agent和对应的team_id
            cursor = DB.execute_sql("""
                SELECT DISTINCT team_id
                FROM agent_config
                WHERE status = 'active' AND team_id != 'ALL'
            """)

            agent_teams = [row[0] for row in cursor.fetchall()]
            print(f"找到 {len(agent_teams)} 个需要处理的团队")

            # 2. 获取所有用户
            user_cursor = DB.execute_sql("SELECT id, email FROM user WHERE status = '1'")
            users = user_cursor.fetchall()
            print(f"找到 {len(users)} 个用户")

            # 3. 为每个用户添加到所有Agent团队的权限
            added_permissions = 0
            for user_id, email in users:
                for team_id in agent_teams:
                    # 检查用户是否已经有该团队的权限
                    check_cursor = DB.execute_sql("""
                        SELECT COUNT(*)
                        FROM user_tenant
                        WHERE user_id = %s AND tenant_id = %s AND status = '1'
                    """, (user_id, team_id))

                    if check_cursor.fetchone()[0] == 0:
                        # 添加用户到团队
                        tenant_role_data = {
                            "id": get_uuid(),
                            "user_id": user_id,
                            "tenant_id": team_id,
                            "role": UserTenantRole.NORMAL,
                            "invited_by": team_id,
                            "status": "1"
                        }

                        DB.execute_sql("""
                            INSERT INTO user_tenant (id, user_id, tenant_id, role, invited_by, status)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            tenant_role_data["id"],
                            tenant_role_data["user_id"],
                            tenant_role_data["tenant_id"],
                            tenant_role_data["role"],
                            tenant_role_data["invited_by"],
                            tenant_role_data["status"]
                        ))

                        added_permissions += 1
                        print(f"✅ 为用户 {email} 添加团队 {team_id} 权限")

            print(f"\n✅ 权限修复完成！总共添加了 {added_permissions} 个权限记录")

            # 4. 验证修复结果
            verification_cursor = DB.execute_sql("""
                SELECT u.email, ut.tenant_id, ut.role
                FROM user u
                JOIN user_tenant ut ON u.id = ut.user_id
                WHERE ut.status = '1'
                ORDER BY u.email, ut.tenant_id
            """)

            print("\n📊 当前用户权限状态：")
            for email, tenant_id, role in verification_cursor.fetchall():
                print(f"  用户: {email} -> 团队: {tenant_id} (角色: {role})")

    except Exception as e:
        print(f"❌ 修复失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_agent_permissions()