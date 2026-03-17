import { Form, Input, Button, Card, Typography, message } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import type { RegisterRequest } from '../types';

const { Title } = Typography;

const Register = () => {
  const navigate = useNavigate();

  const onFinish = async (values: RegisterRequest) => {
    try {
      const response = await api.post('/api/auth/register', values);

      if (response.code === 200) {
        message.success('注册成功，请登录');
        navigate('/login');
      }
    } catch (error: any) {
      message.error(error.message || '注册失败');
    }
  };

  return (
    <Card
      style={{
        width: 400,
        boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
      }}
    >
      <div style={{ textAlign: 'center', marginBottom: 32 }}>
        <Title level={2} style={{ margin: 0 }}>
          GEO 平台
        </Title>
        <div style={{ color: '#666', marginTop: 8 }}>
          创建您的账户
        </div>
      </div>

      <Form name="register" onFinish={onFinish} size="large" autoComplete="off">
        <Form.Item
          name="username"
          rules={[{ required: true, message: '请输入用户名' }]}
        >
          <Input
            prefix={<UserOutlined />}
            placeholder="用户名"
          />
        </Form.Item>

        <Form.Item
          name="email"
          rules={[
            { required: true, message: '请输入邮箱' },
            { type: 'email', message: '请输入有效的邮箱地址' },
          ]}
        >
          <Input
            prefix={<MailOutlined />}
            placeholder="邮箱"
          />
        </Form.Item>

        <Form.Item
          name="password"
          rules={[
            { required: true, message: '请输入密码' },
            { min: 6, message: '密码至少6位' },
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="密码"
          />
        </Form.Item>

        <Form.Item
          name="confirmPassword"
          dependencies={['password']}
          rules={[
            { required: true, message: '请确认密码' },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue('password') === value) {
                  return Promise.resolve();
                }
                return Promise.reject(new Error('两次输入的密码不一致'));
              },
            }),
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="确认密码"
          />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" block>
            注册
          </Button>
        </Form.Item>

        <div style={{ textAlign: 'center', color: '#666' }}>
          已有账户？
          <Button
            type="link"
            onClick={() => navigate('/login')}
            style={{ padding: 0 }}
          >
            登录
          </Button>
        </div>
      </Form>
    </Card>
  );
};

export default Register;
