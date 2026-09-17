# -*- coding: utf-8 -*-
r"""
auto_leftright.py — 批量把文件中的西文括号 ( ) [ ] \{ \} 替换成 \left ... \right 版本。

规则:
  - 全文查找西文括号，直接替换（正文里只用中文括号，所以不会误伤正文）
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


def convert(text: str) -> str:
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
    print(f"已转换: {path}  (+\\left( ×{n1}, +\\left[ ×{n2}, +\\left\\{{ ×{n3})")


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
