<template>
  <div class="kb-tree">
    <div class="tree-header">
      <div class="header-left">
        <h4>{{ knowledgeBase?.name || '知识库文档' }}</h4>
        <span class="doc-count">{{ totalDocuments }} 个文档</span>
      </div>
      <div class="header-right">
        <el-button 
          type="text" 
          :icon="Refresh" 
          @click="refreshTree"
          :loading="loading"
          size="small"
        >
          刷新
        </el-button>
      </div>
    </div>
    
    <div class="tree-content" v-loading="loading">
      <el-tree
        ref="treeRef"
        :data="treeData"
        :props="treeProps"
        :expand-on-click-node="false"
        :check-on-click-node="false"
        node-key="id"
        class="kb-document-tree"
        @node-click="handleNodeClick"
        :default-expanded-keys="defaultExpandedKeys"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <div class="node-content">
              <el-icon class="node-icon">
                <Folder v-if="data.type === 'folder'" />
                <Document v-else />
              </el-icon>
              <span class="node-label" :title="node.label">{{ node.label }}</span>
              <div class="node-info">
                <span v-if="data.type === 'folder' && data.fileCount" class="file-count">
                  {{ data.fileCount }}
                </span>
                <span v-if="data.type === 'file'" class="file-size">
                  {{ formatFileSize(data.size) }}
                </span>
              </div>
            </div>
            
            <!-- 文档状态和操作 -->
            <div v-if="data.type === 'file'" class="node-actions">
              <el-tag 
                :type="getParseStatusType(data.progress)" 
                size="small"
                class="status-tag"
              >
                {{ formatParseStatus(data.progress) }}
              </el-tag>
              
              <div class="action-buttons">
                <el-button
                  type="success"
                  size="small"
                  :icon="CaretRight"
                  @click.stop="handleParseDocument(data)"
                  :loading="data.parsing"
                  :disabled="data.progress === 1"
                >
                  {{ data.parsing ? '解析中' : '解析' }}
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  :icon="Delete"
                  @click.stop="handleRemoveDocument(data)"
                >
                  移除
                </el-button>
              </div>
            </div>
          </div>
        </template>
      </el-tree>
      
      <div v-if="treeData.length === 0 && !loading" class="empty-tree">
        <el-empty description="暂无文档" :image-size="80" />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElTree, ElMessage, ElMessageBox } from 'element-plus'
import { Folder, Document, Refresh, CaretRight, Delete } from '@element-plus/icons-vue'
import { getDocumentListApi, runDocumentParseApi, deleteDocumentApi } from '@@/apis/kbs/document'

interface Props {
  knowledgeBase?: {
    id: string
    name: string
  }
}

interface DocumentData {
  id: string
  name: string
  type: 'file' | 'folder'
  size?: number
  progress?: number
  parsing?: boolean
  parent_id?: string
  children?: DocumentData[]
  fileCount?: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  documentClick: [document: DocumentData]
  documentParsed: [document: DocumentData]
  documentRemoved: [document: DocumentData]
  refresh: []
}>()

// 树形数据
const treeRef = ref<InstanceType<typeof ElTree>>()
const treeData = ref<DocumentData[]>([])
const loading = ref(false)
const defaultExpandedKeys = ref<string[]>([])

const treeProps = {
  children: 'children',
  label: 'name',
  isLeaf: (data: DocumentData) => data.type !== 'folder'
}

// 计算总文档数
const totalDocuments = computed(() => {
  const countDocuments = (nodes: DocumentData[]): number => {
    let count = 0
    nodes.forEach(node => {
      if (node.type === 'file') {
        count++
      } else if (node.children) {
        count += countDocuments(node.children)
      }
    })
    return count
  }
  return countDocuments(treeData.value)
})

// 加载知识库文档
const loadDocuments = async () => {
  if (!props.knowledgeBase?.id) {
    treeData.value = []
    return
  }
  
  loading.value = true
  try {
    const response = await getDocumentListApi({
      kb_id: props.knowledgeBase.id,
      page: 1,
      size: 1000, // 获取所有文档
      name: '',
      sort_by: 'create_time',
      sort_order: 'desc'
    })
    
    if (response.code === 0) {
      // 构建树形结构
      const documents = response.data.list
      treeData.value = buildDocumentTree(documents)
      
      // 默认展开第一级文件夹
      defaultExpandedKeys.value = treeData.value
        .filter(item => item.type === 'folder')
        .map(item => item.id)
    } else {
      ElMessage.error(response.message || '加载文档失败')
      treeData.value = []
    }
  } catch (error) {
    console.error('加载文档失败:', error)
    ElMessage.error('加载文档失败')
    treeData.value = []
  } finally {
    loading.value = false
  }
}

// 构建文档树形结构
const buildDocumentTree = (documents: any[]): DocumentData[] => {
  const documentMap = new Map<string, DocumentData>()
  const rootNodes: DocumentData[] = []
  
  // 首先创建所有节点
  documents.forEach(doc => {
    const node: DocumentData = {
      id: doc.id,
      name: doc.name,
      type: 'file',
      size: doc.size,
      progress: doc.progress,
      parsing: false,
      parent_id: doc.parent_id,
      children: []
    }
    documentMap.set(doc.id, node)
  })
  
  // 构建树形结构
  documents.forEach(doc => {
    const node = documentMap.get(doc.id)!
    
    if (doc.parent_id && documentMap.has(doc.parent_id)) {
      // 有父节点，添加到父节点的children中
      const parent = documentMap.get(doc.parent_id)!
      if (!parent.children) parent.children = []
      parent.children.push(node)
    } else {
      // 没有父节点或父节点不存在，作为根节点
      rootNodes.push(node)
    }
  })
  
  // 为了更好的展示效果，我们可以按文件夹和文件分组
  // 这里简化处理，直接返回平铺的文档列表
  return rootNodes.sort((a, b) => {
    // 文件夹排在前面，然后按名称排序
    if (a.type !== b.type) {
      return a.type === 'folder' ? -1 : 1
    }
    return a.name.localeCompare(b.name)
  })
}

// 刷新树
const refreshTree = () => {
  emit('refresh')
  loadDocuments()
}

// 节点点击事件
const handleNodeClick = (data: DocumentData) => {
  emit('documentClick', data)
}

// 解析文档
const handleParseDocument = async (document: DocumentData) => {
  try {
    document.parsing = true
    
    const response = await runDocumentParseApi({
      doc_id: document.id,
      kb_id: props.knowledgeBase!.id
    })
    
    if (response.code === 0) {
      ElMessage.success('文档解析已开始')
      document.progress = 0.1 // 设置为解析中状态
      emit('documentParsed', document)
    } else {
      ElMessage.error(response.message || '启动文档解析失败')
    }
  } catch (error) {
    console.error('解析文档失败:', error)
    ElMessage.error('解析文档失败')
  } finally {
    document.parsing = false
  }
}

// 移除文档
const handleRemoveDocument = async (document: DocumentData) => {
  try {
    await ElMessageBox.confirm(
      `确定要从知识库中移除文档 "${document.name}" 吗？`,
      '确认移除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await deleteDocumentApi({
      doc_id: document.id,
      kb_id: props.knowledgeBase!.id
    })
    
    if (response.code === 0) {
      ElMessage.success('文档移除成功')
      emit('documentRemoved', document)
      // 重新加载文档列表
      loadDocuments()
    } else {
      ElMessage.error(response.message || '移除文档失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('移除文档失败:', error)
      ElMessage.error('移除文档失败')
    }
  }
}

// 格式化文件大小
const formatFileSize = (size?: number) => {
  if (!size) return 'N/A'
  
  if (size < 1024) {
    return `${size} B`
  } else if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(2)} KB`
  } else if (size < 1024 * 1024 * 1024) {
    return `${(size / (1024 * 1024)).toFixed(2)} MB`
  } else {
    return `${(size / (1024 * 1024 * 1024)).toFixed(2)} GB`
  }
}

// 格式化解析状态
const formatParseStatus = (progress?: number) => {
  if (progress === undefined || progress === null) return '未解析'
  if (progress === 0) return '等待解析'
  if (progress > 0 && progress < 1) return '解析中'
  if (progress === 1) return '已完成'
  return '解析失败'
}

// 获取解析状态类型
const getParseStatusType = (progress?: number) => {
  if (progress === undefined || progress === null) return 'info'
  if (progress === 0) return 'warning'
  if (progress > 0 && progress < 1) return 'primary'
  if (progress === 1) return 'success'
  return 'danger'
}

// 监听知识库变化
watch(() => props.knowledgeBase, (newKb) => {
  if (newKb) {
    loadDocuments()
  } else {
    treeData.value = []
  }
}, { immediate: true })

// 暴露方法给父组件
defineExpose({
  refreshTree,
  loadDocuments
})
</script>

<style scoped>
.kb-tree {
  height: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
  background-color: #fafafa;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;
    
    h4 {
      margin: 0;
      font-size: 14px;
      font-weight: 500;
    }
    
    .doc-count {
      font-size: 12px;
      color: #909399;
      background-color: #f0f2f5;
      padding: 2px 8px;
      border-radius: 12px;
    }
  }
}

.tree-content {
  flex: 1;
  overflow: auto;
  padding: 8px;
}

.kb-document-tree {
  :deep(.el-tree-node__content) {
    height: auto;
    min-height: 40px;
    padding: 4px 0;
  }
  
  :deep(.el-tree-node__content:hover) {
    background-color: #f5f7fa;
  }
}

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 4px 8px;
  
  .node-content {
    display: flex;
    align-items: center;
    flex: 1;
    min-width: 0;
    
    .node-icon {
      margin-right: 8px;
      color: #606266;
    }
    
    .node-label {
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      margin-right: 8px;
    }
    
    .node-info {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .file-count,
      .file-size {
        font-size: 12px;
        color: #909399;
      }
    }
  }
  
  .node-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-left: 12px;
    
    .status-tag {
      font-size: 11px;
    }
    
    .action-buttons {
      display: flex;
      gap: 4px;
      opacity: 0;
      transition: opacity 0.2s;
      
      .el-button {
        padding: 4px 8px;
        font-size: 12px;
      }
    }
  }
  
  &:hover .action-buttons {
    opacity: 1;
  }
}

.empty-tree {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
}
</style>