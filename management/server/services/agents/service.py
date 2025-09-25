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

            # 查询列表
            offset = (page - 1) * size
            list_query = f"""
                SELECT
                    a.id, a.name, a.team_id, a.description, a.model_name,
                    a.kb_ids, a.system_prompt, a.welcome_message, a.language,
                    a.empty_response, a.similarity_threshold, a.vector_similarity_weight,
                    a.vector_keywords_weight, a.top_n, a.rerank_enabled, a.rerank_model,
                    a.temperature, a.max_tokens, a.top_p, a.frequency_penalty,
                    a.presence_penalty, a.stream, a.is_default, a.status,
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

            # 处理知识库名称
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
                    a.id, a.name, a.team_id, a.description, a.model_name,
                    a.kb_ids, a.system_prompt, a.welcome_message, a.is_default,
                    a.status, a.create_time, a.create_date, a.update_time, a.update_date,
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

            # 如果设为默认，先取消同团队其他Agent的默认状态
            if data.get("is_default", False):
                # 导入RAGFlow的数据库模块来正确处理事务
                import sys
                sys.path.insert(0, '/ragflow')
                sys.path.insert(0, '/ragflow/api')
                from api.db.db_models import DB

                with DB.connection_context():
                    DB.execute_sql("UPDATE agent_config SET is_default = 0 WHERE team_id = %s", (data["team_id"],))

            # 创建Agent
            agent_id = get_uuid()
            current_time = int(datetime.now().timestamp())
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            kb_ids_json = json.dumps(data.get("kb_ids", [])) if data.get("kb_ids") else "[]"

            insert_query = """
                INSERT INTO agent_config (
                    id, name, team_id, description, model_name, kb_ids,
                    system_prompt, welcome_message, language, empty_response,
                    similarity_threshold, vector_similarity_weight, vector_keywords_weight,
                    top_n, rerank_enabled, rerank_model, temperature, max_tokens,
                    top_p, frequency_penalty, presence_penalty, stream,
                    is_default, status, create_time, create_date, update_time, update_date
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            cursor.execute(insert_query, (
                agent_id, data["name"], data["team_id"], data.get("description", ""),
                data["model_name"], kb_ids_json, data.get("system_prompt", ""),
                data.get("welcome_message", ""), data.get("language", "zh-CN"),
                data.get("empty_response") or "抱歉，我无法理解您的问题。",
                data.get("similarity_threshold", 0.2), data.get("vector_similarity_weight", 0.3),
                data.get("vector_keywords_weight", 0.7), data.get("top_n", 8),
                data.get("rerank_enabled", False), data.get("rerank_model", ""),
                data.get("temperature", 0.1), data.get("max_tokens", 512),
                data.get("top_p", 0.3), data.get("frequency_penalty", 0.7),
                data.get("presence_penalty", 0.4), data.get("stream", False),
                data.get("is_default", False), data.get("status", "active"),
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

            # 如果设为默认，先取消同团队其他Agent的默认状态
            if data.get("is_default", False):
                # 导入RAGFlow的数据库模块来正确处理事务
                import sys
                sys.path.insert(0, '/ragflow')
                sys.path.insert(0, '/ragflow/api')
                from api.db.db_models import DB

                with DB.connection_context():
                    DB.execute_sql("UPDATE agent_config SET is_default = 0 WHERE team_id = %s AND id != %s",
                                   (existing_agent["team_id"], agent_id))

            # 更新Agent
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
            if "model_name" in data:
                update_fields.append("model_name = %s")
                params.append(data["model_name"])
            if kb_ids_json is not None:
                update_fields.append("kb_ids = %s")
                params.append(kb_ids_json)
            if "system_prompt" in data:
                update_fields.append("system_prompt = %s")
                params.append(data["system_prompt"])
            if "welcome_message" in data:
                update_fields.append("welcome_message = %s")
                params.append(data["welcome_message"])
            if "is_default" in data:
                update_fields.append("is_default = %s")
                params.append(data["is_default"])
            if "status" in data:
                update_fields.append("status = %s")
                params.append(data["status"])

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
        """删除Agent配置 - 使用RAGFlow的数据库连接方式"""
        try:
            # 导入RAGFlow的数据库模块
            import sys
            sys.path.insert(0, '/ragflow')
            sys.path.insert(0, '/ragflow/api')
            from api.db.db_models import DB

            with DB.connection_context():
                # 检查Agent是否存在
                cursor = DB.execute_sql("SELECT id FROM agent_config WHERE id = %s", (agent_id,))
                if not cursor.fetchone():
                    return False

                # 删除Agent
                DB.execute_sql("DELETE FROM agent_config WHERE id = %s", (agent_id,))

            return True

        except Exception as e:
            print(f"删除Agent失败: {str(e)}")
            raise e

    @classmethod
    def set_default_agent(cls, agent_id, is_default):
        """设置默认Agent - 使用RAGFlow的数据库连接方式"""
        try:
            # 导入RAGFlow的数据库模块
            import sys
            sys.path.insert(0, '/ragflow')
            sys.path.insert(0, '/ragflow/api')
            from api.db.db_models import DB

            with DB.connection_context():
                # 获取Agent信息
                cursor = DB.execute_sql("SELECT id, team_id FROM agent_config WHERE id = %s", (agent_id,))
                row = cursor.fetchone()
                if not row:
                    return False

                columns = [desc[0] for desc in cursor.description]
                agent = dict(zip(columns, row))

                if is_default:
                    # 先取消同团队其他Agent的默认状态
                    DB.execute_sql("UPDATE agent_config SET is_default = 0 WHERE team_id = %s AND id != %s",
                                   (agent["team_id"], agent_id))

                # 更新当前Agent的默认状态
                DB.execute_sql("UPDATE agent_config SET is_default = %s WHERE id = %s",
                               (is_default, agent_id))

            return True

        except Exception as e:
            print(f"设置默认Agent失败: {str(e)}")
            raise e

    @classmethod
    def get_team_default_agent(cls, team_id):
        """获取团队默认Agent"""
        try:
            conn = cls._get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT 
                    id, name, description, model_name, kb_ids,
                    system_prompt, welcome_message, status
                FROM agent_config 
                WHERE team_id = %s AND is_default = 1 AND status = 'active'
                LIMIT 1
            """
            cursor.execute(query, (team_id,))
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
            print(f"获取团队默认Agent失败: {str(e)}")
            raise e