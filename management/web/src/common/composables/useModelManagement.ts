import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as ModelsApi from '@/common/apis/models'
import type * as Models from '@/common/apis/models/type'

// 管理员级别的模型管理hooks

export function useAllUserModels() {
  const loading = ref(false)
  const userModels = ref<Models.UserModelData[]>([])

  const fetchAllUserModels = async () => {
    loading.value = true
    try {
      const response = await ModelsApi.getAllUserModelsApi()
      if (response.code === 0) {
        userModels.value = response.data || []
      } else {
        ElMessage.error(response.message || '获取用户模型失败')
      }
    } catch (error) {
      ElMessage.error('获取用户模型失败')
      console.error('获取用户模型失败:', error)
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    userModels,
    fetchAllUserModels
  }
}

export function useModelFactories() {
  const loading = ref(false)
  const factories = ref<Models.ModelFactoryData[]>([])

  const fetchFactories = async () => {
    loading.value = true
    try {
      const response = await ModelsApi.getModelFactoriesApi()
      if (response.code === 0) {
        factories.value = response.data || []
      } else {
        ElMessage.error(response.message || '获取模型工厂失败')
      }
    } catch (error) {
      ElMessage.error('获取模型工厂失败')
      console.error('获取模型工厂失败:', error)
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    factories,
    fetchFactories
  }
}

export function useUserModels(userId?: string) {
  const loading = ref(false)
  const myLlmList = ref<Record<string, Models.LlmItemData>>({})
  const factoryList = ref<Models.ModelFactoryData[]>([])

  const fetchUserModels = async (targetUserId?: string) => {
    if (!targetUserId && !userId) {
      console.warn('需要提供用户ID')
      return
    }

    loading.value = true
    try {
      const response = await ModelsApi.getUserModelsApi({
        userId: targetUserId || userId!
      })
      if (response.code === 0) {
        myLlmList.value = response.data?.myLlmList || {}
        factoryList.value = response.data?.factoryList || []
      } else {
        ElMessage.error(response.message || '获取用户模型失败')
      }
    } catch (error) {
      ElMessage.error('获取用户模型失败')
      console.error('获取用户模型失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 转换为管理端需要的格式
  const llmList = computed(() => {
    return Object.entries(myLlmList.value).map(([key, value]) => ({
      ...value,
      name: key,
      llm: value.llm.map((x) => ({ ...x, name: x.name }))
    }))
  })

  const availableFactories = computed(() => {
    return factoryList.value.filter((x) =>
      Object.keys(myLlmList.value).every((y) => y !== x.name)
    )
  })

  return {
    loading,
    myLlmList,
    factoryList,
    llmList,
    availableFactories,
    fetchUserModels
  }
}

export function useAddUserModel() {
  const loading = ref(false)

  const addModel = async (params: Models.AddUserModelParams) => {
    loading.value = true
    try {
      const response = await ModelsApi.addUserModelApi(params)
      if (response.code === 0) {
        ElMessage.success('添加模型成功')
        return true
      } else {
        ElMessage.error(response.message || '添加模型失败')
        return false
      }
    } catch (error) {
      ElMessage.error('添加模型失败')
      console.error('添加模型失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    addModel
  }
}

export function useDeleteUserModel() {
  const loading = ref(false)

  const deleteModel = async (params: Models.DeleteUserModelParams) => {
    loading.value = true
    try {
      const response = await ModelsApi.deleteUserModelApi(params)
      if (response.code === 0) {
        ElMessage.success('删除模型成功')
        return true
      } else {
        ElMessage.error(response.message || '删除模型失败')
        return false
      }
    } catch (error) {
      ElMessage.error('删除模型失败')
      console.error('删除模型失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    deleteModel
  }
}

export function useDeleteUserFactory() {
  const loading = ref(false)

  const deleteFactory = async (params: Models.DeleteUserFactoryParams) => {
    loading.value = true
    try {
      const response = await ModelsApi.deleteUserFactoryApi(params)
      if (response.code === 0) {
        ElMessage.success('删除模型工厂成功')
        return true
      } else {
        ElMessage.error(response.message || '删除模型工厂失败')
        return false
      }
    } catch (error) {
      ElMessage.error('删除模型工厂失败')
      console.error('删除模型工厂失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    deleteFactory
  }
}

export function useSetUserApiKey() {
  const loading = ref(false)

  const setApiKey = async (params: Models.SetUserApiKeyParams) => {
    loading.value = true
    try {
      const response = await ModelsApi.setUserApiKeyApi(params)
      if (response.code === 0) {
        ElMessage.success('设置API Key成功')
        return true
      } else {
        ElMessage.error(response.message || '设置API Key失败')
        return false
      }
    } catch (error) {
      ElMessage.error('设置API Key失败')
      console.error('设置API Key失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    setApiKey
  }
}

export function useGlobalDefaultModels() {
  const loading = ref(false)
  const defaults = ref<Models.GlobalDefaultModelsData>({
    llm_id: '',
    embd_id: '',
    asr_id: '',
    img2txt_id: '',
    update_time: ''
  })

  const fetchDefaults = async () => {
    loading.value = true
    try {
      const response = await ModelsApi.getGlobalDefaultModelsApi()
      if (response.code === 0) {
        defaults.value = response.data || defaults.value
      } else {
        ElMessage.error(response.message || '获取全局默认模型失败')
      }
    } catch (error) {
      ElMessage.error('获取全局默认模型失败')
      console.error('获取全局默认模型失败:', error)
    } finally {
      loading.value = false
    }
  }

  const setDefaults = async (params: Models.SetGlobalDefaultModelsParams) => {
    loading.value = true
    try {
      const response = await ModelsApi.setGlobalDefaultModelsApi(params)
      if (response.code === 0) {
        ElMessage.success('设置全局默认模型成功')
        await fetchDefaults() // 重新获取最新数据
        return true
      } else {
        ElMessage.error(response.message || '设置全局默认模型失败')
        return false
      }
    } catch (error) {
      ElMessage.error('设置全局默认模型失败')
      console.error('设置全局默认模型失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    defaults,
    fetchDefaults,
    setDefaults
  }
}