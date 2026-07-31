"""
内置 handler：Python + FastAPI。

它把 `tools/docs/annotations.py` 里的"Python/FastAPI 提取逻辑"抽成
docsforge 的一个官方适配器。职责：

  1. 用 AST 遍历 Python 函数；
  2. 收集函数声明就近的 `docs:` 注释（docstring + 上方 `# docs:` 行）；
  3. 解析成 TaggedDeclaration，并把 FastAPI 装饰器提供的
     method / path / summary 放入 extra（供渲染器回退读取）。

新增语言时，参考本文件实现一个 Handler 即可，渲染/漂移/CLI 全复用。
"""
from __future__ import annotations

import ast
from pathlib import Path

from ..registry import register, tags_from_comment
from ..model import TaggedDeclaration

_VERBS = ("get", "post", "put", "patch", "delete", "options", "head")


def _collect_comments_above(src_lines: list[str], def_line: int) -> str:
    """收集 def 行上方最近的连续注释块（允许穿过装饰器 @app.xxx / 空行）。"""
    comments: list[str] = []
    i = def_line - 2  # def_line 是 1 基，src_lines 是 0 基 → 从 def 上一行起
    while i >= 0:
        stripped = src_lines[i].lstrip()
        if stripped.startswith("#"):
            comments.append(src_lines[i].strip())
            i -= 1
        elif stripped == "" or stripped.startswith("@"):
            i -= 1
            if stripped == "":
                break  # 空行之后不再向上穿透
        else:
            break
    return "\n".join(reversed(comments))


def _fastapi_decorator(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, str] | None:
    """从 FastAPI 路由装饰器提取 (method, path, summary)。非路由返回 None。"""
    for dec in node.decorator_list:
        if not (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute)):
            continue
        method = dec.func.attr.lower()
        if method not in _VERBS or getattr(dec.func.value, "id", "") != "app":
            continue
        path = ""
        summary = ""
        for arg in dec.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.startswith("/"):
                path = arg.value
        for kw in dec.keywords:
            if kw.arg == "path" and isinstance(kw.value, ast.Constant):
                path = str(kw.value.value)
            elif kw.arg == "summary" and isinstance(kw.value, ast.Constant):
                summary = str(kw.value.value)
        if path:
            return {"method": method.upper(), "path": path, "summary": summary}
    return None


@register("python_fastapi")
class PythonFastAPIHandler:
    """扫描 Python 文件，返回所有带 `docs:` 标签的函数声明。

    既是 Python 通用提取器，也针对 FastAPI 路由做了 method/path/summary 回退。
    """

    name = "python_fastapi"

    def scan(self, path: str | Path) -> list[TaggedDeclaration]:
        p = Path(path)
        if not p.exists():
            return []
        text = p.read_text(encoding="utf-8")
        lines = text.splitlines()
        tree = ast.parse(text)
        out: list[TaggedDeclaration] = []

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            doc = ast.get_docstring(node) or ""
            above = _collect_comments_above(lines, node.lineno)
            tags = tags_from_comment(above + "\n" + doc)
            if not tags:
                continue  # 没带 docs: 标签的函数不关心

            extra: dict = {}
            deco = _fastapi_decorator(node)
            if deco:
                extra.update(deco)

            out.append(
                TaggedDeclaration(
                    name=node.name,
                    docs_tags=tags,
                    line=node.lineno,
                    source=doc,
                    extra=extra,
                )
            )
        return out


__all__ = ["PythonFastAPIHandler"]
