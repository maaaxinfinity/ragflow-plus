<template>
  <div class="file-tree">
    <div class="tree-header">
      <el-button 
        type="primary" 
        :icon="FolderAdd" 
        size="small"
        @click="showCreateFolderDialog"
      >
        新建文件夹
      </el-button>
    </div>
    
    <el-tree
      ref="treeRef"
      :data="treeData"
      :props="treeProps"
      :expand-on-click-node="false"
      :check-on-click-node="true"
      :show-checkbox="showCheckbox"
      node-key="id"
      class="file-tree-container"
      @node-click="handleNodeClick"
      @check="handleNodeCheck"
    >
      <template #default="{ node, data }">
        <div class="tree-node">
          <el-icon class="node-icon">
            <Folder v-if="data.type === 'folder'" />
            <Document v-else />
          </el-icon>
          <span class="node-label">{{ node.label }}</span>
          <span class="node-size" v-if="data.type !== 'folder'">
            {{ formatFileSize(data.size) }}
          </span>
        </div>
      </template>
    </el-tree>

    <!-- 创建文件夹对话框 -->
    <el-dialog
      v-model="createFolderVisible"
      title="创建文件夹"
      width="400px"
      @close="resetCreateFolderForm"
    >
      <el-form :model="createFolderForm" :rules="createFolderRules" ref="createFolderFormRef">
        <el-form-item label="文件夹名称" prop="name">
          <el-input
            v-model="createFolderForm.name"
            placeholder="请输入文件夹名称"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="父文件夹">
          <el-select
            v-model="createFolderForm.parent_id"
            placeholder="选择父文件夹（留空为根目录）"
            clearable
            style="width: 100%"
          >
            <el-option label="根目录" value="" />
            <el-option
              v-for="folder in folderOptions"
              :key="folder.id"
              :label="folder.name"
              :value="folder.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="createFolderVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateFolder" :loading="createFolderLoading">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElTree, ElMessage, ElMessageBox } from 'element-plus'
import { FolderAdd, Folder, Document } from '@element-plus/icons-vue'
import { getFileTreeApi, createFolderApi } from '@@/apis/files'
import type { FileTreeNode } from '@@/apis/files/type'

interface Props {
  showCheckbox?: boolean
  selectable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showCheckbox: false,
  selectable: true
})

const emit = defineEmits<{
  nodeClick: [node: FileTreeNode]
  nodeCheck: [checkedNodes: FileTreeNode[], checkedKeys: string[]]
  folderChange: [folderId: string | null]
}>()

// 树形数据
const treeRef = ref<InstanceType<typeof ElTree>>()
const treeData = ref<FileTreeNode[]>([])
const treeProps = {
  children: 'children',
  label: 'name',
  isLeaf: (data: any) => data.type !== 'folder'
}

// 创建文件夹
const createFolderVisible = ref(false)
const createFolderLoading = ref(false)
const createFolderFormRef = ref()
const createFolderForm = reactive({
  name: '',
  parent_id: ''
})

const createFolderRules = {
  name: [
    { required: true, message: '请输入文件夹名称', trigger: 'blur' },
    { min: 1, max: 50, message: '文件夹名称长度在 1 到 50 个字符', trigger: 'blur' }
  ]
}

// 文件夹选项（用于创建文件夹时选择父目录）
const folderOptions = computed(() => {
  const folders: FileTreeNode[] = []
  
  const collectFolders = (nodes: FileTreeNode[], prefix = '') => {
    nodes.forEach(node => {
      if (node.type === 'folder') {
        folders.push({
          ...node,
          name: prefix + node.name
        })
        if (node.children) {
          collectFolders(node.children, prefix + node.name + '/')
        }
      }
    })
  }
  
  collectFolders(treeData.value)
  return folders
})

// 加载文件树
const loadFileTree = async (parentId?: string) => {
  try {
    const response = await getFileTreeApi(parentId)
    if (response.code === 0) {
      if (parentId) {
        // 如果是加载子节点，需要更新对应节点的children
        // 这里简化处理，重新加载整个树
        await loadFileTree()
      } else {
        treeData.value = response.data
      }
    } else {
      ElMessage.error(response.message || '加载文件树失败')
    }
  } catch (error) {
    console.error('加载文件树失败:', error)
    ElMessage.error('加载文件树失败')
  }
}

// 节点点击事件
const handleNodeClick = (data: FileTreeNode) => {
  emit('nodeClick', data)
  if (data.type === 'folder') {
    emit('folderChange', data.id)
  }
}

// 节点勾选事件
const handleNodeCheck = () => {
  if (!treeRef.value) return
  
  const checkedNodes = treeRef.value.getCheckedNodes() as FileTreeNode[]
  const checkedKeys = treeRef.value.getCheckedKeys() as string[]
  
  emit('nodeCheck', checkedNodes, checkedKeys)
}

// 显示创建文件夹对话框
const showCreateFolderDialog = () => {
  createFolderVisible.value = true
}

// 重置创建文件夹表单
const resetCreateFolderForm = () => {
  createFolderForm.name = ''
  createFolderForm.parent_id = ''
  createFolderFormRef.value?.resetFields()
}

// 创建文件夹
const handleCreateFolder = async () => {
  if (!createFolderFormRef.value) return
  
  try {
    await createFolderFormRef.value.validate()
    
    createFolderLoading.value = true
    
    const response = await createFolderApi(
      createFolderForm.name,
      createFolderForm.parent_id || undefined
    )
    
    if (response.code === 0) {
      ElMessage.success('创建文件夹成功')
      createFolderVisible.value = false
      resetCreateFolderForm()
      // 重新加载文件树
      await loadFileTree()
    } else {
      ElMessage.error(response.message || '创建文件夹失败')
    }
  } catch (error) {
    console.error('创建文件夹失败:', error)
    ElMessage.error('创建文件夹失败')
  } finally {
    createFolderLoading.value = false
  }
}

// 格式化文件大小
const formatFileSize = (size: number) => {
  if (size === undefined || size === null) {
    return 'N/A'
  }
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

// 获取选中的节点
const getCheckedNodes = () => {
  return treeRef.value?.getCheckedNodes() as FileTreeNode[] || []
}

// 获取选中的节点键
const getCheckedKeys = () => {
  return treeRef.value?.getCheckedKeys() as string[] || []
}

// 设置选中的节点
const setCheckedKeys = (keys: string[]) => {
  treeRef.value?.setCheckedKeys(keys)
}

// 暴露方法给父组件
defineExpose({
  loadFileTree,
  getCheckedNodes,
  getCheckedKeys,
  setCheckedKeys
})

// 初始化
onMounted(() => {
  loadFileTree()
})
</script>

<style scoped>
.file-tree {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.tree-header {
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
}

.file-tree-container {
  flex: 1;
  overflow: auto;
  padding: 8px;
}

.tree-node {
  display: flex;
  align-items: center;
  width: 100%;
}

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

.node-size {
  margin-left: 8px;
  font-size: 12px;
  color: #909399;
}

:deep(.el-tree-node__content) {
  height: 32px;
}

:deep(.el-tree-node__content:hover) {
  background-color: #f5f7fa;
}
</style>