#!/usr/bin/env python3
"""
修复Agent团队模型权限问题
为Agent所属团队添加必要的模型权限
"""

import sys
import os
import time
sys.path.insert(0, '/ragflow')
sys.path.insert(0, '/ragflow/api')

def fix_agent_model_permissions():
    """为Agent团队添加deepseek-chat模型权限"""
    try:
        from api.db.db_models import DB

        # Agent团队ID和用户ID
        agent_team_id = '4e4f2d5c97ae11f0a426624cd6fd4012'
        main_user_id = '9936c08cf36211efb1090242ac160006'

        with DB.connection_context():
            print("开始修复Agent团队模型权限...")

            # 1. 检查当前Agent团队的模型权限
            cursor = DB.execute_sql("""
                SELECT tenant_id, llm_factory, llm_name, model_type, api_key, api_base, max_tokens
                FROM tenant_llm
                WHERE tenant_id = %s
            """, (agent_team_id,))

            current_permissions = cursor.fetchall()
            print(f"\n📊 Agent团队 {agent_team_id} 当前模型权限:")
            if current_permissions:
                for perm in current_permissions:
                    tenant_id, factory, name, model_type, api_key, api_base, max_tokens = perm
                    print(f"  {name} ({factory}) - {model_type}")
            else:
                print("  ❌ 无任何模型权限")

            # 2. 获取主用户的deepseek-chat配置
            cursor = DB.execute_sql("""
                SELECT llm_factory, model_type, api_key, api_base, max_tokens, used_tokens
                FROM tenant_llm
                WHERE tenant_id = %s AND llm_name = %s
            """, (main_user_id, 'deepseek-chat'))

            main_user_config = cursor.fetchone()
            if not main_user_config:
                print(f"❌ 主用户 {main_user_id} 没有deepseek-chat配置")
                return

            factory, model_type, api_key, api_base, max_tokens, used_tokens = main_user_config
            print(f"\n✅ 找到主用户的deepseek-chat配置:")
            print(f"  Factory: {factory}")
            print(f"  Model Type: {model_type}")
            print(f"  Max Tokens: {max_tokens}")

            # 3. 检查Agent团队是否已有deepseek-chat权限
            cursor = DB.execute_sql("""
                SELECT COUNT(*)
                FROM tenant_llm
                WHERE tenant_id = %s AND llm_name = %s
            """, (agent_team_id, 'deepseek-chat'))

            exists = cursor.fetchone()[0] > 0
            if exists:
                print(f"✅ Agent团队已有deepseek-chat权限，无需添加")
                return

            # 4. 为Agent团队添加deepseek-chat权限
            current_time = int(time.time() * 1000)
            current_datetime = time.strftime('%Y-%m-%d %H:%M:%S')

            DB.execute_sql("""
                INSERT INTO tenant_llm (
                    create_time, create_date, update_time, update_date,
                    tenant_id, llm_factory, model_type, llm_name,
                    api_key, api_base, max_tokens, used_tokens
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                current_time, current_datetime, current_time, current_datetime,
                agent_team_id, factory, model_type, 'deepseek-chat',
                api_key, api_base, max_tokens, 0  # used_tokens设为0
            ))

            print(f"\n✅ 成功为Agent团队 {agent_team_id} 添加deepseek-chat权限")

            # 5. 验证添加结果
            cursor = DB.execute_sql("""
                SELECT llm_factory, model_type, max_tokens
                FROM tenant_llm
                WHERE tenant_id = %s AND llm_name = %s
            """, (agent_team_id, 'deepseek-chat'))

            new_config = cursor.fetchone()
            if new_config:
                factory, model_type, max_tokens = new_config
                print(f"✅ 验证成功: {factory} - {model_type} - {max_tokens} tokens")
            else:
                print("❌ 验证失败: 权限添加不成功")

            print("\n🎉 模型权限修复完成！")

    except Exception as e:
        print(f"❌ 修复失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_agent_model_permissions()