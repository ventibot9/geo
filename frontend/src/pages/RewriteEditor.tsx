import { useState } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Space,
  message,
  Row,
  Col,
  Statistic,
} from 'antd';
import { SendOutlined, ClearOutlined, CopyOutlined } from '@ant-design/icons';
import { api } from '../services/api';

const { TextArea } = Input;

const RewriteEditor = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [originalText, setOriginalText] = useState('');
  const [rewrittenText, setRewrittenText] = useState('');
  const [similarityBefore, setSimilarityBefore] = useState(0);
  const [similarityAfter, setSimilarityAfter] = useState(0);

  const handleRewrite = async () => {
    if (!originalText.trim()) {
      message.warning('请输入原始文本');
      return;
    }

    setLoading(true);
    try {
      const response = await api.post<{
        rewrittenText: string;
        similarityBefore: number;
        similarityAfter: number;
      }>('/api/rewrite', {
        originalText,
      });

      setRewrittenText(response.data.rewrittenText);
      setSimilarityBefore(response.data.similarityBefore);
      setSimilarityAfter(response.data.similarityAfter);
      message.success('改写成功');
    } catch (error: any) {
      message.error(error.message || '改写失败');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    form.resetFields();
    setOriginalText('');
    setRewrittenText('');
    setSimilarityBefore(0);
    setSimilarityAfter(0);
  };

  const handleCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      message.success('复制成功');
    } catch (error) {
      message.error('复制失败');
    }
  };

  const getSimilarityColor = (similarity: number) => {
    if (similarity < 0.3) return 'green';
    if (similarity < 0.6) return 'orange';
    return 'red';
  };

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card
            title="原始文本"
            extra={
              <Button
                icon={<ClearOutlined />}
                onClick={() => {
                  setOriginalText('');
                  form.setFieldValue('originalText', '');
                }}
              >
                清空
              </Button>
            }
          >
            <Form form={form}>
              <Form.Item name="originalText">
                <TextArea
                  value={originalText}
                  onChange={(e) => setOriginalText(e.target.value)}
                  placeholder="请输入需要改写的文本..."
                  rows={15}
                  style={{ resize: 'none' }}
                />
              </Form.Item>
            </Form>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card
            title="改写结果"
            extra={
              <Button
                icon={<CopyOutlined />}
                onClick={() => handleCopy(rewrittenText)}
                disabled={!rewrittenText}
              >
                复制
              </Button>
            }
          >
            <TextArea
              value={rewrittenText}
              placeholder="改写结果将在这里显示..."
              rows={15}
              readOnly
              style={{ resize: 'none', background: '#fafafa' }}
            />
          </Card>
        </Col>
      </Row>

      {similarityBefore > 0 && similarityAfter > 0 && (
        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} md={12}>
            <Card>
              <Statistic
                title="改写前相似度"
                value={Math.round(similarityBefore * 100)}
                suffix="%"
                valueStyle={{ color: getSimilarityColor(similarityBefore) }}
              />
            </Card>
          </Col>
          <Col xs={24} md={12}>
            <Card>
              <Statistic
                title="改写后相似度"
                value={Math.round(similarityAfter * 100)}
                suffix="%"
                valueStyle={{ color: getSimilarityColor(similarityAfter) }}
              />
            </Card>
          </Col>
        </Row>
      )}

      <div style={{ marginTop: 16, textAlign: 'center' }}>
        <Space>
          <Button
            type="primary"
            size="large"
            icon={<SendOutlined />}
            onClick={handleRewrite}
            loading={loading}
          >
            开始改写
          </Button>
          <Button size="large" icon={<ClearOutlined />} onClick={handleClear}>
            清空全部
          </Button>
        </Space>
      </div>
    </div>
  );
};

export default RewriteEditor;
