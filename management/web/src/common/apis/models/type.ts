// 基础响应接口
export interface BaseResponseData {
  code: number
  data?: any
  message?: string
}

// 全局模型配置数据结构 (管理员权限)
export interface GlobalLlmModel {
  id: number
  fid: string
  llm_factory: string
  llm_name: string
  model_type: string
  max_tokens: number
  api_key: string
  api_base?: string
  available: boolean
  status: string
  tags: string
  create_date: string
  create_time: number
  update_date: string
  update_time: number
  // 管理面板显示字段
  model_name?: string
  usage_count?: number
  total_users?: number // 使用此模型的用户数量
  is_global?: boolean // 是否为全局模型
}

// 用户模型使用统计
export interface UserModelUsage {
  user_id: string
  user_name: string
  tenant_id: string
  tenant_name: string
  llm_factory: string
  llm_name: string
  used_token: number
  last_used?: string
}

// 保留原有的LlmModel以兼容web端格式
export interface LlmModel {
  name: string
  type: string
  used_token: number
  available: boolean
  create_date: string
  create_time: number
  fid: string
  id: number
  llm_name: string
  max_tokens: number
  model_type: string
  status: string
  tags: string
  update_date: string
  update_time: number
  // 为管理面板显示添加的字段
  llm_factory?: string
  model_name?: string
  usage_count?: number
  user_name?: string
  tenant_name?: string
  api_key?: string
  api_base?: string
  last_used?: string
}

export interface MyLlmValue {
  llm: LlmModel[]
  tags: string
}

// my_llms接口返回的数据格式 Record<string, MyLlmValue>
export type MyLlmCollection = Record<string, MyLlmValue>

// 模型工厂数据
export interface ModelFactoryData {
  name: string
  tags: string
  description?: string
  supported_types: string[]
  available: boolean
}

// 模型数据
export interface ModelData {
  name: string
  type: string
  available: boolean
  fid: string
}

// LLM项目数据 (对应原有的LlmItem)
export interface LlmItemData {
  name: string
  tags: string
  llm: ModelData[]
}

// 全局默认模型配置
export interface GlobalDefaultModelsData {
  llm_id: string        // 默认聊天模型
  embd_id: string       // 默认嵌入模型
  asr_id: string        // 默认语音识别模型
  img2txt_id: string    // 默认图像识别模型
  update_time: string
}

// API请求参数接口
export interface GetUserModelsParams {
  userId: string
}

export interface AddUserModelParams {
  llm_factory: string
  llm_name: string
  model_type: string
  api_base?: string
  api_key: string
  max_tokens: number
  is_global?: boolean // 是否为全局模型（管理员权限）
  // 以下为各供应商特定字段，根据实际需要动态包含
  [key: string]: any
}

export interface DeleteUserModelParams {
  llm_factory: string
  llm_name: string
}

export interface DeleteUserFactoryParams {
  llm_factory: string
}

export interface SetGlobalDefaultModelsParams {
  llm_id: string
  embd_id: string
  asr_id: string
  img2txt_id: string
}

export interface SetUserApiKeyParams {
  user_id: string
  llm_factory: string
  api_key: string
  base_url?: string
}

// API响应数据接口
export interface AllUserModelsResponseData extends BaseResponseData {
  data: GlobalLlmModel[] | MyLlmCollection
}

export interface ModelFactoriesResponseData extends BaseResponseData {
  data: ModelFactoryData[]
}

export interface UserModelsResponseData extends BaseResponseData {
  data: {
    myLlmList: Record<string, LlmItemData>
    factoryList: ModelFactoryData[]
  }
}

export interface GlobalDefaultModelsResponseData extends BaseResponseData {
  data: GlobalDefaultModelsData
}

// 新增的API参数和响应类型

export interface TestModelConnectionParams {
  llm_factory: string
  llm_name?: string
  model_type?: string
  api_key: string
  api_base?: string
  [key: string]: any // 支持不同供应商的特定参数
}

export interface PromoteUserModelParams {
  user_model_id: string
  llm_factory: string
  llm_name: string
}