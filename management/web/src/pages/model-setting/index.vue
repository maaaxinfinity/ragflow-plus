<script lang="ts" setup>
import { ref, reactive, onMounted, computed } from 'vue'
import type { FormInstance } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { usePagination } from '@/common/composables/usePagination'
import { Refresh, Search, View, User, Delete, Setting, Plus } from '@element-plus/icons-vue'
import {
  useAllUserModels,
  useModelFactories,
  useUserModels,
  useAddUserModel,
  useDeleteUserModel,
  useDeleteUserFactory,
  useSetUserApiKey,
  useGlobalDefaultModels
} from '@/common/composables/useModelManagement'
import {
  MODEL_PROVIDERS,
  getProviderConfig,
  getProviderDefaultValues,
  type ModelProviderConfig,
  type ModelField
} from '@/common/constants/model-providers'

defineOptions({
  name: 'ModelSetting'
})

const loading = ref<boolean>(false)
const { paginationData, handleCurrentChange, handleSizeChange } = usePagination()

// 使用管理员级别的hooks
const { userModels: allUserModels, fetchAllUserModels } = useAllUserModels()
const { factories: allFactories, fetchFactories } = useModelFactories()
const { addModel } = useAddUserModel()
const { deleteModel } = useDeleteUserModel()
const { deleteFactory } = useDeleteUserFactory()
const { setApiKey } = useSetUserApiKey()
const { defaults: globalDefaults, fetchDefaults, setDefaults } = useGlobalDefaultModels()

// 搜索表单
const searchFormRef = ref<FormInstance | null>(null)
const searchData = reactive({
  user_name: '',
  tenant_name: '',
  model_name: '',
  model_type: '',
  llm_factory: ''
})

// 多选数据
const multipleSelection = ref<any[]>([])

// 模型类型选项
const modelTypes = [
  { label: '聊天模型', value: 'chat' },
  { label: '嵌入模型', value: 'embedding' },
  { label: '图像生成', value: 'image2text' },
  { label: '语音合成', value: 'tts' },
  { label: '语音识别', value: 'asr' }
]

// 模型供应商选项
const modelProviders = [
  { label: 'OpenAI', value: 'openai' },
  { label: 'Azure OpenAI', value: 'azure_openai' },
  { label: 'Google', value: 'google' },
  { label: 'Anthropic', value: 'anthropic' },
  { label: 'Ollama', value: 'ollama' },
  { label: '通义千问', value: 'tongyi_qianwen' },
  { label: '文心一言', value: 'wenxin' },
  { label: '智谱AI', value: 'zhipu' },
  { label: '讯飞星火', value: 'spark' },
  { label: '腾讯混元', value: 'hunyuan' },
  { label: '月之暗面', value: 'moonshot' },
  { label: '百川', value: 'baichuan' },
  { label: 'DeepSeek', value: 'deepseek' },
  { label: 'AWS Bedrock', value: 'bedrock' },
  { label: '火山引擎', value: 'volc_engine' },
  { label: 'Fish Audio', value: 'fish_audio' }
]

// 状态选项
const statusOptions = [
  { label: '可用', value: true },
  { label: '不可用', value: false }
]

// 过滤后的表格数据
const filteredTableData = computed(() => {
  let filtered = allUserModels.value || []

  // 应用搜索过滤
  if (searchData.user_name) {
    filtered = filtered.filter(item =>
      item.user_name.toLowerCase().includes(searchData.user_name.toLowerCase())
    )
  }
  if (searchData.tenant_name) {
    filtered = filtered.filter(item =>
      item.tenant_name.toLowerCase().includes(searchData.tenant_name.toLowerCase())
    )
  }
  if (searchData.model_name) {
    filtered = filtered.filter(item =>
      item.model_name.toLowerCase().includes(searchData.model_name.toLowerCase())
    )
  }
  if (searchData.model_type) {
    filtered = filtered.filter(item => item.model_type === searchData.model_type)
  }
  if (searchData.llm_factory) {
    filtered = filtered.filter(item => item.llm_factory === searchData.llm_factory)
  }

  return filtered
})

// 分页后的表格数据
const paginatedTableData = computed(() => {
  const start = (paginationData.currentPage - 1) * paginationData.pageSize
  const end = start + paginationData.pageSize
  return filteredTableData.value.slice(start, end)
})

// 更新分页总数
const updatePaginationTotal = () => {
  paginationData.total = filteredTableData.value.length
}

// 对话框控制
const addModelDialogVisible = ref(false)
const globalDefaultsDialogVisible = ref(false)
const viewModelDialogVisible = ref(false)
const currentViewModel = ref<any>(null)

// 添加模型表单
const addModelFormRef = ref<FormInstance | null>(null)
const addModelForm = reactive<Record<string, any>>({
  // 基础字段
  user_id: '',
  user_name: '',
  llm_factory: '',
  api_key: '',
  api_base: '',
  llm_name: '',
  model_type: '',
  // 高级配置字段
  temperature: 0.7,
  max_tokens: 4096,
  timeout: 30000
})

// 获取当前选择供应商的配置
const currentProviderConfig = computed(() => {
  if (!addModelForm.llm_factory) return null
  return getProviderConfig(addModelForm.llm_factory)
})

// 获取当前供应商的字段列表
const currentProviderFields = computed(() => {
  return currentProviderConfig.value?.fields || []
})

// 监听供应商变化，重置和初始化相关字段
watch(() => addModelForm.llm_factory, (newProvider, oldProvider) => {
  if (newProvider !== oldProvider && newProvider) {
    // 清除旧供应商的字段
    if (oldProvider) {
      const oldConfig = getProviderConfig(oldProvider)
      oldConfig?.fields.forEach(field => {
        delete addModelForm[field.name]
      })
    }

    // 设置新供应商的默认值
    const defaultValues = getProviderDefaultValues(newProvider)
    Object.assign(addModelForm, defaultValues)

    // 设置默认模型类型
    const config = getProviderConfig(newProvider)
    if (config?.defaultModelType) {
      addModelForm.model_type = config.defaultModelType
    }
  }
})

// 检查字段显示条件
function checkFieldCondition(condition: string): boolean {
  const [field, value] = condition.split('=')
  return addModelForm[field] === value
}

// 全局默认模型表单
const globalDefaultsForm = reactive({
  llm_id: '',
  embd_id: '',
  asr_id: '',
  img2txt_id: ''
})

// 获取表格数据
async function getTableData() {
  loading.value = true
  try {
    await Promise.all([
      fetchAllUserModels(),
      fetchFactories(),
      fetchDefaults()
    ])
  } finally {
    loading.value = false
    updatePaginationTotal()
  }
}

// 搜索
function handleSearch() {
  paginationData.currentPage = 1
  updatePaginationTotal()
}

// 重置搜索
function resetSearch() {
  searchFormRef.value?.resetFields()
  handleSearch()
}

// 查看模型详情
function handleViewModel(row: any) {
  currentViewModel.value = row
  viewModelDialogVisible.value = true
}

// 删除模型配置
function handleDeleteModel(row: any) {
  ElMessageBox.confirm(
    `确定要删除用户 "${row.user_name}" 的模型配置 "${row.model_name}" 吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    const success = await deleteModel({
      user_id: row.user_id,
      llm_factory: row.llm_factory,
      llm_name: row.model_name
    })
    if (success) {
      getTableData()
    }
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 批量删除
function handleBatchDelete() {
  if (multipleSelection.value.length === 0) {
    ElMessage.warning('请先选择要删除的模型配置')
    return
  }

  ElMessageBox.confirm(
    `确定要删除选中的 ${multipleSelection.value.length} 个模型配置吗？`,
    '确认批量删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    const promises = multipleSelection.value.map(row =>
      deleteModel({
        user_id: row.user_id,
        llm_factory: row.llm_factory,
        llm_name: row.model_name
      })
    )
    await Promise.all(promises)
    getTableData()
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 添加模型
function handleAddModel() {
  addModelForm.user_id = ''
  addModelForm.user_name = ''
  addModelForm.llm_factory = ''
  addModelForm.api_key = ''
  addModelForm.base_url = ''
  addModelForm.model_type = ''
  addModelDialogVisible.value = true
}

// 提交添加模型
async function submitAddModel() {
  if (!addModelFormRef.value) return

  await addModelFormRef.value.validate(async (valid) => {
    if (valid) {
      // 处理vision字段逻辑（与原始modal一致）
      const modelType = addModelForm.model_type === 'chat' && addModelForm.vision
        ? 'image2text'
        : addModelForm.model_type

      // 构建基础提交数据
      const submitData: Record<string, any> = {
        user_id: addModelForm.user_id,
        llm_factory: addModelForm.llm_factory,
        llm_name: addModelForm.llm_name,
        model_type: modelType,
        max_tokens: addModelForm.max_tokens,
        // 高级配置
        temperature: addModelForm.temperature,
        timeout: addModelForm.timeout
      }

      // 动态添加供应商特定字段（排除vision字段）
      currentProviderFields.value.forEach(field => {
        if (field.name !== 'vision' && addModelForm[field.name] !== undefined && addModelForm[field.name] !== '') {
          submitData[field.name] = addModelForm[field.name]
        }
      })

      // 添加通用字段
      if (addModelForm.api_key) {
        submitData.api_key = addModelForm.api_key
      }
      if (addModelForm.api_base) {
        submitData.api_base = addModelForm.api_base
      }

      console.info('提交模型配置数据:', submitData)

      const success = await addModel(submitData)
      if (success) {
        addModelDialogVisible.value = false
        getTableData()
      }
    }
  })
}

// 显示全局默认设置
function showGlobalDefaults() {
  globalDefaultsForm.llm_id = globalDefaults.value.llm_id
  globalDefaultsForm.embd_id = globalDefaults.value.embd_id
  globalDefaultsForm.asr_id = globalDefaults.value.asr_id
  globalDefaultsForm.img2txt_id = globalDefaults.value.img2txt_id
  globalDefaultsDialogVisible.value = true
}

// 提交全局默认设置
async function submitGlobalDefaults() {
  const success = await setDefaults(globalDefaultsForm)
  if (success) {
    globalDefaultsDialogVisible.value = false
  }
}

// 测试连接
const testLoading = ref(false)
function testConnection() {
  addModelFormRef.value?.validate((valid) => {
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
function handleSelectionChange(selection: any[]) {
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

// 隐藏API密钥
function maskApiKey(apiKey: string) {
  if (!apiKey || apiKey.length <= 8) return apiKey
  return apiKey.substring(0, 8) + '****' + apiKey.substring(apiKey.length - 4)
}

// 表单验证规则
const addModelRules = computed(() => {
  const baseRules: Record<string, any> = {
    user_id: [{ required: true, message: '请输入用户ID', trigger: 'blur' }],
    llm_factory: [{ required: true, message: '请选择模型供应商', trigger: 'change' }],
    model_type: [{ required: true, message: '请选择模型类型', trigger: 'change' }],
    llm_name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
    max_tokens: [
      { required: true, message: '请输入最大令牌数', trigger: 'blur' },
      { type: 'number', min: 0, message: '最大令牌数不能小于0', trigger: 'blur' }
    ]
  }

  // 动态添加供应商特定字段的验证规则
  currentProviderFields.value.forEach(field => {
    if (field.required) {
      const trigger = field.type === 'select' ? 'change' : 'blur'
      baseRules[field.name] = [{
        required: true,
        message: `请${field.type === 'select' ? '选择' : '输入'}${field.label}`,
        trigger
      }]

      // 数字类型添加额外验证
      if (field.type === 'number') {
        baseRules[field.name].push({ type: 'number', min: field.min || 0 })
      }
    }
  })

  // 特殊处理：Azure OpenAI中API Key可选
  if (addModelForm.llm_factory === 'azure_openai') {
    baseRules.api_key = [{ required: false, message: '请输入API Key', trigger: 'blur' }]
  } else {
    baseRules.api_key = [{ required: true, message: '请输入API Key', trigger: 'blur' }]
  }

  return baseRules
})

onMounted(() => {
  getTableData()
})
</script>

<template>
  <div class="app-container">
    <!-- 页面标题 -->
    <el-card shadow="never" class="header-wrapper">
      <div class="header-content">
        <div class="header-left">
          <h2>模型设置管理</h2>
          <p>管理所有用户的AI模型供应商及其模型配置</p>
        </div>
        <div class="header-right">
          <el-space>
            <el-button type="primary" :icon="Plus" @click="handleAddModel">
              添加模型配置
            </el-button>
            <el-button type="success" :icon="Setting" @click="showGlobalDefaults">
              全局默认设置
            </el-button>
          </el-space>
        </div>
      </div>
    </el-card>

    <!-- 搜索区域 -->
    <el-card v-loading="loading" shadow="never" class="search-wrapper">
      <el-form ref="searchFormRef" :inline="true" :model="searchData">
        <el-form-item prop="user_name" label="用户名称">
          <el-input v-model="searchData.user_name" placeholder="请输入用户名称" />
        </el-form-item>
        <el-form-item prop="tenant_name" label="租户名称">
          <el-input v-model="searchData.tenant_name" placeholder="请输入租户名称" />
        </el-form-item>
        <el-form-item prop="model_name" label="模型名称">
          <el-input v-model="searchData.model_name" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item prop="model_type" label="模型类型">
          <el-select v-model="searchData.model_type" placeholder="请选择模型类型" clearable>
            <el-option
              v-for="item in modelTypes"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item prop="llm_factory" label="供应商">
          <el-select v-model="searchData.llm_factory" placeholder="请选择供应商" clearable>
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
          <el-button type="danger" :icon="Delete" @click="handleBatchDelete">
            批量删除
          </el-button>
        </div>
        <div class="total-info">
          共 {{ filteredTableData.length }} 条记录
        </div>
      </div>

      <div class="table-wrapper">
        <el-table :data="paginatedTableData" @selection-change="handleSelectionChange">
          <el-table-column type="selection" width="50" align="center" />
          <el-table-column prop="user_name" label="用户名称" align="center" width="120" />
          <el-table-column prop="tenant_name" label="租户名称" align="center" width="120" />
          <el-table-column prop="model_name" label="模型名称" align="center" width="150" />
          <el-table-column prop="model_type" label="类型" align="center" width="100">
            <template #default="{ row }">
              <el-tag>{{ getTypeLabel(row.model_type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="llm_factory" label="供应商" align="center" width="120">
            <template #default="{ row }">
              {{ getProviderLabel(row.llm_factory) }}
            </template>
          </el-table-column>
          <el-table-column prop="api_key" label="API密钥" align="center" width="120">
            <template #default="{ row }">
              <span>{{ maskApiKey(row.api_key) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="usage_count" label="使用次数" align="center" width="100" />
          <el-table-column prop="available" label="状态" align="center" width="80">
            <template #default="{ row }">
              <el-tag :type="row.available ? 'success' : 'danger'">
                {{ row.available ? '可用' : '不可用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="last_used" label="最后使用" align="center" width="150" />
          <el-table-column prop="create_time" label="创建时间" align="center" width="150" />
          <el-table-column fixed="right" label="操作" width="150" align="center">
            <template #default="{ row }">
              <el-button type="primary" text bg size="small" :icon="View" @click="handleViewModel(row)">
                查看
              </el-button>
              <el-button type="danger" text bg size="small" :icon="Delete" @click="handleDeleteModel(row)">
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

    <!-- 查看模型详情对话框 -->
    <el-dialog v-model="viewModelDialogVisible" title="模型配置详情" width="600px">
      <el-descriptions v-if="currentViewModel" :column="2" border>
        <el-descriptions-item label="用户名称">{{ currentViewModel.user_name }}</el-descriptions-item>
        <el-descriptions-item label="租户名称">{{ currentViewModel.tenant_name }}</el-descriptions-item>
        <el-descriptions-item label="模型名称">{{ currentViewModel.model_name }}</el-descriptions-item>
        <el-descriptions-item label="模型类型">{{ getTypeLabel(currentViewModel.model_type) }}</el-descriptions-item>
        <el-descriptions-item label="供应商">{{ getProviderLabel(currentViewModel.llm_factory) }}</el-descriptions-item>
        <el-descriptions-item label="API密钥">{{ maskApiKey(currentViewModel.api_key) }}</el-descriptions-item>
        <el-descriptions-item label="API基址" span="2">{{ currentViewModel.api_base || '默认' }}</el-descriptions-item>
        <el-descriptions-item label="最大令牌数">{{ currentViewModel.max_tokens || '默认' }}</el-descriptions-item>
        <el-descriptions-item label="使用次数">{{ currentViewModel.usage_count }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentViewModel.available ? 'success' : 'danger'">
            {{ currentViewModel.available ? '可用' : '不可用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="最后使用">{{ currentViewModel.last_used || '从未使用' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ currentViewModel.create_time }}</el-descriptions-item>
        <el-descriptions-item label="更新时间" span="2">{{ currentViewModel.update_time }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="viewModelDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 添加模型配置对话框 -->
    <el-dialog v-model="addModelDialogVisible" title="添加模型配置" width="800px" max-height="80vh">
      <el-form ref="addModelFormRef" :model="addModelForm" :rules="addModelRules" label-width="120px">
        <el-form-item label="用户ID" prop="user_id">
          <el-input v-model="addModelForm.user_id" placeholder="请输入用户ID" />
        </el-form-item>

        <el-form-item label="供应商" prop="llm_factory">
          <el-select v-model="addModelForm.llm_factory" placeholder="请选择模型供应商" style="width: 100%">
            <el-option
              v-for="item in modelProviders"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="模型类型" prop="model_type">
          <el-select v-model="addModelForm.model_type" placeholder="请选择模型类型" style="width: 100%">
            <el-option
              v-for="item in modelTypes"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="模型名称" prop="llm_name">
          <el-input v-model="addModelForm.llm_name" placeholder="请输入模型名称，如: gpt-4, text-embedding-3-large" />
        </el-form-item>

        <el-form-item label="API Base URL" prop="api_base">
          <el-input v-model="addModelForm.api_base" placeholder="请输入API基础地址" />
        </el-form-item>

        <el-form-item label="API Key" prop="api_key">
          <el-input v-model="addModelForm.api_key" type="password" placeholder="请输入API Key" show-password />
        </el-form-item>

        <!-- 动态供应商专用字段 -->
        <template v-for="field in currentProviderFields" :key="field.name">
          <!-- 条件显示字段 -->
          <el-form-item
            v-if="!field.showWhen || checkFieldCondition(field.showWhen)"
            :label="field.label"
            :prop="field.name"
          >
            <!-- 文本输入 -->
            <el-input
              v-if="field.type === 'input'"
              v-model="addModelForm[field.name]"
              :placeholder="field.placeholder"
            />

            <!-- 密码输入 -->
            <el-input
              v-else-if="field.type === 'password'"
              v-model="addModelForm[field.name]"
              type="password"
              show-password
              :placeholder="field.placeholder"
            />

            <!-- 多行文本 -->
            <el-input
              v-else-if="field.type === 'textarea'"
              v-model="addModelForm[field.name]"
              type="textarea"
              :rows="field.rows || 3"
              :placeholder="field.placeholder"
            />

            <!-- 数字输入 -->
            <el-input-number
              v-else-if="field.type === 'number'"
              v-model="addModelForm[field.name]"
              :min="field.min"
              :max="field.max"
              :step="field.step"
              :placeholder="field.placeholder"
              style="width: 100%"
            />

            <!-- 选择器 -->
            <el-select
              v-else-if="field.type === 'select'"
              v-model="addModelForm[field.name]"
              :placeholder="field.placeholder"
              style="width: 100%"
            >
              <el-option
                v-for="option in field.options"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>

            <!-- 开关 -->
            <div v-else-if="field.type === 'switch'">
              <el-switch v-model="addModelForm[field.name]" />
              <div v-if="field.name === 'vision'" style="font-size: 12px; color: #666; margin-top: 4px;">
                启用后可处理图像输入（模型类型将自动设置为image2text）
              </div>
            </div>
          </el-form-item>
        </template>

        <!-- 高级配置 -->
        <el-divider content-position="left">高级配置</el-divider>

        <el-form-item label="温度参数" prop="temperature">
          <el-input-number
            v-model="addModelForm.temperature"
            :min="0"
            :max="2"
            :step="0.1"
            :precision="1"
            placeholder="0.7"
            style="width: 100%"
          />
          <div style="font-size: 12px; color: #666;">控制输出的随机性，0表示确定性输出，2表示最高随机性</div>
        </el-form-item>

        <el-form-item label="最大令牌数" prop="max_tokens">
          <el-input-number
            v-model="addModelForm.max_tokens"
            :min="1"
            :max="32768"
            :step="1"
            placeholder="4096"
            style="width: 100%"
          />
          <div style="font-size: 12px; color: #666;">生成响应的最大令牌数</div>
        </el-form-item>

        <el-form-item label="请求超时(ms)" prop="timeout">
          <el-input-number
            v-model="addModelForm.timeout"
            :min="1000"
            :max="300000"
            :step="1000"
            placeholder="30000"
            style="width: 100%"
          />
          <div style="font-size: 12px; color: #666;">API请求的超时时间，单位毫秒</div>
        </el-form-item>
      </el-form>

      <template #footer>
        <div style="text-align: left; margin-bottom: 10px;">
          <el-button type="info" @click="testConnection" :loading="testLoading">
            测试连接
          </el-button>
        </div>
        <el-button @click="addModelDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAddModel" :loading="loading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 全局默认模型设置对话框 -->
    <el-dialog v-model="globalDefaultsDialogVisible" title="全局默认模型设置" width="600px">
      <el-form :model="globalDefaultsForm" label-width="120px">
        <el-form-item label="默认聊天模型">
          <el-input v-model="globalDefaultsForm.llm_id" placeholder="请输入默认聊天模型ID" />
        </el-form-item>
        <el-form-item label="默认嵌入模型">
          <el-input v-model="globalDefaultsForm.embd_id" placeholder="请输入默认嵌入模型ID" />
        </el-form-item>
        <el-form-item label="默认语音识别模型">
          <el-input v-model="globalDefaultsForm.asr_id" placeholder="请输入默认语音识别模型ID" />
        </el-form-item>
        <el-form-item label="默认图像识别模型">
          <el-input v-model="globalDefaultsForm.img2txt_id" placeholder="请输入默认图像识别模型ID" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="globalDefaultsDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitGlobalDefaults">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.header-wrapper {
  margin-bottom: 20px;

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .header-left {
      h2 {
        margin: 0 0 8px 0;
        font-size: 24px;
        font-weight: 600;
      }

      p {
        margin: 0;
        color: #666;
        font-size: 14px;
      }
    }
  }
}

.search-wrapper {
  margin-bottom: 20px;
  :deep(.el-card__body) {
    padding-bottom: 2px;
  }
}

.toolbar-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  .total-info {
    color: #666;
    font-size: 14px;
  }
}

.table-wrapper {
  margin-bottom: 20px;
}

.pager-wrapper {
  display: flex;
  justify-content: flex-end;
}
</style>