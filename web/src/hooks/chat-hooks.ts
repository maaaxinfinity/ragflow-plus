import { ChatSearchParams } from '@/constants/chat';
import {
  IConversation,
  IDialog,
  IStats,
  IToken,
} from '@/interfaces/database/chat';
import {
  IAskRequestBody,
  IFeedbackRequestBody,
} from '@/interfaces/request/chat';
import i18n from '@/locales/config';
import { IClientConversation } from '@/pages/chat/interface';
import { useGetSharedChatSearchParams } from '@/pages/chat/shared-hooks';
import chatService from '@/services/chat-service';
import {
  buildMessageListWithUuid,
  getConversationId,
  isConversationIdExist,
} from '@/utils/chat';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';
import dayjs, { Dayjs } from 'dayjs';
import { has, set } from 'lodash';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { history, useSearchParams } from 'umi';

//#region logic

export const useClickDialogCard = () => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [_, setSearchParams] = useSearchParams();

  const newQueryParameters: URLSearchParams = useMemo(() => {
    return new URLSearchParams();
  }, []);

  const handleClickDialog = useCallback(
    (dialogId: string) => {
      newQueryParameters.set(ChatSearchParams.DialogId, dialogId);
      // newQueryParameters.set(
      //   ChatSearchParams.ConversationId,
      //   EmptyConversationId,
      // );
      setSearchParams(newQueryParameters);
    },
    [newQueryParameters, setSearchParams],
  );

  return { handleClickDialog };
};

export const useClickConversationCard = () => {
  const [currentQueryParameters, setSearchParams] = useSearchParams();
  const newQueryParameters: URLSearchParams = useMemo(
    () => new URLSearchParams(currentQueryParameters.toString()),
    [currentQueryParameters],
  );

  const handleClickConversation = useCallback(
    (conversationId: string, isNew: string) => {
      newQueryParameters.set(ChatSearchParams.ConversationId, conversationId);
      newQueryParameters.set(ChatSearchParams.isNew, isNew);
      setSearchParams(newQueryParameters);
    },
    [setSearchParams, newQueryParameters],
  );

  return { handleClickConversation };
};

export const useGetChatSearchParams = () => {
  const [currentQueryParameters] = useSearchParams();

  const params = {
    dialogId: currentQueryParameters.get(ChatSearchParams.DialogId) || '',
    conversationId:
      currentQueryParameters.get(ChatSearchParams.ConversationId) || '',
    isNew: currentQueryParameters.get(ChatSearchParams.isNew) || '',
  };

  return params;
};

//#endregion

//#region dialog

export const useFetchNextDialogList = () => {
  const { handleClickDialog } = useClickDialogCard();
  const { dialogId } = useGetChatSearchParams();

  const {
    data,
    isFetching: loading,
    refetch,
  } = useQuery<IDialog[]>({
    queryKey: ['fetchDialogList', 'withManagementAgents'],
    initialData: [],
    gcTime: 0,
    staleTime: 0, // 确保数据总是新鲜的
    refetchOnWindowFocus: true, // 窗口聚焦时刷新
    refetchInterval: 30000, // 每30秒自动刷新一次
    queryFn: async (...params) => {
      console.log('🚀 ~ queryFn: ~ params:', params);

      // 获取原有的 dialogs
      const { data: dialogData } = await chatService.listDialog();

      // 从原有dialogs中获取用户可访问的租户ID
      let userTenants: string[] = [];
      if (dialogData && dialogData.code === 0 && dialogData.data) {
        const tenantIds = new Set(
          dialogData.data.map((d: any) => d.tenant_id).filter(Boolean),
        );
        userTenants = Array.from(tenantIds);
      }

      console.log('🔍 [DEBUG] User tenants:', userTenants);

      // 获取管理系统的 agents，并过滤用户可访问的团队
      let managementAgents: any[] = [];
      try {
        console.log('📡 [DEBUG] Fetching management agents...');
        const agentResponse = await fetch('/api/v1/agents');

        if (agentResponse.ok) {
          const agentResult = await agentResponse.json();
          console.log('📊 [DEBUG] Agent API response:', agentResult);

          const allAgents = agentResult.data?.list || [];
          console.log('👥 [DEBUG] All agents:', allAgents.length);

          // Agent权限检查逻辑：
          // 1. 'ALL'团队的Agent对所有用户可见
          // 2. 如果用户没有租户信息，显示所有Agent（兼容模式）
          // 3. 如果用户有租户信息，显示所属团队的Agent
          managementAgents = allAgents.filter((agent: any) => {
            const isAllTeam = agent.team_id === 'ALL';
            // 修改权限检查逻辑，更宽松地处理Agent访问
            const userHasAccess =
              userTenants.length === 0 || // 用户没有租户信息时允许访问
              userTenants.includes(agent.team_id) || // 用户属于Agent的团队
              isAllTeam; // ALL团队的Agent对所有人可见

            console.log(
              `🔐 [DEBUG] Agent ${agent.name}: team=${agent.team_id}, isAll=${isAllTeam}, hasAccess=${userHasAccess}`,
            );

            return userHasAccess;
          });

          console.log(
            '✅ [DEBUG] Filtered management agents:',
            managementAgents.length,
          );
        } else {
          console.error(
            '❌ [DEBUG] Agent API failed:',
            agentResponse.status,
            agentResponse.statusText,
          );
        }
      } catch (error) {
        console.error('❌ [DEBUG] Failed to fetch management agents:', error);
      }

      // 转换 agents 为 dialog 格式
      const convertedAgents: IDialog[] = managementAgents.map((agent: any) => {
        return {
          id: `agent_${agent.id}`, // 添加前缀避免ID冲突
          dialog_id: `agent_${agent.id}`,
          name:
            agent.is_recommended === 1 || agent.is_recommended === true
              ? `${agent.name} ⭐`
              : agent.name, // 为推荐agent添加星标
          description: agent.description || '',
          icon: agent.avatar || '/assets/agent/Agent-icon.svg', // 使用agent头像或默认图标
          kb_ids: agent.kb_ids || [],
          kb_names: agent.kb_names || [],
          language: agent.language === 'Chinese' ? 'zh' : 'en',
          llm_id: agent.model_name || '',
          llm_setting: {
            temperature: agent.temperature || 0.1,
            max_tokens: agent.max_tokens || 512,
            top_p: agent.top_p || 0.3,
            frequency_penalty: agent.frequency_penalty || 0.7,
            presence_penalty: agent.presence_penalty || 0.4,
          },
          llm_setting_type: 'Precise',
          prompt_config: {
            system: agent.system_prompt || '',
            prologue: agent.welcome_message || '',
            empty_response:
              agent.empty_response || '抱歉，我无法回答您的问题。',
            parameters: [{ key: 'knowledge', optional: false }],
          },
          prompt_type: 'simple',
          similarity_threshold: agent.similarity_threshold || 0.2,
          vector_similarity_weight: agent.vector_similarity_weight || 0.3,
          vector_keywords_weight: agent.vector_keywords_weight || 0.7,
          top_n: agent.top_n || 6,
          top_k: 1024,
          do_refer: '1',
          rerank_id: agent.rerank_enabled ? agent.rerank_model || '' : '',
          status: agent.status === 'active' ? '1' : '0', // 转换状态格式
          tenant_id: agent.team_id || '',
          create_date: agent.create_date || new Date().toISOString(),
          create_time: agent.create_time || Math.floor(Date.now() / 1000),
          update_date: agent.update_date || new Date().toISOString(),
          update_time: agent.update_time || Math.floor(Date.now() / 1000),
          // 标记为来自管理系统
          source: 'management',
          team_id: agent.team_id,
          is_recommended: agent.is_recommended, // 保留推荐标识
        };
      });

      let allDialogs: IDialog[] = [];

      if (dialogData?.code === 0) {
        const originalDialogs: IDialog[] = dialogData.data || [];
        allDialogs = [...originalDialogs, ...convertedAgents];

        console.log('🔗 [DEBUG] Combined dialogs:', {
          original: originalDialogs.length,
          management: convertedAgents.length,
          total: allDialogs.length,
        });

        if (allDialogs.length > 0) {
          if (allDialogs.every((x) => x.id !== dialogId)) {
            handleClickDialog(allDialogs[0].id);
          }
        } else {
          console.warn('⚠️ [DEBUG] No dialogs found, redirecting to chat');
          history.push('/chat');
        }
      } else {
        console.warn(
          '⚠️ [DEBUG] Dialog API failed, using management agents only',
        );
        allDialogs = convertedAgents;
      }

      console.log(
        '🚀 [DEBUG] Final dialog list:',
        allDialogs.map((d) => ({
          id: d.id,
          name: d.name,
          source: d.source || 'ragflow',
        })),
      );

      return allDialogs;
    },
  });

  // 监听management系统的agent更新事件
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'agent_updated') {
        console.log('🔄 [DEBUG] Agent updated event detected, refreshing...');
        refetch();
      }
    };

    // 同时监听自定义事件（用于同域内的实时更新）
    const handleCustomEvent = (e: Event) => {
      if ((e as CustomEvent).detail?.type === 'agent_updated') {
        console.log('🔄 [DEBUG] Agent custom event detected, refreshing...');
        refetch();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('agentUpdated', handleCustomEvent);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('agentUpdated', handleCustomEvent);
    };
  }, [refetch]);

  return { data, loading, refetch };
};

// 辅助函数：触发agent更新事件（供管理系统使用）
export const triggerAgentUpdate = () => {
  // 触发localStorage事件（跨标签页）
  localStorage.setItem('agent_updated', Date.now().toString());

  // 触发自定义事件（当前页面）
  window.dispatchEvent(
    new CustomEvent('agentUpdated', {
      detail: { type: 'agent_updated', timestamp: Date.now() },
    }),
  );

  console.log('🚀 [DEBUG] Agent update event triggered');
};

export const useFetchChatAppList = () => {
  const {
    data,
    isFetching: loading,
    refetch,
  } = useQuery<IDialog[]>({
    queryKey: ['fetchChatAppList'],
    initialData: [],
    gcTime: 0,
    refetchOnWindowFocus: false,
    queryFn: async () => {
      const { data } = await chatService.listDialog();

      return data?.data ?? [];
    },
  });

  return { data, loading, refetch };
};

export const useSetNextDialog = () => {
  const queryClient = useQueryClient();

  const {
    data,
    isPending: loading,
    mutateAsync,
  } = useMutation({
    mutationKey: ['setDialog'],
    mutationFn: async (params: IDialog) => {
      const { data } = await chatService.setDialog(params);
      if (data.code === 0) {
        queryClient.invalidateQueries({
          exact: false,
          queryKey: ['fetchDialogList'],
        });

        queryClient.invalidateQueries({
          queryKey: ['fetchDialog'],
        });
        message.success(
          i18n.t(`message.${params.dialog_id ? 'modified' : 'created'}`),
        );
      }
      return data?.code;
    },
  });

  return { data, loading, setDialog: mutateAsync };
};

export const useFetchNextDialog = () => {
  const { dialogId } = useGetChatSearchParams();

  const {
    data,
    isFetching: loading,
    refetch,
  } = useQuery<IDialog>({
    queryKey: ['fetchDialog', dialogId],
    gcTime: 0,
    initialData: {} as IDialog,
    enabled: !!dialogId,
    refetchOnWindowFocus: false,
    queryFn: async () => {
      const { data } = await chatService.getDialog({ dialogId });

      return data?.data ?? ({} as IDialog);
    },
  });

  return { data, loading, refetch };
};

export const useFetchManualDialog = () => {
  const {
    data,
    isPending: loading,
    mutateAsync,
  } = useMutation({
    mutationKey: ['fetchManualDialog'],
    gcTime: 0,
    mutationFn: async (dialogId: string) => {
      const { data } = await chatService.getDialog({ dialogId });

      return data;
    },
  });

  return { data, loading, fetchDialog: mutateAsync };
};

export const useRemoveNextDialog = () => {
  const queryClient = useQueryClient();

  const {
    data,
    isPending: loading,
    mutateAsync,
  } = useMutation({
    mutationKey: ['removeDialog'],
    mutationFn: async (dialogIds: string[]) => {
      // 检查是否有management系统的agent
      const managementDialogs = dialogIds.filter((id) =>
        id.startsWith('agent_'),
      );
      const regularDialogs = dialogIds.filter((id) => !id.startsWith('agent_'));

      if (managementDialogs.length > 0) {
        message.error(
          '管理系统创建的Agent无法在此处删除，请前往管理系统���行删除',
        );
        return -1; // 返回错误码
      }

      if (regularDialogs.length === 0) {
        return 0; // 没有需要删除的dialog
      }

      const { data } = await chatService.removeDialog({
        dialogIds: regularDialogs,
      });
      if (data.code === 0) {
        queryClient.invalidateQueries({ queryKey: ['fetchDialogList'] });

        message.success(i18n.t('message.deleted'));
      }
      return data.code;
    },
  });

  return { data, loading, removeDialog: mutateAsync };
};

//#endregion

//#region conversation

export const useFetchNextConversationList = () => {
  const { dialogId } = useGetChatSearchParams();
  const { handleClickConversation } = useClickConversationCard();
  const {
    data,
    isFetching: loading,
    refetch,
  } = useQuery<IConversation[]>({
    queryKey: ['fetchConversationList', dialogId],
    initialData: [],
    gcTime: 0,
    refetchOnWindowFocus: false,
    enabled: !!dialogId,
    queryFn: async () => {
      const { data } = await chatService.listConversation({ dialogId });
      if (data.code === 0) {
        if (data.data.length > 0) {
          handleClickConversation(data.data[0].id, '');
        } else {
          handleClickConversation('', '');
        }
      }
      return data?.data;
    },
  });

  return { data, loading, refetch };
};

export const useFetchNextConversation = () => {
  const { isNew, conversationId, dialogId } = useGetChatSearchParams();
  const { sharedId } = useGetSharedChatSearchParams();
  const queryClient = useQueryClient();
  const {
    data,
    isFetching: loading,
    refetch,
  } = useQuery<IClientConversation>({
    queryKey: ['fetchConversation', conversationId],
    initialData: {} as IClientConversation,
    // enabled: isConversationIdExist(conversationId),
    gcTime: 0,
    refetchOnWindowFocus: false,
    queryFn: async () => {
      if (
        isNew !== 'true' &&
        isConversationIdExist(sharedId || conversationId)
      ) {
        const { data } = await chatService.getConversation({
          conversationId: conversationId || sharedId,
        });

        const conversation = data?.data ?? {};

        const messageList = buildMessageListWithUuid(conversation?.message);

        return { ...conversation, message: messageList };
      }

      // Handle new conversations for agent dialogs
      if (isNew === 'true' && dialogId && dialogId.startsWith('agent_')) {
        try {
          // Create a new conversation via backend API first
          // 使用固定的新对话标题
          const newConversationName = '新对话';

          console.log('[DEBUG] Creating conversation:', {
            conversation_id: conversationId,
            dialog_id: dialogId,
            name: newConversationName,
          });

          const createResponse = await chatService.setConversation({
            conversation_id: conversationId,
            dialog_id: dialogId,
            name: newConversationName,
            is_new: true, // 明确指定这是新建对话
          });

          console.log('[DEBUG] Create conversation response:', createResponse);

          if (createResponse?.data?.code === 0) {
            // Now fetch the created conversation
            const { data: fetchResponse } = await chatService.getConversation({
              conversationId,
            });

            if (fetchResponse?.code === 0) {
              const conversation = fetchResponse.data ?? {};
              const messageList = buildMessageListWithUuid(
                conversation?.message,
              );

              // 刷新对话列表缓存，确保新对话立即显示
              queryClient.invalidateQueries({
                queryKey: ['fetchConversationList', dialogId],
              });

              return { ...conversation, message: messageList };
            }
          }

          // Fallback: if backend creation fails, create a temporary conversation
          console.warn(
            'Failed to create conversation via backend, using fallback',
          );
          const agentResponse = await fetch('/api/v1/agents');
          if (agentResponse.ok) {
            const agentResult = await agentResponse.json();
            const allAgents = agentResult.data?.list || [];

            const agentId = dialogId.replace('agent_', '');
            const agent = allAgents.find((a: any) => a.id === agentId);

            if (agent) {
              // 刷新对话列表缓存，确保fallback对话也能显示
              queryClient.invalidateQueries({
                queryKey: ['fetchConversationList', dialogId],
              });

              return {
                id: conversationId,
                name: `与${agent.name}的对话`,
                avatar: agent.avatar || '/assets/agent/Agent-icon.svg',
                dialog_id: dialogId,
                message: [],
                reference: [],
              };
            }
          }
        } catch (error) {
          console.warn('Failed to handle new agent conversation:', error);
        }
      }

      return { message: [] };
    },
  });

  return { data, loading, refetch };
};

export const useFetchNextConversationSSE = () => {
  const { isNew } = useGetChatSearchParams();
  const { sharedId } = useGetSharedChatSearchParams();
  const {
    data,
    isFetching: loading,
    refetch,
  } = useQuery<IClientConversation>({
    queryKey: ['fetchConversationSSE', sharedId],
    initialData: {} as IClientConversation,
    gcTime: 0,
    refetchOnWindowFocus: false,
    queryFn: async () => {
      if (isNew !== 'true' && isConversationIdExist(sharedId || '')) {
        if (!sharedId) return {};
        const { data } = await chatService.getConversationSSE({}, sharedId);
        const conversation = data?.data ?? {};
        const messageList = buildMessageListWithUuid(conversation?.message);
        return { ...conversation, message: messageList };
      }
      return { message: [] };
    },
  });

  return { data, loading, refetch };
};

export const useFetchManualConversation = () => {
  const {
    data,
    isPending: loading,
    mutateAsync,
  } = useMutation({
    mutationKey: ['fetchManualConversation'],
    gcTime: 0,
    mutationFn: async (conversationId: string) => {
      const { data } = await chatService.getConversation({ conversationId });

      return data;
    },
  });

  return { data, loading, fetchConversation: mutateAsync };
};

export const useUpdateNextConversation = () => {
  const queryClient = useQueryClient();
  const {
    data,
    isPending: loading,
    mutateAsync,
  } = useMutation({
    mutationKey: ['updateConversation'],
    mutationFn: async (params: Record<string, any>) => {
      const { data } = await chatService.setConversation({
        ...params,
        conversation_id: params.conversation_id
          ? params.conversation_id
          : getConversationId(),
      });
      if (data.code === 0) {
        queryClient.invalidateQueries({ queryKey: ['fetchConversationList'] });
        message.success(i18n.t(`message.modified`));
      }
      return data;
    },
  });

  return { data, loading, updateConversation: mutateAsync };
};

export const useRemoveNextConversation = () => {
  const queryClient = useQueryClient();
  const { dialogId } = useGetChatSearchParams();

  const {
    data,
    isPending: loading,
    mutateAsync,
  } = useMutation({
    mutationKey: ['removeConversation'],
    mutationFn: async (conversationIds: string[]) => {
      const { data } = await chatService.removeConversation({
        conversationIds,
        dialogId,
      });
      if (data.code === 0) {
        queryClient.invalidateQueries({ queryKey: ['fetchConversationList'] });
      }
      return data.code;
    },
  });

  return { data, loading, removeConversation: mutateAsync };
};

export const useDeleteMessage = () => {
  const { conversationId } = useGetChatSearchParams();

  const {
    data,
    isPending: loading,
    mutateAsync,
  } = useMutation({
    mutationKey: ['deleteMessage'],
    mutationFn: async (messageId: string) => {
      const { data } = await chatService.deleteMessage({
        messageId,
        conversationId,
      });

      if (data.code === 0) {
        message.success(i18n.t(`message.deleted`));
      }

      return data.code;
    },
  });

  return { data, loading, deleteMessage: mutateAsync };
};

export const useFeedback = () => {
  const { conversationId } = useGetChatSearchParams();

  const {
    data,
    isPending: loading,
    mutateAsync,
  } = useMutation({
    mutationKey: ['feedback'],
    mutationFn: async (params: IFeedbackRequestBody) => {
      const { data } = await chatService.thumbup({
        ...params,
        conversationId,
      });
      if (data.code === 0) {
        message.success(i18n.t(`message.operated`));
      }
      return data.code;
    },
  });

  return { data, loading, feedback: mutateAsync };
};

//#endregion

// #region API provided for external calls

export const useCreateNextToken = () => {
  const queryClient = useQueryClient();
  const {
    data,
    isPending: loading,
    mutateAsync,
  } = useMutation({
    mutationKey: ['createToken'],
    mutationFn: async (params: Record<string, any>) => {
      const { data } = await chatService.createToken(params);
      if (data.code === 0) {
        queryClient.invalidateQueries({ queryKey: ['fetchTokenList'] });
      }
      return data?.data ?? [];
    },
  });

  return { data, loading, createToken: mutateAsync };
};

export const useFetchTokenList = (params: Record<string, any>) => {
  const {
    data,
    isFetching: loading,
    refetch,
  } = useQuery<IToken[]>({
    queryKey: ['fetchTokenList', params],
    initialData: [],
    gcTime: 0,
    queryFn: async () => {
      const { data } = await chatService.listToken(params);

      return data?.data ?? [];
    },
  });

  return { data, loading, refetch };
};

export const useRemoveNextToken = () => {
  const queryClient = useQueryClient();
  const {
    data,
    isPending: loading,
    mutateAsync,
  } = useMutation({
    mutationKey: ['removeToken'],
    mutationFn: async (params: {
      tenantId: string;
      dialogId?: string;
      tokens: string[];
    }) => {
      const { data } = await chatService.removeToken(params);
      if (data.code === 0) {
        queryClient.invalidateQueries({ queryKey: ['fetchTokenList'] });
      }
      return data?.data ?? [];
    },
  });

  return { data, loading, removeToken: mutateAsync };
};

type RangeValue = [Dayjs | null, Dayjs | null] | null;

const getDay = (date?: Dayjs) => date?.format('YYYY-MM-DD');

export const useFetchNextStats = () => {
  const [pickerValue, setPickerValue] = useState<RangeValue>([
    dayjs().subtract(7, 'day'),
    dayjs(),
  ]);
  const { data, isFetching: loading } = useQuery<IStats>({
    queryKey: ['fetchStats', pickerValue],
    initialData: {} as IStats,
    gcTime: 0,
    queryFn: async () => {
      if (Array.isArray(pickerValue) && pickerValue[0]) {
        const { data } = await chatService.getStats({
          fromDate: getDay(pickerValue[0]),
          toDate: getDay(pickerValue[1] ?? dayjs()),
        });
        return data?.data ?? {};
      }
      return {};
    },
  });

  return { data, loading, pickerValue, setPickerValue };
};

//#endregion

//#region shared chat

export const useCreateNextSharedConversation = () => {
  const {
    data,
    isPending: loading,
    mutateAsync,
  } = useMutation({
    mutationKey: ['createSharedConversation'],
    mutationFn: async (userId?: string) => {
      const { data } = await chatService.createExternalConversation({ userId });

      return data;
    },
  });

  return { data, loading, createSharedConversation: mutateAsync };
};

// deprecated
export const useFetchNextSharedConversation = (
  conversationId?: string | null,
) => {
  const { data, isPending: loading } = useQuery({
    queryKey: ['fetchSharedConversation'],
    enabled: !!conversationId,
    queryFn: async () => {
      if (!conversationId) {
        return {};
      }
      const { data } = await chatService.getExternalConversation(
        null,
        conversationId,
      );

      const messageList = buildMessageListWithUuid(data?.data?.message);

      set(data, 'data.message', messageList);

      return data;
    },
  });

  return { data, loading };
};

//#endregion

//#region search page

export const useFetchMindMap = () => {
  const {
    data,
    isPending: loading,
    mutateAsync,
  } = useMutation({
    mutationKey: ['fetchMindMap'],
    gcTime: 0,
    mutationFn: async (params: IAskRequestBody) => {
      try {
        const ret = await chatService.getMindMap(params);
        return ret?.data?.data ?? {};
      } catch (error: any) {
        if (has(error, 'message')) {
          message.error(error.message);
        }

        return [];
      }
    },
  });

  return { data, loading, fetchMindMap: mutateAsync };
};

export const useFetchRelatedQuestions = () => {
  const {
    data,
    isPending: loading,
    mutateAsync,
  } = useMutation({
    mutationKey: ['fetchRelatedQuestions'],
    gcTime: 0,
    mutationFn: async (question: string): Promise<string[]> => {
      const { data } = await chatService.getRelatedQuestions({ question });

      return data?.data ?? [];
    },
  });

  return { data, loading, fetchRelatedQuestions: mutateAsync };
};
//#endregion
