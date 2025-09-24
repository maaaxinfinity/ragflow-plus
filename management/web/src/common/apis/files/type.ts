/**
 * 文件数据类型
 */
export interface FileData {
  /** 文件ID */
  id: string
  /** 文件名称 */
  name: string
  /** 文件大小(字节) */
  size: number
  /** 文件类型 */
  type: string
  /** 父文件夹ID */
  parent_id?: string
  /** 知识库ID */
  kb_id?: string
  /** 存储位置 */
  location: string
  /** 创建时间 */
  create_time?: number
  /** 更新时间 */
  update_time?: number
  /** 创建日期 */
  create_date?: string
  /** 子文件夹和文件（用于树形结构） */
  children?: FileData[]
  /** 是否展开（前端状态） */
  expanded?: boolean
}

/**
 * 文件夹数据类型
 */
export interface FolderData extends FileData {
  type: 'folder'
  children: FileData[]
}

/**
 * 文件树节点
 */
export interface FileTreeNode {
  /** 节点ID */
  id: string
  /** 节点名称 */
  name: string
  /** 节点类型 */
  type: 'file' | 'folder'
  /** 父节点ID */
  parent_id?: string
  /** 子节点 */
  children?: FileTreeNode[]
  /** 是否展开 */
  expanded?: boolean
  /** 是否选中 */
  checked?: boolean
  /** 原始文件数据 */
  data?: FileData
  /** 文件数量（用于文件夹） */
  fileCount?: number
}

/**
 * 文件列表结果
 */
export interface FileListResult {
  /** 文件列表 */
  list: FileData[]
  /** 总条数 */
  total: number
}

/**
 * 分页查询参数
 */
export interface PageQuery {
  /** 当前页码 */
  currentPage: number
  /** 每页条数 */
  size: number
  /** 排序字段 */
  sort_by: string
  /** 排序方式 */
  sort_order: string
}

/**
 * 分页结果
 */
export interface PageResult<T> {
  /** 数据列表 */
  list: T[]
  /** 总条数 */
  total: number
}

/**
 * 通用响应结构
 */
export interface ApiResponse<T> {
  /** 状态码 */
  code: number
  /** 响应数据 */
  data: T
  /** 响应消息 */
  message: string
}
