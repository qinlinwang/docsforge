# docsforge

从源码 `docs:` 注释注解自动生成文档的**独立工具**（跨语言、插件化）。

> 本项目从 AI-NPC 仓库的 `tools/docs` 抽离出的通用核心。
> 语义："只要你按规范写注释，它就帮你生成整洁文档 + 检查漂移"。

## 核心思路

在源码里**就近声明**文档语义，工具负责扫描、渲染、查重：

```python
# docs:api method="GET" path="/api/tickets" group="工单" summary="工单列表"
# docs:seq                                    # 生成时序图
def list_tickets():
    "列出当前所有工单。"

# 普通函数没写 docs: 标签 → 不会被扫描进文档
def _helper(): ...
```

- `docs:` 前缀是**纯注释文本**，不侵入运行时代码，任何语言都能承载。
- `scan` 扫描 → 渲染成 Markdown 生成区 → 可写入文档；`check` 比对生成区，
  拦截"改了源码忘了重新生成"的漂移。

## 快速开始

无需安装可用（直接跑源码）：

```bash
# 安装（正式使用）
pip install .                          # 在 docsforge/ 目录下

# 扫描源码，把路由分组表写入文档（生成区用 <!-- BEGIN/END GENERATED --> 包裹）
docsforge scan backend/app/main.py --out docs/api.docsforge.md --anchor "## 认证"

# 检查文档是否与源码注解漂移（适合放进 CI / pre-commit）
docsforge check backend/app/main.py docs/api.docsforge.md
```

不指定 `--out` 时打印到 stdout，方便预览。

## 命令

```
docsforge scan <源码> [--handler <name>] [--token <token>]
                     [--out <文档.md>] [--anchor <章节标题>]
docsforge check <源码> <文档.md> [--handler <name>] [--token <token>]
docsforge handlers
```

| 命令 | 作用 |
|---|---|
| `scan` | 扫描源码 → 渲染生成区 → 写入或打印 |
| `check` | 校验文档现有生成区与源码注解一致（退出码 0=通过 / 1=漂移） |
| `handlers` | 列出已注册的语言适配器 |

## 架构

```
docsforge/
├── pyproject.toml        # 独立打包 + CLI 入口
├── docsforge/
│   ├── tags.py           # [语言无关] docs: 标签解析器
│   ├── model.py          # [语言无关] IR：TaggedDeclaration
│   ├── registry.py       # [语言无关] Handler 协议 + 注册表（插件点）
│   ├── render.py         # [语言无关] Markdown 渲染器
│   ├── drift.py          # [语言无关] 生成区替换 + 漂移检查
│   ├── cli.py            # [入口]
│   └── handlers/
│       └── python_fastapi.py   # 内置适配器：Python + FastAPI 装饰器回退
└── examples/
    └── main.py           # 规范写法示例
```

**跨语言的关键**：只有 `handlers/<lang>.py` 负责"如何从源码提取注释"，
解析（`tags`）、渲染（`render`）、漂移（`drift`）、CLI 全部与语言无关。
换语言只需实现一个 Handler，其余原样复用。

## 接入新语言 / 新框架

在 `handlers/` 加一个文件，实现 `LanguageHandler` 协议并注册：

```python
# docsforge/docsforge/handlers/typescript_openapi.py
from ..registry import register
from ..model import TaggedDeclaration

@register("typescript_openapi")      # 注册名，--handler 参数用它
class TypeScriptOpenAPIHandler:
    name = "typescript_openapi"
    def scan(self, path) -> list[TaggedDeclaration]:
        # 1. 解析 TS 源码，找出带 docs: 标签的声明（函数/类…）
        # 2. 收集声明就近的注释文本
        # 3. 用 tags_from_comment(text) 解析 docs_tags
        # 4. 把框架提供的 method/path/summary 放入 decl.extra
        ...
```

> 内置 `python_fastapi` 是完整参考实现。

## 标签规范

统一前缀 `docs:`，`key="value"` 键值对（值用引号包裹，可跨多行）：

| 主题 | 典型键 | 用途 |
|---|---|---|
| `api` | `method / path / group / summary` | 生成 API 路由分组表 |
| `seq` | `-` | 标记要生成时序图（配合外界时序图生成器） |
| `config` | `-` | （可扩展）生成配置参考 |

优先级：渲染时字段先取注解里的值，其次回退 handler 提供的框架元数据
（如 FastAPI 装饰器的 method/path/summary）。

## 漂移检查

文档中的自动生成区用：

```markdown
<!-- BEGIN GENERATED: api-routes -->
…自动生成内容…
<!-- END GENERATED: api-routes -->
```

包裹。`check` 会比对"现有生成区"与"重新扫描的最新结果"，不一致即报漂移，
强制开发者提交与源码一致的文档，防止"改代码忘更新文档"。

## 外部生态定位

docsforge 在"文档即代码"工具生态中的定位与差异化依据，见本仓库
[《文档生成工具生态调研一览》](../docs/design/docgen-tool-ecosystem.md)
（含与 apidoc / mkdocstrings / Doxygen / Sphinx 等的对比）。

## roadmap（尚未实现）

- [ ] `entry_points` 自动发现第三方 handler 插件
- [ ] 配置驱动（YAML）：声明扫描哪些文件、如何分组
- [ ] 文档站点渲染（接入 MkDocs/VitePress 而非裸 Markdown）
- [ ] 时序图生成器集成（当前仅识别 `docs:seq` 标记，渲染交给外部工具）
- [ ] 更多内置 handler：TypeScript/Go/Java

## License

MIT
