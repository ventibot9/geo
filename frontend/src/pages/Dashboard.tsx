import { Row, Col, Card, Statistic, Table, Tag, Button } from 'antd';
import {
  FileTextOutlined,
  ScanOutlined,
  AlertOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { useEffect, useState } from 'react';
import { api } from '../services/api';

interface DashboardData {
  totalArticles: number;
  totalScans: number;
  suspiciousCount: number;
  processedCount: number;
  recentActivities: Array<{
    id: string;
    type: string;
    message: string;
    timestamp: string;
  }>;
}

const Dashboard = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<DashboardData>({
    totalArticles: 0,
    totalScans: 0,
    suspiciousCount: 0,
    processedCount: 0,
    recentActivities: [],
  });

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const response = await api.get<DashboardData>('/api/dashboard');
      setData(response.data);
    } catch (error) {
      console.error('获取数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const activityColumns = [
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => {
        const colorMap: Record<string, string> = {
          scan: 'blue',
          alert: 'red',
          success: 'green',
        };
        return <Tag color={colorMap[type] || 'default'}>{type}</Tag>;
      },
    },
    {
      title: '消息',
      dataIndex: 'message',
      key: 'message',
    },
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
    },
  ];

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总文章数"
              value={data.totalArticles}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#3f8600' }}
              loading={loading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总扫描次数"
              value={data.totalScans}
              prefix={<ScanOutlined />}
              loading={loading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="可疑文章"
              value={data.suspiciousCount}
              prefix={<AlertOutlined />}
              valueStyle={{ color: '#cf1322' }}
              loading={loading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已处理"
              value={data.processedCount}
              prefix={<CheckCircleOutlined />}
              loading={loading}
            />
          </Card>
        </Col>
      </Row>

      <Card
        title="最近活动"
        style={{ marginTop: 16 }}
        extra={
          <Button type="primary" onClick={fetchDashboardData}>
            刷新
          </Button>
        }
      >
        <Table
          columns={activityColumns}
          dataSource={data.recentActivities}
          rowKey="id"
          loading={loading}
          pagination={false}
        />
      </Card>
    </div>
  );
};

export default Dashboard;
