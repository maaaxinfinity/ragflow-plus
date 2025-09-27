"""
Global LLM Management API Routes for Management Panel
全局模型管理API - 具有管理员权限，无需用户鉴权
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import time
import json
import logging

from services.models.service import GlobalLLMService
from .. import models_bp
logger = logging.getLogger(__name__)

@models_bp.route('/list', methods=['GET'])
def list_global_models():
    """
    获取所有全局模型配置列表
    GET /v1/management/llm/list
    """
    try:
        models_data = GlobalLLMService.get_all_active_models()

        return jsonify({
            "code": 0,
            "data": models_data,
            "message": "success"
        })

    except Exception as e:
        logger.error(f"Failed to list global models: {str(e)}")
        return jsonify({
            "code": 1005,
            "message": f"获取全局模型列表失败: {str(e)}"
        }), 500

@models_bp.route('/add', methods=['POST'])
def add_global_model():
    """
    添加全局模型配置
    POST /v1/management/llm/add
    """
    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ['llm_factory', 'llm_name', 'model_type', 'api_key', 'max_tokens']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    "code": 1001,
                    "message": f"缺少必填字段: {field}"
                }), 400

        # 构建模型数据
        model_data = {
            "fid": f"{data['llm_factory']}_{data['llm_name']}_{data['model_type']}",
            "llm_factory": data['llm_factory'],
            "llm_name": data['llm_name'],
            "model_type": data['model_type'],
            "api_key": data['api_key'],
            "api_base": data.get('api_base'),
            "max_tokens": data['max_tokens'],
            "provider_config": json.dumps({k: v for k, v in data.items()
                                         if k not in required_fields + ['api_base']}),
            "available": True,
            "status": "active",
            "created_by": "management_admin",
            "create_time": int(time.time() * 1000),
            "create_date": datetime.now(),
            "update_time": int(time.time() * 1000),
            "update_date": datetime.now()
        }

        model_id = GlobalLLMService.create_model(model_data)

        logger.info(f"Global model added: {data['llm_factory']}/{data['llm_name']} (ID: {model_id})")

        return jsonify({
            "code": 0,
            "data": {"id": model_id},
            "message": "全局模型添加成功"
        })

    except Exception as e:
        logger.error(f"Failed to add global model: {str(e)}")
        return jsonify({
            "code": 1005,
            "message": f"添加全局模型失败: {str(e)}"
        }), 500

@models_bp.route('/delete', methods=['POST'])
def delete_global_model():
    """
    删除全局模型配置
    POST /v1/management/llm/delete
    """
    try:
        data = request.get_json()

        llm_factory = data.get('llm_factory')
        llm_name = data.get('llm_name')

        if not llm_factory or not llm_name:
            return jsonify({
                "code": 1001,
                "message": "缺少必填字段: llm_factory, llm_name"
            }), 400

        success = GlobalLLMService.delete_model(llm_factory, llm_name)

        if success:
            logger.info(f"Global model deleted: {llm_factory}/{llm_name}")
            return jsonify({
                "code": 0,
                "message": "全局模型删除成功"
            })
        else:
            return jsonify({
                "code": 1004,
                "message": f"模型 {llm_factory}/{llm_name} 不存在"
            }), 404

    except Exception as e:
        logger.error(f"Failed to delete global model: {str(e)}")
        return jsonify({
            "code": 1005,
            "message": f"删除全局模型失败: {str(e)}"
        }), 500

@models_bp.route('/delete_factory', methods=['POST'])
def delete_model_factory():
    """
    删除整个模型工厂
    POST /v1/management/llm/delete_factory
    """
    try:
        data = request.get_json()
        llm_factory = data.get('llm_factory')

        if not llm_factory:
            return jsonify({
                "code": 1001,
                "message": "缺少必填字段: llm_factory"
            }), 400

        deleted_count = GlobalLLMService.delete_factory_models(llm_factory)

        logger.info(f"Model factory deleted: {llm_factory}, deleted {deleted_count} models")

        return jsonify({
            "code": 0,
            "data": {"deleted_count": deleted_count},
            "message": f"模型工厂删除成功，共删除 {deleted_count} 个模型"
        })

    except Exception as e:
        logger.error(f"Failed to delete model factory: {str(e)}")
        return jsonify({
            "code": 1005,
            "message": f"删除模型工厂失败: {str(e)}"
        }), 500

@models_bp.route('/usage_stats', methods=['GET'])
def get_usage_statistics():
    """
    获取所有用户的模型使用统计
    GET /v1/management/llm/usage_stats
    """
    try:
        stats_data = GlobalLLMService.get_usage_statistics()

        return jsonify({
            "code": 0,
            "data": stats_data,
            "message": "success"
        })

    except Exception as e:
        logger.error(f"Failed to get usage statistics: {str(e)}")
        return jsonify({
            "code": 1005,
            "message": f"获取使用统计失败: {str(e)}"
        }), 500

@models_bp.route('/model_users', methods=['GET'])
def get_model_users():
    """
    获取指定模型的用户使用情况
    GET /v1/management/llm/model_users?llm_factory=openai&llm_name=gpt-4
    """
    try:
        llm_factory = request.args.get('llm_factory')
        llm_name = request.args.get('llm_name')

        if not llm_factory or not llm_name:
            return jsonify({
                "code": 1001,
                "message": "缺少必填参数: llm_factory, llm_name"
            }), 400

        users_data = GlobalLLMService.get_model_users(llm_factory, llm_name)

        return jsonify({
            "code": 0,
            "data": users_data,
            "message": "success"
        })

    except Exception as e:
        logger.error(f"Failed to get model users: {str(e)}")
        return jsonify({
            "code": 1005,
            "message": f"获取模型用户失败: {str(e)}"
        }), 500

@models_bp.route('/user_models', methods=['GET'])
def get_user_models():
    """
    获取指定用户的模型列表
    GET /v1/management/llm/user_models?user_id=user123
    """
    try:
        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({
                "code": 1001,
                "message": "缺少必填参数: user_id"
            }), 400

        models_data = GlobalLLMService.get_user_available_models(user_id)

        return jsonify({
            "code": 0,
            "data": models_data,
            "message": "success"
        })

    except Exception as e:
        logger.error(f"Failed to get user models: {str(e)}")
        return jsonify({
            "code": 1005,
            "message": f"获取用户模型失败: {str(e)}"
        }), 500


@models_bp.route('/promote', methods=['POST'])
def promote_user_model_to_global():
    """
    将用户模型升级为全局模型
    POST /v1/management/llm/promote
    """
    try:
        data = request.get_json()

        user_model_id = data.get('user_model_id')
        llm_factory = data.get('llm_factory')
        llm_name = data.get('llm_name')

        if not all([user_model_id, llm_factory, llm_name]):
            return jsonify({
                "code": 1001,
                "message": "缺少必填参数: user_model_id, llm_factory, llm_name"
            }), 400

        # 获取用户模型详细信息
        user_model = GlobalLLMService.get_user_model_by_id(user_model_id)
        if not user_model:
            return jsonify({
                "code": 1004,
                "message": f"用户模型 {user_model_id} 不存在"
            }), 404

        # 创建全局模型
        global_model_data = {
            "fid": f"{llm_factory}_{llm_name}_global",
            "llm_factory": llm_factory,
            "llm_name": llm_name,
            "model_type": user_model.get('model_type', 'chat'),
            "api_key": user_model.get('api_key'),
            "api_base": user_model.get('api_base'),
            "max_tokens": user_model.get('max_tokens', 4096),
            "provider_config": user_model.get('provider_config'),
            "available": True,
            "status": "active",
            "tags": f"从用户模型升级: {user_model.get('user_name', 'unknown')}",
            "description": f"从用户 {user_model.get('user_name', 'unknown')} 的模型升级为全局模型",
            "total_usage_count": user_model.get('usage_count', 0),
            "active_users_count": 1,
            "created_by": "model_promotion",
            "create_time": int(time.time() * 1000),
            "create_date": datetime.now(),
            "update_time": int(time.time() * 1000),
            "update_date": datetime.now()
        }

        global_model_id = GlobalLLMService.create_model(global_model_data)

        # 创建使用统计记录
        GlobalLLMService.update_model_usage(
            user_id=user_model.get('user_id'),
            tenant_id=user_model.get('tenant_id'),
            global_llm_id=int(global_model_id),
            llm_factory=llm_factory,
            llm_name=llm_name,
            model_type=user_model.get('model_type', 'chat'),
            usage_increment=user_model.get('usage_count', 0),
            token_increment=user_model.get('token_usage', 0)
        )

        logger.info(f"User model promoted to global: {user_model_id} -> {global_model_id}")

        return jsonify({
            "code": 0,
            "data": {"global_model_id": global_model_id},
            "message": "模型升级为全局模型成功"
        })

    except Exception as e:
        logger.error(f"Failed to promote user model: {str(e)}")
        return jsonify({
            "code": 1005,
            "message": f"模型升级失败: {str(e)}"
        }), 500


@models_bp.route('/test', methods=['POST'])
def test_model_connection():
    """
    测试模型连接
    POST /v1/management/llm/test
    """
    try:
        data = request.get_json()

        llm_factory = data.get('llm_factory')
        model_type = data.get('model_type', 'chat')
        api_key = data.get('api_key')
        api_base = data.get('api_base')
        llm_name = data.get('llm_name')

        if not all([llm_factory, api_key]):
            return jsonify({
                "code": 1001,
                "message": "缺少必填参数: llm_factory, api_key"
            }), 400

        # 调用实际的模型测试逻辑
        test_result = GlobalLLMService.test_model_connection({
            "llm_factory": llm_factory,
            "llm_name": llm_name,
            "model_type": model_type,
            "api_key": api_key,
            "api_base": api_base
        })

        if test_result.get('success'):
            return jsonify({
                "code": 0,
                "data": test_result.get('data', {}),
                "message": "模型连接测试成功"
            })
        else:
            return jsonify({
                "code": 1006,
                "message": f"模型连接测试失败: {test_result.get('error', '未知错误')}"
            }), 400

    except Exception as e:
        logger.error(f"Failed to test model connection: {str(e)}")
        return jsonify({
            "code": 1005,
            "message": f"连接测试失败: {str(e)}"
        }), 500


@models_bp.route('/all_models', methods=['GET'])
def get_all_models_including_user():
    """
    获取所有模型（包括用户创建的和全局模型）
    GET /v1/management/llm/all_models
    """
    try:
        # 获取全局模型
        global_models = GlobalLLMService.get_all_active_models()

        # 获取用户创建的模型（从原始用户表获取）
        user_models = GlobalLLMService.get_all_user_models()

        # 合并数据并标记来源
        all_models = []

        # 添加全局模型
        for model in global_models:
            model['source'] = 'global'
            all_models.append(model)

        # 添加用户模型
        for model in user_models:
            model['source'] = 'user_web'
            all_models.append(model)

        return jsonify({
            "code": 0,
            "data": all_models,
            "message": "success"
        })

    except Exception as e:
        logger.error(f"Failed to get all models: {str(e)}")
        return jsonify({
            "code": 1005,
            "message": f"获取所有模型失败: {str(e)}"
        }), 500