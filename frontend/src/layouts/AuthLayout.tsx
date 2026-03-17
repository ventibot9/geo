import { Outlet } from 'react-router-dom';
import { ConfigProvider, App as AntdApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';

const AuthLayout = () => {
  return (
    <ConfigProvider locale={zhCN}>
      <AntdApp>
        <div
          style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          }}
        >
          <Outlet />
        </div>
      </AntdApp>
    </ConfigProvider>
  );
};

export default AuthLayout;
