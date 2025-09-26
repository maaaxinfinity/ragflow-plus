#!/usr/bin/env python3
"""
修复agent权限问题的数据库迁移脚本
1. 为agent_config表添加user_id字段
2. 修复现有数据的权限关联
"""

from database import get_db_connection
import sys
import os

def fix_agent_permissions():
    """修复agent权限问题"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        print("开始修复agent权限问题...")

        # 1. 检查user_id字段是否已存在
        cursor.execute("DESCRIBE agent_config")
        columns = [row[0] for row in cursor.fetchall()]

        if 'user_id' not in columns:
            print("添加user_id字段到agent_config表...")
            # 添加user_id字段
            alter_sql = """
            ALTER TABLE agent_config
            ADD COLUMN user_id VARCHAR(32) NULL AFTER team_id,
            ADD INDEX idx_user_id (user_id)
            """
            cursor.execute(alter_sql)
            conn.commit()
            print("✅ user_id字段添加成功")
        else:
            print("✅ user_id字段已存在")

        # 2. 添加created_by字段（如果不存在）
        if 'created_by' not in columns:
            print("添加created_by字段到agent_config表...")
            alter_sql = """
            ALTER TABLE agent_config
            ADD COLUMN created_by VARCHAR(32) NULL AFTER user_id,
            ADD INDEX idx_created_by (created_by)
            """
            cursor.execute(alter_sql)
            conn.commit()
            print("✅ created_by字段添加成功")

        # 3. 为现有的agent记录设置默认的user_id
        # 这里需要根据实际业务逻辑来设置，暂时设置为管理员用户
        print("更新现有agent记录的user_id...")
        
        # 查找系统管理员用户（假设是第一个创建的用户或超级用户）
        try:
            # 尝试导入RAGFlow的用户模块
            ragflow_path = '/ragflow'
            if ragflow_path not in sys.path:
                sys.path.insert(0, ragflow_path)
            if os.path.join(ragflow_path, 'api') not in sys.path:
                sys.path.insert(0, os.path.join(ragflow_path, 'api'))

            from api.db.db_models import DB, User
            
            with DB.connection_context():
                # 查找超级用户或第一个用户
                admin_user = User.select().where(
                    (User.is_superuser == True) | (User.status == '1')
                ).order_by(User.create_time.asc()).first()
                
                if admin_user:
                    admin_user_id = admin_user.id
                    print(f"找到管理员用户: {admin_user_id}")
                    
                    # 更新所有没有user_id的agent记录
                    update_sql = """
                    UPDATE agent_config 
                    SET user_id = %s, created_by = %s 
                    WHERE user_id IS NULL OR user_id = ''
                    """
                    cursor.execute(update_sql, (admin_user_id, admin_user_id))
                    conn.commit()
                    
                    updated_count = cursor.rowcount
                    print(f"✅ 更新了 {updated_count} 条agent记录的user_id")
                else:
                    print("⚠️ 未找到管理员用户，跳过user_id更新")
                    
        except ImportError as e:
            print(f"⚠️ 无法导入RAGFlow模块: {e}")
            print("跳过user_id自动更新，请手动设置")

        # 4. 创建权限验证视图（可选）
        print("创建agent权限验证视图...")
        view_sql = """
        CREATE OR REPLACE VIEW agent_with_permissions AS
        SELECT 
            a.*,
            ut.user_id as accessible_user_id,
            ut.role as user_role
        FROM agent_config a
        LEFT JOIN user_tenant ut ON a.team_id = ut.tenant_id
        WHERE a.status = 'active'
        """
        cursor.execute(view_sql)
        conn.commit()
        print("✅ 权限验证视图创建成功")

        cursor.close()
        conn.close()
        
        print("🎉 agent权限问题修复完成！")
        print("\n后续步骤：")
        print("1. 更新agent创建逻辑，确保设置正确的user_id")
        print("2. 更新权限验证逻辑，检查用户是否有访问agent的权限")
        print("3. 测试management面板创建的agent是否能正常使用")

    except Exception as e:
        print(f"❌ 修复agent权限问题失败: {str(e)}")
        raise e

if __name__ == "__main__":
    fix_agent_permissions()