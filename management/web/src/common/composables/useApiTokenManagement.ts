import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as ApiTokensApi from '@/common/apis/api-tokens'
import type * as ApiTokens from '@/common/apis/api-tokens/type'

// 管理员级别的API Token管理hooks

export function useAllApiTokens() {
  const loading = ref(false)
  const apiTokens = ref<ApiTokens.ApiTokenData[]>([])

  const fetchAllApiTokens = async () => {
    loading.value = true
    try {
      const response = await ApiTokensApi.getAllApiTokensApi()
      if (response.code === 0) {
        apiTokens.value = response.data || []
      } else {
        ElMessage.error(response.message || '获取API Token失败')
      }
    } catch (error) {
      ElMessage.error('获取API Token失败')
      console.error('获取API Token失败:', error)
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    apiTokens,
    fetchAllApiTokens
  }
}

export function useUserApiTokens(userId?: string) {
  const loading = ref(false)
  const userTokens = ref<ApiTokens.ApiTokenData[]>([])

  const fetchUserApiTokens = async (targetUserId?: string) => {
    if (!targetUserId && !userId) {
      console.warn('需要提供用户ID')
      return
    }

    loading.value = true
    try {
      const response = await ApiTokensApi.getUserApiTokensApi({
        userId: targetUserId || userId!
      })
      if (response.code === 0) {
        userTokens.value = response.data || []
      } else {
        ElMessage.error(response.message || '获取用户API Token失败')
      }
    } catch (error) {
      ElMessage.error('获取用户API Token失败')
      console.error('获取用户API Token失败:', error)
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    userTokens,
    fetchUserApiTokens
  }
}

export function useCreateApiToken() {
  const loading = ref(false)

  const createToken = async (params: ApiTokens.CreateUserApiTokenParams) => {
    loading.value = true
    try {
      const response = await ApiTokensApi.createUserApiTokenApi(params)
      if (response.code === 0) {
        ElMessage.success('创建API Token成功')
        return response.data
      } else {
        ElMessage.error(response.message || '创建API Token失败')
        return null
      }
    } catch (error) {
      ElMessage.error('创建API Token失败')
      console.error('创建API Token失败:', error)
      return null
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    createToken
  }
}

export function useDeleteApiToken() {
  const loading = ref(false)

  const deleteToken = async (params: ApiTokens.DeleteUserApiTokenParams) => {
    loading.value = true
    try {
      const response = await ApiTokensApi.deleteUserApiTokenApi(params)
      if (response.code === 0) {
        ElMessage.success('删除API Token成功')
        return true
      } else {
        ElMessage.error(response.message || '删除API Token失败')
        return false
      }
    } catch (error) {
      ElMessage.error('删除API Token失败')
      console.error('删除API Token失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    deleteToken
  }
}

export function useRegenerateApiToken() {
  const loading = ref(false)

  const regenerateToken = async (params: ApiTokens.RegenerateUserApiTokenParams) => {
    loading.value = true
    try {
      const response = await ApiTokensApi.regenerateUserApiTokenApi(params)
      if (response.code === 0) {
        ElMessage.success('重新生成API Token成功')
        return response.data
      } else {
        ElMessage.error(response.message || '重新生成API Token失败')
        return null
      }
    } catch (error) {
      ElMessage.error('重新生成API Token失败')
      console.error('重新生成API Token失败:', error)
      return null
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    regenerateToken
  }
}

export function useUpdateApiTokenStatus() {
  const loading = ref(false)

  const updateStatus = async (params: ApiTokens.UpdateUserApiTokenStatusParams) => {
    loading.value = true
    try {
      const response = await ApiTokensApi.updateUserApiTokenStatusApi(params)
      if (response.code === 0) {
        ElMessage.success('更新API Token状态成功')
        return true
      } else {
        ElMessage.error(response.message || '更新API Token状态失败')
        return false
      }
    } catch (error) {
      ElMessage.error('更新API Token状态失败')
      console.error('更新API Token状态失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    updateStatus
  }
}