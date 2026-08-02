"""docsforge — 从源码 `docs:` 注释注解自动生成文档。

docs:index summary="包入口：暴露主要公共 API（parse_docs_tags / TaggedDeclaration）"
"""
from __future__ import annotations

from .tags import parse_docs_tags
from .model import TaggedDeclaration
from . import render
from . import drift

__version__ = "0.1.0"

__all__ = [
    "parse_docs_tags",
    "TaggedDeclaration",
    "render",
    "drift",
    "__version__",
]
