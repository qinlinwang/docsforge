# 部署指南

> **手写区**：面向使用者/维护者的操作指南，人工维护，不会被子文档工具覆盖。

本文说明如何构建、发布 docsforge，以及把它接入目标项目的 CI 作为漂移门槛。

## 构建与发布

```bash
# 构建 wheel
python -m build

# 发布（需合适权限）
pip publish docsforge-<version>.tar.gz
```

## 接入 CI 漂移检查

在目标仓库的 CI / pre-commit 中挂 `docsforge check`，拦截"改代码忘更新文档"：

```yaml
# .pre-commit-config.yaml 片段
- repo: local
  hooks:
    - id: docsforge-check
      name: docsforge drift check
      entry: docsforge check examples/main.py docs/reference/api-routes.md
      language: system
```

- `check` 退出码 0=无漂移，非 0=漂移（阻断提交）。
- 漂移时先 `docsforge scan` 重新生成区，再提交。

## 版本语义

- 0.x：内部功能逐步落地中（见 [roadmap](../design/roadmap.md)），API 可能变动。
