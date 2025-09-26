#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from flask import request
from flask_login import login_required, current_user
from api.db.services.dialog_service import DialogService
from api.db import StatusEnum
from api.db.services.llm_service import TenantLLMService
from api.db.services.knowledgebase_service import KnowledgebaseService
from api.db.services.user_service import TenantService, UserTenantService
from api import settings
from api.utils.api_utils import server_error_response, get_data_error_result, validate_request
from api.utils import get_uuid
from api.utils.api_utils import get_json_result


@manager.route("/set", methods=["POST"])  # noqa: F821
@login_required
def set_dialog():
    req = request.json
    dialog_id = req.get("dialog_id")
    name = req.get("name", "New Dialog")
    description = req.get("description", "一个智慧小帮手")
    icon = req.get("icon", "")
    top_n = req.get("top_n", 6)
    top_k = req.get("top_k", 1024)
    rerank_id = req.get("rerank_id", "")
    if not rerank_id:
        req["rerank_id"] = ""
    similarity_threshold = req.get("similarity_threshold", 0.1)
    vector_similarity_weight = req.get("vector_similarity_weight", 0.3)
    llm_setting = req.get("llm_setting", {})
    default_prompt = {
        "system": """你是一个智能助手，请总结知识库的内容来回答问题，请列举知识库中的数据详细回答。当所有知识库内容都与问题无关时，你的回答必须包括“知识库中未找到您要的答案！”这句话。回答需要考虑聊天历史。
以下是知识库：
{knowledge}
以上是知识库。""",
        "prologue": "您好，我是您的助手小樱，长得可爱又善良，can I help you?",
        "parameters": [{"key": "knowledge", "optional": False}],
        "empty_response": "Sorry! 知识库中未找到相关内容！",
    }
    prompt_config = req.get("prompt_config", default_prompt)

    if not prompt_config["system"]:
        prompt_config["system"] = default_prompt["system"]

    for p in prompt_config["parameters"]:
        if p["optional"]:
            continue
        if prompt_config["system"].find("{%s}" % p["key"]) < 0:
            return get_data_error_result(message="Parameter '{}' is not used".format(p["key"]))

    try:
        e, tenant = TenantService.get_by_id(current_user.id)
        if not e:
            return get_data_error_result(message="Tenant not found!")
        kbs = KnowledgebaseService.get_by_ids(req.get("kb_ids", []))
        embd_ids = [TenantLLMService.split_model_name_and_factory(kb.embd_id)[0] for kb in kbs]  # remove vendor suffix for comparison
        embd_count = len(set(embd_ids))
        if embd_count > 1:
            return get_data_error_result(message=f'Datasets use different embedding models: {[kb.embd_id for kb in kbs]}"')

        llm_id = req.get("llm_id", tenant.llm_id)
        if not dialog_id:
            dia = {
                "id": get_uuid(),
                "tenant_id": current_user.id,
                "name": name,
                "kb_ids": req.get("kb_ids", []),
                "description": description,
                "llm_id": llm_id,
                "llm_setting": llm_setting,
                "prompt_config": prompt_config,
                "top_n": top_n,
                "top_k": top_k,
                "rerank_id": rerank_id,
                "similarity_threshold": similarity_threshold,
                "vector_similarity_weight": vector_similarity_weight,
                "icon": icon,
            }
            if not DialogService.save(**dia):
                return get_data_error_result(message="Fail to new a dialog!")
            return get_json_result(data=dia)
        else:
            # 检查更新权限
            tenants = ensure_user_tenant_roles(current_user.id)
            has_permission = False
            for tenant in tenants:
                if DialogService.query(tenant_id=tenant.tenant_id, id=dialog_id):
                    has_permission = True
                    break

            if not has_permission:
                return get_json_result(data=False, message="Only owner of dialog authorized for this operation.", code=settings.RetCode.OPERATING_ERROR)

            del req["dialog_id"]
            if "kb_names" in req:
                del req["kb_names"]
            if not DialogService.update_by_id(dialog_id, req):
                return get_data_error_result(message="Dialog not found!")
            e, dia = DialogService.get_by_id(dialog_id)
            if not e:
                return get_data_error_result(message="Fail to update a dialog!")
            dia = dia.to_dict()
            dia.update(req)
            dia["kb_ids"], dia["kb_names"] = get_kb_names(dia["kb_ids"])
            return get_json_result(data=dia)
    except Exception as e:
        return server_error_response(e)


@manager.route("/get", methods=["GET"])  # noqa: F821
@login_required
def get():
    dialog_id = request.args["dialog_id"]
    try:
        # 检查是否是agent类型的dialog
        if dialog_id.startswith("agent_"):
            agent_id = dialog_id[6:]  # 移除"agent_"前缀

            # 获取agent作为dialog
            agent_dialog = get_agent_as_dialog(agent_id, current_user.id)
            if not agent_dialog:
                return get_data_error_result(message="Dialog not found!")

            # 简化的权限检查：检查用户是否有权限访问该团队的agent
            # 如果agent的team_id是"ALL"，则所有用户都可以访问
            if agent_dialog.tenant_id != 'ALL':
                tenants = ensure_user_tenant_roles(current_user.id)
                has_permission = False
                for tenant in tenants:
                    if tenant.tenant_id == agent_dialog.tenant_id:
                        has_permission = True
                        break

                if not has_permission:
                    return get_json_result(data=False, message="Only owner of dialog authorized for this operation.", code=settings.RetCode.OPERATING_ERROR)

            # 转换为dict并处理知识库信息
            dia = agent_dialog.to_dict()
            dia["kb_ids"], dia["kb_names"] = get_kb_names(dia.get("kb_ids", []))
            return get_json_result(data=dia)

        else:
            # 原有的dialog逻辑
            # 首先检查权限
            tenants = ensure_user_tenant_roles(current_user.id)
            has_permission = False
            for tenant in tenants:
                if DialogService.query(tenant_id=tenant.tenant_id, id=dialog_id):
                    has_permission = True
                    break

            if not has_permission:
                return get_json_result(data=False, message="Only owner of dialog authorized for this operation.", code=settings.RetCode.OPERATING_ERROR)

            e, dia = DialogService.get_by_id(dialog_id)
            if not e:
                return get_data_error_result(message="Dialog not found!")
            dia = dia.to_dict()
            dia["kb_ids"], dia["kb_names"] = get_kb_names(dia["kb_ids"])
            return get_json_result(data=dia)
    except Exception as e:
        return server_error_response(e)


def get_kb_names(kb_ids):
    ids, nms = [], []
    for kid in kb_ids:
        e, kb = KnowledgebaseService.get_by_id(kid)
        if not e or kb.status != StatusEnum.VALID.value:
            continue
        ids.append(kid)
        nms.append(kb.name)
    return ids, nms


def ensure_user_tenant_roles(user_id):
    """确保用户有租户角色，如果没有则自动创建"""
    tenants = UserTenantService.query(user_id=user_id)
    if not tenants:
        from api.utils import get_uuid
        from api.db import UserTenantRole
        tenant_role_data = {
            "id": get_uuid(),
            "user_id": user_id,
            "tenant_id": user_id,
            "role": UserTenantRole.OWNER,
            "invited_by": user_id,
            "status": "1"
        }
        UserTenantService.save(**tenant_role_data)
        tenants = UserTenantService.query(user_id=user_id)
    return tenants


def get_agent_as_dialog(agent_id, user_id=None):
    """从agent_config表获取agent并转换为dialog格式，支持权限验证"""
    try:
        from api.db.db_models import DB

        # 使用RAGFlow的数据库连接方式
        with DB.connection_context():
            # 查询agent信息，包含权限相关字段
            cursor = DB.execute_sql("""
                SELECT
                    id, name, team_id as tenant_id, description, avatar, model_name as llm_id,
                    kb_ids, system_prompt, welcome_message, language, empty_response,
                    similarity_threshold, vector_similarity_weight, top_n,
                    temperature, max_tokens, top_p, frequency_penalty, presence_penalty,
                    is_recommended, status, create_time, create_date, update_time, update_date,
                    user_id, created_by
                FROM agent_config
                WHERE id = %s AND status = 'active'
            """, (agent_id,))

            row = cursor.fetchone()
            if not row:
                return None

            # 转换查询结果为字典
            columns = [desc[0] for desc in cursor.description]
            agent = dict(zip(columns, row))
            
            # 权限验证：如果提供了user_id，检查用户是否有权限访问此agent
            if user_id and agent.get('user_id') and agent['user_id'] != user_id:
                # 检查用户是否属于同一个团队
                team_cursor = DB.execute_sql("""
                    SELECT COUNT(*) as count
                    FROM user_tenant ut
                    WHERE ut.user_id = %s AND ut.tenant_id = %s AND ut.status = '1'
                """, (user_id, agent['tenant_id']))
                
                team_row = team_cursor.fetchone()
                if not team_row or team_row[0] == 0:
                    # 用户不属于该团队，无权限访问
                    return None

        # 转换为dialog格式
        import json
        kb_ids = []
        if agent.get('kb_ids'):
            try:
                kb_ids = json.loads(agent['kb_ids']) if isinstance(agent['kb_ids'], str) else agent['kb_ids']
            except:
                kb_ids = []

        dialog_dict = {
            'id': f"agent_{agent['id']}",
            'name': agent['name'],
            'tenant_id': agent['tenant_id'],
            'description': agent.get('description', ''),
            'icon': agent.get('avatar', '/assets/agent/Agent-icon.svg'),
            'llm_id': agent.get('llm_id', ''),
            'kb_ids': kb_ids,
            'language': agent.get('language', 'Chinese'),
            'similarity_threshold': agent.get('similarity_threshold', 0.2),
            'vector_similarity_weight': agent.get('vector_similarity_weight', 0.3),
            'top_n': agent.get('top_n', 8),
            'status': '1' if agent.get('status') == 'active' else '0',
            'create_time': agent.get('create_time', 0),
            'create_date': agent.get('create_date', ''),
            'update_time': agent.get('update_time', 0),
            'update_date': agent.get('update_date', ''),
            'is_recommended': agent.get('is_recommended', False),
            'prompt_config': {
                'prologue': agent.get('welcome_message', '你好，我是AI助手'),
                'quote': True,
                'parameters': [{'key': 'knowledge', 'optional': False}],
                'system': agent.get('system_prompt', ''),
                'empty_response': agent.get('empty_response', '抱歉，我无法回答您的问题。')
            },
            'llm_setting': {
                'temperature': agent.get('temperature', 0.1),
                'max_tokens': agent.get('max_tokens', 512),
                'top_p': agent.get('top_p', 0.3),
                'frequency_penalty': agent.get('frequency_penalty', 0.7),
                'presence_penalty': agent.get('presence_penalty', 0.4)
            }
        }

        # 创建一个简单的对象来模拟Dialog模型
        class AgentDialog:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)

            def to_dict(self):
                return {key: getattr(self, key) for key in dir(self) if not key.startswith('_') and not callable(getattr(self, key))}

        return AgentDialog(dialog_dict)

    except Exception as e:
        print(f"获取agent作为dialog失败: {e}")
        return None


@manager.route("/list", methods=["GET"])  # noqa: F821
@login_required
def list_dialogs():
    try:
        # 确保用户有租户角色
        tenants = ensure_user_tenant_roles(current_user.id)

        all_dialogs = []

        # 查询每个租户下的Dialog
        for tenant in tenants:
            tenant_dialogs = DialogService.query(tenant_id=tenant.tenant_id, status=StatusEnum.VALID.value, reverse=True, order_by=DialogService.model.create_time)
            all_dialogs.extend(tenant_dialogs)

        # 按创建时间排序
        all_dialogs.sort(key=lambda x: x.create_time, reverse=True)
        diags = all_dialogs
        diags = [d.to_dict() for d in diags]
        for d in diags:
            d["kb_ids"], d["kb_names"] = get_kb_names(d["kb_ids"])
        return get_json_result(data=diags)
    except Exception as e:
        return server_error_response(e)


@manager.route("/rm", methods=["POST"])  # noqa: F821
@login_required
@validate_request("dialog_ids")
def rm():
    req = request.json
    tenants = ensure_user_tenant_roles(current_user.id)
    try:
        for id in req["dialog_ids"]:
            for tenant in tenants:
                if DialogService.query(tenant_id=tenant.tenant_id, id=id):
                    break
            else:
                return get_json_result(data=False, message="Only owner of dialog authorized for this operation.", code=settings.RetCode.OPERATING_ERROR)
            
            DialogService.delete_by_id(id)
        return get_json_result(data=True)
    except Exception as e:
        return server_error_response(e)
