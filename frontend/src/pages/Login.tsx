import { Form, Input, Button, Card, Typography, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { useAuthStore } from '../stores/auth';
import type { LoginRequest } from '../types';

const { Title } = Typography;

const Login = () => {
  const navigate = useNavigate();
  const { setAuth } = useAuthStore();

  const onFinish = async (values: LoginRequest) => {
    try {
      const response = await api.post<{
        user: any;
        token: string;
      }>('/api/auth/login', values);

      if (response.code === 200) {
        setAuth(response.data.user, response.data.token);
        localStorage.setItem('token', response.data.token);
        message.success('登录成功');
        navigate('/dashboard');
      }
    } catch (error: any) {
      message.error(error.message || '登录失败');
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
          登录您的账户
        </div>
      </div>

      <Form name="login" onFinish={onFinish} size="large" autoComplete="off">
        <Form.Item
          name="email"
          rules={[
            { required: true, message: '请输入邮箱' },
            { type: 'email', message: '请输入有效的邮箱地址' },
          ]}
        >
          <Input
            prefix={<UserOutlined />}
            placeholder="邮箱"
          />
        </Form.Item>

        <Form.Item
          name="password"
          rules={[{ required: true, message: '请输入密码' }]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="密码"
          />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" block>
            登录
          </Button>
        </Form.Item>

        <div style={{ textAlign: 'center', color: '#666' }}>
          还没有账户？
          <Button
            type="link"
            onClick={() => navigate('/register')}
            style={{ padding: 0 }}
          >
            注册
          </Button>
        </div>
      </Form>
    </Card>
  );
};

export default Login;
