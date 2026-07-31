"""[示例] docsforge 用法：Python/FastAPI handler。

这个文件演示"就近注解驱动文档"的写法。运行时 `docsforge scan examples/main.py`
即可把路由分组表写入 Markdown 文档，无需手写 API 文档。
"""
from __future__ import annotations


# docs:api method="GET" path="/api/health" group="系统" summary="健康检查"
def health():
    """返回服务健康状态。"""
    return {"status": "ok"}


# docs:api method="GET" path="/api/tickets" group="工单" summary="工单列表"
# docs:seq
def list_tickets():
    """列出当前所有工单。"""
    return []


# docs:api method="POST" path="/api/tickets" group="工单" summary="创建工单"
# 换行值用引号包裹即可，key="value" 支持跨行
# docs:api summary="创建一张新工单（覆盖上文）"
def create_ticket():
    """创建一张工单。

    - 入参：title, project_id
    - 返回：新建工单对象
    """
    return {}


# 普通函数：没写 docs: 标签，不会被扫描进文档
def _helper():
    return 0
