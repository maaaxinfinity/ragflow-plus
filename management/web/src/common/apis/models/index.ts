import type * as Models from "./type"
import { request } from "@/http/axios"

/** 获取所有全局模型配置列表 (管理员权限，无用户鉴权) */
export function getAllUserModelsApi() {
  return request<Models.AllUserModelsResponseData>({
    url: "/v1/management/llm/list",
    method: "get"
  })
}

/** 获取全局模型工厂列表 (管理员权限) */
export function getModelFactoriesApi() {
  return request<Models.ModelFactoriesResponseData>({
    url: "/v1/llm/factories",
    method: "get"
  })
}

/** 获取用户的模型列表 */
export function getUserModelsApi(params: Models.GetUserModelsParams) {
  return request<Models.UserModelsResponseData>({
    url: "/v1/management/llm/user_models",
    method: "get",
    params: { user_id: params.userId }
  })
}

/** 为全局添加模型配置 (管理员权限，统一下发给所有用户) */
export function addUserModelApi(params: Models.AddUserModelParams) {
  return request<Models.BaseResponseData>({
    url: "/v1/management/llm/add",
    method: "post",
    data: params
  })
}

/** 删除全局模型配置 (管理员权限) */
export function deleteUserModelApi(params: Models.DeleteUserModelParams) {
  return request<Models.BaseResponseData>({
    url: "/v1/management/llm/delete",
    method: "post",
    data: params
  })
}

/** 删除整个全局模型工厂 (管理员权限) */
export function deleteUserFactoryApi(params: Models.DeleteUserFactoryParams) {
  return request<Models.BaseResponseData>({
    url: "/v1/management/llm/delete_factory",
    method: "post",
    data: { llm_factory: params.llm_factory }
  })
}

/** 设置全局默认模型 */
export function setGlobalDefaultModelsApi(params: Models.SetGlobalDefaultModelsParams) {
  return request<Models.BaseResponseData>({
    url: "api/v1/models/defaults",
    method: "put",
    data: params
  })
}

/** 获取全局默认模型配置 */
export function getGlobalDefaultModelsApi() {
  return request<Models.GlobalDefaultModelsResponseData>({
    url: "api/v1/models/defaults",
    method: "get"
  })
}

/** 为用户设置API Key */
export function setUserApiKeyApi(params: Models.SetUserApiKeyParams) {
  return request<Models.BaseResponseData>({
    url: `api/v1/models/users/${params.user_id}/api-key`,
    method: "put",
    data: params
  })
}

/** 获取所有用户的模型使用统计 (管理员权限) */
export function getUserModelUsageApi() {
  return request<Models.BaseResponseData>({
    url: "/v1/management/llm/usage_stats",
    method: "get"
  })
}

/** 获取指定模型的用户使用情况 */
export function getModelUserStatsApi(params: { llm_factory: string, llm_name: string }) {
  return request<Models.BaseResponseData>({
    url: "/v1/management/llm/model_users",
    method: "get",
    params
  })
}

/** 获取所有模型（包括用户创建的和全局模型） */
export function getAllModelsIncludingUserApi() {
  return request<Models.BaseResponseData>({
    url: "/v1/management/llm/all_models",
    method: "get"
  })
}

/** 测试模型连接 */
export function testModelConnectionApi(params: Models.TestModelConnectionParams) {
  return request<Models.BaseResponseData>({
    url: "/v1/management/llm/test",
    method: "post",
    data: params
  })
}

/** 将用户模型升级为全局模型 */
export function promoteUserModelToGlobalApi(params: Models.PromoteUserModelParams) {
  return request<Models.BaseResponseData>({
    url: "/v1/management/llm/promote",
    method: "post",
    data: params
  })
}