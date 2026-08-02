"""
docs:index summary="Python/FastAPI handler：AST 遍历提取函数/类/模块/配置的 docs: 注解"

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


def _assign_target_name(node: ast.AnnAssign | ast.Assign) -> str | None:
    """取赋值语句的单一目标变量名。非单一 Name 目标返回 None。"""
    if isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name) and node.target.id != "_":
            return node.target.id
        return None
    # Assign：只处理单目标（covers `X = v`，跳过 `a = b = v` / 元组解包）
    if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        return node.targets[0].id
    return None


def _config_assignment(
    node: ast.AnnAssign | ast.Assign,
    src_lines: list[str],
    src_path: str,
) -> TaggedDeclaration | None:
    """识别一条带 `docs:config` 注解的赋值，返回 TaggedDeclaration；否则 None。

    配置常量形如：
        # docs:config key="PORT" env="PORT" default="8080" desc="服务端口"
        PORT: int = 8080   （AnnAssign）
    或
        DEBUG = False      （Assign）

    只有上方紧邻有 `docs:config` 注解的赋值才被当作配置项，普通变量不受影响。
    默认值从源码标注里取（`desc`/`env`/`default` 由注解提供）；也能从
    注解值回退到实际常量值（无 `default` 时）。
    """
    name = _assign_target_name(node)
    if name is None or name.startswith("_"):
        return None

    above = _collect_comments_above(src_lines, node.lineno)
    tags = tags_from_comment(above)
    if "config" not in tags:
        return None  # 没写 docs:config 的赋值不是配置项

    # 从注解里取配置元数据；无 default 时回退到代码里的实际常数值
    cfg = tags["config"]
    if "default" not in cfg:
        if hasattr(node, "value") and isinstance(node.value, ast.Constant):
            cfg["default"] = str(node.value.value)

    return TaggedDeclaration(
        name=name,
        docs_tags=tags,
        line=node.lineno,
        source="",
        source_path=src_path,
        extra=cfg,
    )


# docs:index summary="扫描 Python 文件，提取带 docs: 标签的函数/类/模块/配置声明"
@register("python_fastapi")
class PythonFastAPIHandler:
    """扫描 Python 文件，返回所有带 `docs:` 标签的函数声明。

    既是 Python 通用提取器，也针对 FastAPI 路由做了 method/path/summary 回退。
    """

    name = "python_fastapi"
    extensions: tuple[str, ...] = (".py", ".pyw", ".pyi")

    def scan(self, path: str | Path) -> list[TaggedDeclaration]:
        p = Path(path)
        if not p.exists():
            return []
        text = p.read_text(encoding="utf-8")
        lines = text.splitlines()
        tree = ast.parse(text)
        out: list[TaggedDeclaration] = []
        src_path = str(p)

        # --- 模块级 docstring（docs:index / docs:api 等标签可放在模块 docstring 中）---
        module_doc = ast.get_docstring(tree) or ""
        if module_doc:
            mod_tags = tags_from_comment(module_doc)
            if mod_tags:
                out.append(
                    TaggedDeclaration(
                        name=p.stem,
                        docs_tags=mod_tags,
                        line=1,
                        source=module_doc,
                        source_path=src_path,
                        extra={"kind": "module"},
                    )
                )

        for node in ast.walk(tree):
            # --- 类定义（带 docs:index / docs:config 注解的类级声明）---
            if isinstance(node, ast.ClassDef):
                cls_doc = ast.get_docstring(node) or ""
                above = _collect_comments_above(lines, node.lineno)
                tags = tags_from_comment(above + "\n" + cls_doc)
                if tags:
                    out.append(
                        TaggedDeclaration(
                            name=node.name,
                            docs_tags=tags,
                            line=node.lineno,
                            source=cls_doc,
                            source_path=src_path,
                            extra={"kind": "class"},
                        )
                    )
                continue  # 类体内部的赋值不另当配置

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
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
                        source_path=src_path,
                        extra=extra,
                    )
                )
                continue  # 函数体内部的赋值不另当配置

            # 配置常量：模块级 / 类级的 (Ann)Assign，带 docs:config 注解
            if isinstance(node, (ast.AnnAssign, ast.Assign)):
                decl = _config_assignment(node, lines, src_path)
                if decl is not None:
                    out.append(decl)
        return out


__all__ = ["PythonFastAPIHandler"]
