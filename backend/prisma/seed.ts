import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  console.log('开始数据库种子...');

  // 创建测试企业
  const enterprise = await prisma.enterprise.upsert({
    where: { domain: 'example.com' },
    update: {},
    create: {
      name: '示例企业',
      domain: 'example.com',
      plan: 'pro',
      status: 'active',
    },
  });

  console.log('企业创建成功:', enterprise.name);

  // 创建管理员用户
  const hashedPassword = await bcrypt.hash('admin123', 10);

  const user = await prisma.user.upsert({
    where: {
      email_enterpriseId: {
        email: 'admin@example.com',
        enterpriseId: enterprise.id,
      },
    },
    update: {},
    create: {
      email: 'admin@example.com',
      password: hashedPassword,
      name: '管理员',
      role: 'admin',
      enterpriseId: enterprise.id,
      status: 'active',
    },
  });

  console.log('用户创建成功:', user.email);

  // 创建站点配置
  const siteConfig = await prisma.siteConfig.upsert({
    where: {
      enterpriseId_url: {
        enterpriseId: enterprise.id,
        url: 'https://example.com',
      },
    },
    update: {},
    create: {
      enterpriseId: enterprise.id,
      url: 'https://example.com',
      scanSchedule: 'weekly',
      active: true,
    },
  });

  console.log('站点配置创建成功:', siteConfig.url);

  console.log('数据库种子完成!');
}

main()
  .catch((e) => {
    console.error('数据库种子错误:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
