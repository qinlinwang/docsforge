# API 路由参考

> ⚠️ **生成区**：此页内容由 `docsforge scan` 从源码 `docs:api` 注解自动生成，
> 请勿手工编辑。以下是**目标形态占位**：真实的生成区由 scan 写入并带
> `<!-- BEGIN/END GENERATED -->` 标记。

<!-- BEGIN GENERATED: api-routes -->

### 系统

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 健康检查 |

### 工单

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/tickets` | 工单列表 |
| POST | `/api/tickets` | 创建工单 |

<!-- END GENERATED: api-routes -->

## 说明

- 本表由源码中的 `docs:api` 注释注解驱动，注解写法见
  [注解规范](../topics/referencing-guidelines.md)。
- 先取注解值，缺省回退 handler 提供的框架元数据（如 FastAPI 装饰器）。
