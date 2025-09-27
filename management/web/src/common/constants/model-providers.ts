// 完整的模型供应商配置定义，基于原始React组件完全一致的字段分析
export interface ModelProviderConfig {
  key: string
  label: string
  fields: ModelField[]
  modelTypes?: string[]
  defaultModelType?: string
  defaultValues?: Record<string, any>
  defaultModelName?: string
}

export interface ModelField {
  name: string
  label: string
  type: 'input' | 'password' | 'select' | 'textarea' | 'number' | 'switch'
  required: boolean
  placeholder?: string
  options?: { label: string; value: string }[]
  min?: number
  max?: number
  step?: number
  rows?: number
  showWhen?: string // 条件显示，如 'model_type=chat'
  defaultValue?: any
}

// Azure OpenAI 配置
const azureOpenAIConfig: ModelProviderConfig = {
  key: 'azure_openai',
  label: 'Azure OpenAI',
  defaultModelType: 'embedding',
  modelTypes: ['chat', 'embedding', 'image2text'],
  defaultModelName: 'gpt-3.5-turbo',
  fields: [
    { name: 'model_type', label: '模型类型', type: 'select', required: true, placeholder: '请选择模型类型', options: [
      { label: 'chat', value: 'chat' },
      { label: 'embedding', value: 'embedding' },
      { label: 'image2text', value: 'image2text' }
    ]},
    { name: 'api_base', label: 'API Base URL', type: 'input', required: true, placeholder: '请输入API基础地址' },
    { name: 'api_key', label: 'API Key', type: 'password', required: false, placeholder: '请输入API Key' },
    { name: 'llm_name', label: '模型名称', type: 'input', required: true, placeholder: '请输入模型名称', defaultValue: 'gpt-3.5-turbo' },
    { name: 'api_version', label: 'API版本', type: 'input', required: false, placeholder: '如: 2024-02-01', defaultValue: '2024-02-01' },
    { name: 'max_tokens', label: '最大令牌数', type: 'number', required: true, placeholder: '请输入最大令牌数', min: 0 },
    { name: 'vision', label: '支持视觉', type: 'switch', required: false, showWhen: 'model_type=chat' }
  ]
}

// AWS Bedrock 配置
const bedrockConfig: ModelProviderConfig = {
  key: 'bedrock',
  label: 'AWS Bedrock',
  defaultModelType: 'chat',
  modelTypes: ['chat', 'embedding'],
  fields: [
    { name: 'model_type', label: '模型类型', type: 'select', required: true, placeholder: '请选择模型类型', options: [
      { label: 'chat', value: 'chat' },
      { label: 'embedding', value: 'embedding' }
    ]},
    { name: 'bedrock_ak', label: 'Bedrock Access Key', type: 'password', required: true, placeholder: '请输入AWS Access Key' },
    { name: 'bedrock_sk', label: 'Bedrock Secret Key', type: 'password', required: true, placeholder: '请输入AWS Secret Key' },
    {
      name: 'bedrock_region',
      label: '区域',
      type: 'select',
      required: true,
      placeholder: '请选择AWS区域',
      options: [
        { label: 'us-east-1', value: 'us-east-1' },
        { label: 'us-west-2', value: 'us-west-2' },
        { label: 'ap-southeast-1', value: 'ap-southeast-1' },
        { label: 'ap-northeast-1', value: 'ap-northeast-1' },
        { label: 'eu-central-1', value: 'eu-central-1' },
        { label: 'us-gov-west-1', value: 'us-gov-west-1' },
        { label: 'ap-southeast-2', value: 'ap-southeast-2' }
      ]
    },
    { name: 'llm_name', label: '模型名称', type: 'input', required: true, placeholder: '请输入模型名称' },
    { name: 'max_tokens', label: '最大令牌数', type: 'number', required: true, placeholder: '请输入最大令牌数', min: 0 }
  ]
}

// Google Cloud 配置
const googleConfig: ModelProviderConfig = {
  key: 'google',
  label: 'Google',
  defaultModelType: 'chat',
  modelTypes: ['chat'],
  fields: [
    { name: 'google_project_id', label: 'Google项目ID', type: 'input', required: true, placeholder: '请输入Google Cloud项目ID' },
    { name: 'google_region', label: 'Google区域', type: 'input', required: true, placeholder: '请输入Google Cloud区域' },
    { name: 'google_service_account_key', label: 'Google服务账户密钥', type: 'textarea', required: true, placeholder: '请输入Google Cloud服务账户JSON密钥', rows: 4 }
  ]
}

// 腾讯混元配置
const hunyuanConfig: ModelProviderConfig = {
  key: 'hunyuan',
  label: '腾讯混元',
  fields: [
    { name: 'hunyuan_sid', label: 'Hunyuan SID', type: 'password', required: true, placeholder: '请输入腾讯云Secret ID' },
    { name: 'hunyuan_sk', label: 'Hunyuan SK', type: 'password', required: true, placeholder: '请输入腾讯云Secret Key' }
  ]
}

// 讯飞星火配置
const sparkConfig: ModelProviderConfig = {
  key: 'spark',
  label: '讯飞星火',
  defaultModelType: 'chat',
  modelTypes: ['chat', 'tts'],
  fields: [
    { name: 'model_type', label: '模型类型', type: 'select', required: true, placeholder: '请选择模型类型', options: [
      { label: 'chat', value: 'chat' },
      { label: 'tts', value: 'tts' }
    ]},
    { name: 'spark_api_password', label: 'Spark API密码', type: 'password', required: true, placeholder: '请输入讯飞星火API密码', showWhen: 'model_type=chat' },
    { name: 'spark_app_id', label: 'Spark应用ID', type: 'input', required: true, placeholder: '请输入讯飞星火App ID', showWhen: 'model_type=tts' },
    { name: 'spark_api_secret', label: 'Spark API密钥', type: 'password', required: true, placeholder: '请输入讯飞星火API Secret', showWhen: 'model_type=tts' },
    { name: 'spark_api_key', label: 'Spark API Key', type: 'password', required: true, placeholder: '请输入讯飞星火API Key', showWhen: 'model_type=tts' },
    { name: 'llm_name', label: '模型名称', type: 'input', required: true, placeholder: '请输入模型名称' },
    { name: 'max_tokens', label: '最大令牌数', type: 'number', required: true, placeholder: '请输入最大令牌数', min: 0 }
  ]
}

// 火山引擎配置
const volcengineConfig: ModelProviderConfig = {
  key: 'volcengine',
  label: '火山引擎',
  defaultModelType: 'chat',
  modelTypes: ['chat', 'embedding'],
  fields: [
    { name: 'endpoint_id', label: '端点ID', type: 'input', required: true, placeholder: '请输入火山引擎端点ID' },
    { name: 'ark_api_key', label: 'Ark API密钥', type: 'password', required: true, placeholder: '请输入火山引擎Ark API密钥' }
  ]
}

// 百度一言配置
const yiyanConfig: ModelProviderConfig = {
  key: 'yiyan',
  label: '文心一言',
  defaultModelType: 'chat',
  modelTypes: ['chat', 'embedding', 'rerank'],
  fields: [
    { name: 'yiyan_ak', label: '一言Access Key', type: 'password', required: true, placeholder: '请输入百度一言Access Key' },
    { name: 'yiyan_sk', label: '一言Secret Key', type: 'password', required: true, placeholder: '请输入百度一言Secret Key' }
  ]
}

// 腾讯云语音配置
const tencentConfig: ModelProviderConfig = {
  key: 'Tencent',
  label: '腾讯云语音',
  defaultModelType: 'speech2text',
  modelTypes: ['speech2text'],
  defaultModelName: '16k_zh',
  fields: [
    { name: 'TencentCloud_sid', label: '腾讯云SID', type: 'password', required: true, placeholder: '请输入腾讯云Secret ID' },
    { name: 'TencentCloud_sk', label: '腾讯云SK', type: 'password', required: true, placeholder: '请输入腾讯云Secret Key' }
  ]
}

// Fish Audio配置
const fishAudioConfig: ModelProviderConfig = {
  key: 'fish-audio',
  label: 'Fish Audio',
  defaultModelType: 'tts',
  modelTypes: ['tts'],
  fields: [
    { name: 'fish_audio_ak', label: 'Fish Audio Access Key', type: 'password', required: true, placeholder: '请输入Fish Audio Access Key' },
    { name: 'fish_audio_refid', label: 'Fish Audio Reference ID', type: 'input', required: true, placeholder: '请输入Fish Audio Reference ID' }
  ]
}

// Ollama及其兼容供应商配置
const ollamaConfig: ModelProviderConfig = {
  key: 'ollama',
  label: 'Ollama',
  defaultModelType: 'embedding',
  modelTypes: ['chat', 'embedding', 'rerank', 'image2text'],
  fields: [
    { name: 'model_type', label: '模型类型', type: 'select', required: true, placeholder: '请选择模型类型', options: [
      { label: 'chat', value: 'chat' },
      { label: 'embedding', value: 'embedding' },
      { label: 'rerank', value: 'rerank' },
      { label: 'image2text', value: 'image2text' }
    ]},
    { name: 'api_base', label: 'API Base URL', type: 'input', required: true, placeholder: '请输入Ollama服务地址，如: http://localhost:11434' },
    { name: 'api_key', label: 'API Key', type: 'password', required: false, placeholder: '请输入API Key（可选）' },
    { name: 'llm_name', label: '模型名称', type: 'input', required: true, placeholder: '请输入模型名称' },
    { name: 'max_tokens', label: '最大令牌数', type: 'number', required: true, placeholder: '请输入最大令牌数', min: 0 },
    { name: 'vision', label: '支持视觉', type: 'switch', required: false, showWhen: 'model_type=chat' }
  ]
}

// HuggingFace配置
const huggingfaceConfig: ModelProviderConfig = {
  key: 'huggingface',
  label: 'HuggingFace',
  defaultModelType: 'embedding',
  modelTypes: ['embedding', 'chat', 'rerank'],
  fields: [
    { name: 'api_base', label: 'API Base URL', type: 'input', required: true, placeholder: '请输入HuggingFace服务地址' },
    { name: 'api_key', label: 'API Key', type: 'password', required: false, placeholder: '请输入API Key（可选）' }
  ]
}

// Xinference配置
const xinferenceConfig: ModelProviderConfig = {
  key: 'xinference',
  label: 'Xinference',
  defaultModelType: 'embedding',
  modelTypes: ['chat', 'embedding', 'rerank', 'image2text', 'speech2text', 'tts'],
  fields: [
    { name: 'api_base', label: 'API Base URL', type: 'input', required: true, placeholder: '请输入Xinference服务地址' },
    { name: 'api_key', label: 'API Key', type: 'password', required: false, placeholder: '请输入API Key（可选）' },
    { name: 'vision', label: '支持视觉', type: 'switch', required: false, showWhen: 'model_type=chat' }
  ]
}

// OpenAI配置
const openaiConfig: ModelProviderConfig = {
  key: 'openai',
  label: 'OpenAI',
  defaultModelType: 'chat',
  modelTypes: ['chat', 'embedding', 'image2text'],
  fields: [
    { name: 'model_type', label: '模型类型', type: 'select', required: true, placeholder: '请选择模型类型', options: [
      { label: 'chat', value: 'chat' },
      { label: 'embedding', value: 'embedding' },
      { label: 'image2text', value: 'image2text' }
    ]},
    { name: 'api_key', label: 'API Key', type: 'password', required: true, placeholder: '请输入OpenAI API Key' },
    { name: 'api_base', label: 'API Base URL', type: 'input', required: false, placeholder: 'API基础地址(可选)' },
    { name: 'llm_name', label: '模型名称', type: 'input', required: true, placeholder: '请输入模型名称' },
    { name: 'max_tokens', label: '最大令牌数', type: 'number', required: true, placeholder: '请输入最大令牌数', min: 0 },
    { name: 'organization', label: '组织ID', type: 'input', required: false, placeholder: '请输入OpenAI组织ID(可选)' }
  ]
}

// Anthropic配置
const anthropicConfig: ModelProviderConfig = {
  key: 'anthropic',
  label: 'Anthropic',
  defaultModelType: 'chat',
  modelTypes: ['chat'],
  fields: [
    { name: 'model_type', label: '模型类型', type: 'select', required: true, placeholder: '请选择模型类型', options: [
      { label: 'chat', value: 'chat' }
    ]},
    { name: 'api_key', label: 'API Key', type: 'password', required: true, placeholder: '请输入Anthropic API Key' },
    { name: 'api_base', label: 'API Base URL', type: 'input', required: false, placeholder: 'API基础地址(可选)' },
    { name: 'llm_name', label: '模型名称', type: 'input', required: true, placeholder: '请输入模型名称' },
    { name: 'max_tokens', label: '最大令牌数', type: 'number', required: true, placeholder: '请输入最大令牌数', min: 0 }
  ]
}

// 其他常用供应商
const moonshotConfig: ModelProviderConfig = {
  key: 'moonshot',
  label: '月之暗面',
  fields: [
    { name: 'api_key', label: 'API Key', type: 'password', required: true, placeholder: '请输入Moonshot API Key' },
    { name: 'api_base', label: 'API Base URL', type: 'input', required: false, placeholder: 'API基础地址(可选)' }
  ]
}

const zhipuConfig: ModelProviderConfig = {
  key: 'zhipu',
  label: '智谱AI',
  fields: [
    { name: 'api_key', label: 'API Key', type: 'password', required: true, placeholder: '请输入智谱AI API Key' }
  ]
}

const qwenConfig: ModelProviderConfig = {
  key: 'tongyi_qianwen',
  label: '通义千问',
  fields: [
    { name: 'api_key', label: 'API Key', type: 'password', required: true, placeholder: '请输入通义千问API Key' }
  ]
}

// 导出所有配置
export const MODEL_PROVIDERS: Record<string, ModelProviderConfig> = {
  azure_openai: azureOpenAIConfig,
  bedrock: bedrockConfig,
  google: googleConfig,
  hunyuan: hunyuanConfig,
  spark: sparkConfig,
  volcengine: volcengineConfig,
  yiyan: yiyanConfig,
  Tencent: tencentConfig,
  'fish-audio': fishAudioConfig,
  ollama: ollamaConfig,
  huggingface: huggingfaceConfig,
  xinference: xinferenceConfig,
  openai: openaiConfig,
  anthropic: anthropicConfig,
  moonshot: moonshotConfig,
  zhipu: zhipuConfig,
  tongyi_qianwen: qwenConfig
}

// 获取供应商配置
export function getProviderConfig(providerKey: string): ModelProviderConfig | undefined {
  return MODEL_PROVIDERS[providerKey]
}

// 获取供应商的默认表单数据
export function getProviderDefaultValues(providerKey: string): Record<string, any> {
  const config = getProviderConfig(providerKey)
  if (!config) return {}

  const defaults: Record<string, any> = {}

  // 设置默认模型名称
  if (config.defaultModelName) {
    defaults.llm_name = config.defaultModelName
  }

  // 设置字段默认值
  config.fields.forEach(field => {
    if (field.defaultValue !== undefined) {
      defaults[field.name] = field.defaultValue
    } else {
      switch (field.type) {
        case 'switch':
          defaults[field.name] = false
          break
        case 'number':
          defaults[field.name] = field.min || 0
          break
        default:
          defaults[field.name] = ''
      }
    }
  })

  if (config.defaultValues) {
    Object.assign(defaults, config.defaultValues)
  }

  return defaults
}