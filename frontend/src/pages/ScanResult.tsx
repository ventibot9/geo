import { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Tag,
  Space,
  Button,
  Input,
  Select,
  Modal,
  Descriptions,
  Progress,
} from 'antd';
import { EyeOutlined } from '@ant-design/icons';
import { api } from '../services/api';
import type { ScanResult } from '../types';

const { Option } = Select;
const { Search } = Input;

const ScanResult = () => {
  const [results, setResults] = useState<ScanResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedResult, setSelectedResult] = useState<ScanResult | null>(null);

  const fetchResults = async () => {
    setLoading(true);
    try {
      const response = await api.get<ScanResult[]>('/api/scan-results');
      setResults(response.data);
    } catch (error) {
      console.error('获取结果失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResults();
  }, []);

  const showDetail = (result: ScanResult) => {
    setSelectedResult(result);
    setDetailModalVisible(true);
  };

  const columns = [
    {
      title: '网站 URL',
      dataIndex: 'websiteUrl',
      key: 'websiteUrl',
    },
    {
      title: '总文章数',
      dataIndex: 'totalArticles',
      key: 'totalArticles',
    },
    {
      title: '可疑文章',
      dataIndex: 'suspiciousArticles',
      key: 'suspiciousArticles',
      render: (count: number) => (
        <Tag color={count > 0 ? 'red' : 'green'}>
          {count}
        </Tag>
      ),
    },
    {
      title: '处理时间',
      dataIndex: 'processedAt',
      key: 'processedAt',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colorMap: Record<string, string> = {
          completed: 'green',
          processing: 'blue',
          failed: 'red',
        };
        const labelMap: Record<string, string> = {
          completed: '完成',
          processing: '处理中',
          failed: '失败',
        };
        return <Tag color={colorMap[status]}>{labelMap[status]}</Tag>;
      },
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: ScanResult) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          onClick={() => showDetail(record)}
        >
          查看详情
        </Button>
      ),
    },
  ];

  const articleColumns = [
    {
      title: '文章标题',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '相似度',
      dataIndex: 'similarity',
      key: 'similarity',
      render: (similarity: number) => (
        <div style={{ width: 150 }}>
          <Progress
            percent={Math.round(similarity * 100)}
            status={similarity > 0.8 ? 'exception' : 'normal'}
          />
        </div>
      ),
    },
    {
      title: '来源',
      dataIndex: 'source',
      key: 'source',
      render: (source: string) => source || '-',
    },
  ];

  return (
    <div>
      <Card
        title="扫描结果"
        extra={
          <Space>
            <Search
              placeholder="搜索网站 URL"
              allowClear
              style={{ width: 200 }}
            />
            <Select
              placeholder="筛选状态"
              style={{ width: 120 }}
              allowClear
            >
              <Option value="completed">完成</Option>
              <Option value="processing">处理中</Option>
              <Option value="failed">失败</Option>
            </Select>
            <Button type="primary" onClick={fetchResults}>
              刷新
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={results}
          rowKey="id"
          loading={loading}
        />
      </Card>

      <Modal
        title="扫描详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedResult && (
          <div>
            <Descriptions column={2} bordered>
              <Descriptions.Item label="网站 URL">
                {selectedResult.websiteUrl}
              </Descriptions.Item>
              <Descriptions.Item label="扫描状态">
                <Tag color={selectedResult.status === 'completed' ? 'green' : 'blue'}>
                  {selectedResult.status}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="总文章数">
                {selectedResult.totalArticles}
              </Descriptions.Item>
              <Descriptions.Item label="可疑文章数">
                <Tag color={selectedResult.suspiciousArticles > 0 ? 'red' : 'green'}>
                  {selectedResult.suspiciousArticles}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="处理时间" span={2}>
                {selectedResult.processedAt}
              </Descriptions.Item>
            </Descriptions>

            {selectedResult.details && (
              <div style={{ marginTop: 24 }}>
                <h3>可疑文章列表</h3>
                <Table
                  columns={articleColumns}
                  dataSource={selectedResult.details}
                  rowKey="id"
                  pagination={false}
                  size="small"
                />
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ScanResult;
