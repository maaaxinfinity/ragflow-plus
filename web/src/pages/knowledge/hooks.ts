import { KnowledgeRouteKey } from '@/constants/knowledge';
import { useSetModalState } from '@/hooks/common-hooks';
import { useCreateKnowledge } from '@/hooks/knowledge-hooks';
import { useCallback, useState } from 'react';
import { useNavigate } from 'umi';

export const useSearchKnowledge = () => {
  const [searchString, setSearchString] = useState<string>('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchString(e.target.value);
  };
  return {
    searchString,
    handleInputChange,
  };
};

export const useSaveKnowledge = () => {
  const { visible: visible, hideModal, showModal } = useSetModalState();
  const { loading, createKnowledge } = useCreateKnowledge();
  const navigate = useNavigate();

  const onCreateOk = useCallback(
    async (name: string) => {
      const ret = await createKnowledge({
        name,
        avatar:
          'PD94bWwgdmVyc2lvbj0iMS4wIiBzdGFuZGFsb25lPSJubyI/PjwhRE9DVFlQRSBzdmcgUFVCTElDICItLy9XM0MvL0RURCBTVkcgMS4xLy9FTiIgImh0dHA6Ly93d3cudzMub3JnL0dyYXBoaWNzL1NWRy8xLjEvRFREL3N2ZzExLmR0ZCI+PHN2ZyB0PSIxNzIzODA5NjI3NTQ4IiBjbGFzcz0iaWNvbiIgdmlld0JveD0iMCAwIDEwMjQgMTAyNCIgdmVyc2lvbj0iMS4xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHAtaWQ9IjQzNDYiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB3aWR0aD0iNjQiIGhlaWdodD0iNjQiPjxwYXRoIGQ9Ik05MjcuODk5MjE4IDgxMi44NjI5MTFhNDguOTE2Nzc2IDQ4LjkxNjc3NiAwIDAgMCA0Ny42Nzk5OTctNDguNzg4ODM0VjQ4Ljc4ODgzNEE0OC45MTY3NzYgNDguOTE2Nzc2IDAgMCAwIDkyNy44OTkyMTggMEgyNDQuNDcxNzE5QTE2MS4yNTA1MDcgMTYxLjI1MDUwNyAwIDAgMCA4NS41MjQxODEgMTYyLjU3MjU4MnY3MTUuMzI3ODkxQTE0Ny4zNDczOTUgMTQ3LjM0NzM5NSAwIDAgMCAyNDQuNDcxNzE5IDEwMjMuNTQxOTY1aDY4My40Mjc0OTljMjUuODQ0NDM1IDAgNDcuNjc5OTk3LTEzLjMwNjA0NiA0Ny42Nzk5OTctMzkuNzQ3NTQ2YTQyLjY0NzU4MiA0Mi42NDc1ODIgMCAwIDAtNDcuNjc5OTk3LTQwLjg1NjM4NGgtMjguNTczODc5di0xMzAuMDc1MTI0eiBtLTExMS4yNjc1NDEgMTMwLjA3NTEyNEgyMjYuMjYxMjAxYTY1LjAzNzU2MiA2NS4wMzc1NjIgMCAwIDEgMC0xMzAuMDc1MTI0aDU5MC4zNzA0NzZ6IG04Mi42OTM2NjItMjA2LjM3MTY0OEgyNDQuNDcxNzE5YTIyMC45MTQ0NzQgMjIwLjkxNDQ3NCAwIDAgMC04MS43MTI3NjcgMTAuMzIwNzE0VjE1OC42NDkwMDVjMC0zNi41OTE2MjUgMjcuODA2MjIzLTg2Ljc0NTE4MiA2My41ODc1NDUtODYuNzQ1MTgybDY3My4wMjE0ODkgMy45MjM1Nzh6IiBmaWxsPSIjQjI3QkRGIiBwLWlkPSI0MzQ3Ij48L3BhdGg+PHBhdGggZD0iTTY2NC43MjA5OTEgMjM1LjQ1NzNsLTY1Ljg0Nzg2NyAyMi4xMzQwOTVhMTMuMjIwNzUgMTMuMjIwNzUgMCAwIDAtNC4yNjQ3NTggNy4zNzgwMzEgMTMuMjIwNzUgMTMuMjIwNzUgMCAwIDAgNC4yNjQ3NTggNy4zNzgwMzJsNjUuODQ3ODY3IDIyLjA5MTQ0NyAyNi4zNTYyMDUgNTUuMjI4NjE5YTE4LjA4MjU3NSAxOC4wODI1NzUgMCAwIDAgOC43ODU0MDIgMy42Njc2OTIgMTguMDgyNTc1IDE4LjA4MjU3NSAwIDAgMCA4Ljc4NTQwMi0zLjY2NzY5MmwyNi4zMTM1NTgtNTUuMzEzOTE0IDY1Ljk3NTgwOS0yMi4wOTE0NDdhMTMuMjIwNzUgMTMuMjIwNzUgMCAwIDAgNC4yNjQ3NTgtNy4zNzgwMzIgMTMuMjIwNzUgMTMuMjIwNzUgMCAwIDAtNC4yNjQ3NTgtNy4yOTI3MzZsLTY1Ljk3NTgwOS0yMi4xMzQwOTUtMjYuMzEzNTU4LTU1LjIyODYxOWExOC4wODI1NzUgMTguMDgyNTc1IDAgMCAwLTguNzg1NDAyLTMuNjY3NjkyIDE4LjA4MjU3NSAxOC4wODI1NzUgMCAwIDAtOC43ODU0MDIgMy42Njc2OTJ6IG0tMjEwLjY3OTA1NSA4OC4zMjMxNDJhMTguNTA5MDUxIDE4LjUwOTA1MSAwIDAgMC0xMy4xNzgxMDMgNy4zNzgwMzFMMzk0Ljc2MTc5NyA0MjEuMzU4MTA5djEuODMzODQ2bC0xMDcuNTU3MjAxIDM2LjgwNDg2M2ExNS4yNjc4MzQgMTUuMjY3ODM0IDAgMCAwLTguNzg1NDAyIDExLjA0NTcyNCAxNS4yNjc4MzQgMTUuMjY3ODM0IDAgMCAwIDguNzg1NDAyIDExLjA0NTcyNGwxMDcuNTU3MjAxIDM4LjYzODcwOSA0Ni4xMDIwMzYgOTAuMTk5NjM1YTE1LjQzODQyNSAxNS40Mzg0MjUgMCAwIDAgMjYuMzU2MjA2IDBsNDYuMDU5Mzg4LTkwLjE5OTYzNSAxMDcuNTU3MjAyLTM4LjYzODcwOWExNS4yNjc4MzQgMTUuMjY3ODM0IDAgMCAwIDguNzg1NDAyLTExLjI1ODk2MiAxNS4yNjc4MzQgMTUuMjY3ODM0IDAgMCAwLTguNzg1NDAyLTExLjA0NTcyNGwtMTA3LjU1NzIwMi0zNi41OTE2MjVWNDIxLjM1ODEwOWwtNDYuMTAyMDM2LTkwLjE5OTYzNmExOC41MDkwNTEgMTguNTA5MDUxIDAgMCAwLTEzLjEzNTQ1NS03LjM3ODAzMXoiIGZpbGw9IiNEODM2RkYiIHAtaWQ9IjQzNDgiPjwvcGF0aD48L3N2Zz4=',
      });

      if (ret?.code === 0) {
        hideModal();
        navigate(
          `/knowledge/${KnowledgeRouteKey.Configuration}?id=${ret.data.kb_id}`,
        );
      }
    },
    [createKnowledge, hideModal, navigate],
  );

  return {
    loading,
    onCreateOk,
    visible,
    hideModal,
    showModal,
  };
};
