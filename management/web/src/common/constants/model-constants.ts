// AWS Bedrock 区域列表
export const BedrockRegionList = [
  'us-east-1',
  'us-west-2',
  'ap-southeast-1',
  'ap-northeast-1',
  'eu-central-1',
  'us-gov-west-1',
  'ap-southeast-2',
];

// Google Cloud 区域列表
export const GoogleCloudRegionList = [
  'us-central1',
  'us-east1',
  'europe-west1',
  'asia-southeast1',
  'asia-northeast1',
];

// Azure OpenAI API 版本列表
export const AzureApiVersionList = [
  '2024-02-15-preview',
  '2023-12-01-preview',
  '2023-05-15',
  '2023-03-15-preview',
];

// 模型供应商专用字段配置
export const ProviderSpecificFields = {
  azure_openai: [
    { key: 'api_version', label: 'API版本', type: 'select', options: AzureApiVersionList, required: true },
    { key: 'deployment_name', label: '部署名称', type: 'input', required: true },
  ],
  bedrock: [
    { key: 'bedrock_ak', label: 'Access Key', type: 'password', required: true },
    { key: 'bedrock_sk', label: 'Secret Key', type: 'password', required: true },
    { key: 'bedrock_region', label: '区域', type: 'select', options: BedrockRegionList, required: true },
  ],
  google: [
    { key: 'project_id', label: '项目ID', type: 'input', required: true },
    { key: 'region', label: '区域', type: 'select', options: GoogleCloudRegionList, required: false },
  ],
  openai: [
    { key: 'organization', label: '组织ID', type: 'input', required: false },
  ],
  // 自定义端点供应商
  localai: [
    { key: 'endpoint', label: '自定义端点', type: 'input', required: true },
  ],
  lmstudio: [
    { key: 'endpoint', label: '自定义端点', type: 'input', required: true },
  ],
  xinference: [
    { key: 'endpoint', label: '自定义端点', type: 'input', required: true },
  ],
  vllm: [
    { key: 'endpoint', label: '自定义端点', type: 'input', required: true },
  ],
  ollama: [
    { key: 'endpoint', label: '自定义端点', type: 'input', required: true },
  ],
};

// 高级配置字段
export const AdvancedConfigFields = [
  { key: 'temperature', label: '温度参数', type: 'number', min: 0, max: 2, step: 0.1, default: 0.7 },
  { key: 'max_tokens', label: '最大令牌数', type: 'number', min: 1, max: 32768, step: 1, default: 4096 },
  { key: 'timeout', label: '请求超时(ms)', type: 'number', min: 1000, max: 300000, step: 1000, default: 30000 },
];