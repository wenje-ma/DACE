# -*- coding: utf-8 -*-
"""
ipynb 转 md 脚本
=================

功能：
    运行后会弹出文件选择对话框，可自由选择一个或多个 .ipynb 文件。
    对每个文件，只保留 markdown 单元格（正文/公式），跳过代码单元格，
    分别输出对应的 .md 文件，保存在与源文件相同的目录下。

用法：
    直接运行本脚本（如：python ipynb_to_md.py），然后在对话框中勾选文件即可。
"""

import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog


def notebook_to_markdown(nb_path: Path) -> str:
    """读取一个 .ipynb 文件，只抽取 markdown 单元格，跳过代码单元格，返回 markdown 文本。"""
    with open(nb_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    cells = notebook.get("cells", [])
    md_parts = []

    for cell in cells:
        cell_type = cell.get("cell_type", "")
        source = cell.get("source", "")

        # source 字段可能是字符串，也可能是字符串列表，统一拼接成字符串
        if isinstance(source, list):
            source = "".join(source)

        # 只保留 markdown 单元格；code / raw 等其他类型一律跳过
        if cell_type == "markdown":
            md_parts.append(source)

    return "\n\n".join(md_parts)


def ipynb_to_md(ipynb_path: str, md_path: str | None = None):
    """将单个 .ipynb 文件转换为 .md"""
    ipynb_file = Path(ipynb_path)
    if not ipynb_file.exists():
        raise FileNotFoundError(f"找不到文件: {ipynb_file}")

    if md_path is None:
        md_file = ipynb_file.with_suffix(".md")
    else:
        md_file = Path(md_path)

    # 转换
    markdown = notebook_to_markdown(ipynb_file)

    # 写入
    md_file.write_text(markdown, encoding="utf-8")
    print(f"✅ 已生成: {md_file}")
    return str(md_file)


def select_and_convert_ipynbs():
    """弹出对话框选择 .ipynb 文件并转换"""
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)  # 窗口置顶

    selected_files = filedialog.askopenfilenames(
        title="请选择要转换的 .ipynb 文件",
        filetypes=[("Jupyter Notebook", "*.ipynb"), ("所有文件", "*.*")],
    )

    if not selected_files:
        print("未选择任何文件，退出。")
        return []

    converted = []
    failed = []
    for ipynb_path in selected_files:
        try:
            output = ipynb_to_md(ipynb_path)
            converted.append(output)
        except Exception as e:
            print(f"❌ 转换失败: {ipynb_path}，错误: {e}")
            failed.append((ipynb_path, str(e)))

    print(f"\n转换完成，成功 {len(converted)} 个，失败 {len(failed)} 个。")
    return converted


if __name__ == "__main__":
    select_and_convert_ipynbs()
