"""
Markdown 渲染器：把 TaggedDeclaration 的规范 IR 渲染成 Markdown。

全部**语言无关**：只消费 TaggedDeclaration（extra 里的 method/path/summary
由 handler 填充）。新语言的 handler 产出同样结构的 IR，这里原样复用。
"""
from __future__ import annotations

from .model import TaggedDeclaration


def decl_extra_value(decl: TaggedDeclaration, key: str, topic: str = "api", fallback: str = "") -> str:
    """从声明取字段，优先取注解 tag 里的值，其次取 handler 的 extra。"""
    return decl.tag(topic).get(key) or (decl.extra.get(key, "") or fallback)


def routes_with_method_path(decls: list[TaggedDeclaration]) -> list[TaggedDeclaration]:
    """过滤出有 method+path 的声明（用于渲染 API 路由表）。"""
    return [d for d in decls if decl_extra_value(d, "method") and decl_extra_value(d, "path")]


def render_api_grouped_table(decls: list[TaggedDeclaration]) -> str:
    """把 API 路由声明渲染成按 group 分组的 Markdown 表格。

    等价物：tools/docs/annotations.py 的 render_api_grouped_table ——
    这里是 docsforge 的独立实现，用 TaggedDeclaration 而非 dict。
    """
    routes = routes_with_method_path(decls)
    if not routes:
        return ""
    by_group: dict[str, list[TaggedDeclaration]] = {}
    for d in routes:
        group = d.tag("api").get("group") or "其他"
        by_group.setdefault(group, []).append(d)

    out: list[str] = []
    for group in sorted(by_group):
        items = sorted(by_group[group], key=lambda d: decl_extra_value(d, "path"))
        out.append(f"### {group}")
        out.append("")
        out.append("| 方法 | 路径 | 说明 |")
        out.append("|---|---|---|")
        for d in items:
            method = decl_extra_value(d, "method")
            path = decl_extra_value(d, "path")
            summary = decl_extra_value(d, "summary")
            out.append(f"| {method} | `{path}` | {summary} |")
        out.append("")
    return "\n".join(out)


def group_by_topic(decls: list[TaggedDeclaration], topic: str) -> list[TaggedDeclaration]:
    """返回声明了指定主题标签的声明列表。"""
    return [d for d in decls if d.has_tag(topic)]


__all__ = [
    "decl_extra_value",
    "routes_with_method_path",
    "render_api_grouped_table",
    "group_by_topic",
]
