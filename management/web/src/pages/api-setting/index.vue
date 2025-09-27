<script lang="ts" setup>
import { ref, reactive, onMounted, computed } from 'vue'
import type { FormInstance } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { usePagination } from '@/common/composables/usePagination'
import { Refresh, Search, Plus, Edit, Delete, Key, View, CopyDocument } from '@element-plus/icons-vue'
import {
  useAllApiTokens,
  useCreateApiToken,
  useDeleteApiToken,
  useRegenerateApiToken,
  useUpdateApiTokenStatus
} from '@/common/composables/useApiTokenManagement'

defineOptions({
  name: 'ApiSetting'
})

const loading = ref<boolean>(false)
const { paginationData, handleCurrentChange, handleSizeChange } = usePagination()

// 使用管理员级别的hooks
const { apiTokens: allApiTokens, fetchAllApiTokens } = useAllApiTokens()
const { createToken } = useCreateApiToken()
const { deleteToken } = useDeleteApiToken()
const { regenerateToken } = useRegenerateApiToken()
const { updateStatus } = useUpdateApiTokenStatus()

// 搜索表单
const searchFormRef = ref<FormInstance | null>(null)
const searchData = reactive({
  user_name: '',
  tenant_name: '',
  name: '',
  source: '',
  status: ''
})

// 多选数据
const multipleSelection = ref<any[]>([])

// 来源选项
const sourceOptions = [
  { label: '通用Token', value: 'none' },
  { label: '对话绑定', value: 'dialog' },
  { label: 'Agent绑定', value: 'agent' }
]

// 权限选项
const permissionOptions = [
  { label: '读取', value: 'read' },
  { label: '写入', value: 'write' },
  { label: '删除', value: 'delete' },
  { label: '管理', value: 'admin' }
]

// 状态选项
const statusOptions = [
  { label: '启用', value: 'active' },
  { label: '禁用', value: 'inactive' }
]

// 过滤后的表格数据
const filteredTableData = computed(() => {
  let filtered = allApiTokens.value || []

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
  if (searchData.name) {
    filtered = filtered.filter(item =>
      item.name.toLowerCase().includes(searchData.name.toLowerCase())
    )
  }
  if (searchData.source) {
    filtered = filtered.filter(item => item.source === searchData.source)
  }
  if (searchData.status) {
    filtered = filtered.filter(item => item.status === searchData.status)
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
const createTokenDialogVisible = ref(false)
const viewTokenDialogVisible = ref(false)
const currentToken = ref('')
const currentTokenData = ref<any>(null)

// 创建Token表单
const createTokenFormRef = ref<FormInstance | null>(null)
const createTokenForm = reactive({
  user_id: '',
  name: '',
  source: 'none',
  dialog_id: '',
  permissions: ['read'],
  status: 'active'
})

// 获取表格数据
async function getTableData() {
  loading.value = true
  try {
    await fetchAllApiTokens()
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

// 创建Token
function handleAdd() {
  createTokenForm.user_id = ''
  createTokenForm.name = ''
  createTokenForm.source = 'none'
  createTokenForm.dialog_id = ''
  createTokenForm.permissions = ['read']
  createTokenForm.status = 'active'
  createTokenDialogVisible.value = true
}

// 编辑Token (这里简单实现为查看详情)
function handleEdit(row: any) {
  handleViewToken(row)
}

// 查看Token
function handleViewToken(row: any) {
  currentTokenData.value = row
  currentToken.value = row.token
  viewTokenDialogVisible.value = true
}

// 复制Token
function handleCopyToken(token: string) {
  navigator.clipboard.writeText(token).then(() => {
    ElMessage.success('Token已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败，请手动复制')
  })
}

// 重新生成Token
function handleRegenerateToken(row: any) {
  ElMessageBox.confirm(
    `确定要重新生成Token "${row.name}" 吗？原Token将失效。`,
    '确认重新生成',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    const result = await regenerateToken({
      user_id: row.user_id,
      token_id: row.id
    })
    if (result) {
      currentToken.value = result.token
      viewTokenDialogVisible.value = true
      getTableData()
    }
  }).catch(() => {
    ElMessage.info('已取消重新生成')
  })
}

// 切换Token状态
async function handleToggleStatus(row: any) {
  const newStatus = row.status === 'active' ? 'inactive' : 'active'
  const success = await updateStatus({
    user_id: row.user_id,
    token_id: row.id,
    status: newStatus
  })
  if (success) {
    getTableData()
  }
}

// 删除Token
function handleDelete(row: any) {
  ElMessageBox.confirm(
    `确定要删除Token "${row.name}" 吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    const success = await deleteToken({
      user_id: row.user_id,
      token_id: row.id
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
    ElMessage.warning('请先选择要删除的Token')
    return
  }

  ElMessageBox.confirm(
    `确定要删除选中的 ${multipleSelection.value.length} 个Token吗？`,
    '确认批量删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    const promises = multipleSelection.value.map(row =>
      deleteToken({
        user_id: row.user_id,
        token_id: row.id
      })
    )
    await Promise.all(promises)
    getTableData()
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 提交创建Token
async function submitCreateToken() {
  if (!createTokenFormRef.value) return

  await createTokenFormRef.value.validate(async (valid) => {
    if (valid) {
      const result = await createToken(createTokenForm)
      if (result) {
        createTokenDialogVisible.value = false
        // 显示新Token
        currentToken.value = result.token
        viewTokenDialogVisible.value = true
        getTableData()
      }
    }
  })
}

// 表格多选
function handleSelectionChange(selection: any[]) {
  multipleSelection.value = selection
}

// 获取来源标签
function getSourceLabel(value: string) {
  const source = sourceOptions.find(s => s.value === value)
  return source ? source.label : value
}

// 获取权限标签
function getPermissionLabels(permissions: string[]) {
  return permissions.map(p => {
    const permission = permissionOptions.find(opt => opt.value === p)
    return permission ? permission.label : p
  }).join('、')
}

// 隐藏Token
function maskToken(token: string) {
  if (token.length <= 8) return token
  return token.substring(0, 8) + '...' + token.substring(token.length - 4)
}

// 表单验证规则
const createTokenRules = {
  user_id: [{ required: true, message: '请输入用户ID', trigger: 'blur' }],
  name: [{ required: true, message: '请输入Token名称', trigger: 'blur' }],
  source: [{ required: true, message: '请选择Token来源', trigger: 'change' }],
  permissions: [{ required: true, message: '请选择权限', trigger: 'change' }]
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
          <h2>API设置管理</h2>
          <p>管理所有用户的RAGFlow API密钥和配置</p>
        </div>
        <div class="header-right">
          <el-button type="primary" :icon="Plus" @click="handleAdd">
            创建API Token
          </el-button>
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
        <el-form-item prop="name" label="Token名称">
          <el-input v-model="searchData.name" placeholder="请输入Token名称" />
        </el-form-item>
        <el-form-item prop="source" label="来源">
          <el-select v-model="searchData.source" placeholder="请选择来源" clearable>
            <el-option
              v-for="item in sourceOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item prop="status" label="状态">
          <el-select v-model="searchData.status" placeholder="请选择状态" clearable>
            <el-option
              v-for="item in statusOptions"
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
          <el-table-column prop="name" label="Token名称" align="center" width="150" />
          <el-table-column prop="token" label="Token" align="center" min-width="200">
            <template #default="{ row }">
              <el-tooltip :content="row.token" placement="top">
                <span class="token-display">{{ maskToken(row.token) }}</span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column prop="source" label="来源" align="center" width="100">
            <template #default="{ row }">
              <el-tag>{{ getSourceLabel(row.source) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="dialog_name" label="绑定对象" align="center" width="120">
            <template #default="{ row }">
              <span v-if="row.dialog_name">{{ row.dialog_name }}</span>
              <span v-else class="text-gray">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="permissions" label="权限" align="center" width="120">
            <template #default="{ row }">
              {{ getPermissionLabels(row.permissions) }}
            </template>
          </el-table-column>
          <el-table-column prop="usage_count" label="使用次数" align="center" width="100" />
          <el-table-column prop="status" label="状态" align="center" width="80">
            <template #default="{ row }">
              <el-switch
                v-model="row.status"
                active-value="active"
                inactive-value="inactive"
                @change="handleToggleStatus(row)"
              />
            </template>
          </el-table-column>
          <el-table-column prop="last_used_time" label="最后使用" align="center" width="150">
            <template #default="{ row }">
              <span v-if="row.last_used_time">{{ row.last_used_time }}</span>
              <span v-else class="text-gray">未使用</span>
            </template>
          </el-table-column>
          <el-table-column prop="create_time" label="创建时间" align="center" width="150" />
          <el-table-column fixed="right" label="操作" width="250" align="center">
            <template #default="{ row }">
              <el-button type="primary" text bg size="small" :icon="View" @click="handleViewToken(row)">
                查看
              </el-button>
              <el-button type="warning" text bg size="small" :icon="Key" @click="handleRegenerateToken(row)">
                重生成
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

    <!-- 创建Token对话框 -->
    <el-dialog v-model="createTokenDialogVisible" title="创建API Token" width="500px">
      <el-form ref="createTokenFormRef" :model="createTokenForm" :rules="createTokenRules" label-width="100px">
        <el-form-item label="用户ID" prop="user_id">
          <el-input v-model="createTokenForm.user_id" placeholder="请输入用户ID" />
        </el-form-item>
        <el-form-item label="Token名称" prop="name">
          <el-input v-model="createTokenForm.name" placeholder="请输入Token名称" />
        </el-form-item>
        <el-form-item label="来源类型" prop="source">
          <el-select v-model="createTokenForm.source" placeholder="请选择来源类型" style="width: 100%">
            <el-option
              v-for="item in sourceOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="createTokenForm.source === 'dialog'" label="绑定对话" prop="dialog_id">
          <el-input v-model="createTokenForm.dialog_id" placeholder="请输入对话ID" />
        </el-form-item>
        <el-form-item label="权限" prop="permissions">
          <el-checkbox-group v-model="createTokenForm.permissions">
            <el-checkbox
              v-for="item in permissionOptions"
              :key="item.value"
              :value="item.value"
            >
              {{ item.label }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="createTokenForm.status">
            <el-radio value="active">启用</el-radio>
            <el-radio value="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createTokenDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCreateToken">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看Token对话框 -->
    <el-dialog v-model="viewTokenDialogVisible" title="API Token详情" width="600px">
      <div class="token-view">
        <el-alert
          title="请妥善保管API Token"
          type="warning"
          :closable="false"
          show-icon
        />
        <div class="token-content">
          <el-input
            v-model="currentToken"
            readonly
            class="token-input"
          >
            <template #append>
              <el-button :icon="CopyDocument" @click="handleCopyToken(currentToken)">
                复制
              </el-button>
            </template>
          </el-input>
        </div>

        <!-- Token详细信息 -->
        <div v-if="currentTokenData" class="token-details">
          <h4>Token信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="用户名称">{{ currentTokenData.user_name }}</el-descriptions-item>
            <el-descriptions-item label="租户名称">{{ currentTokenData.tenant_name }}</el-descriptions-item>
            <el-descriptions-item label="Token名称">{{ currentTokenData.name }}</el-descriptions-item>
            <el-descriptions-item label="来源">{{ getSourceLabel(currentTokenData.source) }}</el-descriptions-item>
            <el-descriptions-item label="权限">{{ getPermissionLabels(currentTokenData.permissions) }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="currentTokenData.status === 'active' ? 'success' : 'danger'">
                {{ currentTokenData.status === 'active' ? '启用' : '禁用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="使用次数">{{ currentTokenData.usage_count }}</el-descriptions-item>
            <el-descriptions-item label="最后使用">{{ currentTokenData.last_used_time || '未使用' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间" :span="2">{{ currentTokenData.create_time }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="token-tips">
          <h4>使用说明</h4>
          <p>• 请将此Token保存在安全的地方</p>
          <p>• 不要在公共代码仓库中暴露此Token</p>
          <p>• 如果Token泄露，请立即重新生成</p>
          <p>• 在HTTP请求头中添加：<code>Authorization: Bearer YOUR_TOKEN</code></p>
        </div>
      </div>
      <template #footer>
        <el-button @click="viewTokenDialogVisible = false">关闭</el-button>
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

.token-display {
  font-family: monospace;
  font-size: 12px;
  cursor: pointer;
}

.token-view {
  .el-alert {
    margin-bottom: 20px;
  }

  .token-content {
    margin: 20px 0;

    .token-input {
      :deep(.el-input__inner) {
        font-family: monospace;
        font-size: 12px;
      }
    }
  }

  .token-details {
    margin: 20px 0;

    h4 {
      margin: 0 0 12px 0;
      font-size: 16px;
      font-weight: 600;
    }
  }

  .token-tips {
    color: #666;
    font-size: 14px;

    h4 {
      margin: 16px 0 8px 0;
      font-size: 16px;
      font-weight: 600;
      color: #333;
    }

    p {
      margin: 5px 0;

      code {
        padding: 2px 6px;
        background: #f5f5f5;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-size: 12px;
      }
    }
  }
}

.text-gray {
  color: #999;
}
</style>