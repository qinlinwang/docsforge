"""
docsforge 的中间表示（IR）：一条"被 docs: 注解标记的源码声明"。

Handler（各语言适配器）从源码提取出这些对象；渲染器（render.py）消费它们。
这样解析与渲染之间通过稳定的 IR 解耦——换语言只需新写一个 handler，渲染器
完全复用。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TaggedDeclaration:
    """源码中一处携带 `docs:` 标签的声明（函数/类/方法…）。

    Attributes:
        name: 声明名（如函数名）。
        docs_tags: parse_docs_tags 的结果，形如 {"api": {...}, "seq": {}}。
        position: 声明所在源码行的行号（1 基）。
        source: 源码文本（可选，供需要回读的渲染器使用）。
        extra: 语言/框架相关的附加字段（如 FastAPI 的 method/path），
            由 handler 自由填充；渲染器按需读取。
    """

    name: str
    docs_tags: dict[str, dict[str, str]] = field(default_factory=dict)
    line: int = 0
    source: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def has_tag(self, topic: str) -> bool:
        return topic in self.docs_tags

    def tag(self, topic: str) -> dict[str, str]:
        return self.docs_tags.get(topic, {})
