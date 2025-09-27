<script lang="ts" setup>
import { ref, reactive, onMounted, onActivated, watch } from 'vue'
import type { FormInstance } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { usePagination } from '@@/composables/usePagination'
import { Refresh, Search, Plus, Edit, Delete, Key, View } from '@element-plus/icons-vue'

defineOptions({
  name: 'ApiSetting'
})

const loading = ref<boolean>(false)
const { paginationData, handleCurrentChange, handleSizeChange } = usePagination()

// API Token数据接口
interface ApiTokenData {
  id: string
  name: string
  token: string
  dialog_id?: string
  dialog_name?: string
  source: string // dialog, agent, none
  permissions: string[]
  status: string
  create_time: string
  update_time: string
  last_used_time?: string
  usage_count: number
}

// 表格数据
const tableData = ref<ApiTokenData[]>([])
const searchFormRef = ref<FormInstance | null>(null)
const searchData = reactive({
  name: '',
  source: '',
  status: ''
})

// 多选数据
const multipleSelection = ref<ApiTokenData[]>([])

// 对话框控制
const dialogVisible = ref(false)
const dialogTitle = ref('创建API Token')
const formRef = ref<FormInstance | null>(null)

// 查看Token对话框
const viewTokenDialogVisible = ref(false)
const currentToken = ref('')

// 表单数据
const DEFAULT_FORM_DATA: Partial<ApiTokenData> = {
  name: '',
  source: 'none',
  dialog_id: '',
  permissions: ['read'],
  status: 'active'
}
const formData = ref<Partial<ApiTokenData>>({ ...DEFAULT_FORM_DATA })

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

// 获取表格数据
function getTableData() {
  loading.value = true
  // 这里应该调用实际的API
  // 暂时使用模拟数据
  setTimeout(() => {
    tableData.value = [
      {
        id: '1',
        name: '主要API Token',
        token: 'sk-proj-1234567890abcdef',
        source: 'none',
        permissions: ['read', 'write'],
        status: 'active',
        create_time: '2024-01-01 10:00:00',
        update_time: '2024-01-01 10:00:00',
        last_used_time: '2024-01-02 15:30:00',
        usage_count: 156
      },
      {
        id: '2',
        name: '客服对话Token',
        token: 'sk-proj-abcdef1234567890',
        dialog_id: 'dialog_123',
        dialog_name: '客服助手',
        source: 'dialog',
        permissions: ['read'],
        status: 'active',
        create_time: '2024-01-01 10:00:00',
        update_time: '2024-01-01 10:00:00',
        last_used_time: '2024-01-02 12:15:00',
        usage_count: 89
      },
      {
        id: '3',
        name: '测试Token',
        token: 'sk-proj-test123456789',
        source: 'none',
        permissions: ['read'],
        status: 'inactive',
        create_time: '2024-01-01 10:00:00',
        update_time: '2024-01-01 10:00:00',
        usage_count: 23
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

// 创建Token
function handleAdd() {
  dialogTitle.value = '创建API Token'
  formData.value = { ...DEFAULT_FORM_DATA }
  dialogVisible.value = true
}

// 编辑Token
function handleEdit(row: ApiTokenData) {
  dialogTitle.value = '编辑API Token'
  formData.value = { ...row }
  dialogVisible.value = true
}

// 查看Token
function handleViewToken(row: ApiTokenData) {
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
function handleRegenerateToken(row: ApiTokenData) {
  ElMessageBox.confirm(
    `确定要重新生成Token "${row.name}" 吗？原Token将失效。`,
    '确认重新生成',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 这里应该调用重新生成API
    const newToken = 'sk-proj-' + Math.random().toString(36).substring(2, 18)
    ElMessage.success('Token重新生成成功')
    // 显示新Token
    currentToken.value = newToken
    viewTokenDialogVisible.value = true
    getTableData()
  }).catch(() => {
    ElMessage.info('已取消重新生成')
  })
}

// 删除Token
function handleDelete(row: ApiTokenData) {
  ElMessageBox.confirm(
    `确定要删除Token "${row.name}" 吗？`,
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
        const newToken = 'sk-proj-' + Math.random().toString(36).substring(2, 18)
        ElMessage.success(dialogTitle.value.includes('创建') ? '创建成功' : '编辑成功')
        dialogVisible.value = false

        // 如果是创建，显示新Token
        if (dialogTitle.value.includes('创建')) {
          currentToken.value = newToken
          viewTokenDialogVisible.value = true
        }

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

// 表格多选
function handleSelectionChange(selection: ApiTokenData[]) {
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
const formRules = {
  name: [{ required: true, message: '请输入Token名称', trigger: 'blur' }],
  source: [{ required: true, message: '请选择Token来源', trigger: 'change' }],
  permissions: [{ required: true, message: '请选择权限', trigger: 'change' }]
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
          <el-button type="primary" :icon="Plus" @click="handleAdd">
            创建Token
          </el-button>
          <el-button type="danger" :icon="Delete" @click="handleBatchDelete">
            批量删除
          </el-button>
        </div>
      </div>

      <div class="table-wrapper">
        <el-table :data="tableData" @selection-change="handleSelectionChange">
          <el-table-column type="selection" width="50" align="center" />
          <el-table-column prop="name" label="Token名称" align="center" />
          <el-table-column prop="token" label="Token" align="center" min-width="200">
            <template #default="{ row }">
              <el-tooltip :content="row.token" placement="top">
                <span class="token-display">{{ maskToken(row.token) }}</span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column prop="source" label="来源" align="center">
            <template #default="{ row }">
              <el-tag>{{ getSourceLabel(row.source) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="dialog_name" label="绑定对象" align="center">
            <template #default="{ row }">
              <span v-if="row.dialog_name">{{ row.dialog_name }}</span>
              <span v-else class="text-gray">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="permissions" label="权限" align="center">
            <template #default="{ row }">
              {{ getPermissionLabels(row.permissions) }}
            </template>
          </el-table-column>
          <el-table-column prop="usage_count" label="使用次数" align="center" />
          <el-table-column prop="status" label="状态" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
                {{ row.status === 'active' ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="last_used_time" label="最后使用" align="center">
            <template #default="{ row }">
              <span v-if="row.last_used_time">{{ row.last_used_time }}</span>
              <span v-else class="text-gray">未使用</span>
            </template>
          </el-table-column>
          <el-table-column fixed="right" label="操作" width="200" align="center">
            <template #default="{ row }">
              <el-button type="primary" text bg size="small" :icon="View" @click="handleViewToken(row)">
                查看
              </el-button>
              <el-button type="warning" text bg size="small" :icon="Key" @click="handleRegenerateToken(row)">
                重生成
              </el-button>
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

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="Token名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入Token名称" />
        </el-form-item>
        <el-form-item label="来源类型" prop="source">
          <el-select v-model="formData.source" placeholder="请选择来源类型">
            <el-option
              v-for="item in sourceOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="formData.source === 'dialog'" label="绑定对话" prop="dialog_id">
          <el-select v-model="formData.dialog_id" placeholder="请选择要绑定的对话">
            <el-option label="客服助手" value="dialog_123" />
            <el-option label="技术支持" value="dialog_456" />
          </el-select>
        </el-form-item>
        <el-form-item label="权限" prop="permissions">
          <el-checkbox-group v-model="formData.permissions">
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
          <el-radio-group v-model="formData.status">
            <el-radio value="active">启用</el-radio>
            <el-radio value="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="loading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看Token对话框 -->
    <el-dialog v-model="viewTokenDialogVisible" title="API Token" width="600px">
      <div class="token-view">
        <el-alert
          title="请妥善保管您的API Token"
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
              <el-button @click="handleCopyToken(currentToken)">
                复制
              </el-button>
            </template>
          </el-input>
        </div>
        <div class="token-tips">
          <p>• 请将此Token保存在安全的地方</p>
          <p>• 不要在公共代码仓库中暴露此Token</p>
          <p>• 如果Token泄露，请立即重新生成</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="viewTokenDialogVisible = false">关闭</el-button>
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

  .token-tips {
    color: #666;
    font-size: 14px;

    p {
      margin: 5px 0;
    }
  }
}

.text-gray {
  color: #999;
}
</style>