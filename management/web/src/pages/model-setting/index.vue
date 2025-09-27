<script lang="ts" setup>
import { ref, reactive, onMounted, onActivated, watch } from 'vue'
import type { FormInstance } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { usePagination } from '@@/composables/usePagination'
import { Refresh, Search, Plus, Edit, Delete } from '@element-plus/icons-vue'

defineOptions({
  name: 'ModelSetting'
})

const loading = ref<boolean>(false)
const { paginationData, handleCurrentChange, handleSizeChange } = usePagination()

// 模型数据接口
interface ModelData {
  id: string
  name: string
  type: string // CHAT, EMBEDDING, TTS, etc.
  provider: string // OpenAI, Azure, etc.
  api_key: string
  api_base?: string
  model_name: string
  status: string
  create_time: string
  update_time: string
  // 扩展配置字段
  api_version?: string // Azure OpenAI API版本
  deployment_name?: string // Azure部署名称
  region?: string // AWS/Azure区域
  project_id?: string // Google Cloud项目ID
  endpoint?: string // 自定义端点
  temperature?: number // 温度参数
  max_tokens?: number // 最大令牌数
  timeout?: number // 请求超时时间
  organization?: string // OpenAI组织ID
  secret_key?: string // AWS Secret Key
  access_key?: string // AWS Access Key
}

// 表格数据
const tableData = ref<ModelData[]>([])
const searchFormRef = ref<FormInstance | null>(null)
const searchData = reactive({
  name: '',
  type: '',
  provider: ''
})

// 多选数据
const multipleSelection = ref<ModelData[]>([])

// 对话框控制
const dialogVisible = ref(false)
const dialogTitle = ref('添加模型')
const formRef = ref<FormInstance | null>(null)

// 表单数据
const DEFAULT_FORM_DATA: Partial<ModelData> = {
  name: '',
  type: 'CHAT',
  provider: '',
  api_key: '',
  api_base: '',
  model_name: '',
  status: 'active',
  api_version: '',
  deployment_name: '',
  region: '',
  project_id: '',
  endpoint: '',
  temperature: 0.7,
  max_tokens: 4096,
  timeout: 30000,
  organization: '',
  secret_key: '',
  access_key: ''
}
const formData = ref<Partial<ModelData>>({ ...DEFAULT_FORM_DATA })

// 模型类型选项
const modelTypes = [
  { label: '聊天模型', value: 'CHAT' },
  { label: '嵌入模型', value: 'EMBEDDING' },
  { label: '语音合成', value: 'TTS' },
  { label: '语音识别', value: 'ASR' },
  { label: '图像生成', value: 'IMAGE' }
]

// 模型供应商选项
const modelProviders = [
  { label: 'OpenAI', value: 'openai' },
  { label: 'Azure OpenAI', value: 'azure' },
  { label: 'Google', value: 'google' },
  { label: 'Anthropic', value: 'anthropic' },
  { label: 'Ollama', value: 'ollama' },
  { label: '通义千问', value: 'qwen' },
  { label: '文心一言', value: 'baidu' },
  { label: '智谱AI', value: 'zhipu' },
  { label: '百川', value: 'baichuan' },
  { label: '月之暗面', value: 'moonshot' },
  { label: 'DeepSeek', value: 'deepseek' },
  { label: 'AWS Bedrock', value: 'bedrock' },
  { label: 'Cohere', value: 'cohere' },
  { label: 'Hugging Face', value: 'huggingface' },
  { label: 'Replicate', value: 'replicate' },
  { label: 'Together AI', value: 'together' },
  { label: 'LM Studio', value: 'lmstudio' },
  { label: 'LocalAI', value: 'localai' },
  { label: 'Xinference', value: 'xinference' },
  { label: 'vLLM', value: 'vllm' },
  { label: '讯飞星火', value: 'spark' },
  { label: '腾讯混元', value: 'hunyuan' },
  { label: '火山引擎', value: 'volcengine' },
  { label: 'Fish Audio', value: 'fishaudio' },
  { label: 'OpenRouter', value: 'openrouter' },
  { label: 'Groq', value: 'groq' },
  { label: 'Mistral AI', value: 'mistral' },
  { label: 'Perplexity', value: 'perplexity' }
]

// 获取表格数据
function getTableData() {
  loading.value = true
  // 这里应该调用实际的API
  // 暂时使用模拟数据
  setTimeout(() => {
    tableData.value = [
      {
        id: '1',
        name: 'GPT-4',
        type: 'CHAT',
        provider: 'openai',
        api_key: 'sk-****',
        api_base: 'https://api.openai.com/v1',
        model_name: 'gpt-4-turbo-preview',
        status: 'active',
        create_time: '2024-01-01 10:00:00',
        update_time: '2024-01-01 10:00:00'
      },
      {
        id: '2',
        name: 'Text Embedding',
        type: 'EMBEDDING',
        provider: 'openai',
        api_key: 'sk-****',
        api_base: 'https://api.openai.com/v1',
        model_name: 'text-embedding-3-large',
        status: 'active',
        create_time: '2024-01-01 10:00:00',
        update_time: '2024-01-01 10:00:00'
      }
    ]
    paginationData.total = tableData.value.length
    loading.value = false
  }, 1000)
}

// 搜索
function handleSearch() {
  paginationData.currentPage === 1 ? getTableData() : (paginationData.currentPage = 1)
}

// 重置搜索
function resetSearch() {
  searchFormRef.value?.resetFields()
  handleSearch()
}

// 添加模型
function handleAdd() {
  dialogTitle.value = '添加模型'
  formData.value = { ...DEFAULT_FORM_DATA }
  dialogVisible.value = true
}

// 编辑模型
function handleEdit(row: ModelData) {
  dialogTitle.value = '编辑模型'
  formData.value = { ...row }
  dialogVisible.value = true
}

// 删除模型
function handleDelete(row: ModelData) {
  ElMessageBox.confirm(
    `确定要删除模型 "${row.name}" 吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 这里应该调用删除API
    ElMessage.success('删除成功')
    getTableData()
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 批量删除
function handleBatchDelete() {
  if (multipleSelection.value.length === 0) {
    ElMessage.warning('请先选择要删除的模型')
    return
  }

  ElMessageBox.confirm(
    `确定要删除选中的 ${multipleSelection.value.length} 个模型吗？`,
    '确认批量删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 这里应该调用批量删除API
    ElMessage.success('批量删除成功')
    getTableData()
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 提交表单
function submitForm() {
  formRef.value?.validate((valid) => {
    if (valid) {
      loading.value = true
      // 这里应该调用保存API
      setTimeout(() => {
        ElMessage.success(dialogTitle.value.includes('添加') ? '添加成功' : '编辑成功')
        dialogVisible.value = false
        getTableData()
        loading.value = false
      }, 1000)
    }
  })
}

// 取消操作
function handleCancel() {
  dialogVisible.value = false
  formRef.value?.resetFields()
}

// 测试连接
const testLoading = ref(false)
function testConnection() {
  formRef.value?.validate((valid) => {
    if (valid) {
      testLoading.value = true
      // 这里应该调用测试API连接的接口
      setTimeout(() => {
        ElMessage.success('模型连接测试成功！')
        testLoading.value = false
      }, 2000)
    } else {
      ElMessage.warning('请先填写必填字段')
    }
  })
}

// 表格多选
function handleSelectionChange(selection: ModelData[]) {
  multipleSelection.value = selection
}

// 获取供应商标签
function getProviderLabel(value: string) {
  const provider = modelProviders.find(p => p.value === value)
  return provider ? provider.label : value
}

// 获取类型标签
function getTypeLabel(value: string) {
  const type = modelTypes.find(t => t.value === value)
  return type ? type.label : value
}

// 表单验证规则
const formRules = {
  name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择模型类型', trigger: 'change' }],
  provider: [{ required: true, message: '请选择模型供应商', trigger: 'change' }],
  api_key: [{ required: true, message: '请输入API密钥', trigger: 'blur' }],
  model_name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }]
}

// 监听分页参数变化
watch([() => paginationData.currentPage, () => paginationData.pageSize], getTableData, { immediate: true })

onMounted(() => {
  getTableData()
})

onActivated(() => {
  getTableData()
})
</script>

<template>
  <div class="app-container">
    <!-- 搜索区域 -->
    <el-card v-loading="loading" shadow="never" class="search-wrapper">
      <el-form ref="searchFormRef" :inline="true" :model="searchData">
        <el-form-item prop="name" label="模型名称">
          <el-input v-model="searchData.name" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item prop="type" label="模型类型">
          <el-select v-model="searchData.type" placeholder="请选择模型类型" clearable>
            <el-option
              v-for="item in modelTypes"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item prop="provider" label="供应商">
          <el-select v-model="searchData.provider" placeholder="请选择供应商" clearable>
            <el-option
              v-for="item in modelProviders"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">
            查询
          </el-button>
          <el-button :icon="Refresh" @click="resetSearch">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 表格区域 -->
    <el-card v-loading="loading" shadow="never">
      <div class="toolbar-wrapper">
        <div>
          <el-button type="primary" :icon="Plus" @click="handleAdd">
            添加模型
          </el-button>
          <el-button type="danger" :icon="Delete" @click="handleBatchDelete">
            批量删除
          </el-button>
        </div>
      </div>

      <div class="table-wrapper">
        <el-table :data="tableData" @selection-change="handleSelectionChange">
          <el-table-column type="selection" width="50" align="center" />
          <el-table-column prop="name" label="模型名称" align="center" />
          <el-table-column prop="type" label="类型" align="center">
            <template #default="{ row }">
              <el-tag>{{ getTypeLabel(row.type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="provider" label="供应商" align="center">
            <template #default="{ row }">
              {{ getProviderLabel(row.provider) }}
            </template>
          </el-table-column>
          <el-table-column prop="model_name" label="模型标识" align="center" />
          <el-table-column prop="api_key" label="API密钥" align="center">
            <template #default="{ row }">
              <span>{{ row.api_key.replace(/.(?=.{4})/g, '*') }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
                {{ row.status === 'active' ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="update_time" label="更新时间" align="center" />
          <el-table-column fixed="right" label="操作" width="150" align="center">
            <template #default="{ row }">
              <el-button type="primary" text bg size="small" :icon="Edit" @click="handleEdit(row)">
                编辑
              </el-button>
              <el-button type="danger" text bg size="small" :icon="Delete" @click="handleDelete(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="pager-wrapper">
        <el-pagination
          background
          :layout="paginationData.layout"
          :page-sizes="paginationData.pageSizes"
          :total="paginationData.total"
          :page-size="paginationData.pageSize"
          :current-page="paginationData.currentPage"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="800px" max-height="80vh">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item label="模型类型" prop="type">
          <el-select v-model="formData.type" placeholder="请选择模型类型">
            <el-option
              v-for="item in modelTypes"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="供应商" prop="provider">
          <el-select v-model="formData.provider" placeholder="请选择供应商">
            <el-option
              v-for="item in modelProviders"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="API密钥" prop="api_key">
          <el-input v-model="formData.api_key" type="password" placeholder="请输入API密钥" show-password />
        </el-form-item>
        <el-form-item label="API地址" prop="api_base">
          <el-input v-model="formData.api_base" placeholder="请输入API基础地址（可选）" />
        </el-form-item>

        <!-- Azure OpenAI 专用字段 -->
        <template v-if="formData.provider === 'azure'">
          <el-form-item label="API版本" prop="api_version">
            <el-input v-model="formData.api_version" placeholder="例如: 2024-02-15-preview" />
          </el-form-item>
          <el-form-item label="部署名称" prop="deployment_name">
            <el-input v-model="formData.deployment_name" placeholder="请输入Azure部署名称" />
          </el-form-item>
        </template>

        <!-- AWS Bedrock 专用字段 -->
        <template v-if="formData.provider === 'bedrock'">
          <el-form-item label="Access Key" prop="access_key">
            <el-input v-model="formData.access_key" type="password" placeholder="请输入AWS Access Key" show-password />
          </el-form-item>
          <el-form-item label="Secret Key" prop="secret_key">
            <el-input v-model="formData.secret_key" type="password" placeholder="请输入AWS Secret Key" show-password />
          </el-form-item>
          <el-form-item label="区域" prop="region">
            <el-select v-model="formData.region" placeholder="请选择AWS区域">
              <el-option label="美国东部 (us-east-1)" value="us-east-1" />
              <el-option label="美国西部 (us-west-2)" value="us-west-2" />
              <el-option label="欧洲 (eu-west-1)" value="eu-west-1" />
              <el-option label="亚太地区 (ap-southeast-1)" value="ap-southeast-1" />
            </el-select>
          </el-form-item>
        </template>

        <!-- Google Cloud 专用字段 -->
        <template v-if="formData.provider === 'google'">
          <el-form-item label="项目ID" prop="project_id">
            <el-input v-model="formData.project_id" placeholder="请输入Google Cloud项目ID" />
          </el-form-item>
          <el-form-item label="区域" prop="region">
            <el-select v-model="formData.region" placeholder="请选择Google Cloud区域">
              <el-option label="美国中部 (us-central1)" value="us-central1" />
              <el-option label="美国东部 (us-east1)" value="us-east1" />
              <el-option label="欧洲西部 (europe-west1)" value="europe-west1" />
              <el-option label="亚洲东南部 (asia-southeast1)" value="asia-southeast1" />
            </el-select>
          </el-form-item>
        </template>

        <!-- OpenAI 专用字段 -->
        <template v-if="formData.provider === 'openai'">
          <el-form-item label="组织ID" prop="organization">
            <el-input v-model="formData.organization" placeholder="请输入OpenAI组织ID（可选）" />
          </el-form-item>
        </template>

        <!-- 自定义端点字段 -->
        <template v-if="formData.provider && ['localai', 'lmstudio', 'xinference', 'vllm', 'ollama'].includes(formData.provider)">
          <el-form-item label="自定义端点" prop="endpoint">
            <el-input v-model="formData.endpoint" placeholder="请输入自定义服务端点" />
          </el-form-item>
        </template>

        <el-form-item label="模型标识" prop="model_name">
          <el-input v-model="formData.model_name" placeholder="请输入模型标识" />
        </el-form-item>

        <!-- 高级配置 -->
        <el-form-item label="温度参数" prop="temperature">
          <el-input-number v-model="formData.temperature" :min="0" :max="2" :step="0.1" placeholder="0.7" />
        </el-form-item>
        <el-form-item label="最大令牌数" prop="max_tokens">
          <el-input-number v-model="formData.max_tokens" :min="1" :max="32768" :step="1" placeholder="4096" />
        </el-form-item>
        <el-form-item label="请求超时(ms)" prop="timeout">
          <el-input-number v-model="formData.timeout" :min="1000" :max="300000" :step="1000" placeholder="30000" />
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio value="active">启用</el-radio>
            <el-radio value="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <div style="text-align: left; margin-bottom: 10px;">
          <el-button type="info" @click="testConnection" :loading="testLoading">
            测试连接
          </el-button>
        </div>
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="loading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.search-wrapper {
  margin-bottom: 20px;
  :deep(.el-card__body) {
    padding-bottom: 2px;
  }
}

.toolbar-wrapper {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.table-wrapper {
  margin-bottom: 20px;
}

.pager-wrapper {
  display: flex;
  justify-content: flex-end;
}
</style>