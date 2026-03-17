import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { ConfigProvider, App as AntdApp, Layout, Menu } from 'antd';
import {
  DashboardOutlined,
  ScanOutlined,
  FileTextOutlined,
  EditOutlined,
  EyeOutlined,
  BarChartOutlined,
  LogoutOutlined,
} from '@ant-design/icons';
import zhCN from 'antd/locale/zh_CN';
import { useAuthStore } from '../stores/auth';
import type { MenuProps } from 'antd';

const { Header, Sider, Content } = Layout;

const MainLayout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const menuItems: MenuProps['items'] = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '控制台',
    },
    {
      key: '/scan-config',
      icon: <ScanOutlined />,
      label: '扫描配置',
    },
    {
      key: '/scan-result',
      icon: <FileTextOutlined />,
      label: '扫描结果',
    },
    {
      key: '/rewrite-editor',
      icon: <EditOutlined />,
      label: 'AI 改写',
    },
    {
      key: '/citation-monitor',
      icon: <EyeOutlined />,
      label: '引用监控',
    },
    {
      key: '/analytics',
      icon: <BarChartOutlined />,
      label: '数据分析',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
    },
  ];

  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    if (key === 'logout') {
      logout();
      localStorage.removeItem('token');
      navigate('/login');
    } else {
      navigate(key);
    }
  };

  return (
    <ConfigProvider locale={zhCN}>
      <AntdApp>
        <Layout style={{ minHeight: '100vh' }}>
          <Sider width={256} theme="dark">
            <div
              style={{
                height: 64,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontSize: 20,
                fontWeight: 'bold',
                borderBottom: '1px solid rgba(255,255,255,0.1)',
              }}
            >
              GEO 平台
            </div>
            <Menu
              theme="dark"
              mode="inline"
              selectedKeys={[location.pathname]}
              items={menuItems}
              onClick={handleMenuClick}
            />
          </Sider>
          <Layout>
            <Header
              style={{
                background: '#fff',
                padding: '0 24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                borderBottom: '1px solid #f0f0f0',
              }}
            >
              <div style={{ fontSize: 18, fontWeight: 500 }}>
                {user?.username || '欢迎'}
              </div>
              <div style={{ color: '#666' }}>{user?.email}</div>
            </Header>
            <Content style={{ padding: '24px', background: '#f0f2f5' }}>
              <Outlet />
            </Content>
          </Layout>
        </Layout>
      </AntdApp>
    </ConfigProvider>
  );
};

export default MainLayout;
