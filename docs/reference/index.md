# 参考索引

> ⚠️ **生成区**：此页内容由 `docsforge scan` 从源码 `docs:index` 注解自动生成，
> 请勿手工编辑。每次源码变更后重新运行 `docsforge scan` 更新。

<!-- BEGIN GENERATED: module-index -->
<!-- 由 docsforge 从源码 `docs:` 注解自动生成，请勿手工编辑 -->

### `__init__`
> 包入口：暴露主要公共 API（parse_docs_tags / TaggedDeclaration）

| 声明 | 类型 | 说明 | 位置 |
|---|---|---|---|

### `cli`
> 命令行入口：argparse CLI（scan/check/handlers 三个子命令）

| 声明 | 类型 | 说明 | 位置 |
|---|---|---|---|
| `main` | 函数 | CLI 入口：argparse 解析三个子命令（scan/check/handlers） | `cli.py:121` |

### `drift`
> 漂移检查：生成区替换 + 幂等替换 + check_drift 校验

| 声明 | 类型 | 说明 | 位置 |
|---|---|---|---|
| `render_section` | 函数 | 构造规范生成区（BEGIN/END GENERATED 标记包裹） | `drift.py:27` |
| `check_drift` | 函数 | 校验文档生成区与源码注解是否一致（True=无漂移） | `drift.py:93` |

### `python_fastapi`
> Python/FastAPI handler：AST 遍历提取函数/类/模块/配置的 docs: 注解

| 声明 | 类型 | 说明 | 位置 |
|---|---|---|---|
| `PythonFastAPIHandler` | 类 | 扫描 Python 文件，提取带 docs: 标签的函数/类/模块/配置声明 | `python_fastapi.py:124` |

### `model`
> 中间表示 IR：TaggedDeclaration 数据类，承载 docs_tags/extra/source_path

| 声明 | 类型 | 说明 | 位置 |
|---|---|---|---|
| `TaggedDeclaration` | 类 | IR 数据类：一条带 docs: 注解的源码声明（name/docs_tags/extra/source_path） | `model.py:18` |

### `registry`
> Handler 协议 + 注册表（插件点）：LanguageHandler / @register / get_handler

| 声明 | 类型 | 说明 | 位置 |
|---|---|---|---|
| `LanguageHandler` | 类 | 语言适配器协议：实现 scan(path) → list[TaggedDeclaration] | `registry.py:26` |
| `register` | 函数 | 类装饰器：把 Handler 类按 name 注册到全局注册表 | `registry.py:45` |

### `render`
> Markdown 渲染器：按 token 分派的注册表机制，IR → Markdown

| 声明 | 类型 | 说明 | 位置 |
|---|---|---|---|
| `render` | 函数 | 按 token 路由到对应渲染器，是渲染器的统一入口 | `render.py:61` |
| `render_api_grouped_table` | 函数 | 按 group 分组的 API 路由 Markdown 表格 | `render.py:88` |
| `render_module_index` | 函数 | 按模块+类/函数分组、含源码位置的模块索引表 | `render.py:120` |
| `render_config_reference` | 函数 | 按 key/环境变量/默认值/说明 四列的配置参考表 | `render.py:176` |

### `scan`
> 多文件扫描（S4）：resolve_inputs + scan_files，目录/glob → IR 聚合

| 声明 | 类型 | 说明 | 位置 |
|---|---|---|---|
| `resolve_inputs` | 函数 | 把文件/目录/glob 展开为去重、排序的源码文件清单 | `scan.py:55` |
| `scan_files` | 函数 | 用指定 handler 扫描多文件/目录/glob 并聚合所有声明 | `scan.py:77` |

### `tags`
> 语言无关的 `docs:` 标签解析器，正则匹配 key=&quot;value&quot; 键值对

| 声明 | 类型 | 说明 | 位置 |
|---|---|---|---|
| `parse_docs_tags` | 函数 | 从注释文本解析 docs: 标签，返回 {主题: {键: 值}} | `tags.py:27` |
<!-- END GENERATED: module-index -->
