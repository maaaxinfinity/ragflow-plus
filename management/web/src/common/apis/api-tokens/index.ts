import type * as ApiTokens from "./type"
import { request } from "@/http/axios"

/** 获取所有用户的API Token列表 */
export function getAllApiTokensApi() {
  return request<ApiTokens.AllApiTokensResponseData>({
    url: "api/v1/api-tokens",
    method: "get"
  })
}

/** 获取用户的API Token列表 */
export function getUserApiTokensApi(params: ApiTokens.GetUserApiTokensParams) {
  return request<ApiTokens.UserApiTokensResponseData>({
    url: `api/v1/api-tokens/users/${params.userId}`,
    method: "get"
  })
}

/** 为用户创建API Token */
export function createUserApiTokenApi(params: ApiTokens.CreateUserApiTokenParams) {
  return request<ApiTokens.CreateApiTokenResponseData>({
    url: "api/v1/api-tokens",
    method: "post",
    data: params
  })
}

/** 删除用户的API Token */
export function deleteUserApiTokenApi(params: ApiTokens.DeleteUserApiTokenParams) {
  return request<ApiTokens.BaseResponseData>({
    url: `api/v1/api-tokens/${params.token_id}`,
    method: "delete",
    params: { user_id: params.user_id }
  })
}

/** 重新生成用户的API Token */
export function regenerateUserApiTokenApi(params: ApiTokens.RegenerateUserApiTokenParams) {
  return request<ApiTokens.CreateApiTokenResponseData>({
    url: `api/v1/api-tokens/${params.token_id}/regenerate`,
    method: "post",
    data: { user_id: params.user_id }
  })
}

/** 更新用户的API Token状态 */
export function updateUserApiTokenStatusApi(params: ApiTokens.UpdateUserApiTokenStatusParams) {
  return request<ApiTokens.BaseResponseData>({
    url: `api/v1/api-tokens/${params.token_id}/status`,
    method: "patch",
    data: { user_id: params.user_id, status: params.status }
  })
}