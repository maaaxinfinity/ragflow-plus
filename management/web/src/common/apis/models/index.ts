import type * as Models from "./type"
import { request } from "@/http/axios"

/** 获取所有用户的模型配置列表 */
export function getAllUserModelsApi() {
  return request<Models.AllUserModelsResponseData>({
    url: "api/v1/models/users",
    method: "get"
  })
}

/** 获取全局模型工厂列表 */
export function getModelFactoriesApi() {
  return request<Models.ModelFactoriesResponseData>({
    url: "api/v1/models/factories",
    method: "get"
  })
}

/** 获取用户的模型列表 */
export function getUserModelsApi(params: Models.GetUserModelsParams) {
  return request<Models.UserModelsResponseData>({
    url: `api/v1/models/users/${params.userId}`,
    method: "get"
  })
}

/** 为用户添加模型配置 */
export function addUserModelApi(params: Models.AddUserModelParams) {
  return request<Models.BaseResponseData>({
    url: "api/v1/models",
    method: "post",
    data: params
  })
}

/** 删除用户的模型配置 */
export function deleteUserModelApi(params: Models.DeleteUserModelParams) {
  return request<Models.BaseResponseData>({
    url: `api/v1/models/users/${params.user_id}/models/${params.llm_name}`,
    method: "delete",
    params: { llm_factory: params.llm_factory }
  })
}

/** 删除用户的整个模型工厂 */
export function deleteUserFactoryApi(params: Models.DeleteUserFactoryParams) {
  return request<Models.BaseResponseData>({
    url: `api/v1/models/users/${params.user_id}/factories/${params.llm_factory}`,
    method: "delete"
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