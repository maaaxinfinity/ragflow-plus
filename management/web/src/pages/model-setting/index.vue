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
const addModelForm = reactive({
  user_id: '',
  user_name: '',
  llm_factory: '',
  api_key: '',
  base_url: '',
  model_type: ''
})

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
      const success = await addModel({
        user_id: addModelForm.user_id,
        llm_factory: addModelForm.llm_factory,
        api_key: addModelForm.api_key,
        base_url: addModelForm.base_url,
        model_type: addModelForm.model_type
      })
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
const addModelRules = {
  user_id: [{ required: true, message: '请输入用户ID', trigger: 'blur' }],
  llm_factory: [{ required: true, message: '请选择模型供应商', trigger: 'change' }],
  api_key: [{ required: true, message: '请输入API Key', trigger: 'blur' }]
}

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
    <el-dialog v-model="addModelDialogVisible" title="添加模型配置" width="500px">
      <el-form ref="addModelFormRef" :model="addModelForm" :rules="addModelRules" label-width="100px">
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
        <el-form-item label="API Key" prop="api_key">
          <el-input v-model="addModelForm.api_key" type="password" placeholder="请输入API Key" />
        </el-form-item>
        <el-form-item label="Base URL">
          <el-input v-model="addModelForm.base_url" placeholder="可选，默认使用官方API地址" />
        </el-form-item>
        <el-form-item label="模型类型">
          <el-select v-model="addModelForm.model_type" placeholder="请选择模型类型" style="width: 100%">
            <el-option
              v-for="item in modelTypes"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addModelDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAddModel">确定</el-button>
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