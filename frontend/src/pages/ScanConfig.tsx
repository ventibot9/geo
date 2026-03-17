import { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  Select,
  Button,
  Table,
  Tag,
  Space,
  Modal,
  message,
  Switch,
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { api } from '../services/api';
import type { ScanConfig } from '../types';

const { Option } = Select;

const ScanConfig = () => {
  const [form] = Form.useForm();
  const [configs, setConfigs] = useState<ScanConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingConfig, setEditingConfig] = useState<ScanConfig | null>(null);

  const fetchConfigs = async () => {
    setLoading(true);
    try {
      const response = await api.get<ScanConfig[]>('/api/scan-configs');
      setConfigs(response.data);
    } catch (error) {
      message.error('获取配置失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConfigs();
  }, []);

  const handleSubmit = async (values: any) => {
    try {
      if (editingConfig) {
        await api.put(`/api/scan-configs/${editingConfig.id}`, values);
        message.success('更新成功');
      } else {
        await api.post('/api/scan-configs', values);
        message.success('创建成功');
      }
      setModalVisible(false);
      form.resetFields();
      setEditingConfig(null);
      fetchConfigs();
    } catch (error: any) {
      message.error(error.message || '操作失败');
    }
  };

  const handleEdit = (config: ScanConfig) => {
    setEditingConfig(config);
    form.setFieldsValue(config);
    setModalVisible(true);
  };

  const handleDelete = async (id: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个扫描配置吗？',
      onOk: async () => {
        try {
          await api.delete(`/api/scan-configs/${id}`);
          message.success('删除成功');
          fetchConfigs();
        } catch (error: any) {
          message.error(error.message || '删除失败');
        }
      },
    });
  };

  const handleToggleStatus = async (id: string, status: string) => {
    try {
      const newStatus: 'active' | 'paused' | 'stopped' = status === 'active' ? 'paused' : 'active';
      await api.put(`/api/scan-configs/${id}`, { status: newStatus });
      message.success('状态更新成功');
      fetchConfigs();
    } catch (error: any) {
      message.error(error.message || '更新失败');
    }
  };

  const columns = [
    {
      title: '网站 URL',
      dataIndex: 'websiteUrl',
      key: 'websiteUrl',
    },
    {
      title: '扫描频率',
      dataIndex: 'scanFrequency',
      key: 'scanFrequency',
      render: (frequency: string) => {
        const map: Record<string, string> = {
          daily: '每天',
          weekly: '每周',
          monthly: '每月',
        };
        return map[frequency] || frequency;
      },
    },
    {
      title: '关键词',
      dataIndex: 'keywords',
      key: 'keywords',
      render: (keywords: string[]) => (
        <>
          {keywords.map((kw) => (
            <Tag key={kw}>{kw}</Tag>
          ))}
        </>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string, record: ScanConfig) => (
        <Switch
          checked={status === 'active'}
          onChange={() => handleToggleStatus(record.id, status)}
          checkedChildren="开启"
          unCheckedChildren="暂停"
        />
      ),
    },
    {
      title: '上次扫描',
      dataIndex: 'lastScanAt',
      key: 'lastScanAt',
      render: (date: string) => date || '-',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: ScanConfig) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card
        title="扫描配置"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setEditingConfig(null);
              form.resetFields();
              setModalVisible(true);
            }}
          >
            新建配置
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={configs}
          rowKey="id"
          loading={loading}
        />
      </Card>

      <Modal
        title={editingConfig ? '编辑配置' : '新建配置'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          setEditingConfig(null);
          form.resetFields();
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="websiteUrl"
            label="网站 URL"
            rules={[
              { required: true, message: '请输入网站 URL' },
              { type: 'url', message: '请输入有效的 URL' },
            ]}
          >
            <Input placeholder="https://example.com" />
          </Form.Item>

          <Form.Item
            name="scanFrequency"
            label="扫描频率"
            rules={[{ required: true, message: '请选择扫描频率' }]}
          >
            <Select placeholder="请选择">
              <Option value="daily">每天</Option>
              <Option value="weekly">每周</Option>
              <Option value="monthly">每月</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="keywords"
            label="关键词"
            rules={[{ required: true, message: '请输入关键词' }]}
          >
            <Select
              mode="tags"
              placeholder="输入关键词后回车"
              tokenSeparators={[',', ' ']}
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                保存
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ScanConfig;
