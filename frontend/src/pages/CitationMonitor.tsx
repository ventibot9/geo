import { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Tag,
  Space,
  Button,
  Input,
  Select,
  Row,
  Col,
  Statistic,
} from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { api } from '../services/api';
import type { CitationData } from '../types';

const { Option } = Select;
const { Search } = Input;

const CitationMonitor = () => {
  const [citations, setCitations] = useState<CitationData[]>([]);
  const [loading, setLoading] = useState(false);
  const [totalCitations, setTotalCitations] = useState(0);
  const [growthRate, setGrowthRate] = useState(0);

  const fetchCitations = async () => {
    setLoading(true);
    try {
      const response = await api.get<{
        citations: CitationData[];
        total: number;
        growthRate: number;
      }>('/api/citations');

      setCitations(response.data.citations);
      setTotalCitations(response.data.total);
      setGrowthRate(response.data.growthRate);
    } catch (error) {
      console.error('获取数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCitations();
  }, []);

  const columns = [
    {
      title: '来源 URL',
      dataIndex: 'sourceUrl',
      key: 'sourceUrl',
      ellipsis: true,
      render: (url: string) => (
        <a href={url} target="_blank" rel="noopener noreferrer">
          {url}
        </a>
      ),
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: '引用次数',
      dataIndex: 'citationCount',
      key: 'citationCount',
      sorter: (a: CitationData, b: CitationData) => a.citationCount - b.citationCount,
      defaultSortOrder: 'descend' as const,
    },
    {
      title: '最后引用时间',
      dataIndex: 'lastCitedAt',
      key: 'lastCitedAt',
    },
    {
      title: '趋势',
      dataIndex: 'trend',
      key: 'trend',
      render: (trend: string) => {
        if (trend === 'up') {
          return (
            <Tag icon={<ArrowUpOutlined />} color="green">
              上升
            </Tag>
          );
        } else if (trend === 'down') {
          return (
            <Tag icon={<ArrowDownOutlined />} color="red">
              下降
            </Tag>
          );
        }
        return <Tag color="blue">稳定</Tag>;
      },
    },
  ];

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12}>
          <Card>
            <Statistic
              title="总引用次数"
              value={totalCitations}
              valueStyle={{ color: '#3f8600' }}
              loading={loading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12}>
          <Card>
            <Statistic
              title="增长率"
              value={growthRate}
              precision={2}
              suffix="%"
              valueStyle={{ color: growthRate >= 0 ? '#3f8600' : '#cf1322' }}
              prefix={growthRate >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              loading={loading}
            />
          </Card>
        </Col>
      </Row>

      <Card
        title="引用监控"
        style={{ marginTop: 16 }}
        extra={
          <Space>
            <Search
              placeholder="搜索标题或 URL"
              allowClear
              style={{ width: 200 }}
            />
            <Select
              placeholder="筛选趋势"
              style={{ width: 120 }}
              allowClear
            >
              <Option value="up">上升</Option>
              <Option value="down">下降</Option>
              <Option value="stable">稳定</Option>
            </Select>
            <Button type="primary" onClick={fetchCitations}>
              刷新
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={citations}
          rowKey="id"
          loading={loading}
          scroll={{ x: true }}
        />
      </Card>
    </div>
  );
};

export default CitationMonitor;
