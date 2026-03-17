import { useState, useEffect, useRef } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Button,
  Select,
  DatePicker,
  Space,
} from 'antd';
import {
  FileTextOutlined,
  SyncOutlined,
  BarChartOutlined,
} from '@ant-design/icons';
import { api } from '../services/api';
import type { AnalyticsData } from '../types';

const { RangePicker } = DatePicker;
const { Option } = Select;

const Analytics = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<AnalyticsData>({
    totalArticles: 0,
    totalRewrites: 0,
    avgSimilarity: 0,
    citationGrowth: [],
    topCitations: [],
    recentActivity: [],
  });

  const canvasRef = useRef<HTMLCanvasElement>(null);

  const fetchAnalyticsData = async (params?: { startDate?: string; endDate?: string }) => {
    setLoading(true);
    try {
      const query = new URLSearchParams();
      if (params?.startDate) query.append('startDate', params.startDate);
      if (params?.endDate) query.append('endDate', params.endDate);

      const response = await api.get<AnalyticsData>(
        `/api/analytics?${query.toString()}`
      );
      setData(response.data);
    } catch (error) {
      console.error('获取数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  useEffect(() => {
    if (data.citationGrowth.length > 0 && canvasRef.current) {
      drawChart();
    }
  }, [data.citationGrowth]);

  const drawChart = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    const padding = 40;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;

    // 清空画布
    ctx.clearRect(0, 0, width, height);

    // 绘制坐标轴
    ctx.strokeStyle = '#ccc';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();

    // 绘制数据
    if (data.citationGrowth.length > 1) {
      const maxValue = Math.max(...data.citationGrowth);
      const stepX = chartWidth / (data.citationGrowth.length - 1);

      ctx.strokeStyle = '#1890ff';
      ctx.lineWidth = 2;
      ctx.beginPath();

      data.citationGrowth.forEach((value, index) => {
        const x = padding + index * stepX;
        const y = height - padding - (value / maxValue) * chartHeight;

        if (index === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });

      ctx.stroke();

      // 绘制数据点
      ctx.fillStyle = '#1890ff';
      data.citationGrowth.forEach((value, index) => {
        const x = padding + index * stepX;
        const y = height - padding - (value / maxValue) * chartHeight;

        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fill();
      });
    }
  };

  const topCitationColumns = [
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
    },
  ];

  const activityColumns = [
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => {
        const colorMap: Record<string, string> = {
          scan: 'blue',
          rewrite: 'green',
          citation: 'orange',
          alert: 'red',
        };
        return <span style={{ color: colorMap[type] }}>{type}</span>;
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
              title="改写次数"
              value={data.totalRewrites}
              prefix={<SyncOutlined />}
              loading={loading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="平均相似度"
              value={data.avgSimilarity}
              precision={2}
              suffix="%"
              valueStyle={{ color: data.avgSimilarity < 0.3 ? '#3f8600' : '#cf1322' }}
              loading={loading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="增长率"
              value={
                data.citationGrowth.length > 1
                  ? ((data.citationGrowth[data.citationGrowth.length - 1] -
                      data.citationGrowth[0]) /
                      data.citationGrowth[0]) *
                    100
                  : 0
              }
              precision={2}
              suffix="%"
              prefix={<BarChartOutlined />}
              loading={loading}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24}>
          <Card
            title="引用增长趋势"
            extra={
              <Space>
                <RangePicker onChange={(dates) => {
                  if (dates && dates[0] && dates[1]) {
                    fetchAnalyticsData({
                      startDate: dates[0].format('YYYY-MM-DD'),
                      endDate: dates[1].format('YYYY-MM-DD'),
                    });
                  }
                }} />
                <Select defaultValue="7d" style={{ width: 100 }}>
                  <Option value="7d">7天</Option>
                  <Option value="30d">30天</Option>
                  <Option value="90d">90天</Option>
                </Select>
                <Button type="primary" onClick={() => fetchAnalyticsData()}>
                  刷新
                </Button>
              </Space>
            }
          >
            <canvas
              ref={canvasRef}
              width={800}
              height={300}
              style={{ width: '100%', height: '300px' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card title="热门引用">
            <Table
              columns={topCitationColumns}
              dataSource={data.topCitations}
              rowKey="id"
              loading={loading}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="最近活动">
            <Table
              columns={activityColumns}
              dataSource={data.recentActivity}
              rowKey="id"
              loading={loading}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Analytics;
