# -*- coding: utf-8 -*-
r"""
auto_leftright.py — 批量把文件中的西文括号 ( ) [ ] \{ \} 以及 | \| 替换成 \left ... \right 版本。

规则:
  - 全文查找西文括号，直接替换（正文里只用中文括号，所以不会误伤正文）
  - | 和 \|（绝对值 / 范数）只在数学环境（$...$ 与 $$...$$）内处理，
    避免误伤 Markdown 表格的竖线分隔符；同一数学片段内按出现顺序左右配对，
    奇数个裸竖线的片段无法可靠配对，整段跳过并打印警告
  - 已用 \left / \right / \big 系列包裹的定界符自动跳过（幂等，可反复运行）
  - \( \) \[ \]（数学定界符）不处理；裸 { }（分组大括号）不处理
  - 直接原地替换源文件；无变化时不写回

用法:
    python auto_leftright.py              # 弹窗多选 Markdown 文件
"""

import re
from pathlib import Path
from tkinter import Tk, filedialog

# markdown 图片/链接（整体保留，避免把图片路径转坏）
MD_LINK = r"!?\[[^\]]*\]\([^)]*\)"
# 已包裹的定界符（原样保留）: \left( \right] \bigl\{ \left. 等
DELIM = r"(?:\(|\)|\[|\]|\\\{|\\\}|\||\.)"
WRAPPED = (
    MD_LINK
    + r"|\\left\s*" + DELIM
    + r"|\\right\s*" + DELIM
    + r"|\\[bB]ig(?:g|l|r)?\s*" + DELIM
)
# 裸定界符（要被替换的）: 前面不是反斜杠的 ( ) [ ]，以及 \{ \}
BARE = r"(?<!\\)(\(|\)|\[|\])|(\\\{|\\\})"
PAT = re.compile(WRAPPED + "|" + BARE)

# --- | 与 \| 的数学环境内左右配对 ---
# 匹配一段反斜杠（0 对 + 可选单个）后紧跟的 |；
# 反斜杠个数为奇数 => \|（双竖线/范数），偶数 => |（单竖线/绝对值）
BAR = re.compile(r"(?<!\\)((?:\\\\)*\\?)\|")
# 定界符前面已经是 \left / \right / \big 系列 => 已包裹，跳过且不参与配对
WRAPPED_PRE = re.compile(r"(?:\\left|\\right|\\[bB]ig(?:g|l|r)?)\s*$")


def math_spans(text: str):
    r"""返回 $...$ 与 $$...$$ 数学片段的 (start, end) 列表；\$ 转义不视为定界符。"""
    spans = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "\\":
            i += 2  # 跳过转义字符
            continue
        if c == "$":
            if i + 1 < n and text[i + 1] == "$":
                j = text.find("$$", i + 2)
                if j < 0:
                    break
                spans.append((i, j + 2))
                i = j + 2
            else:
                j = text.find("$", i + 1)
                if j < 0:
                    break
                spans.append((i, j + 1))
                i = j + 1
        else:
            i += 1
    return spans


def convert_bars(text: str) -> str:
    r"""只转换数学片段内的裸 | / \|：按出现顺序交替加 \left / \right。"""
    out = []
    pos = 0
    for a, b in math_spans(text):
        out.append(text[pos:a])
        span = text[a:b]
        bars = [m for m in BAR.finditer(span)
                if not WRAPPED_PRE.search(m.string, 0, m.start())]
        if len(bars) % 2:
            print(f"警告: 数学片段内 | 数量为奇数（无法可靠配对，整段跳过）: {span[:60]!r}")
            out.append(span)
        else:
            new_span = span
            for k in range(len(bars) - 1, -1, -1):  # 从后往前替换，前面的偏移不受影响
                m = bars[k]
                tok = m.group(1) + "|"
                lr = "\\left" if k % 2 == 0 else "\\right"
                new_span = new_span[:m.start()] + lr + tok + new_span[m.end():]
            out.append(new_span)
        pos = b
    out.append(text[pos:])
    return "".join(out)


def convert(text: str) -> str:
    text = convert_bars(text)  # 先处理 | \|（需要数学环境扫描），再处理括号

    def repl(m):
        s = m.group(0)
        if s in ("(", "["):
            return "\\left" + s
        if s in (")", "]"):
            return "\\right" + s
        if s == "\\{":
            return "\\left\\{"
        if s == "\\}":
            return "\\right\\}"
        return s  # 已包裹的，原样保留

    return PAT.sub(repl, text)


def process_file(path: Path):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    data = raw[3:] if bom else raw
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        print(f"跳过（非 UTF-8）: {path}")
        return
    new = convert(text)
    if new == text:
        print(f"无需修改: {path}")
        return
    path.write_bytes((("\ufeff" if bom else "") + new).encode("utf-8"))
    n1 = new.count("\\left(") - text.count("\\left(")
    n2 = new.count("\\left[") - text.count("\\left[")
    n3 = new.count("\\left\\{") - text.count("\\left\\{")
    n4 = new.count("\\left|") - text.count("\\left|")
    n5 = new.count("\\left\\|") - text.count("\\left\\|")
    print(f"已转换: {path}  (+\\left( ×{n1}, +\\left[ ×{n2}, +\\left\\{{ ×{n3}, "
          f"+\\left| ×{n4}, +\\left\\| ×{n5})")


def select_and_convert_mds():
    root = Tk()
    root.withdraw()

    selected_files = filedialog.askopenfilenames(
        title="请选择要转换的 Markdown 文件",
        filetypes=[("Markdown 文件", "*.md"), ("All Files", "*.*")]
    )

    if not selected_files:
        print("未选择任何文件，退出。")
        return []

    for md_path in selected_files:
        process_file(Path(md_path))

    print(f"转换完成，共处理 {len(selected_files)} 个文件。")


if __name__ == "__main__":
    select_and_convert_mds()
