import { ChatSearchParams, MessageType } from '@/constants/chat';
import { fileIconMap } from '@/constants/common';
import {
  useFetchManualConversation,
  useFetchManualDialog,
  useFetchNextConversation,
  useFetchNextConversationList,
  useFetchNextDialog,
  useGetChatSearchParams,
  useRemoveNextConversation,
  useRemoveNextDialog,
  useSetNextDialog,
  useUpdateNextConversation,
} from '@/hooks/chat-hooks';
import {
  useSetModalState,
  useShowDeleteConfirm,
  useTranslate,
} from '@/hooks/common-hooks';
import {
  useRegenerateMessage,
  useSelectDerivedMessages,
  useSendMessageWithSse,
} from '@/hooks/logic-hooks';
import { IConversation, IDialog, Message } from '@/interfaces/database/chat';
import chatService from '@/services/chat-service';
import { getFileExtension } from '@/utils';
import api from '@/utils/api';
import { getConversationId } from '@/utils/chat';
import { useMutationState } from '@tanstack/react-query';
import { get } from 'lodash';
import trim from 'lodash/trim';
import {
  ChangeEventHandler,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { useSearchParams } from 'umi';
import { v4 as uuid } from 'uuid';
import {
  IClientConversation,
  IMessage,
  VariableTableDataType,
} from './interface';

export const useSetChatRouteParams = () => {
  const [currentQueryParameters, setSearchParams] = useSearchParams();
  const newQueryParameters: URLSearchParams = useMemo(
    () => new URLSearchParams(currentQueryParameters.toString()),
    [currentQueryParameters],
  );

  const setConversationIsNew = useCallback(
    (value: string) => {
      newQueryParameters.set(ChatSearchParams.isNew, value);
      setSearchParams(newQueryParameters);
    },
    [newQueryParameters, setSearchParams],
  );

  const getConversationIsNew = useCallback(() => {
    return newQueryParameters.get(ChatSearchParams.isNew);
  }, [newQueryParameters]);

  return { setConversationIsNew, getConversationIsNew };
};

export const useSetNewConversationRouteParams = () => {
  const [currentQueryParameters, setSearchParams] = useSearchParams();
  const newQueryParameters: URLSearchParams = useMemo(
    () => new URLSearchParams(currentQueryParameters.toString()),
    [currentQueryParameters],
  );

  const setNewConversationRouteParams = useCallback(
    (conversationId: string, isNew: string) => {
      newQueryParameters.set(ChatSearchParams.ConversationId, conversationId);
      newQueryParameters.set(ChatSearchParams.isNew, isNew);
      setSearchParams(newQueryParameters);
    },
    [newQueryParameters, setSearchParams],
  );

  return { setNewConversationRouteParams };
};

export const useSelectCurrentDialog = () => {
  const data = useMutationState({
    filters: { mutationKey: ['fetchDialog'] },
    select: (mutation) => {
      return get(mutation, 'state.data.data', {});
    },
  });

  return (data.at(-1) ?? {}) as IDialog;
};

export const useSelectPromptConfigParameters = (): VariableTableDataType[] => {
  const { data: currentDialog } = useFetchNextDialog();

  const finalParameters: VariableTableDataType[] = useMemo(() => {
    const parameters = currentDialog?.prompt_config?.parameters ?? [];
    if (!currentDialog.id) {
      // The newly created chat has a default parameter
      return [{ key: uuid(), variable: 'knowledge', optional: true }];
    }
    return parameters.map((x) => ({
      key: uuid(),
      variable: x.key,
      optional: x.optional,
    }));
  }, [currentDialog]);

  return finalParameters;
};

export const useDeleteDialog = () => {
  const showDeleteConfirm = useShowDeleteConfirm();

  const { removeDialog } = useRemoveNextDialog();

  const onRemoveDialog = (dialogIds: Array<string>) => {
    showDeleteConfirm({ onOk: () => removeDialog(dialogIds) });
  };

  return { onRemoveDialog };
};

export const useHandleItemHover = () => {
  const [activated, setActivated] = useState<string>('');

  const handleItemEnter = (id: string) => {
    setActivated(id);
  };

  const handleItemLeave = () => {
    setActivated('');
  };

  return {
    activated,
    handleItemEnter,
    handleItemLeave,
  };
};

export const useEditDialog = () => {
  const [dialog, setDialog] = useState<IDialog>({} as IDialog);
  const { fetchDialog } = useFetchManualDialog();
  const { setDialog: submitDialog, loading } = useSetNextDialog();

  const {
    visible: dialogEditVisible,
    hideModal: hideDialogEditModal,
    showModal: showDialogEditModal,
  } = useSetModalState();

  const hideModal = useCallback(() => {
    setDialog({} as IDialog);
    hideDialogEditModal();
  }, [hideDialogEditModal]);

  const onDialogEditOk = useCallback(
    async (dialog: IDialog) => {
      const ret = await submitDialog(dialog);

      if (ret === 0) {
        hideModal();
      }
    },
    [submitDialog, hideModal],
  );

  const handleShowDialogEditModal = useCallback(
    async (dialogId?: string) => {
      if (dialogId) {
        const ret = await fetchDialog(dialogId);
        if (ret.code === 0) {
          setDialog(ret.data);
        }
      }
      showDialogEditModal();
    },
    [showDialogEditModal, fetchDialog],
  );

  const clearDialog = useCallback(() => {
    setDialog({} as IDialog);
  }, []);

  return {
    dialogSettingLoading: loading,
    initialDialog: dialog,
    onDialogEditOk,
    dialogEditVisible,
    hideDialogEditModal: hideModal,
    showDialogEditModal: handleShowDialogEditModal,
    clearDialog,
  };
};

//#region conversation

export const useSelectDerivedConversationList = () => {
  const { t } = useTranslate('chat');

  const [list, setList] = useState<Array<IConversation>>([]);
  const { data: currentDialog } = useFetchNextDialog();
  const { data: conversationList, loading } = useFetchNextConversationList();
  const { dialogId } = useGetChatSearchParams();
  const prologue = currentDialog?.prompt_config?.prologue ?? '';
  const { setNewConversationRouteParams } = useSetNewConversationRouteParams();

  const addTemporaryConversation = useCallback(() => {
    const conversationId = getConversationId();
    setList((pre) => {
      if (dialogId) {
        setNewConversationRouteParams(conversationId, 'true');
        const nextList = [
          {
            id: conversationId,
            name: t('newConversation'),
            dialog_id: dialogId,
            is_new: true,
            message: [
              {
                content: prologue,
                role: MessageType.Assistant,
              },
            ],
          } as any,
          ...(Array.isArray(conversationList) ? conversationList : []),
        ];
        return nextList;
      }

      return pre;
    });
  }, [conversationList, dialogId, prologue, t, setNewConversationRouteParams]);

  // When you first enter the page, select the top conversation card

  useEffect(() => {
    if (Array.isArray(conversationList)) {
      setList([...conversationList]);
    }
  }, [conversationList]);

  return { list, addTemporaryConversation, loading };
};

export const useSetConversation = () => {
  const { dialogId } = useGetChatSearchParams();
  const { updateConversation } = useUpdateNextConversation();
  const { setDialog } = useSetNextDialog();

  const setConversation = useCallback(
    async (
      message: string,
      isNew: boolean = false,
      conversationId?: string,
    ) => {
      let actualDialogId = dialogId;

      // Handle agent dialogs - create RAGFlow dialog first if needed
      if (dialogId && dialogId.startsWith('agent_')) {
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
              // Parse kb_ids properly - it's heavily escaped in the database
              let kbIds = [];
              try {
                if (agent.kb_ids) {
                  // Try to parse the heavily escaped JSON string
                  let kbIdsStr = agent.kb_ids;
                  // Remove extra escaping layers
                  while (
                    typeof kbIdsStr === 'string' &&
                    kbIdsStr.startsWith('"') &&
                    kbIdsStr.endsWith('"')
                  ) {
                    kbIdsStr = JSON.parse(kbIdsStr);
                  }
                  if (Array.isArray(kbIdsStr)) {
                    kbIds = kbIdsStr;
                  } else if (typeof kbIdsStr === 'string') {
                    kbIds = JSON.parse(kbIdsStr);
                  }
                }
              } catch (error) {
                console.warn('Failed to parse kb_ids:', agent.kb_ids, error);
                kbIds = [];
              }

              // Create RAGFlow dialog from agent - use simplified structure
              const ragflowDialog = {
                name: agent.name,
                description: agent.description || '',
                icon: agent.avatar || '/assets/agent/Agent-icon.svg',
                kb_ids: kbIds,
                language: agent.language || 'zh',
                llm_id: agent.model_name || '',
                llm_setting: {
                  temperature: parseFloat(agent.temperature) || 0.1,
                  max_tokens: parseInt(agent.max_tokens) || 512,
                  top_p: parseFloat(agent.top_p) || 0.3,
                  frequency_penalty: parseFloat(agent.frequency_penalty) || 0.7,
                  presence_penalty: parseFloat(agent.presence_penalty) || 0.4,
                },
                prompt_config: {
                  system: agent.system_prompt || '',
                  prologue: agent.welcome_message || '',
                  empty_response:
                    agent.empty_response || '抱歉，我无法回答您的问题。',
                },
                tenant_id: agent.team_id || '',
                similarity_threshold:
                  parseFloat(agent.similarity_threshold) || 0.2,
                vector_similarity_weight:
                  parseFloat(agent.vector_similarity_weight) || 0.3,
                top_n: parseInt(agent.top_n) || 8,
              };

              console.log(
                '[DEBUG] Creating RAGFlow dialog from agent:',
                ragflowDialog,
              );

              // Create the dialog in RAGFlow system directly
              const { data: dialogResult } =
                await chatService.setDialog(ragflowDialog);
              if (dialogResult.code === 0) {
                console.log(
                  '[DEBUG] Successfully created RAGFlow dialog for agent:',
                  dialogResult,
                );
                // Use the newly created dialog ID if available
                if (dialogResult.data && dialogResult.data.dialog_id) {
                  actualDialogId = dialogResult.data.dialog_id;
                  console.log('[DEBUG] Using new dialog ID:', actualDialogId);
                } else {
                  console.log(
                    '[DEBUG] No dialog ID returned, using agent format',
                  );
                }
              } else {
                console.error(
                  '[DEBUG] Failed to create RAGFlow dialog:',
                  dialogResult,
                );
              }
            }
          }
        } catch (error) {
          console.warn('Failed to create RAGFlow dialog from agent:', error);
        }
      }

      const data = await updateConversation({
        dialog_id: actualDialogId,
        name: message,
        is_new: isNew,
        conversation_id: conversationId,
        message: [
          {
            role: MessageType.Assistant,
            content: message,
          },
        ],
      });

      return data;
    },
    [updateConversation, dialogId, setDialog],
  );

  return { setConversation };
};

export const useSelectNextMessages = () => {
  const {
    ref,
    setDerivedMessages,
    derivedMessages,
    addNewestAnswer,
    addNewestQuestion,
    removeLatestMessage,
    removeMessageById,
    removeMessagesAfterCurrentMessage,
  } = useSelectDerivedMessages();
  const { data: conversation, loading } = useFetchNextConversation();
  const { data: dialog } = useFetchNextDialog();
  const { conversationId, dialogId, isNew } = useGetChatSearchParams();

  const addPrologue = useCallback(() => {
    if (dialogId !== '' && isNew === 'true') {
      const prologue = dialog.prompt_config?.prologue;

      const nextMessage = {
        role: MessageType.Assistant,
        content: prologue,
        id: uuid(),
      } as IMessage;

      setDerivedMessages([nextMessage]);
    }
  }, [isNew, dialog, dialogId, setDerivedMessages]);

  useEffect(() => {
    addPrologue();
  }, [addPrologue]);

  useEffect(() => {
    if (
      conversationId &&
      isNew !== 'true' &&
      conversation.message?.length > 0
    ) {
      setDerivedMessages(conversation.message);
    }

    if (!conversationId) {
      setDerivedMessages([]);
    }
  }, [conversation.message, conversationId, setDerivedMessages, isNew]);

  return {
    ref,
    derivedMessages,
    loading,
    addNewestAnswer,
    addNewestQuestion,
    removeLatestMessage,
    removeMessageById,
    removeMessagesAfterCurrentMessage,
  };
};

export const useHandleMessageInputChange = () => {
  const [value, setValue] = useState('');

  const handleInputChange: ChangeEventHandler<HTMLTextAreaElement> = (e) => {
    const value = e.target.value;
    const nextValue = value.replaceAll('\\n', '\n').replaceAll('\\t', '\t');
    setValue(nextValue);
  };

  return {
    handleInputChange,
    value,
    setValue,
  };
};

export const useSendNextMessage = (controller: AbortController) => {
  const { setConversation } = useSetConversation();
  const { conversationId, isNew } = useGetChatSearchParams();
  const { handleInputChange, value, setValue } = useHandleMessageInputChange();
  const { data: dialog } = useFetchNextDialog(); // 在hook顶层获取dialog数据

  const { send, answer, done } = useSendMessageWithSse(
    api.completeConversation,
  );
  const {
    ref,
    derivedMessages,
    loading,
    addNewestAnswer,
    addNewestQuestion,
    removeLatestMessage,
    removeMessageById,
    removeMessagesAfterCurrentMessage,
  } = useSelectNextMessages();
  const { setConversationIsNew, getConversationIsNew } =
    useSetChatRouteParams();

  const stopOutputMessage = useCallback(() => {
    controller.abort();
  }, [controller]);

  const sendMessage = useCallback(
    async ({
      message,
      currentConversationId,
      messages,
    }: {
      message: Message;
      currentConversationId?: string;
      messages?: Message[];
    }) => {
      const res = await send(
        {
          conversation_id: currentConversationId ?? conversationId,
          messages: [...(messages ?? derivedMessages ?? []), message],
        },
        controller,
      );

      if (res && (res?.response.status !== 200 || res?.data?.code !== 0)) {
        // cancel loading
        setValue(message.content);
        console.info('removeLatestMessage111');
        removeLatestMessage();
      }
    },
    [
      derivedMessages,
      conversationId,
      removeLatestMessage,
      setValue,
      send,
      controller,
    ],
  );

  const handleSendMessage = useCallback(
    async (message: Message) => {
      const isNew = getConversationIsNew();

      if (isNew !== 'true') {
        sendMessage({ message });
      } else {
        const data = await setConversation(
          message.content,
          true,
          conversationId,
        );
        if (data.code === 0) {
          setConversationIsNew('');
          const id = data.data.id;
          sendMessage({
            message,
            currentConversationId: id,
            messages: data.data.message,
          });
        }
      }
    },
    [
      setConversation,
      sendMessage,
      setConversationIsNew,
      getConversationIsNew,
      conversationId,
    ],
  );

  const { regenerateMessage } = useRegenerateMessage({
    removeMessagesAfterCurrentMessage,
    sendMessage,
    messages: derivedMessages,
  });

  useEffect(() => {
    //  #1289
    if (answer.answer && conversationId && isNew !== 'true') {
      addNewestAnswer(answer);
    }
  }, [answer, addNewestAnswer, conversationId, isNew]);

  const handlePressEnter = useCallback(
    (documentIds: string[], tempFileIds?: string[], tempFileInfos?: any[]) => {
      if (trim(value) === '') return;
      const id = uuid();

      // 如果有临时文件，构建附件内容显示
      let displayContent = value;
      if (tempFileInfos && tempFileInfos.length > 0) {
        displayContent += '\n\n[附件内容]:\n';
        tempFileInfos.forEach((fileInfo) => {
          displayContent += `\n文件名: ${fileInfo.filename}\n内容: [文件内容已上传]\n`;
        });
      }

      addNewestQuestion({
        content: displayContent,
        doc_ids: documentIds,
        temp_file_ids: tempFileIds,
        id,
        role: MessageType.User,
      });
      if (done) {
        setValue('');
        handleSendMessage({
          id,
          content: value.trim(),
          role: MessageType.User,
          doc_ids: documentIds,
          temp_file_ids: tempFileIds,
        });
      }
    },
    [addNewestQuestion, handleSendMessage, done, setValue, value],
  );

  return {
    handlePressEnter,
    handleInputChange,
    value,
    setValue,
    regenerateMessage,
    sendLoading: !done,
    loading,
    ref,
    derivedMessages,
    removeMessageById,
    stopOutputMessage,
  };
};

export const useGetFileIcon = () => {
  const getFileIcon = (filename: string) => {
    const ext: string = getFileExtension(filename);
    const iconPath = fileIconMap[ext as keyof typeof fileIconMap];
    return `@/assets/svg/file-icon/${iconPath}`;
  };

  return getFileIcon;
};

export const useDeleteConversation = () => {
  const showDeleteConfirm = useShowDeleteConfirm();
  const { removeConversation } = useRemoveNextConversation();

  const deleteConversation = (conversationIds: Array<string>) => async () => {
    const ret = await removeConversation(conversationIds);

    return ret;
  };

  const onRemoveConversation = (conversationIds: Array<string>) => {
    showDeleteConfirm({ onOk: deleteConversation(conversationIds) });
  };

  return { onRemoveConversation };
};

export const useRenameConversation = () => {
  const [conversation, setConversation] = useState<IClientConversation>(
    {} as IClientConversation,
  );
  const { fetchConversation } = useFetchManualConversation();
  const {
    visible: conversationRenameVisible,
    hideModal: hideConversationRenameModal,
    showModal: showConversationRenameModal,
  } = useSetModalState();
  const { updateConversation, loading } = useUpdateNextConversation();

  const onConversationRenameOk = useCallback(
    async (name: string) => {
      const ret = await updateConversation({
        conversation_id: conversation.id,
        name,
        is_new: false,
      });

      if (ret.code === 0) {
        hideConversationRenameModal();
      }
    },
    [updateConversation, conversation, hideConversationRenameModal],
  );

  const handleShowConversationRenameModal = useCallback(
    async (conversationId: string) => {
      const ret = await fetchConversation(conversationId);
      if (ret.code === 0) {
        setConversation(ret.data);
      }
      showConversationRenameModal();
    },
    [showConversationRenameModal, fetchConversation],
  );

  return {
    conversationRenameLoading: loading,
    initialConversationName: conversation.name,
    onConversationRenameOk,
    conversationRenameVisible,
    hideConversationRenameModal,
    showConversationRenameModal: handleShowConversationRenameModal,
  };
};

export const useGetSendButtonDisabled = () => {
  const { dialogId, conversationId } = useGetChatSearchParams();

  return dialogId === '' || conversationId === '';
};

export const useSendButtonDisabled = (value: string) => {
  return trim(value) === '';
};

export const useCreateConversationBeforeUploadDocument = () => {
  const { setConversation } = useSetConversation();
  const { dialogId } = useGetChatSearchParams();
  const { getConversationIsNew } = useSetChatRouteParams();

  const createConversationBeforeUploadDocument = useCallback(
    async (message: string) => {
      const isNew = getConversationIsNew();
      if (isNew === 'true') {
        const data = await setConversation(message, true);

        return data;
      }
    },
    [setConversation, getConversationIsNew],
  );

  return {
    createConversationBeforeUploadDocument,
    dialogId,
  };
};
//#endregion
