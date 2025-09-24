<template>
  <div class="folder-selector">
    <el-dialog
      v-model="visible"
      :title="title"
      width="60%"
      :close-on-click-modal="false"
      @close="handleClose"
    >
      <div class="selector-content">
        <div class="left-panel">
          <div class="panel-header">
            <h4>文件夹结构</h4>
            <el-button 
              type="text" 
              :icon="Refresh" 
              @click="refreshTree"
              :loading="treeLoading"
            >
              刷新
            </el-button>
          </div>
          <div class="tree-container" v-loading="treeLoading">
            <el-tree
              ref="treeRef"
              :data="treeData"
              :props="treeProps"
              :expand-on-click-node="false"
              :check-on-click-node="true"
              show-checkbox
              node-key="id"
              class="folder-tree"
              @check="handleTreeCheck"
              @node-click="handleNodeClick"
            >
              <template #default="{ node, data }">
                <div class="tree-node">
                  <el-icon class="node-icon">
                    <Folder v-if="data.type === 'folder'" />
                    <Document v-else />
                  </el-icon>
                  <span class="node-label">{{ node.label }}</span>
                  <span class="node-count" v-if="data.type === 'folder' && data.fileCount">
                    ({{ data.fileCount }} 个文件)
                  </span>
                </div>
              </template>
            </el-tree>
          </div>
        </div>
        
        <div class="right-panel">
          <div class="panel-header">
            <h4>已选择的项目 ({{ selectedItems.length }})</h4>
            <el-button 
              type="text" 
              :icon="Delete" 
              @click="clearSelection"
              :disabled="selectedItems.length === 0"
            >
              清空
            </el-button>
          </div>
          <div class="selected-list">
            <div 
              v-for="item in selectedItems" 
              :key="item.id"
              class="selected-item"
            >
              <div class="item-info">
                <el-icon class="item-icon">
                  <Folder v-if="item.type === 'folder'" />
                  <Document v-else />
                </el-icon>
                <span class="item-name">{{ item.name }}</span>
                <span class="item-path">{{ item.path }}</span>
              </div>
              <el-button 
                type="text" 
                :icon="Close" 
                @click="removeSelectedItem(item.id)"
                class="remove-btn"
              />
            </div>
            
            <div v-if="selectedItems.length === 0" class="empty-selection">
              <el-empty description="请从左侧选择文件夹或文件" :image-size="80" />
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <div class="selection-summary">
            已选择 {{ selectedFolders.length }} 个文件夹，{{ selectedFiles.length }} 个文件
          </div>
          <div class="footer-buttons">
            <el-button @click="handleClose">取消</el-button>
            <el-button 
              type="primary" 
              @click="handleConfirm"
              :disabled="selectedItems.length === 0"
            >
              确认选择
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElTree, ElMessage } from 'element-plus'
import { Folder, Document, Refresh, Delete, Close } from '@element-plus/icons-vue'
import { getFileTreeApi } from '@@/apis/files'
import type { FileTreeNode } from '@@/apis/files/type'

interface Props {
  modelValue: boolean
  title?: string
  multiple?: boolean
  allowFiles?: boolean
  allowFolders?: boolean
}

interface SelectedItem {
  id: string
  name: string
  type: 'file' | 'folder'
  path: string
  data: FileTreeNode
}

const props = withDefaults(defineProps<Props>(), {
  title: '选择文件夹',
  multiple: true,
  allowFiles: true,
  allowFolders: true
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: [selectedItems: SelectedItem[]]
  cancel: []
}>()

// 对话框显示状态
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 树形数据
const treeRef = ref<InstanceType<typeof ElTree>>()
const treeData = ref<FileTreeNode[]>([])
const treeLoading = ref(false)
const selectedItems = ref<SelectedItem[]>([])

const treeProps = {
  children: 'children',
  label: 'name',
  isLeaf: (data: FileTreeNode) => data.type !== 'folder'
}

// 计算属性
const selectedFolders = computed(() => 
  selectedItems.value.filter(item => item.type === 'folder')
)

const selectedFiles = computed(() => 
  selectedItems.value.filter(item => item.type === 'file')
)

// 加载文件树
const loadFileTree = async () => {
  treeLoading.value = true
  try {
    const response = await getFileTreeApi()
    if (response.code === 0) {
      treeData.value = response.data
      // 计算文件夹中的文件数量
      calculateFileCount(treeData.value)
    } else {
      ElMessage.error(response.message || '加载文件树失败')
    }
  } catch (error) {
    console.error('加载文件树失败:', error)
    ElMessage.error('加载文件树失败')
  } finally {
    treeLoading.value = false
  }
}

// 计算文件夹中的文件数量
const calculateFileCount = (nodes: FileTreeNode[]) => {
  nodes.forEach(node => {
    if (node.type === 'folder' && node.children) {
      let fileCount = 0
      const countFiles = (children: FileTreeNode[]) => {
        children.forEach(child => {
          if (child.type === 'file') {
            fileCount++
          } else if (child.type === 'folder' && child.children) {
            countFiles(child.children)
          }
        })
      }
      countFiles(node.children)
      node.fileCount = fileCount
      calculateFileCount(node.children)
    }
  })
}

// 刷新树
const refreshTree = () => {
  loadFileTree()
}

// 构建节点路径
const buildNodePath = (nodeId: string, nodes: FileTreeNode[], currentPath = ''): string => {
  for (const node of nodes) {
    const nodePath = currentPath ? `${currentPath}/${node.name}` : node.name
    if (node.id === nodeId) {
      return nodePath
    }
    if (node.children) {
      const childPath = buildNodePath(nodeId, node.children, nodePath)
      if (childPath) return childPath
    }
  }
  return ''
}

// 获取节点数据
const findNodeData = (nodeId: string, nodes: FileTreeNode[]): FileTreeNode | null => {
  for (const node of nodes) {
    if (node.id === nodeId) {
      return node
    }
    if (node.children) {
      const found = findNodeData(nodeId, node.children)
      if (found) return found
    }
  }
  return null
}

// 树节点勾选事件
const handleTreeCheck = (data: FileTreeNode, checkState: any) => {
  const checkedKeys = checkState.checkedKeys as string[]
  const halfCheckedKeys = checkState.halfCheckedKeys as string[]
  
  // 更新选中项列表
  selectedItems.value = []
  
  // 添加完全选中的节点
  checkedKeys.forEach(key => {
    const nodeData = findNodeData(key, treeData.value)
    if (nodeData) {
      // 检查是否允许选择该类型
      if ((nodeData.type === 'folder' && props.allowFolders) || 
          (nodeData.type === 'file' && props.allowFiles)) {
        selectedItems.value.push({
          id: nodeData.id,
          name: nodeData.name,
          type: nodeData.type,
          path: buildNodePath(nodeData.id, treeData.value),
          data: nodeData
        })
      }
    }
  })
}

// 树节点点击事件
const handleNodeClick = (data: FileTreeNode) => {
  // 可以在这里添加节点点击的逻辑
}

// 移除选中项
const removeSelectedItem = (itemId: string) => {
  selectedItems.value = selectedItems.value.filter(item => item.id !== itemId)
  
  // 更新树的选中状态
  if (treeRef.value) {
    const checkedKeys = selectedItems.value.map(item => item.id)
    treeRef.value.setCheckedKeys(checkedKeys)
  }
}

// 清空选择
const clearSelection = () => {
  selectedItems.value = []
  if (treeRef.value) {
    treeRef.value.setCheckedKeys([])
  }
}

// 确认选择
const handleConfirm = () => {
  emit('confirm', selectedItems.value)
  handleClose()
}

// 关闭对话框
const handleClose = () => {
  emit('cancel')
  visible.value = false
}

// 监听对话框显示状态
watch(visible, (newVal) => {
  if (newVal) {
    nextTick(() => {
      loadFileTree()
    })
  } else {
    // 关闭时清空选择
    clearSelection()
  }
})
</script>

<style scoped>
.folder-selector {
  .selector-content {
    display: flex;
    height: 500px;
    border: 1px solid #ebeef5;
    border-radius: 4px;
  }
  
  .left-panel,
  .right-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  
  .left-panel {
    border-right: 1px solid #ebeef5;
  }
  
  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid #ebeef5;
    background-color: #fafafa;
    
    h4 {
      margin: 0;
      font-size: 14px;
      font-weight: 500;
    }
  }
  
  .tree-container {
    flex: 1;
    overflow: auto;
    padding: 8px;
  }
  
  .folder-tree {
    :deep(.el-tree-node__content) {
      height: 32px;
    }
    
    :deep(.el-tree-node__content:hover) {
      background-color: #f5f7fa;
    }
  }
  
  .tree-node {
    display: flex;
    align-items: center;
    width: 100%;
    
    .node-icon {
      margin-right: 8px;
      color: #606266;
    }
    
    .node-label {
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    
    .node-count {
      margin-left: 8px;
      font-size: 12px;
      color: #909399;
    }
  }
  
  .selected-list {
    flex: 1;
    overflow: auto;
    padding: 8px;
  }
  
  .selected-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    margin-bottom: 4px;
    background-color: #f5f7fa;
    border-radius: 4px;
    
    &:hover {
      background-color: #e6f7ff;
    }
    
    .item-info {
      display: flex;
      align-items: center;
      flex: 1;
      min-width: 0;
      
      .item-icon {
        margin-right: 8px;
        color: #606266;
      }
      
      .item-name {
        font-weight: 500;
        margin-right: 8px;
      }
      
      .item-path {
        font-size: 12px;
        color: #909399;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
    
    .remove-btn {
      margin-left: 8px;
      color: #f56c6c;
      
      &:hover {
        color: #f56c6c;
        background-color: transparent;
      }
    }
  }
  
  .empty-selection {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 200px;
  }
  
  .dialog-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .selection-summary {
      font-size: 14px;
      color: #606266;
    }
    
    .footer-buttons {
      display: flex;
      gap: 12px;
    }
  }
}
</style>