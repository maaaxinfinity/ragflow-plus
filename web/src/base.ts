import isObject from 'lodash/isObject';
import { BaseState } from './interfaces/common';

// 定义 DvaModel 接口，替代从 umi 导入
interface DvaModel<T = any> {
  namespace?: string;
  state?: T;
  reducers?: Record<
    string,
    (state: T, action: { payload?: any; type?: string }) => T
  >;
  effects?: Record<string, any>;
  subscriptions?: Record<string, any>;
}

type State = Record<string, any>;
type DvaModelKey<T> = keyof DvaModel<T>;

export const modelExtend = <T>(
  baseModel: Partial<DvaModel<any>>,
  extendModel: DvaModel<any>,
): DvaModel<T> => {
  return Object.keys(extendModel).reduce<DvaModel<T>>((pre, cur) => {
    const baseValue = baseModel[cur as DvaModelKey<State>];
    const value = extendModel[cur as DvaModelKey<State>];

    if (isObject(value) && isObject(baseValue) && typeof value !== 'string') {
      const key = cur as Exclude<DvaModelKey<State>, 'namespace'>;

      pre[key] = {
        ...baseValue,
        ...value,
      } as any;
    } else {
      pre[cur as DvaModelKey<State>] = value as any;
    }

    return pre;
  }, {} as DvaModel<T>);
};

export const paginationModel: Partial<DvaModel<BaseState>> = {
  state: {
    searchString: '',
    pagination: {
      total: 0,
      current: 1,
      pageSize: 10,
    },
  },
  reducers: {
    setSearchString(
      state: BaseState,
      action: { payload?: any; type?: string },
    ) {
      return { ...state, searchString: action.payload };
    },
    setPagination(state: BaseState, action: { payload?: any; type?: string }) {
      return {
        ...state,
        pagination: { ...state.pagination, ...action.payload },
      };
    },
  },
};
