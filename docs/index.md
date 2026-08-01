# docsforge 文档

> 这是 docsforge 自身的文档库，也是**"标准文档目录结构"的活示例**。
> 目的：既说明 docsforge 怎么用，也示范它要产出的文档该长什么样。
>
> 📍 目录约定（docsforge 标准骨架）
> - `reference/` —— **生成区**：由 `docsforge scan` 自动生成，勿手工编辑
> - `guides/` —— **手写区**：面向使用者的操作指南，人工维护
> - `topics/` —— **手写区**：概念性长文，人工维护

## 关于 docsforge

docsforge 从源码 `docs:` 注释注解自动生成标准、高质量的文档，并在源码改动时
检查文档是否漂移。一句话：**"你写 `docs:` 注释，它生成文档 + 检查过期。"**

## 从哪里开始

- 想快速上手 → [快速上手](getting-started.md)
- 想看 API / 配置 / 模块参考 → [参考索引](reference/index.md)（自动生成）
- 想看怎么部署发布 → [部署指南](guides/deployment.md)
- 想理解架构设计 → [架构说明](topics/architecture.md)

## 文档全景

| 章节 | 类型 | 内容 | 维护方式 |
|---|---|---|---|
| [参考索引](reference/index.md) | 生成区 | 模块/类/函数索引 | `docsforge scan` 自动填 |
| [API 路由](reference/api-routes.md) | 生成区 | 路由分组表 | 源码 `docs:api` 注解驱动 |
| [配置参考](reference/config.md) | 生成区 | 配置项/环境变量 | 源码 `docs:config` 注解驱动 |
| [部署指南](guides/deployment.md) | 手写区 | 安装/部署/发布 | 人工维护 |
| [迁移指南](guides/migration.md) | 手写区 | 版本间迁移 | 人工维护 |
| [架构说明](topics/architecture.md) | 手写区 | 模块与设计 | 人工维护 |
| [注解规范](topics/referencing-guidelines.md) | 手写区 | `docs:` 标签用法 | 人工维护 |
