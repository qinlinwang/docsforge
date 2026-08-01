"""
多文件扫描（S4）：把"单个源码文件"升级为"一次扫描整个项目"。

设计原则：**多文件展开是语言无关的通用能力**，绝不放进某个语言 handler 里重复
实现。本模块负责：

  - resolve_inputs(paths, extensions)  ：把 文件 / 目录 / glob 展开成源码文件清单，
                                         并按 handler 的扩展名过滤；
  - scan_files(handler, paths)         ：对清单里的每个文件调用 handler.scan(path)，
                                         合并返回所有 TaggedDeclaration。

Handler 的契约**保持不变**：每个 handler 只管"解析单个文件"（scan(path)），
多文件的遍历与聚合在这里统一完成。新增语言只需实现单文件 scan 并声明 extensions，
即可自动获得多文件/项目级扫描能力。

由于逐文件只回读声明、不持有整项目内存快照，对大型 monorepo 也能保持流式、
低内存的处理方式（聚合的是已解析的 IR，而非源码文本）。
"""
from __future__ import annotations

from pathlib import Path
from glob import glob
from typing import Iterable, Sequence

from .model import TaggedDeclaration
from . import registry


def _expand_one(raw: str, extensions: Sequence[str]) -> list[Path]:
    """把单个输入（文件/目录/glob）展开为源码文件清单。"""
    p = Path(raw)

    # 显式文件：存在即用（不强制匹配扩展名，允许用户硬性指定某文件）
    if p.is_file():
        return [p]

    # 目录：递归收集匹配扩展名的文件
    if p.is_dir():
        return sorted(
            f for f in p.rglob("*") if f.is_file() and f.suffix.lower() in extensions
        )

    # 剩下的当成 glob（可能含 * ? [ 等通配符）—— 目录未找到也走这里
    candidates = [
        Path(m) for m in glob(raw, recursive=True) if Path(m).is_file()
    ]
    if extensions:
        candidates = [c for c in candidates if c.suffix.lower() in extensions]
    return sorted(candidates)


def resolve_inputs(paths: Iterable[str | Path], extensions: Sequence[str]) -> list[Path]:
    """把多个输入参数（文件/目录/glob）展开成去重、排序后的源码文件清单。

    Args:
        paths: 命令行传入的多个路径；支持文件、目录、glob（含 ** 递归）。
        extensions: 该语言 handler 支持的扩展名集合（含点，如 {".py"}）。

    Returns:
        去重并按字符串排序后的文件路径列表。
    """
    seen: set[Path] = set()
    out: list[Path] = []
    for raw in paths:
        for f in _expand_one(str(raw), list(extensions)):
            if f not in seen:
                seen.add(f)
                out.append(f)
    out.sort(key=str)
    return out


def scan_files(
    handler_name: str,
    paths: Iterable[str | Path],
) -> list[TaggedDeclaration]:
    """用指定 handler 扫描多个输入，聚合所有声明。

    Args:
        handler_name: 已注册的 handler 名（如 "python_fastapi"）。
        paths: 文件 / 目录 / glob，可多个。

    Returns:
        按文件、再按声明行号排序后的 TaggedDeclaration 列表。
    """
    registry.load_builtin_handlers()
    cls = registry.get_handler(handler_name)
    if cls is None:
        raise ValueError(
            f"未知 handler: {handler_name}。可用: {', '.join(registry.available_handlers())}"
        )
    handler = cls()

    extensions = list(getattr(handler, "extensions", ()))
    files = resolve_inputs(paths, extensions)

    decls: list[TaggedDeclaration] = []
    for f in files:
        decls.extend(handler.scan(f))

    # 稳定排序：先按文件路径，再按行号，保证渲染/漂移输出可预测、幂等
    decls.sort(key=lambda d: (str(d.source_path), d.line))
    return decls


__all__ = ["resolve_inputs", "scan_files"]
