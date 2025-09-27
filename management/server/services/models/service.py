"""
Global LLM Management Service
全局模型管理服务层
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

from database import get_db_connection


class GlobalLLMService:
    """全局模型管理服务"""

    @staticmethod
    def get_all_active_models() -> List[Dict[str, Any]]:
        """
        获取所有活跃的全局模型

        Returns:
            List[Dict]: 模型列表
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT id, fid, llm_factory, llm_name, model_type, max_tokens,
                       api_key, api_base, available, status, tags, description,
                       total_usage_count, active_users_count, created_by,
                       create_time, create_date, update_time, update_date
                FROM global_llm
                WHERE status = 'active' AND available = TRUE
                ORDER BY llm_factory, model_type, llm_name
            """
            cursor.execute(query)
            models = cursor.fetchall()

            # 处理敏感信息
            for model in models:
                if model.get('api_key'):
                    # 掩码显示API密钥
                    api_key = model['api_key']
                    if len(api_key) > 8:
                        model['api_key'] = f"{api_key[:4]}***{api_key[-4:]}"
                    else:
                        model['api_key'] = "***masked***"

                # 转换时间格式
                if isinstance(model.get('create_date'), datetime):
                    model['create_date'] = model['create_date'].strftime('%Y-%m-%d')
                if isinstance(model.get('update_date'), datetime):
                    model['update_date'] = model['update_date'].strftime('%Y-%m-%d')

            cursor.close()
            conn.close()

            return models

        except Exception as e:
            print(f"获取全局模型列表失败: {str(e)}")
            raise e

    @staticmethod
    def create_model(model_data: Dict[str, Any]) -> str:
        """
        创建全局模型

        Args:
            model_data: 模型数据

        Returns:
            str: 创建的模型ID
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # 检查是否已存在相同的模型
            check_query = """
                SELECT COUNT(*) as count FROM global_llm
                WHERE llm_factory = %s AND llm_name = %s AND model_type = %s
            """
            cursor.execute(check_query, [
                model_data['llm_factory'],
                model_data['llm_name'],
                model_data['model_type']
            ])

            if cursor.fetchone()[0] > 0:
                raise ValueError(f"模型 {model_data['llm_factory']}/{model_data['llm_name']} ({model_data['model_type']}) 已存在")

            # 插入新模型
            insert_query = """
                INSERT INTO global_llm (
                    fid, llm_factory, llm_name, model_type, api_key, api_base,
                    max_tokens, provider_config, available, status, tags, description,
                    total_usage_count, active_users_count, created_by,
                    create_time, create_date, update_time, update_date
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """

            cursor.execute(insert_query, [
                model_data['fid'],
                model_data['llm_factory'],
                model_data['llm_name'],
                model_data['model_type'],
                model_data['api_key'],
                model_data.get('api_base'),
                model_data['max_tokens'],
                model_data.get('provider_config'),
                model_data.get('available', True),
                model_data.get('status', 'active'),
                model_data.get('tags', ''),
                model_data.get('description', ''),
                model_data.get('total_usage_count', 0),
                model_data.get('active_users_count', 0),
                model_data['created_by'],
                model_data['create_time'],
                model_data['create_date'],
                model_data['update_time'],
                model_data['update_date']
            ])

            model_id = cursor.lastrowid
            conn.commit()

            cursor.close()
            conn.close()

            return str(model_id)

        except Exception as e:
            print(f"创建全局模型失败: {str(e)}")
            raise e

    @staticmethod
    def delete_model(llm_factory: str, llm_name: str, model_type: str = None) -> bool:
        """
        删除全局模型

        Args:
            llm_factory: 模型工厂
            llm_name: 模型名称
            model_type: 模型类型（可选）

        Returns:
            bool: 是否删除成功
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # 构建删除条件
            where_clause = "WHERE llm_factory = %s AND llm_name = %s"
            params = [llm_factory, llm_name]

            if model_type:
                where_clause += " AND model_type = %s"
                params.append(model_type)

            # 删除模型
            delete_query = f"DELETE FROM global_llm {where_clause}"
            cursor.execute(delete_query, params)

            affected_rows = cursor.rowcount
            conn.commit()

            cursor.close()
            conn.close()

            return affected_rows > 0

        except Exception as e:
            print(f"删除全局模型失败: {str(e)}")
            raise e

    @staticmethod
    def delete_factory_models(llm_factory: str) -> int:
        """
        删除整个模型工厂下的所有模型

        Args:
            llm_factory: 模型工厂

        Returns:
            int: 删除的模型数量
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # 删除工厂下的所有模型
            delete_query = "DELETE FROM global_llm WHERE llm_factory = %s"
            cursor.execute(delete_query, [llm_factory])

            affected_rows = cursor.rowcount
            conn.commit()

            cursor.close()
            conn.close()

            return affected_rows

        except Exception as e:
            print(f"删除模型工厂失败: {str(e)}")
            raise e

    @staticmethod
    def get_usage_statistics() -> List[Dict[str, Any]]:
        """
        获取全局模型使用统计

        Returns:
            List[Dict]: 使用统计列表
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT
                    ulu.user_id,
                    u.nickname as user_name,
                    ulu.tenant_id,
                    t.name as tenant_name,
                    ulu.llm_factory,
                    ulu.llm_name,
                    ulu.model_type,
                    ulu.usage_count,
                    ulu.token_usage,
                    FROM_UNIXTIME(ulu.last_used_time / 1000) as last_used
                FROM user_llm_usage ulu
                LEFT JOIN user u ON ulu.user_id = u.id
                LEFT JOIN tenant t ON ulu.tenant_id = t.id
                ORDER BY ulu.last_used_time DESC
                LIMIT 1000
            """
            cursor.execute(query)
            stats = cursor.fetchall()

            # 处理时间格式
            for stat in stats:
                if stat.get('last_used'):
                    if isinstance(stat['last_used'], datetime):
                        stat['last_used'] = stat['last_used'].strftime('%Y-%m-%d %H:%M:%S')

            cursor.close()
            conn.close()

            return stats

        except Exception as e:
            print(f"获取使用统计失败: {str(e)}")
            raise e

    @staticmethod
    def get_model_users(llm_factory: str, llm_name: str, model_type: str = None) -> List[Dict[str, Any]]:
        """
        获取指定模型的用户使用情况

        Args:
            llm_factory: 模型工厂
            llm_name: 模型名称
            model_type: 模型类型（可选）

        Returns:
            List[Dict]: 用户使用情况列表
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # 构建查询条件
            where_clause = "WHERE ulu.llm_factory = %s AND ulu.llm_name = %s"
            params = [llm_factory, llm_name]

            if model_type:
                where_clause += " AND ulu.model_type = %s"
                params.append(model_type)

            query = f"""
                SELECT
                    ulu.user_id,
                    u.nickname as user_name,
                    ulu.tenant_id,
                    t.name as tenant_name,
                    ulu.usage_count,
                    ulu.token_usage,
                    FROM_UNIXTIME(ulu.last_used_time / 1000) as last_used,
                    FROM_UNIXTIME(ulu.first_used_time / 1000) as first_used
                FROM user_llm_usage ulu
                LEFT JOIN user u ON ulu.user_id = u.id
                LEFT JOIN tenant t ON ulu.tenant_id = t.id
                {where_clause}
                ORDER BY ulu.usage_count DESC
            """
            cursor.execute(query, params)
            users = cursor.fetchall()

            # 处理时间格式
            for user in users:
                for time_field in ['last_used', 'first_used']:
                    if user.get(time_field):
                        if isinstance(user[time_field], datetime):
                            user[time_field] = user[time_field].strftime('%Y-%m-%d %H:%M:%S')

            cursor.close()
            conn.close()

            return users

        except Exception as e:
            print(f"获取模型用户失败: {str(e)}")
            raise e

    @staticmethod
    def get_user_available_models(user_id: str) -> Dict[str, Any]:
        """
        获取用户可用的全局模型列表

        Args:
            user_id: 用户ID

        Returns:
            Dict: 用户可用的模型列表（兼容原始格式）
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # 获取所有可用的全局模型
            query = """
                SELECT fid, llm_factory, llm_name, model_type, api_key, api_base, max_tokens
                FROM global_llm
                WHERE status = 'active' AND available = TRUE
                ORDER BY llm_factory, model_type, llm_name
            """
            cursor.execute(query)
            models = cursor.fetchall()

            # 转换为原始格式（按工厂分组）
            result = {}
            for model in models:
                factory = model['llm_factory']
                if factory not in result:
                    result[factory] = {}

                # 构建模型键名
                model_key = f"{model['llm_name']}"
                if model['model_type'] != 'chat':
                    model_key += f"_{model['model_type']}"

                result[factory][model_key] = {
                    "fid": model['fid'],
                    "llm_name": model['llm_name'],
                    "model_type": model['model_type'],
                    "api_key": model['api_key'],
                    "api_base": model.get('api_base', ''),
                    "max_tokens": model['max_tokens']
                }

            cursor.close()
            conn.close()

            return result

        except Exception as e:
            print(f"获取用户模型失败: {str(e)}")
            raise e

    @staticmethod
    def update_model_usage(user_id: str, tenant_id: str, global_llm_id: int,
                          llm_factory: str, llm_name: str, model_type: str,
                          usage_increment: int = 1, token_increment: int = 0):
        """
        更新模型使用统计

        Args:
            user_id: 用户ID
            tenant_id: 租户ID
            global_llm_id: 全局模型ID
            llm_factory: 模型工厂
            llm_name: 模型名称
            model_type: 模型类型
            usage_increment: 使用次数增量
            token_increment: Token使用增量
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            current_time = int(time.time() * 1000)
            current_date = datetime.now()

            # 检查是否已存在使用记录
            check_query = """
                SELECT id FROM user_llm_usage
                WHERE user_id = %s AND global_llm_id = %s
            """
            cursor.execute(check_query, [user_id, global_llm_id])
            existing_record = cursor.fetchone()

            if existing_record:
                # 更新现有记录
                update_query = """
                    UPDATE user_llm_usage
                    SET usage_count = usage_count + %s,
                        token_usage = token_usage + %s,
                        last_used_time = %s,
                        last_used_date = %s,
                        update_time = %s,
                        update_date = %s
                    WHERE id = %s
                """
                cursor.execute(update_query, [
                    usage_increment, token_increment, current_time, current_date,
                    current_time, current_date, existing_record[0]
                ])
            else:
                # 创建新记录
                insert_query = """
                    INSERT INTO user_llm_usage (
                        user_id, tenant_id, global_llm_id, llm_factory, llm_name, model_type,
                        usage_count, token_usage, last_used_time, last_used_date,
                        first_used_time, first_used_date, create_time, create_date,
                        update_time, update_date
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, [
                    user_id, tenant_id, global_llm_id, llm_factory, llm_name, model_type,
                    usage_increment, token_increment, current_time, current_date,
                    current_time, current_date, current_time, current_date,
                    current_time, current_date
                ])

            # 更新全局模型的使用统计
            update_global_query = """
                UPDATE global_llm
                SET total_usage_count = total_usage_count + %s,
                    active_users_count = (
                        SELECT COUNT(DISTINCT user_id)
                        FROM user_llm_usage
                        WHERE global_llm_id = %s
                    ),
                    update_time = %s,
                    update_date = %s
                WHERE id = %s
            """
            cursor.execute(update_global_query, [
                usage_increment, global_llm_id, current_time, current_date, global_llm_id
            ])

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            print(f"更新模型使用统计失败: {str(e)}")
            raise e

    @staticmethod
    def get_user_model_by_id(model_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取用户模型详细信息

        Args:
            model_id: 模型ID

        Returns:
            Dict: 模型信息，如果不存在则返回None
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # 先从用户模型表查询
            query = """
                SELECT tl.*, u.nickname as user_name, t.name as tenant_name
                FROM tenant_llm tl
                LEFT JOIN user u ON tl.tenant_id = u.tenant_id
                LEFT JOIN tenant t ON tl.tenant_id = t.id
                WHERE tl.id = %s
                LIMIT 1
            """
            cursor.execute(query, [model_id])
            user_model = cursor.fetchone()

            if user_model:
                cursor.close()
                conn.close()
                return user_model

            # 如果用户模型表没有，再从全局模型表查询
            query = """
                SELECT * FROM global_llm WHERE id = %s LIMIT 1
            """
            cursor.execute(query, [model_id])
            global_model = cursor.fetchone()

            cursor.close()
            conn.close()

            return global_model

        except Exception as e:
            print(f"获取用户模型失败: {str(e)}")
            raise e

    @staticmethod
    def get_all_user_models() -> List[Dict[str, Any]]:
        """
        获取所有用户创建的模型

        Returns:
            List[Dict]: 用户模型列表
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT tl.id, tl.llm_factory, tl.llm_name, tl.model_type,
                       tl.api_key, tl.api_base, tl.max_tokens, tl.used_tokens as usage_count,
                       tl.create_date, tl.update_date, tl.create_time, tl.update_time,
                       u.nickname as user_name, t.name as tenant_name,
                       CASE WHEN tl.llm_name IS NOT NULL AND tl.llm_name != '' THEN tl.llm_name ELSE tl.llm_factory END as model_name,
                       TRUE as available
                FROM tenant_llm tl
                LEFT JOIN user u ON tl.tenant_id = u.tenant_id
                LEFT JOIN tenant t ON tl.tenant_id = t.id
                WHERE tl.api_key IS NOT NULL AND tl.api_key != ''
                ORDER BY tl.create_time DESC
            """
            cursor.execute(query)
            models = cursor.fetchall()

            # 处理敏感信息
            for model in models:
                if model.get('api_key'):
                    api_key = model['api_key']
                    if len(api_key) > 8:
                        model['api_key'] = f"{api_key[:4]}***{api_key[-4:]}"
                    else:
                        model['api_key'] = "***masked***"

                # 转换时间格式
                if isinstance(model.get('create_date'), datetime):
                    model['create_date'] = model['create_date'].strftime('%Y-%m-%d')
                if isinstance(model.get('update_date'), datetime):
                    model['update_date'] = model['update_date'].strftime('%Y-%m-%d')

            cursor.close()
            conn.close()

            return models

        except Exception as e:
            print(f"获取用户模型列表失败: {str(e)}")
            raise e

    @staticmethod
    def test_model_connection(model_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        测试模型连接

        Args:
            model_config: 模型配置信息

        Returns:
            Dict: 测试结果
        """
        try:
            llm_factory = model_config.get('llm_factory')
            api_key = model_config.get('api_key')
            api_base = model_config.get('api_base')
            model_type = model_config.get('model_type', 'chat')

            # 这里应该根据不同的供应商实现实际的连接测试
            # 为了演示，我们实现一个简单的测试逻辑

            if llm_factory == 'openai':
                return GlobalLLMService._test_openai_connection(api_key, api_base)
            elif llm_factory == 'azure_openai':
                return GlobalLLMService._test_azure_connection(model_config)
            elif llm_factory == 'anthropic':
                return GlobalLLMService._test_anthropic_connection(api_key)
            else:
                # 默认测试逻辑
                return GlobalLLMService._test_generic_connection(model_config)

        except Exception as e:
            print(f"模型连接测试失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def _test_openai_connection(api_key: str, api_base: Optional[str] = None) -> Dict[str, Any]:
        """测试OpenAI连接"""
        try:
            import requests

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            base_url = api_base or "https://api.openai.com/v1"
            url = f"{base_url}/models"

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return {
                    "success": True,
                    "data": {"status": "connected", "models_count": len(response.json().get('data', []))}
                }
            else:
                return {
                    "success": False,
                    "error": f"API请求失败: {response.status_code}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"连接测试失败: {str(e)}"
            }

    @staticmethod
    def _test_azure_connection(model_config: Dict[str, Any]) -> Dict[str, Any]:
        """测试Azure OpenAI连接"""
        try:
            import requests

            api_key = model_config.get('api_key')
            api_base = model_config.get('api_base')
            api_version = model_config.get('api_version', '2023-05-15')

            headers = {
                "api-key": api_key,
                "Content-Type": "application/json"
            }

            url = f"{api_base}/openai/deployments?api-version={api_version}"

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return {
                    "success": True,
                    "data": {"status": "connected", "deployments": response.json()}
                }
            else:
                return {
                    "success": False,
                    "error": f"Azure API请求失败: {response.status_code}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Azure连接测试失败: {str(e)}"
            }

    @staticmethod
    def _test_anthropic_connection(api_key: str) -> Dict[str, Any]:
        """测试Anthropic连接"""
        try:
            import requests

            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }

            # Anthropic没有models端点，我们发送一个简单的消息测试
            url = "https://api.anthropic.com/v1/messages"
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "test"}]
            }

            response = requests.post(url, headers=headers, json=data, timeout=10)

            if response.status_code == 200:
                return {
                    "success": True,
                    "data": {"status": "connected"}
                }
            else:
                return {
                    "success": False,
                    "error": f"Anthropic API请求失败: {response.status_code}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Anthropic连接测试失败: {str(e)}"
            }

    @staticmethod
    def _test_generic_connection(model_config: Dict[str, Any]) -> Dict[str, Any]:
        """通用连接测试"""
        try:
            # 对于不支持的供应商，返回基础验证结果
            api_key = model_config.get('api_key')
            llm_factory = model_config.get('llm_factory')

            if not api_key or len(api_key) < 10:
                return {
                    "success": False,
                    "error": "API密钥格式不正确"
                }

            return {
                "success": True,
                "data": {
                    "status": "validated",
                    "message": f"{llm_factory} 供应商配置验证通过（未实现实际连接测试）"
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"通用连接测试失败: {str(e)}"
            }