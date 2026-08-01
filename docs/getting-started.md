# 快速上手

本文讲**如何安装并使用 docsforge**，作为 docsforge 自身文档的"快速开始"示例。

## 安装

无需安装也能跑源码：

```bash
# 正式使用（在仓库根目录）
pip install .

# 或直接用源码（无需安装）
python -m docsforge.cli --help
```

## 最小工作流

三步：注解 → 扫描 → 校验。

```bash
# 1. 在源码里就近写 docs: 注释（示例见源码 / examples/main.py）
#    # docs:api method="GET" path="/api/health" group="系统" summary="健康检查"

# 2. 扫描并把生成区写入文档
docsforge scan examples/main.py --out docs/reference/api-routes.md

# 3. 提交前校验文档是否与源码漂移（适合进 CI / pre-commit）
docsforge check examples/main.py docs/reference/api-routes.md
```

## 常用命令

- `docsforge scan <源码>` —— 扫描并写入生成区
- `docsforge check <源码> <文档.md>` —— 漂移校验（退出码 0=通过 / 1=漂移）
- `docsforge handlers` —— 列出已注册的语言适配器

## 下一步

- 了解各种标签的写法 → [注解规范](topics/referencing-guidelines.md)
- 了解标准文档目录是怎么组织的 → [文档首页](index.md)
