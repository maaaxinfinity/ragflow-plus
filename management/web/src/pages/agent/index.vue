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
          <el-table-column label="所属团队" width="120">
            <template #default="{ row }">
              {{ row.team_id === 'ALL' ? '所有团队' : row.team_name }}
            </template>
          </el-table-column>
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
          <el-table-column prop="is_recommended" label="推荐" width="80" align="center">
            <template #default="scope">
              <el-icon
                v-if="scope.row.is_recommended"
                :size="18"
                style="color: #f39c12; cursor: pointer"
                @click="handleRecommendedChange(scope.row)"
              >
                <StarFilled />
              </el-icon>
              <el-icon
                v-else
                :size="18"
                style="color: #ddd; cursor: pointer"
                @click="handleRecommendedChange(scope.row)"
              >
                <Star />
              </el-icon>
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
      width="80%"
      :close-on-click-modal="false"
    >
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 助理设置 -->
        <el-tab-pane label="助理设置" name="assistant">
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
                      label="所有团队"
                      value="ALL"
                    />
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

            <el-form-item label="头像" prop="avatar">
              <el-upload
                class="avatar-uploader"
                action=""
                :show-file-list="false"
                :before-upload="handleAvatarUpload"
                accept="image/jpeg,image/png,image/svg+xml"
              >
                <img v-if="formData.avatar" :src="formData.avatar" class="avatar" />
                <div v-else class="avatar-placeholder">
                  <el-icon class="avatar-uploader-icon"><Plus /></el-icon>
                  <div class="upload-text">上传头像</div>
                </div>
              </el-upload>
              <div class="form-tip">
                支持 JPG、PNG、SVG 格式，建议尺寸 200x200 像素
              </div>
            </el-form-item>

            <el-form-item label="语言" prop="language">
              <el-select v-model="formData.language" style="width: 100%">
                <el-option label="中文" value="Chinese" />
                <el-option label="English" value="English" />
              </el-select>
            </el-form-item>

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

            <el-form-item label="空回复内容">
              <el-input
                v-model="formData.empty_response"
                type="textarea"
                :rows="2"
                placeholder="当无法从知识库中找到相关信息时的回复"
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

            <el-form-item label="状态" prop="status">
              <el-select v-model="formData.status" style="width: 100%">
                <el-option label="启用" value="active" />
                <el-option label="禁用" value="inactive" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 提示引擎 -->
        <el-tab-pane label="提示引擎" name="prompt">
          <el-form
            ref="promptFormRef"
            :model="formData"
            label-width="120px"
          >
            <el-form-item label="系统提示词" prop="system_prompt">
              <el-input
                v-model="formData.system_prompt"
                type="textarea"
                :rows="6"
                placeholder="请输入系统提示词，用于指导Agent的行为和回答方式"
              />
            </el-form-item>

            <el-form-item label="欢迎语" prop="welcome_message">
              <el-input
                v-model="formData.welcome_message"
                type="textarea"
                :rows="3"
                placeholder="请输入欢迎语，用户开始对话时显示"
              />
            </el-form-item>

            <el-divider>检索设置</el-divider>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="相似度阈值">
                  <el-slider
                    v-model="formData.similarity_threshold"
                    :min="0"
                    :max="1"
                    :step="0.1"
                    show-input
                    style="width: 100%"
                  />
                  <div class="form-tip">
                    文档片段与问题的最低相似度阈值
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="向量权重">
                  <el-slider
                    v-model="formData.vector_similarity_weight"
                    :min="0"
                    :max="1"
                    :step="0.1"
                    show-input
                    style="width: 100%"
                  />
                  <div class="form-tip">
                    向量检索与关键词检索的权重比例
                  </div>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="检索数量">
                  <el-input-number
                    v-model="formData.top_n"
                    :min="1"
                    :max="50"
                    style="width: 100%"
                  />
                  <div class="form-tip">
                    从知识库中检索的文档片段数量
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="启用重排">
                  <el-switch
                    v-model="formData.rerank_enabled"
                    active-text="是"
                    inactive-text="否"
                  />
                  <div class="form-tip">
                    对检索结果进行重新排序以提升准确性
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>

        <!-- 模型设置 -->
        <el-tab-pane label="模型设置" name="model">
          <el-form
            ref="modelFormRef"
            :model="formData"
            label-width="120px"
          >
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

            <el-divider>模型参数</el-divider>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="温度">
                  <el-slider
                    v-model="formData.temperature"
                    :min="0"
                    :max="2"
                    :step="0.1"
                    show-input
                    style="width: 100%"
                  />
                  <div class="form-tip">
                    控制回答的创造性，数值越高回答越有创意
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="最大Token">
                  <el-input-number
                    v-model="formData.max_tokens"
                    :min="1"
                    :max="8192"
                    style="width: 100%"
                  />
                  <div class="form-tip">
                    模型生成回答的最大长度
                  </div>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Top P">
                  <el-slider
                    v-model="formData.top_p"
                    :min="0"
                    :max="1"
                    :step="0.1"
                    show-input
                    style="width: 100%"
                  />
                  <div class="form-tip">
                    核采样参数，控制生成词汇的多样性
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="频率惩罚">
                  <el-slider
                    v-model="formData.frequency_penalty"
                    :min="0"
                    :max="2"
                    :step="0.1"
                    show-input
                    style="width: 100%"
                  />
                  <div class="form-tip">
                    减少重复内容的生成
                  </div>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="存在惩罚">
                  <el-slider
                    v-model="formData.presence_penalty"
                    :min="0"
                    :max="2"
                    :step="0.1"
                    show-input
                    style="width: 100%"
                  />
                  <div class="form-tip">
                    鼓励模型谈论新主题
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="流式响应">
                  <el-switch
                    v-model="formData.stream"
                    active-text="是"
                    inactive-text="否"
                  />
                  <div class="form-tip">
                    启用后回答将实时显示
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>
      </el-tabs>

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
import { Plus, Search, Refresh, Edit, Delete, Star, StarFilled } from '@element-plus/icons-vue'
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
const activeTab = ref('assistant')

// 表单数据
const formData = reactive({
  id: '',
  name: '',
  team_id: '',
  description: '',
  avatar: '/assets/agent/Agent-icon.svg', // 添加头像字段，设置默认头像
  model_name: '',
  kb_ids: [] as string[],
  system_prompt: '你是一个学术领域的专家，请根据知识库的内容来尽可能详细的回答问题。\n        以下是知识库：\n        {knowledge}\n        以上是知识库。',
  welcome_message: '',
  is_recommended: false,
  status: 'active',
  language: 'zh-CN',
  empty_response: '抱歉，我无法理解您的问题。',
  similarity_threshold: 0.2,
  vector_similarity_weight: 0.3,
  vector_keywords_weight: 0.7,
  top_n: 8,
  rerank_enabled: false,
  rerank_model: '',
  temperature: 0.1,
  max_tokens: 512,
  top_p: 0.3,
  frequency_penalty: 0.7,
  presence_penalty: 0.4,
  stream: false
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
    avatar: row.avatar || getDefaultAvatar(),
    model_name: row.model_name,
    kb_ids: row.kb_ids || [],
    system_prompt: row.system_prompt,
    welcome_message: row.welcome_message,
    language: row.language || 'zh-CN',
    empty_response: row.empty_response || '抱歉，我无法理解您的问题。',
    similarity_threshold: row.similarity_threshold || 0.2,
    vector_similarity_weight: row.vector_similarity_weight || 0.3,
    vector_keywords_weight: row.vector_keywords_weight || 0.7,
    top_n: row.top_n || 8,
    rerank_enabled: row.rerank_enabled || false,
    rerank_model: row.rerank_model || '',
    temperature: row.temperature || 0.1,
    max_tokens: row.max_tokens || 512,
    top_p: row.top_p || 0.3,
    frequency_penalty: row.frequency_penalty || 0.7,
    presence_penalty: row.presence_penalty || 0.4,
    stream: row.stream || false,
    is_recommended: row.is_recommended,
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

    // 调用真实删除API
    const response = await fetch(`/api/v1/agents/${row.id}`, {
      method: 'DELETE'
    })

    if (response.ok) {
      const result = await response.json()
      if (result.code === 0) {
        ElMessage.success('删除成功')
        getTableData()
      } else {
        ElMessage.error(result.message || '删除失败')
      }
    } else {
      ElMessage.error('删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 推荐状态变化
const handleRecommendedChange = async (row: any) => {
  row.updating = true
  try {
    // 切换推荐状态
    const newRecommendedStatus = !row.is_recommended

    // 调用真实API设置推荐状态
    const response = await fetch(`/api/v1/agents/${row.id}/recommended`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        is_recommended: newRecommendedStatus
      })
    })

    if (response.ok) {
      const result = await response.json()
      if (result.code === 0) {
        row.is_recommended = newRecommendedStatus
        ElMessage.success(newRecommendedStatus ? '已设为推荐Agent' : '已取消推荐Agent')
      } else {
        ElMessage.error(result.message || '操作失败')
      }
    } else {
      ElMessage.error('操作失败')
    }
  } catch (error) {
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
        avatar: formData.avatar,
        model_name: formData.model_name,
        kb_ids: formData.kb_ids,
        system_prompt: formData.system_prompt,
        welcome_message: formData.welcome_message,
        language: formData.language,
        empty_response: formData.empty_response,
        similarity_threshold: formData.similarity_threshold,
        vector_similarity_weight: formData.vector_similarity_weight,
        vector_keywords_weight: formData.vector_keywords_weight,
        top_n: formData.top_n,
        rerank_enabled: formData.rerank_enabled,
        rerank_model: formData.rerank_model,
        temperature: formData.temperature,
        max_tokens: formData.max_tokens,
        top_p: formData.top_p,
        frequency_penalty: formData.frequency_penalty,
        presence_penalty: formData.presence_penalty,
        stream: formData.stream,
        is_recommended: formData.is_recommended,
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

// 获取默认头像
const getDefaultAvatar = () => {
  return '/assets/agent/Agent-icon.svg'
}

// 头像上传处理
const handleAvatarUpload = (file: File) => {
  const isValidFormat = file.type === 'image/jpeg' || file.type === 'image/png' || file.type === 'image/svg+xml'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isValidFormat) {
    ElMessage.error('头像图片只能是 JPG/PNG/SVG 格式!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('头像图片大小不能超过 2MB!')
    return false
  }

  // 转换为base64
  const reader = new FileReader()
  reader.onload = (e) => {
    formData.avatar = e.target?.result as string
  }
  reader.readAsDataURL(file)

  return false // 阻止自动上传
}

// 重置表单
const resetForm = () => {
  Object.assign(formData, {
    id: '',
    name: '',
    team_id: '',
    description: '',
    avatar: getDefaultAvatar(), // 设置默认头像
    model_name: '',
    kb_ids: [],
    system_prompt: '你是一个学术领域的专家，请根据知识库的内容来尽可能详细的回答问题。\n        以下是知识库：\n        {knowledge}\n        以上是知识库。',
    welcome_message: '',
    is_recommended: false,
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

.avatar-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
  width: 100px;
  height: 100px;
  display: block;
}

.avatar-uploader:hover {
  border-color: #409eff;
}

.avatar {
  width: 100px;
  height: 100px;
  object-fit: cover;
  display: block;
}

.avatar-placeholder {
  width: 100px;
  height: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #fafafa;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
}

.upload-text {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
</style>