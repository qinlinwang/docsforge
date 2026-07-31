"""
Handler 协议与注册表：docsforge 的**插件点**。

不同语言/框架只有"如何从源码提取声明附近的注释块"不同。为支持跨语言，
docsforge 把这一步抽成注册表 + 语言适配器（handlers/ 目录下每个文件一个）：

    registry.LanguageHandler
    handlers/<lang>.py 实现 scan() 并用 @register("name") 注册

- 内置：python_fastapi（Python + FastAPI 装饰器回退）
- 扩展：实现 Handler 或子类化后经 register 注册即可
  （后续可接 entry_points 自动发现，见 README 路线图）
"""
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .model import TaggedDeclaration
from .tags import parse_docs_tags


class LanguageHandler(Protocol):
    """一个语言/框架的"注释提取适配器"。"""

    name: str

    def scan(self, path: str | Path) -> list[TaggedDeclaration]:
        """扫描给定源码文件，返回带 docs: 标签的声明列表。"""
        ...


# 全局注册表：name -> Handler 类
_REGISTRY: dict[str, type[LanguageHandler]] = {}


def register(name: str):
    """类装饰器：注册一个 handler。"""

    def deco(cls):
        cls.name = name
        _REGISTRY[name] = cls
        return cls

    return deco


def get_handler(name: str) -> type[LanguageHandler] | None:
    return _REGISTRY.get(name)


def available_handlers() -> list[str]:
    return sorted(_REGISTRY)


def load_builtin_handlers() -> None:
    """导入内置 handler 使其注册（幂等）。"""
    from .handlers.python_fastapi import PythonFastAPIHandler  # noqa: F401


# 便捷：把一段注释文本解析为 docs_tags（跨语言共用的入口）
def tags_from_comment(text: str) -> dict[str, dict[str, str]]:
    return parse_docs_tags(text)


__all__ = [
    "LanguageHandler",
    "TaggedDeclaration",
    "register",
    "get_handler",
    "available_handlers",
    "load_builtin_handlers",
    "tags_from_comment",
]
