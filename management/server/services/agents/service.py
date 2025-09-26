import json
from datetime import datetime
from database import get_db_connection
from services.files.utils import get_uuid


class AgentService:
    """Agent配置服务"""

    @classmethod
    def _get_db_connection(cls):
        """获取数据库连接"""
        return get_db_connection()

    @classmethod
    def get_agent_list(cls, page=1, size=10, team_id="", name="", sort_by="create_time", sort_order="desc"):
        """获取Agent配置列表"""
        try:
            conn = cls._get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # 构建查询条件
            where_conditions = []
            params = []

            if team_id:
                where_conditions.append("a.team_id = %s")
                params.append(team_id)

            if name:
                where_conditions.append("a.name LIKE %s")
                params.append(f"%{name}%")

            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

            # 验证排序字段
            valid_sort_fields = ["name", "create_time", "update_time"]
            if sort_by not in valid_sort_fields:
                sort_by = "create_time"

            sort_clause = f"ORDER BY a.{sort_by} {sort_order.upper()}"

            # 查询总数
            count_query = f"""
                SELECT COUNT(*) as total
                FROM agent_config a
                {where_clause}
            """
            cursor.execute(count_query, params)
            total = cursor.fetchone()["total"]

            # 查询列表 - 只使用基础字段，避免字段不存在错误
            offset = (page - 1) * size
            list_query = f"""
                SELECT
                    a.id, a.name, a.team_id, a.user_id, a.created_by, a.description,
                    a.avatar, a.model_name, a.kb_ids,
                    a.system_prompt, a.welcome_message, a.language, a.empty_response,
                    a.similarity_threshold, a.vector_similarity_weight, a.vector_keywords_weight,
                    a.top_n, a.rerank_enabled, a.rerank_model,
                    a.temperature, a.max_tokens, a.top_p, a.frequency_penalty,
                    a.presence_penalty, a.stream, a.is_recommended, a.status,
                    a.create_time, a.create_date, a.update_time, a.update_date,
                    t.name as team_name
                FROM agent_config a
                LEFT JOIN tenant t ON a.team_id = t.id
                {where_clause}
                {sort_clause}
                LIMIT %s OFFSET %s
            """
            params.extend([size, offset])
            cursor.execute(list_query, params)
            agents = cursor.fetchall()

            # 处理知识库名称和数据转换
            for agent in agents:
                if agent["kb_ids"]:
                    try:
                        kb_ids = json.loads(agent["kb_ids"]) if isinstance(agent["kb_ids"], str) else agent["kb_ids"]
                        if kb_ids:
                            # 查询知识库名称
                            kb_query = "SELECT name FROM knowledgebase WHERE id IN (%s)" % ",".join(["%s"] * len(kb_ids))
                            cursor.execute(kb_query, kb_ids)
                            kb_names = [row["name"] for row in cursor.fetchall()]
                            agent["kb_names"] = kb_names
                        else:
                            agent["kb_names"] = []
                    except:
                        agent["kb_names"] = []
                else:
                    agent["kb_names"] = []

                # 格式化日期
                if isinstance(agent.get("create_date"), datetime):
                    agent["create_date"] = agent["create_date"].strftime("%Y-%m-%d %H:%M:%S")

                # 为了向后兼容，添加一些扁平化字段（web前端可能需要）
                try:
                    if agent.get("llm_setting"):
                        llm_setting = json.loads(agent["llm_setting"]) if isinstance(agent["llm_setting"], str) else agent["llm_setting"]
                        agent["temperature"] = llm_setting.get("temperature", 0.1)
                        agent["max_tokens"] = llm_setting.get("max_tokens", 512)
                        agent["top_p"] = llm_setting.get("top_p", 0.3)
                        agent["frequency_penalty"] = llm_setting.get("frequency_penalty", 0.7)
                        agent["presence_penalty"] = llm_setting.get("presence_penalty", 0.4)
                except:
                    pass

                try:
                    if agent.get("prompt_config"):
                        prompt_config = json.loads(agent["prompt_config"]) if isinstance(agent["prompt_config"], str) else agent["prompt_config"]
                        agent["system_prompt"] = prompt_config.get("system", "")
                        agent["welcome_message"] = prompt_config.get("prologue", "")
                        agent["empty_response"] = prompt_config.get("empty_response", "")
                except:
                    pass

            cursor.close()
            conn.close()

            return {
                "list": agents,
                "total": total
            }

        except Exception as e:
            print(f"获取Agent列表失败: {str(e)}")
            raise e

    @classmethod
    def get_agent_detail(cls, agent_id):
        """获取Agent详情"""
        try:
            conn = cls._get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT
                    a.id, a.name, a.team_id, a.user_id, a.created_by, a.description,
                    a.avatar, a.model_name, a.kb_ids,
                    a.system_prompt, a.welcome_message, a.language, a.empty_response,
                    a.similarity_threshold, a.vector_similarity_weight, a.vector_keywords_weight,
                    a.top_n, a.rerank_enabled, a.rerank_model,
                    a.temperature, a.max_tokens, a.top_p, a.frequency_penalty,
                    a.presence_penalty, a.stream, a.is_recommended, a.status,
                    a.create_time, a.create_date, a.update_time, a.update_date,
                    t.name as team_name
                FROM agent_config a
                LEFT JOIN tenant t ON a.team_id = t.id
                WHERE a.id = %s
            """
            cursor.execute(query, (agent_id,))
            agent = cursor.fetchone()

            if agent and agent["kb_ids"]:
                try:
                    kb_ids = json.loads(agent["kb_ids"]) if isinstance(agent["kb_ids"], str) else agent["kb_ids"]
                    agent["kb_ids"] = kb_ids
                except:
                    agent["kb_ids"] = []

            cursor.close()
            conn.close()

            return agent

        except Exception as e:
            print(f"获取Agent详情失败: {str(e)}")
            raise e

    @classmethod
    def create_agent(cls, **data):
        """创建Agent配置"""
        try:
            conn = cls._get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # 检查名称是否已存在
            check_query = "SELECT COUNT(*) as count FROM agent_config WHERE name = %s AND team_id = %s"
            cursor.execute(check_query, (data["name"], data["team_id"]))
            if cursor.fetchone()["count"] > 0:
                raise Exception("该团队中已存在同名Agent")

            # 推荐状态不需要互斥，可以多个Agent同时推荐

            # 创建Agent - 与RAGFlow Dialog模型保持一致
            agent_id = get_uuid()
            current_time = int(datetime.now().timestamp())
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            kb_ids_json = json.dumps(data.get("kb_ids", [])) if data.get("kb_ids") else "[]"

            # 获取创建者信息（从请求上下文或参数中获取）
            user_id = data.get("user_id") or data.get("created_by")
            created_by = user_id

            # 构建llm_setting对象
            llm_setting = {
                "temperature": data.get("temperature", 0.1),
                "top_p": data.get("top_p", 0.3),
                "frequency_penalty": data.get("frequency_penalty", 0.7),
                "presence_penalty": data.get("presence_penalty", 0.4),
                "max_tokens": data.get("max_tokens", 512)
            }
            llm_setting_json = json.dumps(llm_setting)

            # 构建prompt_config对象
            prompt_config = {
                "system": data.get("system_prompt", ""),
                "prologue": data.get("welcome_message", "Hi! I'm your assistant, what can I do for you?"),
                "parameters": [{"key": "knowledge", "optional": False}],
                "empty_response": data.get("empty_response", "Sorry! No relevant content was found in the knowledge base!")
            }
            prompt_config_json = json.dumps(prompt_config)

            # 处理语言字段
            language = data.get("language", "Chinese")
            if language == "zh-CN":
                language = "Chinese"
            elif language == "en-US":
                language = "English"

            # 处理状态字段
            status = "1" if data.get("status", "active") == "active" else "0"

            insert_query = """
                INSERT INTO agent_config (
                    id, name, team_id, user_id, created_by, description, avatar,
                    model_name, kb_ids, system_prompt, welcome_message, language,
                    empty_response, similarity_threshold, vector_similarity_weight, vector_keywords_weight,
                    top_n, rerank_enabled, rerank_model, temperature, max_tokens,
                    top_p, frequency_penalty, presence_penalty, stream,
                    is_recommended, status, create_time, create_date, update_time, update_date
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            cursor.execute(insert_query, (
                agent_id, data["name"], data["team_id"], user_id, created_by,
                data.get("description", ""), data.get("avatar", "/assets/agent/Agent-icon.svg"),
                data.get("model_name"), kb_ids_json, data.get("system_prompt", ""),
                data.get("welcome_message", ""), language,
                data.get("empty_response") or "抱歉，我无法理解您的问题。",
                data.get("similarity_threshold", 0.2), data.get("vector_similarity_weight", 0.3),
                data.get("vector_keywords_weight", 0.7), data.get("top_n", 8),
                data.get("rerank_enabled", False), data.get("rerank_model", ""),
                data.get("temperature", 0.1), data.get("max_tokens", 512),
                data.get("top_p", 0.3), data.get("frequency_penalty", 0.7),
                data.get("presence_penalty", 0.4), data.get("stream", True),
                data.get("is_recommended", False), data.get("status", "active"),
                current_time, current_date, current_time, current_date
            ))

            conn.commit()
            cursor.close()
            conn.close()

            return cls.get_agent_detail(agent_id)

        except Exception as e:
            print(f"创建Agent失败: {str(e)}")
            raise e

    @classmethod
    def update_agent(cls, agent_id, **data):
        """更新Agent配置"""
        try:
            conn = cls._get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # 检查Agent是否存在
            check_query = "SELECT id, team_id FROM agent_config WHERE id = %s"
            cursor.execute(check_query, (agent_id,))
            existing_agent = cursor.fetchone()
            if not existing_agent:
                return None

            # 推荐状态不需要互斥，可以多个Agent同时推荐

            # 更新Agent - 与RAGFlow Dialog模型保持一致
            current_time = int(datetime.now().timestamp())
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            kb_ids_json = json.dumps(data.get("kb_ids", [])) if "kb_ids" in data else None

            update_fields = []
            params = []

            if "name" in data:
                update_fields.append("name = %s")
                params.append(data["name"])
            if "description" in data:
                update_fields.append("description = %s")
                params.append(data["description"])
            if "avatar" in data:
                update_fields.append("avatar = %s")
                params.append(data["avatar"])
            if "model_name" in data:
                update_fields.append("model_name = %s")
                params.append(data["model_name"])
            if kb_ids_json is not None:
                update_fields.append("kb_ids = %s")
                params.append(kb_ids_json)
            if "language" in data:
                language = data["language"]
                if language == "zh-CN":
                    language = "Chinese"
                elif language == "en-US":
                    language = "English"
                update_fields.append("language = %s")
                params.append(language)
            # 处理llm_setting更新
            if any(key in data for key in ["temperature", "top_p", "frequency_penalty", "presence_penalty", "max_tokens"]):
                llm_setting = {
                    "temperature": data.get("temperature", 0.1),
                    "top_p": data.get("top_p", 0.3),
                    "frequency_penalty": data.get("frequency_penalty", 0.7),
                    "presence_penalty": data.get("presence_penalty", 0.4),
                    "max_tokens": data.get("max_tokens", 512)
                }
                update_fields.append("llm_setting = %s")
                params.append(json.dumps(llm_setting))
            # 处理prompt_config更新
            if any(key in data for key in ["system_prompt", "welcome_message", "empty_response"]):
                prompt_config = {
                    "system": data.get("system_prompt", ""),
                    "prologue": data.get("welcome_message", "Hi! I'm your assistant, what can I do for you?"),
                    "parameters": [{"key": "knowledge", "optional": False}],
                    "empty_response": data.get("empty_response", "Sorry! No relevant content was found in the knowledge base!")
                }
                update_fields.append("prompt_config = %s")
                params.append(json.dumps(prompt_config))
            if "similarity_threshold" in data:
                update_fields.append("similarity_threshold = %s")
                params.append(data["similarity_threshold"])
            if "vector_similarity_weight" in data:
                update_fields.append("vector_similarity_weight = %s")
                params.append(data["vector_similarity_weight"])
            if "top_n" in data:
                update_fields.append("top_n = %s")
                params.append(data["top_n"])
            if "top_k" in data:
                update_fields.append("top_k = %s")
                params.append(data["top_k"])
            if "rerank_model" in data:
                update_fields.append("rerank_id = %s")
                params.append(data["rerank_model"])
            if "is_recommended" in data:
                update_fields.append("is_recommended = %s")
                params.append(data["is_recommended"])
            if "status" in data:
                status = "1" if data["status"] == "active" else "0"
                update_fields.append("status = %s")
                params.append(status)

            update_fields.extend(["update_time = %s", "update_date = %s"])
            params.extend([current_time, current_date, agent_id])

            update_query = f"""
                UPDATE agent_config 
                SET {', '.join(update_fields)}
                WHERE id = %s
            """
            cursor.execute(update_query, params)

            conn.commit()
            cursor.close()
            conn.close()

            return cls.get_agent_detail(agent_id)

        except Exception as e:
            print(f"更新Agent失败: {str(e)}")
            raise e

    @classmethod
    def delete_agent(cls, agent_id):
        """删除Agent配置"""
        try:
            # 使用RAGFlow的数据库模块来正确处理事务
            import sys
            import os
            ragflow_path = '/ragflow'
            if ragflow_path not in sys.path:
                sys.path.insert(0, ragflow_path)
            if os.path.join(ragflow_path, 'api') not in sys.path:
                sys.path.insert(0, os.path.join(ragflow_path, 'api'))

            try:
                from api.db.db_models import DB
                with DB.connection_context():
                    # 检查Agent是否存在
                    cursor = DB.execute_sql("SELECT id FROM agent_config WHERE id = %s", (agent_id,))
                    if not cursor.fetchone():
                        return False

                    # 删除Agent
                    DB.execute_sql("DELETE FROM agent_config WHERE id = %s", (agent_id,))

                return True
            except ImportError:
                # 如果导入失败，使用普通的数据库连接
                conn = cls._get_db_connection()
                cursor = conn.cursor(dictionary=True)

                # 检查Agent是否存在
                check_query = "SELECT id FROM agent_config WHERE id = %s"
                cursor.execute(check_query, (agent_id,))
                if not cursor.fetchone():
                    cursor.close()
                    conn.close()
                    return False

                # 删除Agent
                delete_query = "DELETE FROM agent_config WHERE id = %s"
                cursor.execute(delete_query, (agent_id,))
                conn.commit()

                cursor.close()
                conn.close()
                return True

        except Exception as e:
            print(f"删除Agent失败: {str(e)}")
            raise e

    @classmethod
    def set_recommended_agent(cls, agent_id, is_recommended):
        """设置推荐Agent"""
        try:
            # 使用RAGFlow的数据库模块来正确处理事务
            import sys
            import os
            ragflow_path = '/ragflow'
            if ragflow_path not in sys.path:
                sys.path.insert(0, ragflow_path)
            if os.path.join(ragflow_path, 'api') not in sys.path:
                sys.path.insert(0, os.path.join(ragflow_path, 'api'))

            try:
                from api.db.db_models import DB
                with DB.connection_context():
                    # 获取Agent信息
                    cursor = DB.execute_sql("SELECT id, team_id FROM agent_config WHERE id = %s", (agent_id,))
                    row = cursor.fetchone()
                    if not row:
                        return False

                    columns = [desc[0] for desc in cursor.description]
                    agent = dict(zip(columns, row))

                    # 直接更新当前Agent的推荐状态（推荐状态不需要互斥）
                    DB.execute_sql("UPDATE agent_config SET is_recommended = %s WHERE id = %s",
                                   (is_recommended, agent_id))

                return True
            except ImportError:
                # 如果导入失败，使用普通的数据库连接
                conn = cls._get_db_connection()
                cursor = conn.cursor(dictionary=True)

                # 获取Agent信息
                check_query = "SELECT id, team_id FROM agent_config WHERE id = %s"
                cursor.execute(check_query, (agent_id,))
                agent = cursor.fetchone()
                if not agent:
                    cursor.close()
                    conn.close()
                    return False

                # 直接更新当前Agent的推荐状态（推荐状态不需要互斥）
                update_query = "UPDATE agent_config SET is_recommended = %s WHERE id = %s"
                cursor.execute(update_query, (is_recommended, agent_id))

                conn.commit()
                cursor.close()
                conn.close()
                return True

        except Exception as e:
            print(f"设置推荐Agent失败: {str(e)}")
            raise e

    @classmethod
    def get_team_recommended_agents(cls, team_id):
        """获取团队推荐Agent列表"""
        try:
            conn = cls._get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT
                    id, name, description, model_name, kb_ids,
                    system_prompt, welcome_message, status
                FROM agent_config
                WHERE team_id = %s AND is_recommended = 1 AND status = 'active'
                ORDER BY create_time DESC
            """
            cursor.execute(query, (team_id,))
            agents = cursor.fetchall()

            for agent in agents:
                if agent and agent["kb_ids"]:
                    try:
                        kb_ids = json.loads(agent["kb_ids"]) if isinstance(agent["kb_ids"], str) else agent["kb_ids"]
                        agent["kb_ids"] = kb_ids
                    except:
                        agent["kb_ids"] = []

            cursor.close()
            conn.close()

            return agents

        except Exception as e:
            print(f"获取团队推荐Agent失败: {str(e)}")
            raise e