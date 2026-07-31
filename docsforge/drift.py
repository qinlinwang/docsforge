"""
漂移检查（drift）：生成区与"重新生成结果"的一致性校验。

文档的自动生成区用 `<!-- BEGIN GENERATED: <id> -->` … `<!-- END GENERATED: <id> -->`
标记。drift 模块负责：

  - render_section(token, body)：构造一个规范生成区；
  - replace_or_insert(content, token, section, insert_before)：把生成区插入/替换进文档，
    并折叠多余空行（保证幂等）；
  - extract_section(content, token)：取回文档中现有生成区；
  - check_drift(text, expected_section, token)：判断文档是否与最新生成结果一致。

所有逻辑**语言无关、与框架无关**——不管 source 是哪个语言写的，渲染产物
都是 Markdown 文本，这里只比较字符串。
"""
from __future__ import annotations


def section_markers(token: str) -> tuple[str, str]:
    """由 token 生成开始/结束标记。"""
    return f"<!-- BEGIN GENERATED: {token} -->", f"<!-- END GENERATED: {token} -->"


def render_section(token: str, body_lines: list[str]) -> str:
    """构造规范生成区，首尾不加多余空行，段落间空一行。"""
    start, end = section_markers(token)
    block = [start] + body_lines + [end]
    return "\n".join(block)


def extract_section(content: str, token: str) -> str | None:
    """取回文档中现有生成区（含标记）。缺失返回 None，未闭合返回 None。"""
    start_mk, end_mk = section_markers(token)
    s = content.find(start_mk)
    if s == -1:
        return None
    e = content.find(end_mk, s)
    if e == -1:
        return None
    return content[s : e + len(end_mk)]


def replace_or_insert(content: str, token: str, section: str, insert_before: str = "") -> str:
    """把生成区写入文档：已有则替换，没有则插到 anchor 前（或末尾）。"""
    start_mk, end_mk = section_markers(token)
    s = content.find(start_mk)
    if s != -1:
        e = content.find(end_mk, s)
        if e != -1:
            content = content[:s] + section + content[e + len(end_mk):]
            return collapse_blank_lines(content)
    # 未找到：插到 anchor 前
    if insert_before:
        pos = content.find(insert_before)
        if pos != -1:
            content = content[:pos] + section + "\n\n" + content[pos:]
            return collapse_blank_lines(content)
    content = content + "\n\n" + section + "\n"
    return collapse_blank_lines(content)


def collapse_blank_lines(text: str, max_blank: int = 2) -> str:
    """折叠连续超过 max_blank 的空行（跳过代码围栏内），保证幂等。

    Markdown 代码围栏（```）内的空行不折叠，避免破坏代码块排版。
    """
    in_fence = False
    out: list[str] = []
    blank = 0
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            blank = 0
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        if line.strip() == "":
            blank += 1
            if blank > max_blank:
                continue
        else:
            blank = 0
        out.append(line)
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def check_drift(content: str, expected_section: str, token: str) -> bool:
    """校验文档里现有生成区与期望的一致。返回 True 表示无漂移。"""
    existing = extract_section(content, token)
    if existing is None:
        return False
    return existing == expected_section


__all__ = [
    "section_markers",
    "render_section",
    "extract_section",
    "replace_or_insert",
    "collapse_blank_lines",
    "check_drift",
]
