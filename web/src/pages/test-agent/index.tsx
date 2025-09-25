import { useFetchNextDialogList } from '@/hooks/chat-hooks';
import { Card, Spin, Typography } from 'antd';
import { useEffect } from 'react';

const { Title, Text } = Typography;

const TestAgent = () => {
  const { data: dialogList, loading } = useFetchNextDialogList();

  useEffect(() => {
    console.log('Dialog List:', dialogList);
  }, [dialogList]);

  return (
    <div style={{ padding: '20px' }}>
      <Title level={2}>Agent 整合测试页面</Title>

      <Card title="Dialog 列表" style={{ marginTop: '20px' }}>
        {loading ? (
          <Spin size="large" />
        ) : (
          <div>
            <Text>总数: {dialogList?.length || 0}</Text>
            {dialogList?.map((dialog) => (
              <Card
                key={dialog.id}
                size="small"
                style={{ marginTop: '10px' }}
                title={dialog.name}
              >
                <p>
                  <strong>ID:</strong> {dialog.id}
                </p>
                <p>
                  <strong>描述:</strong> {dialog.description}
                </p>
                <p>
                  <strong>来源:</strong> {(dialog as any).source || 'original'}
                </p>
                <p>
                  <strong>团队ID:</strong> {(dialog as any).team_id || 'N/A'}
                </p>
                <p>
                  <strong>模型:</strong> {dialog.llm_id}
                </p>
                <p>
                  <strong>系统提示:</strong>{' '}
                  {dialog.prompt_config?.system || 'N/A'}
                </p>
                <p>
                  <strong>欢迎语:</strong>{' '}
                  {dialog.prompt_config?.prologue || 'N/A'}
                </p>
              </Card>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};

export default TestAgent;
