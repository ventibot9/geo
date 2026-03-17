import { Request, Response, NextFunction } from 'express';

export const validate = (schema: {
  validate: (data: any) => { error?: Error; value: any };
}) => {
  return (req: Request, res: Response, next: NextFunction) => {
    const { error, value } = schema.validate(req.body);

    if (error) {
      return res.status(400).json({
        error: '请求数据验证失败',
        details: error.message,
      });
    }

    req.body = value;
    next();
  };
};

// 简单验证函数（如果不想引入Joi或Zod）
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePassword = (password: string): boolean => {
  return password.length >= 6;
};
