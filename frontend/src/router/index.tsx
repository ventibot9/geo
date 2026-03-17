import { createBrowserRouter } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import AuthLayout from '../layouts/AuthLayout';
import Login from '../pages/Login';
import Register from '../pages/Register';
import Dashboard from '../pages/Dashboard';
import ScanConfig from '../pages/ScanConfig';
import ScanResult from '../pages/ScanResult';
import RewriteEditor from '../pages/RewriteEditor';
import CitationMonitor from '../pages/CitationMonitor';
import Analytics from '../pages/Analytics';

const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <Dashboard />,
      },
      {
        path: 'dashboard',
        element: <Dashboard />,
      },
      {
        path: 'scan-config',
        element: <ScanConfig />,
      },
      {
        path: 'scan-result',
        element: <ScanResult />,
      },
      {
        path: 'rewrite-editor',
        element: <RewriteEditor />,
      },
      {
        path: 'citation-monitor',
        element: <CitationMonitor />,
      },
      {
        path: 'analytics',
        element: <Analytics />,
      },
    ],
  },
  {
    path: '/login',
    element: <AuthLayout />,
    children: [
      {
        index: true,
        element: <Login />,
      },
    ],
  },
  {
    path: '/register',
    element: <AuthLayout />,
    children: [
      {
        index: true,
        element: <Register />,
      },
    ],
  },
]);

export default router;
