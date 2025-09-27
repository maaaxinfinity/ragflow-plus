// 基础响应接口
export interface BaseResponseData {
  code: number
  data?: any
  message?: string
}

// 用户模型配置数据
export interface UserModelData {
  id: string
  user_id: string
  user_name: string
  tenant_id: string
  tenant_name: string
  model_name: string
  model_type: string // chat, embedding, image2text, etc.
  llm_factory: string // OpenAI, Azure, etc.
  api_key: string
  api_base?: string
  max_tokens?: number
  last_used?: string
  usage_count: number
  create_time: string
  update_time: string
  available: boolean
}

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
  user_id: string
  llm_factory: string
  api_key: string
  llm_name?: string
  model_type?: string
  base_url?: string
}

export interface DeleteUserModelParams {
  user_id: string
  llm_factory: string
  llm_name: string
}

export interface DeleteUserFactoryParams {
  user_id: string
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
  data: UserModelData[]
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