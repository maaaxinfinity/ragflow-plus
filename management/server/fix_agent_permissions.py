#!/usr/bin/env python3
"""
修复agent权限问题的脚本
- 为agent_config表添加user_id和created_by字段
- 更新现有agent记录的权限信息
- 创建权限验证视图
"""

import sys
import os
from pathlib import Path

# 添加RAGFlow API路径到sys.path
ragflow_root = Path(__file__).parent.parent.parent
api_path = ragflow_root / "api"
sys.path.insert(0, str(ragflow_root))
sys.path.insert(0, str(api_path))

try:
    from api.db.db_models import DB
    from playhouse.migrate import MySQLMigrator, migrate
    from peewee import CharField, IntegerField
    print("✅ 成功导入RAGFlow数据库模块")
except ImportError as e:
    print(f"❌ 导入RAGFlow模块失败: {e}")
    sys.exit(1)

def fix_agent_permissions():
    """修复agent权限问题"""
    try:
        print("开始修复agent权限问题...")
        
        # 使用RAGFlow的数据库连接
        with DB.connection_context():
            # 创建迁移器
            migrator = MySQLMigrator(DB)
            
            # 1. 添加user_id字段
            try:
                print("添加user_id字段到agent_config表...")
                migrate(
                    migrator.add_column("agent_config", "user_id", CharField(max_length=32, null=True, index=True))
                )
                print("✅ user_id字段添加成功")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("✅ user_id字段已存在")
                else:
                    print(f"⚠️ 添加user_id字段时出错: {e}")
            
            # 2. 添加created_by字段
            try:
                print("添加created_by字段到agent_config表...")
                migrate(
                    migrator.add_column("agent_config", "created_by", CharField(max_length=32, null=True, index=True))
                )
                print("✅ created_by字段添加成功")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("✅ created_by字段已存在")
                else:
                    print(f"⚠️ 添加created_by字段时出错: {e}")
            
            # 3. 更新现有agent记录的user_id
            try:
                print("更新现有agent记录的user_id...")
                
                # 执行原生SQL查询和更新
                cursor = DB.execute_sql("SELECT COUNT(*) FROM agent_config WHERE user_id IS NULL OR user_id = ''")
                null_count = cursor.fetchone()[0]
                
                if null_count > 0:
                    print(f"发现 {null_count} 条需要更新的agent记录")
                    
                    # 查找第一个用户作为默认创建者
                    try:
                        from api.db.db_models import User
                        first_user = User.select().order_by(User.create_time.asc()).first()
                        if first_user:
                            admin_user_id = first_user.id
                            print(f"使用用户 {admin_user_id} 作为默认创建者")
                            
                            # 更新所有没有user_id的agent记录
                            update_count = DB.execute_sql(
                                "UPDATE agent_config SET user_id = %s, created_by = %s WHERE user_id IS NULL OR user_id = ''",
                                (admin_user_id, admin_user_id)
                            )
                            print(f"✅ 更新了 {null_count} 条agent记录的user_id")
                        else:
                            print("⚠️ 未找到用户，跳过user_id更新")
                    except Exception as e:
                        print(f"⚠️ 查找用户时出错: {e}")
                        print("跳过user_id自动更新，请手动设置")
                else:
                    print("✅ 所有agent记录都已有user_id")
                    
            except Exception as e:
                print(f"⚠️ 更新agent记录时出错: {e}")
            
            # 4. 创建权限验证视图（可选）
            try:
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
                DB.execute_sql(view_sql)
                print("✅ 权限验证视图创建成功")
            except Exception as e:
                print(f"⚠️ 创建视图时出错: {e}")
        
        print("🎉 agent权限问题修复完成！")
        print("\n后续步骤：")
        print("1. 重启RAGFlow服务以应用代码更改")
        print("2. 测试management面板创建的agent是否能正常使用")
        print("3. 验证用户权限控制是否生效")

    except Exception as e:
        print(f"❌ 修复agent权限问题失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e

if __name__ == "__main__":
    fix_agent_permissions()