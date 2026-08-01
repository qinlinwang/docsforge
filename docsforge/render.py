"""
Markdown 渲染器：把 TaggedDeclaration 的规范 IR 渲染成 Markdown。

全部**语言无关**：只消费 TaggedDeclaration（extra 里的 method/path/summary
由 handler 填充）。新语言的 handler 产出同样结构的 IR，这里原样复用。

S1：渲染器改为**按 token 分派**。核心思想：

  - 每种产出物 = 一个 token + 一个渲染器函数（@register_renderer(token)）。
  - render(token, decls) 按 token 查注册表路由到对应渲染器；未注册的 token
    给明确报错，而非静默当成 api-routes。
  - 新增产出物只加一个 @register_renderer 函数，不用改 CLI / 流水线。

现有 api-routes 渲染器原样保留，行为完全不变（回归安全）。
"""
from __future__ import annotations

from typing import Callable

from .model import TaggedDeclaration


def decl_extra_value(decl: TaggedDeclaration, key: str, topic: str = "api", fallback: str = "") -> str:
    """从声明取字段，优先取注解 tag 里的值，其次取 handler 的 extra。"""
    return decl.tag(topic).get(key) or (decl.extra.get(key, "") or fallback)


def routes_with_method_path(decls: list[TaggedDeclaration]) -> list[TaggedDeclaration]:
    """过滤出有 method+path 的声明（用于渲染 API 路由表）。"""
    return [d for d in decls if decl_extra_value(d, "method") and decl_extra_value(d, "path")]


# ---------------------------------------------------------------------------
# S1：token -> 渲染器 注册表
# 渲染器契约：fn(decls: list[TaggedDeclaration]) -> str（产出一段 Markdown 正文）
# ---------------------------------------------------------------------------
_RENDERERS: dict[str, Callable[[list[TaggedDeclaration]], str]] = {}


def register_renderer(token: str):
    """装饰器：把一个渲染函数注册到指定 token。

    新增产出物 = 写一个 fn(decls)->str，再 @register_renderer("<token>") 挂上，
    render() 即可用该 token 路由到它。CLI / 流水线无需改动。
    """
    def deco(fn):
        _RENDERERS[token] = fn
        return fn
    return deco


def available_tokens() -> list[str]:
    """列出所有已注册的渲染 token（供 CLI / help 展示）。"""
    return sorted(_RENDERERS)


def render(token: str, decls: list[TaggedDeclaration]) -> str:
    """按 token 路由到对应渲染器，产出一段 Markdown 正文。

    Args:
        token: 想产出的文档类型，如 "api-routes"。
        decls: 扫描出的全部声明（渲染器自行决定取哪些）。

    Returns:
        该 token 渲染出的 Markdown 正文（不含生成区标记）。

    Raises:
        KeyError: token 未注册时抛错，提醒新增渲染器，而非静默错结果。
    """
    fn = _RENDERERS.get(token)
    if fn is None:
        raise KeyError(
            f"未知 token: {token!r}。可用: {', '.join(available_tokens())}。"
            "新增产出物请先在 render.py 里 @register_renderer(token) 注册渲染器。"
        )
    return fn(decls)


# ---------------------------------------------------------------------------
# api-routes 渲染器（现状保留，行为不变）
# ---------------------------------------------------------------------------
@register_renderer("api-routes")
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


# ---------------------------------------------------------------------------
# config-reference 渲染器（S2-MVP）
# ---------------------------------------------------------------------------
@register_renderer("config-reference")
def render_config_reference(decls: list[TaggedDeclaration]) -> str:
    """把带 `docs:config` 注解的配置声明渲染成配置参考表。

    来源：模块级 / 类级的配置常量（由 python_fastapi handler 的
    _config_assignment 提取），each 携带 key/env/default/value/desc。

    表列：配置项(key) | 环境变量(env) | 默认值(default) | 说明(desc)
    """
    cfg_decls = [d for d in decls if d.has_tag("config")]
    if not cfg_decls:
        return ""

    rows: list[tuple[str, str, str, str]] = []
    for d in cfg_decls:
        t = d.tag("config")
        key = t.get("key") or d.name
        env = t.get("env") or "-"
        default = t.get("default") or "-"
        desc = t.get("desc") or ""
        rows.append((key, env, default, desc))

    # 按 key 稳定排序，保证幂等
    rows.sort(key=lambda r: r[0])

    out = ["| 配置项 | 环境变量 | 默认值 | 说明 |", "|---|---|---|---|"]
    for key, env, default, desc in rows:
        out.append(f"| {key} | `{env}` | `{default}` | {desc} |")
    return "\n".join(out)


__all__ = [
    "decl_extra_value",
    "routes_with_method_path",
    "register_renderer",
    "available_tokens",
    "render",
    "render_api_grouped_table",
    "render_config_reference",
    "group_by_topic",
]
