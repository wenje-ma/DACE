# -*- coding: utf-8 -*-
"""
批量运行 ipynb 中的 R 代码单元格，并把绘图输出保存为 PNG 图片。
功能：
  - 弹出对话框选择一个或多个 .ipynb 文件，抽取其中的 R 代码单元格
  - 每个代码单元格用独立的 PNG 图形设备运行，图片按「单元格_图序」编号
  - 尺寸解析自 options(repr.plot.width/height)，缺省 7×7 英寸、150 dpi
  - 默认：PNG输出与源ipynb放在**同一文件夹**；可--out指定统一输出目录
  - 单个单元格报错不影响其余单元格，最终打印成功/失败汇总
用法：
  python ipynb_run_figs.py                     # 弹出文件选择框
  python ipynb_run_figs.py --out ./my_pngs     # 全部输出到指定目录
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tkinter
from tkinter import filedialog
from pathlib import Path


def clean_env():
    """构造干净的环境变量：去掉 LANG/LC_*，让 R 使用系统 UTF-8 locale（否则中文会乱码/报错）。"""
    env = dict(os.environ)
    for k in [k for k in env if k == "LANG" or k.startswith("LC_")]:
        del env[k]
    return env


# Rscript 路径：优先用 PATH 里的，否则用常见安装位置
RSCRIPT = shutil.which("Rscript") or r"C:\Program Files\R\R-4.6.1\bin\Rscript.exe"
RES = 150                      # dpi
DEFAULT_W, DEFAULT_H = 7.0, 7.0  # 缺省尺寸（英寸）


def cell_text(cell):
    src = cell.get("source", "")
    if isinstance(src, list):
        src = "".join(src)
    return src


def extract_r_cells(nb_path: Path):
    """抽取 notebook 中所有非空 R 代码单元格的源码，按顺序返回列表。"""
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    cells = []
    for c in nb.get("cells", []):
        if c.get("cell_type") == "code":
            src = cell_text(c)
            if src.strip():
                cells.append(src)
    return cells


def r_string(s):
    """把 Python 字符串转成 R 的字符串字面量（正斜杠路径 + 转义双引号）。"""
    s = s.replace("\\", "/")
    return '"' + s.replace('"', '\\"') + '"'


def build_r_script(out_dir_abs, nb_name, cells):
    """生成一个 R 脚本：逐单元格用独立 png 设备运行，保存图片。"""
    lines = []
    lines.append("# 自动生成：运行 notebook 的 R 代码并保存图片")
    lines.append("dir.create(%s, showWarnings = FALSE, recursive = TRUE)" % r_string(out_dir_abs))
    lines.append("")
    cur_w, cur_h = DEFAULT_W, DEFAULT_H
    for idx, src in enumerate(cells, 1):
        # 解析该单元格内最后一次设置的绘图尺寸（缺省继承上一个单元格）
        wm = re.findall(r"repr\.plot\.width\s*=\s*([0-9.]+)", src)
        hm = re.findall(r"repr\.plot\.height\s*=\s*([0-9.]+)", src)
        if wm:
            cur_w = float(wm[-1])
        if hm:
            cur_h = float(hm[-1])
        w, h = cur_w, cur_h
        # 图片文件名：{nb_name}_c{02d}_{%03d}.png
        png_pattern = os.path.join(out_dir_abs, f"{nb_name}_c{idx:02d}_%03d.png")
        lines.append("# ---- cell %d (%.1f x %.1f in) ----" % (idx, w, h))
        lines.append(
            'png(%s, width = %.1f, height = %.1f, units = "in", res = %d)'
            % (r_string(png_pattern), w, h, RES)
        )
        lines.append("tryCatch({")
        for ln in src.splitlines():
            lines.append("  " + ln)
        lines.append("}, error = function(e) {")
        lines.append(
            '  cat("__CELL_ERROR__ %d:", conditionMessage(e), "\\n", file = stderr())' % idx
        )
        lines.append("})")
        # 关闭本单元格打开的所有图形设备，避免设备泄漏/跨单元格污染
        lines.append("while (dev.cur() > 1) dev.off()")
        lines.append("")
    return "\n".join(lines)


def run_notebook(nb_path: Path, global_out_dir: str | None):
    """
    运行单个 notebook，返回 (状态, 信息)。
    global_out_dir: None=输出到nb所在文件夹；否则全部输出到此统一目录
    """
    nb_dir = os.path.dirname(os.path.abspath(nb_path))
    nb_name = os.path.splitext(os.path.basename(nb_path))[0]
    if global_out_dir is None:
        out_dir_abs = nb_dir
    else:
        out_dir_abs = os.path.abspath(global_out_dir)

    cells = extract_r_cells(nb_path)
    if not cells:
        return "skip", "无代码单元格"

    r_code = build_r_script(out_dir_abs, nb_name, cells)
    # 写临时 R 脚本（UTF‑8 无 BOM，配合清理后的 locale 让中文正确解析）
    fd, tmp_path = tempfile.mkstemp(suffix=".R", prefix="nb_figs_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(r_code)
        proc = subprocess.run(
            [RSCRIPT, tmp_path],
            cwd=nb_dir,
            env=clean_env(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    pattern = os.path.join(out_dir_abs, f"{nb_name}_c*.png")
    n_figs = len(glob.glob(pattern))
    err_cells = re.findall(r"__CELL_ERROR__ (\d+):", proc.stderr)
    if err_cells:
        detail = "cell %s 报错" % ",".join(err_cells)
        first = proc.stderr.strip().splitlines()
        if first:
            detail += "；首个错误：" + first[0][:200]
        return "error", detail
    if n_figs == 0:
        return "warn", "未生成图片（可能有绘图但被吞，或代码无绘图）"
    return "ok", "生成 %d 张图片" % n_figs


def select_ipynb_files():
    """弹出tk多选对话框，选择ipynb文件"""
    root = tkinter.Tk()
    root.withdraw()  # 隐藏主窗口
    root.attributes("-topmost", True)
    file_paths = filedialog.askopenfilenames(
        title="选择一个或多个 .ipynb 文件",
        filetypes=[("Jupyter Notebook", "*.ipynb"), ("所有文件", "*.*")]
    )
    root.destroy()
    return list(file_paths)


def main(argv=None):
    parser = argparse.ArgumentParser(description="弹窗选择ipynb，批量运行R单元格导出PNG")
    parser.add_argument("--out", default=None, help="可选：统一输出PNG到该目录；默认PNG与ipynb同目录")
    args = parser.parse_args(argv)

    if not os.path.isfile(RSCRIPT):
        print("未找到 Rscript，请安装 R 或修改脚本中的 RSCRIPT 路径。")
        return 1

    targets = select_ipynb_files()
    if not targets:
        print("未选择任何文件，退出。")
        return 0

    print("Rscript: %s" % RSCRIPT)
    print("待处理 %d 个 notebook：\n" % len(targets))
    for t in targets:
        print("  - %s" % t)
    print()

    stats = {"ok": 0, "skip": 0, "warn": 0, "error": 0}
    for i, nb_path in enumerate(targets, 1):
        name = os.path.basename(nb_path)
        status, info = run_notebook(Path(nb_path), args.out)
        stats[status] = stats.get(status, 0) + 1
        tag = {"ok": "OK ", "skip": "跳过", "warn": "警告", "error": "失败"}[status]
        print("[%2d/%d] %-6s %-28s %s" % (i, len(targets), tag, name, info))

    print()
    print("汇总：成功 %d，警告 %d，失败 %d，跳过 %d" % (
        stats["ok"], stats["warn"], stats["error"], stats["skip"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
