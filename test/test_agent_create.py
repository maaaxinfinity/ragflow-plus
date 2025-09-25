#!/usr/bin/env python3
"""
测试Agent创建功能的脚本
"""

import sys
import os

# 添加路径，以便导入management的模块
sys.path.append(os.path.join(os.path.dirname(__file__), 'management', 'server'))

def test_agent_creation():
    """测试Agent创建功能"""
    try:
        # 导入必要的模块
        from database import get_db_connection
        from services.agents.service import AgentService
        from services.files.utils import get_uuid

        print("1. 测试数据库连接...")
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查agent_config表是否存在
        cursor.execute("SHOW TABLES LIKE 'agent_config'")
        result = cursor.fetchone()

        if result:
            print("✅ agent_config表已存在")
        else:
            print("❌ agent_config表不存在")
            return False

        # 检查表结构
        cursor.execute("DESCRIBE agent_config")
        columns = cursor.fetchall()
        print("表结构:")
        for col in columns:
            print(f"  {col}")

        cursor.close()
        conn.close()

        print("\n2. 测试Agent列表查询...")
        result = AgentService.get_agent_list(page=1, size=10)
        print(f"查询结果: {result}")

        print("\n3. 测试Agent创建...")
        test_data = {
            "name": "测试Agent",
            "team_id": "test_team_id_123",
            "description": "这是一个测试Agent",
            "model_name": "gpt-3.5-turbo",
            "kb_ids": [],
            "system_prompt": "你是一个AI助手",
            "welcome_message": "你好，我是AI助手",
            "language": "zh-CN",
            "empty_response": "抱歉，我无法理解您的问题。",
            "is_default": False,
            "status": "active"
        }

        agent = AgentService.create_agent(**test_data)
        print(f"创建成功: {agent}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_agent_creation()