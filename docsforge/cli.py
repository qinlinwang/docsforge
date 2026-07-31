"""
docsforge CLI。

用法：
    docsforge scan <源码文件> [--handler <name>] [--token <token>]
                   [--out <文档.md>] [--anchor <章节标题>]
    docsforge check <源码文件> <文档.md> --token <token> [--handler <name>]
    docsforge handlers

示例（把本仓库后端当示例源）：
    docsforge scan backend/app/main.py --out docs/api.docsforge.md \
        --token api-routes
    docsforge check backend/app/main.py docs/api.docsforge.md --token api-routes
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import drift
from . import registry as _handlers_mod
from .render import render_api_grouped_table


def _resolve_handler(name: str):
    _handlers_mod.load_builtin_handlers()
    cls = _handlers_mod.get_handler(name)
    if cls is None:
        sys.stderr.write(
            f"未知 handler: {name}。可用: {', '.join(_handlers_mod.available_handlers())}\n"
        )
        sys.exit(2)
    return cls()


def _build_api_section(decls) -> str:
    table = render_api_grouped_table(decls)
    body = [
        "<!-- 由 docsforge 从源码 `docs:` 注解自动生成，请勿手工编辑 -->",
        "",
        "### 路由分组",
        "",
    ]
    if table:
        body.append(table)
    else:
        body.append("（当前没有声明 `docs:` 注解的路由）")
    return drift.render_section("api-routes", body)


def cmd_scan(args) -> int:
    handler = _resolve_handler(args.handler)
    decls = handler.scan(args.source)
    token = args.token if args.token else "api-routes"
    section = _build_api_section(decls)

    if args.out:
        out_path = Path(args.out)
        content = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
        new_content = drift.replace_or_insert(
            content, token, section, insert_before=args.anchor or ""
        )
        out_path.write_text(new_content, encoding="utf-8")
        rc = drift.check_drift(new_content, section, token)
        n = len(decls)
        print(f"✓ {out_path}: 写入生成区（扫描 {n} 个声明）")
        return 0 if rc else 1
    else:
        sys.stdout.write(section + "\n")
        return 0


def cmd_check(args) -> int:
    handler = _resolve_handler(args.handler)
    decls = handler.scan(args.source)
    token = args.token if args.token else "api-routes"
    section = _build_api_section(decls)

    doc = Path(args.doc)
    if not doc.exists():
        sys.stderr.write(f"✗ 文档不存在: {doc}\n")
        return 1
    content = doc.read_text(encoding="utf-8")
    ok = drift.check_drift(content, section, token)
    if ok:
        print(f"✓ 无漂移：{doc} 的 [{token}] 生成区与源码注解一致")
        return 0
    sys.stderr.write(f"✗ 漂移：{doc} 的 [{token}] 生成区与源码注解不一致\n")
    sys.stderr.write("   重新运行 `docsforge scan` 后提交生成区\n")
    return 1


def cmd_handlers(args) -> int:
    _handlers_mod.load_builtin_handlers()
    for name in _handlers_mod.available_handlers():
        print(f"  - {name}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="docsforge", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_scan = sub.add_parser("scan", help="扫描源码并把 docs: 生成区写入文档")
    p_scan.add_argument("source", help="源码文件路径")
    p_scan.add_argument("--handler", default="python_fastapi", help="语言/框架 handler")
    p_scan.add_argument("--token", default="api-routes", help="生成区 token")
    p_scan.add_argument("--out", help="输出 Markdown 文档路径（缺省打印到 stdout）")
    p_scan.add_argument("--anchor", default="", help="尚无生成区时插入到的章节标题前")
    p_scan.set_defaults(func=cmd_scan)

    p_check = sub.add_parser("check", help="检查文档生成区是否与源码注解漂移")
    p_check.add_argument("source", help="源码文件路径")
    p_check.add_argument("doc", help="要检查的 Markdown 文档路径")
    p_check.add_argument("--handler", default="python_fastapi")
    p_check.add_argument("--token", default="api-routes")
    p_check.set_defaults(func=cmd_check)

    p_handlers = sub.add_parser("handlers", help="列出已注册 handler")
    p_handlers.set_defaults(func=cmd_handlers)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
