from flask import request, jsonify
from services.agents.service import AgentService
from utils import error_response, success_response

from .. import agent_bp


@agent_bp.route("", methods=["GET"])
def get_agent_list():
    """获取Agent配置列表"""
    try:
        page = int(request.args.get("currentPage", 1))
        size = int(request.args.get("size", 10))
        team_id = request.args.get("team_id", "")
        name = request.args.get("name", "")
        sort_by = request.args.get("sort_by", "create_time")
        sort_order = request.args.get("sort_order", "desc")

        result = AgentService.get_agent_list(
            page=page,
            size=size,
            team_id=team_id,
            name=name,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return success_response(result, "获取Agent列表成功")
    except Exception as e:
        return error_response(str(e))


@agent_bp.route("/<string:agent_id>", methods=["GET"])
def get_agent_detail(agent_id):
    """获取Agent详情"""
    try:
        agent = AgentService.get_agent_detail(agent_id)
        if not agent:
            return error_response("Agent不存在", code=404)
        return success_response(agent, "获取Agent详情成功")
    except Exception as e:
        return error_response(str(e))


@agent_bp.route("", methods=["POST"])
def create_agent():
    """创建Agent配置"""
    try:
        data = request.json
        print(f"收到创建Agent请求，数据: {data}")

        if not data.get("name"):
            return error_response("Agent名称不能为空", code=400)
        if not data.get("team_id"):
            return error_response("请选择团队", code=400)

        agent = AgentService.create_agent(**data)
        return success_response(agent, "创建Agent成功", code=201)
    except Exception as e:
        print(f"创建Agent失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(str(e))


@agent_bp.route("/<string:agent_id>", methods=["PUT"])
def update_agent(agent_id):
    """更新Agent配置"""
    try:
        data = request.json
        agent = AgentService.update_agent(agent_id=agent_id, **data)
        if not agent:
            return error_response("Agent不存在", code=404)
        return success_response(agent, "更新Agent成功")
    except Exception as e:
        return error_response(str(e))


@agent_bp.route("/<string:agent_id>", methods=["DELETE"])
def delete_agent(agent_id):
    """删除Agent配置"""
    try:
        result = AgentService.delete_agent(agent_id=agent_id)
        if not result:
            return error_response("Agent不存在", code=404)
        return success_response(message="删除Agent成功")
    except Exception as e:
        return error_response(str(e))


@agent_bp.route("/<string:agent_id>/default", methods=["PUT"])
def set_default_agent(agent_id):
    """设置默认Agent"""
    try:
        data = request.json
        is_default = data.get("is_default", False)
        
        result = AgentService.set_default_agent(agent_id, is_default)
        if not result:
            return error_response("Agent不存在", code=404)
            
        message = "已设为默认Agent" if is_default else "已取消默认Agent"
        return success_response(message=message)
    except Exception as e:
        return error_response(str(e))


@agent_bp.route("/teams/<string:team_id>/default", methods=["GET"])
def get_team_default_agent(team_id):
    """获取团队默认Agent"""
    try:
        agent = AgentService.get_team_default_agent(team_id)
        return success_response(agent, "获取团队默认Agent成功")
    except Exception as e:
        return error_response(str(e))