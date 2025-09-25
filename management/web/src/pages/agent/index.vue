<template>
  <div class="app-container">
    <el-card v-loading="loading" shadow="never">
      <div class="page-header">
        <div class="header-left">
          <h2>默认 Agent 配置</h2>
          <p class="page-description">为团队成员配置默认的对话 Agent，便于在对话页面直接使用</p>
        </div>
        <div class="header-right">
          <el-button type="primary" :icon="Plus" @click="handleCreate">
            新建 Agent 配置
          </el-button>
        </div>
      </div>

      <!-- 搜索区域 -->
      <div class="search-wrapper">
        <el-form :model="searchForm" :inline="true">
          <el-form-item label="团队">
            <el-select
              v-model="searchForm.team_id"
              placeholder="选择团队"
              clearable
              style="width: 200px"
            >
              <el-option
                v-for="team in teamList"
                :key="team.id"
                :label="team.name"
                :value="team.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="Agent名称">
            <el-input
              v-model="searchForm.name"
              placeholder="请输入Agent名称"
              clearable
              style="width: 200px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :icon="Search" @click="handleSearch">
              搜索
            </el-button>
            <el-button :icon="Refresh" @click="resetSearch">
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 表格区域 -->
      <div class="table-wrapper">
        <el-table :data="tableData" style="width: 100%" @sort-change="handleSortChange">
          <el-table-column prop="name" label="Agent名称" min-width="150" show-overflow-tooltip />
          <el-table-column prop="team_name" label="所属团队" width="120" />
          <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
          <el-table-column prop="model_name" label="使用模型" width="150" />
          <el-table-column prop="kb_names" label="关联知识库" min-width="200">
            <template #default="scope">
              <el-tag
                v-for="kb in scope.row.kb_names"
                :key="kb"
                size="small"
                style="margin-right: 4px"
              >
                {{ kb }}
              </el-tag>
              <span v-if="!scope.row.kb_names || scope.row.kb_names.length === 0" class="text-muted">
                未关联
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="is_default" label="默认状态" width="100" align="center">
            <template #default="scope">
              <el-switch
                v-model="scope.row.is_default"
                @change="handleDefaultChange(scope.row)"
                :loading="scope.row.updating"
              />
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80" align="center">
            <template #default="scope">
              <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'" size="small">
                {{ scope.row.status === 'active' ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="create_date" label="创建时间" width="180" align="center" />
          <el-table-column label="操作" width="200" align="center" fixed="right">
            <template #default="scope">
              <el-button type="primary" size="small" :icon="Edit" @click="handleEdit(scope.row)">
                编辑
              </el-button>
              <el-button type="danger" size="small" :icon="Delete" @click="handleDelete(scope.row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页区域 -->
      <div class="pager-wrapper">
        <el-pagination
          v-model:current-page="paginationData.currentPage"
          v-model:page-size="paginationData.pageSize"
          :page-sizes="paginationData.pageSizes"
          :layout="paginationData.layout"
          :total="paginationData.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="60%"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Agent名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入Agent名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属团队" prop="team_id">
              <el-select
                v-model="formData.team_id"
                placeholder="选择团队"
                style="width: 100%"
              >
                <el-option
                  v-for="team in teamList"
                  :key="team.id"
                  :label="team.name"
                  :value="team.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入Agent描述"
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="使用模型" prop="model_name">
              <el-select
                v-model="formData.model_name"
                placeholder="选择模型"
                style="width: 100%"
              >
                <el-option
                  v-for="model in modelList"
                  :key="model.name"
                  :label="model.name"
                  :value="model.name"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="formData.status" style="width: 100%">
                <el-option label="启用" value="active" />
                <el-option label="禁用" value="inactive" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="关联知识库">
          <el-select
            v-model="formData.kb_ids"
            multiple
            placeholder="选择关联的知识库"
            style="width: 100%"
          >
            <el-option
              v-for="kb in knowledgeBaseList"
              :key="kb.id"
              :label="kb.name"
              :value="kb.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="系统提示词" prop="system_prompt">
          <el-input
            v-model="formData.system_prompt"
            type="textarea"
            :rows="4"
            placeholder="请输入系统提示词，用于指导Agent的行为"
          />
        </el-form-item>

        <el-form-item label="欢迎语" prop="welcome_message">
          <el-input
            v-model="formData.welcome_message"
            type="textarea"
            :rows="2"
            placeholder="请输入欢迎语，用户开始对话时显示"
          />
        </el-form-item>

        <el-form-item label="设为默认">
          <el-switch
            v-model="formData.is_default"
            active-text="是"
            inactive-text="否"
          />
          <div class="form-tip">
            设为默认后，该团队成员在对话页面将优先使用此Agent
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import { usePagination } from '@@/composables/usePagination'

defineOptions({
  name: 'AgentConfig'
})

// 响应式数据
const loading = ref(false)
const { paginationData, handleCurrentChange, handleSizeChange } = usePagination()

// 搜索表单
const searchForm = reactive({
  team_id: '',
  name: ''
})

// 表格数据
const tableData = ref<any[]>([])

// 团队数据类型
interface TeamItem {
  id: string
  name: string
  owner_name?: string
  create_date?: string
  update_date?: string
  status?: string
}

// 模型数据类型
interface ModelItem {
  name: string
  model_type?: string
  fid?: string
  max_tokens?: number
  tags?: string
  status?: string
}

// 知识库数据类型
interface KnowledgeBaseItem {
  id: string
  name: string
  description?: string
  tenant_id?: string
}

// 团队列表
const teamList = ref<TeamItem[]>([])

// 模型列表
const modelList = ref<ModelItem[]>([])

// 知识库列表
const knowledgeBaseList = ref<KnowledgeBaseItem[]>([])

// 对话框相关
const dialogVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref()

// 表单数据
const formData = reactive({
  id: '',
  name: '',
  team_id: '',
  description: '',
  model_name: '',
  kb_ids: [] as string[],
  system_prompt: '',
  welcome_message: '',
  is_default: false,
  status: 'active'
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入Agent名称', trigger: 'blur' }
  ],
  team_id: [
    { required: true, message: '请选择团队', trigger: 'change' }
  ],
  model_name: [
    { required: true, message: '请选择模型', trigger: 'change' }
  ],
  system_prompt: [
    { required: true, message: '请输入系统提示词', trigger: 'blur' }
  ]
}

// 对话框标题
const dialogTitle = computed(() => {
  return formData.id ? '编辑 Agent 配置' : '新建 Agent 配置'
})

// 获取团队列表
const getTeamList = async () => {
  try {
    const response = await fetch('/api/v1/knowledgebases/rag/tenants')
    if (response.ok) {
      const result = await response.json()
      if (result.code === 0) {
        teamList.value = result.data || []
      }
    }
  } catch (error) {
    console.error('获取团队列表失败:', error)
  }
}

// 获取模型列表
const getModelList = async () => {
  try {
    const response = await fetch('/api/v1/knowledgebases/rag/llms?model_type=LLM')
    if (response.ok) {
      const result = await response.json()
      if (result.code === 0) {
        modelList.value = result.data || []
      }
    }
  } catch (error) {
    console.error('获取模型列表失败:', error)
  }
}

// 获取知识库列表
const getKnowledgeBaseList = async () => {
  try {
    const response = await fetch('/api/v1/knowledgebases/rag/simple')
    if (response.ok) {
      const result = await response.json()
      if (result.code === 0) {
        knowledgeBaseList.value = result.data || []
      }
    }
  } catch (error) {
    console.error('获取知识库列表失败:', error)
  }
}

// 获取表格数据
const getTableData = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      currentPage: paginationData.currentPage.toString(),
      size: paginationData.pageSize.toString(),
      team_id: searchForm.team_id,
      name: searchForm.name
    })

    const response = await fetch(`/api/v1/agents?${params}`)
    if (response.ok) {
      const result = await response.json()
      if (result.code === 0) {
        tableData.value = result.data?.list || []
        paginationData.total = result.data?.total || 0
      } else {
        ElMessage.error(result.message || '获取数据失败')
      }
    } else {
      ElMessage.error('获取数据失败')
    }
  } catch (error) {
    console.error('获取Agent列表失败:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  paginationData.currentPage = 1
  getTableData()
}

// 重置搜索
const resetSearch = () => {
  searchForm.team_id = ''
  searchForm.name = ''
  handleSearch()
}

// 排序变化
const handleSortChange = ({ prop, order }: any) => {
  console.log('排序变化:', prop, order)
  getTableData()
}

// 新建
const handleCreate = () => {
  resetForm()
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: any) => {
  Object.assign(formData, {
    id: row.id,
    name: row.name,
    team_id: row.team_id,
    description: row.description,
    model_name: row.model_name,
    kb_ids: row.kb_ids || [],
    system_prompt: row.system_prompt,
    welcome_message: row.welcome_message,
    is_default: row.is_default,
    status: row.status
  })
  dialogVisible.value = true
}

// 删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 Agent "${row.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 模拟删除API
    ElMessage.success('删除成功')
    getTableData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 默认状态变化
const handleDefaultChange = async (row: any) => {
  row.updating = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (row.is_default) {
      // 如果设为默认，需要取消同团队其他Agent的默认状态
      tableData.value.forEach(item => {
        if (item.team_id === row.team_id && item.id !== row.id) {
          item.is_default = false
        }
      })
    }
    
    ElMessage.success(row.is_default ? '已设为默认Agent' : '已取消默认Agent')
  } catch (error) {
    // 恢复原状态
    row.is_default = !row.is_default
    ElMessage.error('操作失败')
  } finally {
    row.updating = false
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    submitLoading.value = true

    // 调用真实API
    const method = formData.id ? 'PUT' : 'POST'
    const url = formData.id ? `/api/v1/agents/${formData.id}` : '/api/v1/agents'

    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: formData.name,
        team_id: formData.team_id,
        description: formData.description,
        model_name: formData.model_name,
        kb_ids: formData.kb_ids,
        system_prompt: formData.system_prompt,
        welcome_message: formData.welcome_message,
        is_default: formData.is_default,
        status: formData.status
      })
    })

    if (response.ok) {
      const result = await response.json()
      if (result.code === 0) {
        ElMessage.success(formData.id ? '更新成功' : '创建成功')
        dialogVisible.value = false
        getTableData()
      } else {
        ElMessage.error(result.message || '操作失败')
      }
    } else {
      ElMessage.error('操作失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('操作失败')
  } finally {
    submitLoading.value = false
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(formData, {
    id: '',
    name: '',
    team_id: '',
    description: '',
    model_name: '',
    kb_ids: [],
    system_prompt: '',
    welcome_message: '',
    is_default: false,
    status: 'active'
  })
  formRef.value?.resetFields()
}

// 初始化
onMounted(() => {
  getTeamList()
  getModelList()
  getKnowledgeBaseList()
  getTableData()
})
</script>

<style scoped>
.app-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  
  .header-left {
    h2 {
      margin: 0 0 8px 0;
      font-size: 24px;
      font-weight: 600;
    }
    
    .page-description {
      margin: 0;
      color: #666;
      font-size: 14px;
    }
  }
}

.search-wrapper {
  margin-bottom: 20px;
  
  :deep(.el-card__body) {
    padding-bottom: 2px;
  }
}

.table-wrapper {
  margin-bottom: 20px;
}

.pager-wrapper {
  display: flex;
  justify-content: flex-end;
}

.text-muted {
  color: #999;
  font-size: 12px;
}

.form-tip {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

:deep(.el-table .el-table__cell) {
  padding: 12px 0;
}

:deep(.el-dialog__body) {
  padding: 20px;
}
</style>