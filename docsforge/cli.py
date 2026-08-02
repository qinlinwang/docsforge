"""
docs:index summary="命令行入口：argparse CLI（scan/check/handlers 三个子命令）"

docsforge CLI。

用法：
    docsforge scan <源码...> [--handler <name>] [--token <token>]
                   [--out <文档.md>] [--anchor <章节标题>]
    docsforge check <源码...> <文档.md> [--handler <name>] [--token <token>]
    docsforge handlers

<源码...> 支持文件、目录、glob（可多个，将聚合扫描整个项目）。

示例：
    # 单个文件
    docsforge scan examples/main.py
    # 整个项目（目录递归 / glob）
    docsforge scan docsforge --out docs/reference/api-routes.md
    docsforge scan "docsforge/**/*.py" --out docs/reference/api-routes.md
    # 检查漂移
    docsforge check docsforge docs/reference/api-routes.md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import drift
from . import registry as _handlers_mod
from . import scan as _scan
from . import render as _render


def _scan_decls(handler: str, sources) -> list:
    """用通用多文件扫描聚合多个 source（文件/目录/glob）。"""
    try:
        return _scan.scan_files(handler, sources)
    except ValueError as exc:  # 未知 handler
        sys.stderr.write(f"✗ {exc}\n")
        sys.exit(2)


def _build_section(decls, token: str) -> str:
    """按 token 渲染一段生成区（含 BEGIN/END 标记）。

    万能外壳（注释头）+ 该 token 渲染器产出的正文主体。api-routes 渲染器
    只产分组表格本身；不同 token 可各自决定正文排版。
    """
    try:
        body = _render.render(token, decls)
    except KeyError as exc:
        sys.stderr.write(f"✗ {exc}\n")
        sys.exit(2)
    block = [
        "<!-- 由 docsforge 从源码 `docs:` 注解自动生成，请勿手工编辑 -->",
        "",
    ]
    if body and body.strip():
        block.extend(body.splitlines())
    else:
        block.append(f"（当前没有声明 `docs:` 注解的 {token} 内容）")
    return drift.render_section(token, block)


def cmd_scan(args) -> int:
    decls = _scan_decls(args.handler, args.source)
    tokens = args.token if args.token else ["api-routes"]

    if args.out:
        out_path = Path(args.out)
        content = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
        for token in tokens:
            section = _build_section(decls, token)
            content = drift.replace_or_insert(
                content, token, section, insert_before=args.anchor or ""
            )
        out_path.write_text(content, encoding="utf-8")
        n = len(decls)
        print(f"✓ {out_path}: 写入 {len(tokens)} 个生成区（扫描 {n} 个声明）")
        return 0
    else:
        for token in tokens:
            section = _build_section(decls, token)
            sys.stdout.write(section + "\n\n")
        return 0


def cmd_check(args) -> int:
    decls = _scan_decls(args.handler, args.source)
    tokens = args.token if args.token else ["api-routes"]

    doc = Path(args.doc)
    if not doc.exists():
        sys.stderr.write(f"✗ 文档不存在: {doc}\n")
        return 1
    content = doc.read_text(encoding="utf-8")

    ok = True
    for token in tokens:
        section = _build_section(decls, token)
        if not drift.check_drift(content, section, token):
            ok = False
            sys.stderr.write(f"✗ 漂移：{doc} 的 [{token}] 生成区与源码注解不一致\n")
    if ok:
        names = ", ".join(tokens)
        print(f"✓ 无漂移：{doc} 的 [{names}] 生成区与源码注解一致")
        return 0
    sys.stderr.write("   重新运行 `docsforge scan` 后提交生成区\n")
    return 1


def cmd_handlers(args) -> int:
    _handlers_mod.load_builtin_handlers()
    for name in _handlers_mod.available_handlers():
        print(f"  - {name}")
    return 0


# docs:index summary="CLI 入口：argparse 解析三个子命令（scan/check/handlers）"
def main() -> None:
    parser = argparse.ArgumentParser(prog="docsforge", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_scan = sub.add_parser("scan", help="扫描源码并把 docs: 生成区写入文档")
    p_scan.add_argument("source", nargs="+", help="源码文件/目录/glob，可多个")
    p_scan.add_argument("--handler", default="python_fastapi", help="语言/框架 handler")
    p_scan.add_argument("--token", action="append", default=None, help="生成区 token，可多个（如 --token api-routes --token config-reference）；缺省为 api-routes")
    p_scan.add_argument("--out", help="输出 Markdown 文档路径（缺省打印到 stdout）")
    p_scan.add_argument("--anchor", default="", help="尚无生成区时插入到的章节标题前")
    p_scan.set_defaults(func=cmd_scan)

    p_check = sub.add_parser("check", help="检查文档生成区是否与源码注解漂移")
    p_check.add_argument("source", nargs="+", help="源码文件/目录/glob，可多个")
    p_check.add_argument("doc", help="要检查的 Markdown 文档路径")
    p_check.add_argument("--handler", default="python_fastapi")
    p_check.add_argument("--token", action="append", default=None, help="生成区 token，可多个；缺省为 api-routes")
    p_check.set_defaults(func=cmd_check)

    p_handlers = sub.add_parser("handlers", help="列出已注册 handler")
    p_handlers.set_defaults(func=cmd_handlers)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
