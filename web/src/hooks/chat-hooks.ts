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
import { useCallback, useMemo, useState } from 'react';
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
    queryKey: ['fetchDialogList'],
    initialData: [],
    gcTime: 0,
    refetchOnWindowFocus: false,
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

      // 获取管理系统的 agents，并过滤用户可访问的团队
      let managementAgents: any[] = [];
      try {
        const agentResponse = await fetch('/api/v1/agents');
        if (agentResponse.ok) {
          const agentResult = await agentResponse.json();
          const allAgents = agentResult.data?.list || [];
          // 只保留用户属于的团队的agents，或者team_id为"ALL"的agents
          managementAgents = allAgents.filter(
            (agent: any) =>
              agent.team_id === 'ALL' ||
              userTenants.length === 0 ||
              userTenants.includes(agent.team_id),
          );
        }
      } catch (error) {
        console.warn('Failed to fetch management agents:', error);
      }

      // 转换 agents 为 dialog 格式
      const convertedAgents: IDialog[] = managementAgents.map((agent: any) => ({
        id: `agent_${agent.id}`, // 添加前缀避免ID冲突
        dialog_id: `agent_${agent.id}`,
        name: agent.is_recommended ? `${agent.name} ⭐` : agent.name, // 为推荐agent添加星标
        description: agent.description || '',
        icon: agent.avatar || '/assets/agent/Agent-icon.svg', // 使用agent头像或默认图标
        kb_ids: agent.kb_ids || [],
        kb_names: agent.kb_names || [],
        language: 'zh',
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
          empty_response: agent.empty_response || '抱歉，我无法回答您的问题。',
          parameters: [{ key: 'knowledge', optional: false }],
        },
        prompt_type: 'simple',
        status: agent.status || 'active',
        tenant_id: agent.team_id || '',
        create_date: agent.create_date || '',
        create_time: agent.create_time || Date.now(),
        update_date: agent.update_date || '',
        update_time: agent.update_time || Date.now(),
        vector_similarity_weight: agent.vector_similarity_weight || 0.3,
        similarity_threshold: agent.similarity_threshold || 0.2,
        // 标记为来自管理系统
        source: 'management',
        team_id: agent.team_id,
        is_recommended: agent.is_recommended, // 保留推荐标识
      }));

      let allDialogs: IDialog[] = [];

      if (dialogData.code === 0) {
        const originalDialogs: IDialog[] = dialogData.data || [];
        allDialogs = [...originalDialogs, ...convertedAgents];

        if (allDialogs.length > 0) {
          if (allDialogs.every((x) => x.id !== dialogId)) {
            handleClickDialog(allDialogs[0].id);
          }
        } else {
          history.push('/chat');
        }
      } else {
        allDialogs = convertedAgents;
      }

      return allDialogs;
    },
  });

  return { data, loading, refetch };
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
      const { data } = await chatService.removeDialog({ dialogIds });
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
          // Fetch agent details from management API
          const agentResponse = await fetch('/api/v1/agents');
          if (agentResponse.ok) {
            const agentResult = await agentResponse.json();
            const allAgents = agentResult.data?.list || [];

            // Find the agent by matching the dialogId
            const agentId = dialogId.replace('agent_', '');
            const agent = allAgents.find((a: any) => a.id === agentId);

            if (agent) {
              // Create a conversation context for the agent
              return {
                id: conversationId,
                name: `与${agent.name}的对话`,
                avatar: agent.avatar || '/assets/agent/Agent-icon.svg',
                dialog_id: dialogId,
                message: [],
                reference: [],
                // Include agent context for future message handling
                agent_context: {
                  id: agent.id,
                  name: agent.name,
                  description: agent.description,
                  welcome_message: agent.welcome_message,
                  system_prompt: agent.system_prompt,
                  team_id: agent.team_id,
                  kb_ids: agent.kb_ids || [],
                  model_name: agent.model_name,
                },
              };
            }
          }
        } catch (error) {
          console.warn(
            'Failed to fetch agent details for new conversation:',
            error,
          );
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
