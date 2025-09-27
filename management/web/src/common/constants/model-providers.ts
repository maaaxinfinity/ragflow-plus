// 完整的模型供应商配置定义，基于原始React组件
export interface ModelProviderConfig {
  key: string
  label: string
  fields: ModelField[]
  modelTypes?: string[]
  defaultModelType?: string
  defaultValues?: Record<string, any>
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
}

// Azure OpenAI 配置
const azureOpenAIConfig: ModelProviderConfig = {
  key: 'azure_openai',
  label: 'Azure OpenAI',
  defaultModelType: 'embedding',
  fields: [
    { name: 'api_base', label: 'API Base URL', type: 'input', required: true, placeholder: '请输入API基础地址' },
    { name: 'api_key', label: 'API Key', type: 'password', required: false, placeholder: '请输入API Key' },
    { name: 'api_version', label: 'API版本', type: 'input', required: false, placeholder: '如: 2024-02-01' },
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
    { name: 'bedrock_ak', label: 'Access Key', type: 'password', required: true, placeholder: '请输入AWS Access Key' },
    { name: 'bedrock_sk', label: 'Secret Key', type: 'password', required: true, placeholder: '请输入AWS Secret Key' },
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
    }
  ]
}

// Google Cloud 配置
const googleConfig: ModelProviderConfig = {
  key: 'google',
  label: 'Google',
  defaultModelType: 'chat',
  modelTypes: ['chat'],
  fields: [
    { name: 'google_project_id', label: '项目ID', type: 'input', required: true, placeholder: '请输入Google Cloud项目ID' },
    { name: 'google_region', label: '区域', type: 'input', required: true, placeholder: '请输入Google Cloud区域' },
    { name: 'google_service_account_key', label: '服务账户密钥', type: 'textarea', required: false, placeholder: '请输入Google Cloud服务账户JSON密钥', rows: 4 }
  ]
}

// 腾讯混元配置
const hunyuanConfig: ModelProviderConfig = {
  key: 'hunyuan',
  label: '腾讯混元',
  defaultModelType: 'chat',
  fields: [
    { name: 'hunyuan_sid', label: 'Secret ID', type: 'password', required: true, placeholder: '请输入腾讯云Secret ID' },
    { name: 'hunyuan_sk', label: 'Secret Key', type: 'password', required: true, placeholder: '请输入腾讯云Secret Key' },
    { name: 'vision', label: '支持视觉', type: 'switch', required: false, showWhen: 'model_type=chat' }
  ]
}

// 讯飞星火配置
const sparkConfig: ModelProviderConfig = {
  key: 'spark',
  label: '讯飞星火',
  defaultModelType: 'chat',
  fields: [
    { name: 'spark_api_secret', label: 'API Secret', type: 'password', required: true, placeholder: '请输入讯飞星火API Secret' },
    { name: 'spark_app_id', label: 'App ID', type: 'input', required: true, placeholder: '请输入讯飞星火App ID' },
    { name: 'spark_api_key', label: 'API Key', type: 'password', required: true, placeholder: '请输入讯飞星火API Key' }
  ]
}

// 火山引擎配置
const volcengineConfig: ModelProviderConfig = {
  key: 'volcengine',
  label: '火山引擎',
  defaultModelType: 'chat',
  fields: [
    { name: 'volc_ak', label: 'Access Key', type: 'password', required: true, placeholder: '请输入火山引擎Access Key' },
    { name: 'volc_sk', label: 'Secret Key', type: 'password', required: true, placeholder: '请输入火山引擎Secret Key' }
  ]
}

// 月之暗面配置
const moonshotConfig: ModelProviderConfig = {
  key: 'moonshot',
  label: '月之暗面',
  defaultModelType: 'chat',
  fields: [
    { name: 'api_key', label: 'API Key', type: 'password', required: true, placeholder: '请输入Moonshot API Key' },
    { name: 'api_base', label: 'API Base URL', type: 'input', required: false, placeholder: 'API基础地址(可选)' }
  ]
}

// 智谱AI配置
const zhipuConfig: ModelProviderConfig = {
  key: 'zhipu',
  label: '智谱AI',
  defaultModelType: 'chat',
  fields: [
    { name: 'api_key', label: 'API Key', type: 'password', required: true, placeholder: '请输入智谱AI API Key' }
  ]
}

// 通义千问配置
const qwenConfig: ModelProviderConfig = {
  key: 'tongyi_qianwen',
  label: '通义千问',
  defaultModelType: 'chat',
  fields: [
    { name: 'api_key', label: 'API Key', type: 'password', required: true, placeholder: '请输入通义千问API Key' }
  ]
}

// 文心一言配置
const yiyanConfig: ModelProviderConfig = {
  key: 'wenxin',
  label: '文心一言',
  defaultModelType: 'chat',
  fields: [
    { name: 'yiyan_ak', label: 'Access Key', type: 'password', required: true, placeholder: '请输入文心一言Access Key' },
    { name: 'yiyan_sk', label: 'Secret Key', type: 'password', required: true, placeholder: '请输入文心一言Secret Key' }
  ]
}

// OpenAI配置
const openaiConfig: ModelProviderConfig = {
  key: 'openai',
  label: 'OpenAI',
  defaultModelType: 'chat',
  fields: [
    { name: 'api_key', label: 'API Key', type: 'password', required: true, placeholder: '请输入OpenAI API Key' },
    { name: 'api_base', label: 'API Base URL', type: 'input', required: false, placeholder: 'API基础地址(可选)' },
    { name: 'organization', label: '组织ID', type: 'input', required: false, placeholder: '请输入OpenAI组织ID(可选)' }
  ]
}

// Anthropic配置
const anthropicConfig: ModelProviderConfig = {
  key: 'anthropic',
  label: 'Anthropic',
  defaultModelType: 'chat',
  fields: [
    { name: 'api_key', label: 'API Key', type: 'password', required: true, placeholder: '请输入Anthropic API Key' },
    { name: 'api_base', label: 'API Base URL', type: 'input', required: false, placeholder: 'API基础地址(可选)' }
  ]
}

// Ollama配置
const ollamaConfig: ModelProviderConfig = {
  key: 'ollama',
  label: 'Ollama',
  defaultModelType: 'chat',
  fields: [
    { name: 'api_base', label: 'API Base URL', type: 'input', required: true, placeholder: '请输入Ollama服务地址，如: http://localhost:11434' }
  ]
}

// Fish Audio配置
const fishAudioConfig: ModelProviderConfig = {
  key: 'fish_audio',
  label: 'Fish Audio',
  defaultModelType: 'tts',
  fields: [
    { name: 'fish_audio_ak', label: 'Access Key', type: 'password', required: true, placeholder: '请输入Fish Audio Access Key' }
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
  moonshot: moonshotConfig,
  zhipu: zhipuConfig,
  tongyi_qianwen: qwenConfig,
  wenxin: yiyanConfig,
  openai: openaiConfig,
  anthropic: anthropicConfig,
  ollama: ollamaConfig,
  fish_audio: fishAudioConfig,
  // 可继续添加其他供应商...
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
  config.fields.forEach(field => {
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
  })

  if (config.defaultValues) {
    Object.assign(defaults, config.defaultValues)
  }

  return defaults
}