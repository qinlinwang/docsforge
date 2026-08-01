# 架构说明

> **手写区**：概念性说明，人工维护。

docsforge 的设计主线：**只有"如何从源码提取注释"是语言相关的，其余全部语言无关**。

## 分层

```
tags.py         语言无关  解析 docs: 标签注解
model.py        语言无关  IR：TaggedDeclaration
registry.py     插件点      Handler 协议 + 注册表
handlers/<lang> 语言相关   每种语言/框架一个提取器
render.py       语言无关   IR → Markdown
drift.py        语言无关   生成区替换 + 漂移检查
cli.py          入口
```

## 跨语言的关键

- 只有 handlers/ 负责"如何从源码提取注释"。
- 解析（tags）、渲染（render）、漂移（drift）、CLI 全部复用。
- 换语言只需实现一个 Handler，其余原样复用。（参考 `handlers/python_fastapi.py`）

## 标准文档目录（docs/ 骨架）

为了让"标准、高质量"可复用，docs 采用生成区与手写区物理隔离：

- `reference/` = 生成区（由 scan 掌管，`check` 校验）
- `guides/` `topics/` = 手写区（人工维护，不被覆盖）

这条边界是 `drift.py` 的设计前提：`scan` 只替换 `<!-- BEGIN/END GENERATED -->`
包裹的内容，手写部分绝不触碰。

## 生态定位对比

docsforge 与 apidoc / mkdocstrings / Doxygen / Sphinx 的差异依据，见外部调研
（仓库 planning 文档），核心差异 = 就近注解 + 漂移强制。
