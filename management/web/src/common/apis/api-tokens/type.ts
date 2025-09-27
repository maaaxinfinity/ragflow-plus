// 基础响应接口
export interface BaseResponseData {
  code: number
  data?: any
  message?: string
}

// API Token数据
export interface ApiTokenData {
  id: string
  user_id: string
  user_name: string
  tenant_id: string
  tenant_name: string
  name: string
  token: string
  dialog_id?: string
  dialog_name?: string
  source: string // dialog, agent, none
  permissions: string[]
  status: string // active, inactive
  create_time: string
  update_time: string
  last_used_time?: string
  usage_count: number
}

// API请求参数接口
export interface GetUserApiTokensParams {
  userId: string
}

export interface CreateUserApiTokenParams {
  user_id: string
  name: string
  source: string
  dialog_id?: string
  permissions: string[]
  status?: string
}

export interface DeleteUserApiTokenParams {
  user_id: string
  token_id: string
}

export interface RegenerateUserApiTokenParams {
  user_id: string
  token_id: string
}

export interface UpdateUserApiTokenStatusParams {
  user_id: string
  token_id: string
  status: string
}

// API响应数据接口
export interface AllApiTokensResponseData extends BaseResponseData {
  data: ApiTokenData[]
}

export interface UserApiTokensResponseData extends BaseResponseData {
  data: ApiTokenData[]
}

export interface CreateApiTokenResponseData extends BaseResponseData {
  data: {
    token: string
    token_id: string
  }
}