"""docsforge — 从源码 `docs:` 注释注解自动生成文档。"""
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
