"""
GEO Platform AI Rewrite Service - 示例测试脚本

注意：运行前需要先启动服务，并配置好 .env 文件中的 API 密钥
"""

import asyncio
import requests
import json

BASE_URL = "http://localhost:8000"


def test_health_check():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")


def test_get_models():
    """测试获取可用模型"""
    print("\n=== 测试获取可用模型 ===")
    response = requests.get(f"{BASE_URL}/api/v1/rewrite/models")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_single_rewrite():
    """测试单条改写"""
    print("\n=== 测试单条改写 ===")

    content = """
GEO平台是一个地理信息系统平台，支持多种数据格式。

支持的格式包括：Shapefile、GeoJSON、KML、WKT、WKB。

主要功能：
1. 数据导入导出
2. 空间查询
3. 地图可视化
4. 数据编辑

配置参数：
- max_features: 10000
- buffer_size: 1024
- cache_enabled: true
"""

    payload = {
        "content": content,
        "model_provider": "anthropic",
        "optimize_structure": True,
        "extract_tables": True,
        "temperature": 0.7,
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/rewrite",
        json=payload,
    )

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Record ID: {result['id']}")
        print(f"Model: {result['model_provider']} - {result['model']}")
        print(f"\n=== 改写结果 ===")
        print(result["rewritten"])
    else:
        print(f"Error: {response.json()}")


def test_batch_rewrite():
    """测试批量改写"""
    print("\n=== 测试批量改写 ===")

    contents = [
        "API端点：/api/v1/users，方法：GET，描述：获取用户列表",
        "API端点：/api/v1/users/{id}，方法：GET，描述：获取单个用户",
        "API端点：/api/v1/users，方法：POST，描述：创建新用户",
    ]

    payload = {
        "contents": contents,
        "model_provider": "anthropic",
        "optimize_structure": True,
        "extract_tables": True,
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/rewrite/batch",
        json=payload,
    )

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        results = response.json()
        print(f"处理了 {len(results)} 条内容")
        for i, result in enumerate(results, 1):
            print(f"\n--- 结果 {i} ---")
            print(result["rewritten"][:200] + "...")
    else:
        print(f"Error: {response.json()}")


def test_quality_evaluation():
    """测试质量评估"""
    print("\n=== 测试质量评估 ===")

    original = "GEO平台是一个地理信息系统。支持Shapefile和GeoJSON格式。"
    rewritten = """# GEO平台

GEO平台是一个地理信息系统。

## 支持的数据格式

| 格式 | 说明 |
|------|------|
| Shapefile | ESRI Shapefile格式 |
| GeoJSON | GeoJSON格式 |
"""

    payload = {
        "original": original,
        "rewritten": rewritten,
        "model_provider": "anthropic",
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/rewrite/evaluate",
        json=payload,
    )

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        evaluation = response.json()
        print(f"总体评分: {evaluation['overall_score']}")
        print(f"完整性: {evaluation['completeness']}")
        print(f"清晰度: {evaluation['clarity']}")
        print(f"结构化: {evaluation['structure']}")
        print(f"\n改进建议:")
        for suggestion in evaluation['suggestions']:
            print(f"- {suggestion}")
    else:
        print(f"Error: {response.json()}")


def test_get_history():
    """测试获取历史记录"""
    print("\n=== 测试获取历史记录 ===")

    response = requests.get(f"{BASE_URL}/api/v1/rewrite/history?limit=5")

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        records = response.json()
        print(f"获取到 {len(records)} 条记录")
        for record in records:
            print(f"\nID: {record['id']}")
            print(f"Model: {record['model_provider']}")
            print(f"Time: {record['created_at']}")
            print(f"Preview: {record['original'][:100]}...")
    else:
        print(f"Error: {response.json()}")


def main():
    """主函数"""
    print("GEO Platform AI Rewrite Service - 示例测试")
    print("=" * 50)

    try:
        # 健康检查
        test_health_check()

        # 获取可用模型
        test_get_models()

        # 单条改写
        test_single_rewrite()

        # 批量改写
        test_batch_rewrite()

        # 质量评估
        test_quality_evaluation()

        # 获取历史记录
        test_get_history()

        print("\n" + "=" * 50)
        print("所有测试完成！")

    except requests.exceptions.ConnectionError:
        print("\n错误: 无法连接到服务。请确保服务已启动（运行 start.sh 或 python -m uvicorn app.main:app）")
    except Exception as e:
        print(f"\n错误: {str(e)}")


if __name__ == "__main__":
    main()
