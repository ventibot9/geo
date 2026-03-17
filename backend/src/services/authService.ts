import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { config } from '../config';
import prisma from '../config/database';

export interface RegisterData {
  email: string;
  password: string;
  name: string;
  enterpriseName: string;
  domain: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export const authService = {
  async register(data: RegisterData) {
    const { email, password, name, enterpriseName, domain } = data;

    // 检查企业是否已存在
    const existingEnterprise = await prisma.enterprise.findUnique({
      where: { domain },
    });

    if (existingEnterprise) {
      throw new Error('该域名已被注册');
    }

    // 哈希密码
    const hashedPassword = await bcrypt.hash(
      password,
      config.bcrypt.rounds
    );

    // 创建企业
    const enterprise = await prisma.enterprise.create({
      data: {
        name: enterpriseName,
        domain,
        plan: 'free',
        status: 'active',
      },
    });

    // 创建用户（管理员）
    const user = await prisma.user.create({
      data: {
        email,
        password: hashedPassword,
        name,
        role: 'admin',
        enterpriseId: enterprise.id,
      },
    });

    // 生成JWT
    const token = jwt.sign(
      {
        id: user.id,
        email: user.email,
        enterpriseId: user.enterpriseId,
        role: user.role,
      },
      config.jwt.secret,
      { expiresIn: config.jwt.expiresIn }
    );

    return {
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
        enterpriseId: user.enterpriseId,
      },
      token,
    };
  },

  async login(data: LoginData) {
    const { email, password } = data;

    // 查找用户
    const user = await prisma.user.findUnique({
      where: { email },
      include: { enterprise: true },
    });

    if (!user) {
      throw new Error('邮箱或密码错误');
    }

    // 检查用户状态
    if (user.status !== 'active' || user.enterprise.status !== 'active') {
      throw new Error('账户已被禁用');
    }

    // 验证密码
    const isPasswordValid = await bcrypt.compare(password, user.password);

    if (!isPasswordValid) {
      throw new Error('邮箱或密码错误');
    }

    // 更新最后登录时间
    await prisma.user.update({
      where: { id: user.id },
      data: { lastLoginAt: new Date() },
    });

    // 生成JWT
    const token = jwt.sign(
      {
        id: user.id,
        email: user.email,
        enterpriseId: user.enterpriseId,
        role: user.role,
      },
      config.jwt.secret,
      { expiresIn: config.jwt.expiresIn }
    );

    return {
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
        enterpriseId: user.enterpriseId,
      },
      token,
    };
  },

  async getUserById(userId: string) {
    const user = await prisma.user.findUnique({
      where: { id: userId },
      select: {
        id: true,
        email: true,
        name: true,
        role: true,
        enterpriseId: true,
        status: true,
        lastLoginAt: true,
        createdAt: true,
        enterprise: {
          select: {
            id: true,
            name: true,
            domain: true,
            plan: true,
            status: true,
          },
        },
      },
    });

    if (!user) {
      throw new Error('用户不存在');
    }

    return user;
  },
};
