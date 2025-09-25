#!/usr/bin/env python3
"""
创建测试数据的脚本
运行方式: docker exec ragflowplus-server python /opt/ragflow/test/create_test_data.py
"""

import os
import sys

# 添加API路径到系统路径
sys.path.insert(0, '/opt/ragflow')
sys.path.insert(0, '/opt/ragflow/api')

def create_test_data():
    """创建测试用户和Dialog数据"""
    try:
        print("=== 创建测试数据 ===")

        from api.db.services.user_service import UserService
        from api.db.services.dialog_service import DialogService
        from api.db.db_models import DB
        from api.utils import get_uuid
        import hashlib

        # 初始化数据库连接
        if not DB.is_connected():
            DB.connect(reuse_if_open=True)

        print("\n1. 检查现有用户:")
        existing_users = UserService.query()
        if existing_users:
            print(f"  已有 {len(existing_users)} 个用户:")
            for user in existing_users:
                print(f"    用户ID: {user.id}, Email: {user.email}")
        else:
            print("  没有现有用户，创建测试用户...")

            # 创建测试用户
            test_email = "test@ragflow.com"
            test_password = "test123456"

            # 创建用户
            user_id = get_uuid()
            password_hash = hashlib.md5(test_password.encode()).hexdigest()

            try:
                user_dict = {
                    "id": user_id,
                    "email": test_email,
                    "nickname": "测试用户",
                    "password": password_hash,
                    "status": "1",
                    "is_superuser": True
                }

                if not UserService.save(**user_dict):
                    print("  ❌ 用户创建失败")
                    return False

                print(f"  ✅ 测试用户创建成功: {test_email} (ID: {user_id})")

            except Exception as e:
                print(f"  ❌ 创建用户时出错: {e}")
                return False

        print("\n2. 检查现有Dialog:")
        existing_dialogs = DialogService.query()
        if existing_dialogs:
            print(f"  已有 {len(existing_dialogs)} 个Dialog:")
            for dialog in existing_dialogs:
                print(f"    Dialog ID: {dialog.id}, 名称: {dialog.name}, Tenant ID: {dialog.tenant_id}")
        else:
            print("  没有现有Dialog，创建测试Dialog...")

            # 获取用户列表（包括刚创建的）
            users = UserService.query()
            if users:
                user = users[0]
                print(f"  使用用户 {user.id} 创建Dialog...")

                # 创建测试Dialog
                dialog_id = get_uuid()
                dialog_dict = {
                    "id": dialog_id,
                    "name": "测试对话",
                    "description": "这是一个测试对话",
                    "tenant_id": user.id,  # 使用用户ID作为tenant_id
                    "status": "1",
                    "language": "Chinese",
                    "llm_id": "",
                    "llm_setting": {},
                    "prompt_config": {
                        "prologue": "你好，我是AI助手",
                        "quote": True,
                        "parameters": []
                    }
                }

                try:
                    if not DialogService.save(**dialog_dict):
                        print("  ❌ Dialog创建失败")
                        return False

                    print(f"  ✅ 测试Dialog创建成功: {dialog_dict['name']} (ID: {dialog_id})")

                except Exception as e:
                    print(f"  ❌ 创建Dialog时出错: {e}")
                    return False
            else:
                print("  ❌ 没有可用的用户来创建Dialog")
                return False

        print("\n3. 验证数据创建结果:")

        # 重新查询验证
        users = UserService.query()
        dialogs = DialogService.query()

        print(f"  用户总数: {len(users)}")
        print(f"  Dialog总数: {len(dialogs)}")

        if users and dialogs:
            print("\n4. 权限验证:")
            user = users[0]
            dialog = dialogs[0]

            # 测试权限查询
            has_permission = DialogService.query(tenant_id=user.id, id=dialog.id)
            if has_permission:
                print(f"  ✅ 用户 {user.id} 对 Dialog {dialog.id} 有权限")
            else:
                print(f"  ❌ 用户 {user.id} 对 Dialog {dialog.id} 无权限")
                print(f"     用户ID: {user.id}")
                print(f"     Dialog的tenant_id: {dialog.tenant_id}")

        return True

    except Exception as e:
        print(f"❌ 创建测试数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 关闭数据库连接
        if DB.is_connected():
            DB.close()

if __name__ == "__main__":
    create_test_data()