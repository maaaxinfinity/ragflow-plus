import { request } from "@/http/axios"

export interface AgentData {
  id?: string
  name: string
  team_id: string
  team_name?: string
  description?: string
  model_name: string
  kb_ids?: string[]
  kb_names?: string[]
  system_prompt?: string
  welcome_message?: string
  is_default?: boolean
  status?: 'active' | 'inactive'
  create_time?: number
  create_date?: string
  update_time?: number
  update_date?: string
}

export interface AgentListParams {
  currentPage: number
  size: number
  team_id?: string
  name?: string
  sort_by?: string
  sort_order?: string
}

export interface AgentListResponse {
  list: AgentData[]
  total: number
}

/**
 * 获取Agent配置列表
 */
export function getAgentListApi(params: AgentListParams) {
  return request<{ data: AgentListResponse, code: number, message: string }>({
    url: "/api/v1/agents",
    method: "get",
    params
  })
}

/**
 * 获取Agent详情
 */
export function getAgentDetailApi(id: string) {
  return request<{ data: AgentData, code: number, message: string }>({
    url: `/api/v1/agents/${id}`,
    method: "get"
  })
}

/**
 * 创建Agent配置
 */
export function createAgentApi(data: Omit<AgentData, 'id'>) {
  return request<{ data: AgentData, code: number, message: string }>({
    url: "/api/v1/agents",
    method: "post",
    data
  })
}

/**
 * 更新Agent配置
 */
export function updateAgentApi(id: string, data: Partial<AgentData>) {
  return request<{ data: AgentData, code: number, message: string }>({
    url: `/api/v1/agents/${id}`,
    method: "put",
    data
  })
}

/**
 * 删除Agent配置
 */
export function deleteAgentApi(id: string) {
  return request<{ code: number, message: string }>({
    url: `/api/v1/agents/${id}`,
    method: "delete"
  })
}

/**
 * 设置默认Agent
 */
export function setDefaultAgentApi(id: string, isDefault: boolean) {
  return request<{ code: number, message: string }>({
    url: `/api/v1/agents/${id}/default`,
    method: "put",
    data: { is_default: isDefault }
  })
}

/**
 * 获取团队默认Agent
 */
export function getTeamDefaultAgentApi(teamId: string) {
  return request<{ data: AgentData | null, code: number, message: string }>({
    url: `/api/v1/agents/teams/${teamId}/default`,
    method: "get"
  })
}