"""
docs:index summary="语言无关的 `docs:` 标签解析器，正则匹配 key=&quot;value&quot; 键值对"

docsforge — 从源码 `docs:` 注释注解自动生成文档。

本模块提供 **语言无关** 的 `docs:` 标签解析器。不同语言只有"如何从源码
提取注释"不同（见 handlers/），一旦拿到注释文本，解析完全共用这一份。

标签格式（规范见 README）：

    # docs:api method="POST" path="/api/tickets" group="工单" summary="创建工单"
    # docs:seq

统一前缀 `docs:`，后跟 `key="value"` 键值对（值必须用引号包裹，可跨多行）。
前缀后的第一个 token 是**主题**（api / seq / config …），决定这条标签交给
哪个渲染器。同一函数上可有多个主题，同一主题的多行声明会合并。
"""
from __future__ import annotations

import re

_DOCS_TAG_RE = re.compile(r'docs:(\w+)((?:\s+\w+="[^"]*")*)')
_KEY_VALUE_RE = re.compile(r'(\w+)="([^"]*)"')


# docs:index summary="从注释文本解析 docs: 标签，返回 {主题: {键: 值}}"
def parse_docs_tags(text: str) -> dict[str, dict[str, str]]:
    """从注释/文档字符串文本中解析所有 `docs:` 标签。

    Args:
        text: 注释或 docstring 文本（每个实体就近的注释块）。

    Returns:
        {主题: {键: 值}}。例如
        ``{"api": {"group": "工单", "method": "POST"}, "seq": {}}``。

    本函数是纯文本解析，**与语言无关**——只要把"源码声明附近的注释文本"
    喂进来即可（提取注释这件事由各语言的 Handler 负责）。
    """
    if not text:
        return {}
    tags: dict[str, dict[str, str]] = {}
    for m in _DOCS_TAG_RE.finditer(text):
        topic = m.group(1)
        kv = _KEY_VALUE_RE.findall(m.group(2))
        entry = tags.setdefault(topic, {})
        for k, v in kv:
            entry[k] = v
    return tags


__all__ = ["parse_docs_tags"]
