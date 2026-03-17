from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routers import rewrite_router
from contextlib import asynccontextmanager
import uvicorn
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    yield
    # 关闭时的清理工作
    pass


app = FastAPI(
    title="GEO Platform AI Rewrite Service",
    description="AI驱动的内容改写和结构优化服务",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该配置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(rewrite_router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "GEO Platform AI Rewrite Service",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok"}


def main():
    """启动服务"""
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
    )


if __name__ == "__main__":
    main()
