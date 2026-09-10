#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import tkinter as tk
from tkinter import filedialog
from pathlib import Path


LATEX_HEADER = r"""\documentclass{ctexart}
\usepackage[margin=2.5cm]{geometry}
\usepackage{graphicx,float}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{mathrsfs}
\DeclareMathOperator*{\argmin}{arg\,min}
\DeclareMathOperator*{\argmax}{arg\,max}
\usepackage{tcolorbox}
\tcbuselibrary{skins}
\newtcolorbox{mdquote}{blanker,left=2.5em,right=2.5em,top=0.5em,bottom=0.5em,borderline west={3pt}{0pt}{gray!50}}
\usepackage{anyfontsize}

\begin{document}

"""

LATEX_FOOTER = r"""

\end{document}"""


def is_table_separator(line: str) -> bool:
    stripped = line.strip()
    if not stripped.startswith('|') or not stripped.endswith('|'):
        return False
    inner = stripped[1:-1]
    cells = [cell.strip() for cell in inner.split('|')]
    if not cells:
        return False
    for cell in cells:
        content = cell.strip(':').strip()
        if not content:
            return False
        if not re.match(r'^[\s\-]+$', content):
            return False
        if '-' not in content:
            return False
    return True


def protect_math_bars(text: str) -> str:
    """保护公式内的 |，避免被误当表格分隔符"""
    def protect(match):
        content = match.group(0)
        return content.replace('|', '∎PLACEHOLDER∎')
    
    # 保护行内公式 $...$
    text = re.sub(r'\$[^\$]+\$', protect, text)
    # 保护块级公式 $$...$$
    text = re.sub(r'\$\$[^\$]+\$\$', protect, text)
    return text


def restore_math_bars(text: str) -> str:
    """恢复公式内的 |"""
    return text.replace('∎PLACEHOLDER∎', '|')


def process_math_in_quote(text: str) -> str:
    def replace_math(match):
        content = match.group(1).strip()
        env_match = re.match(r'^\\begin\{([a-zA-Z]+[*]?)\}', content)
        if env_match:
            env_name = env_match.group(1)
            if env_name == 'aligned':
                return f'\\begin{{equation*}}\n{content}\n\\end{{equation*}}'
            elif env_name in ['align', 'align*']:
                return content
            else:
                return f'\\begin{{equation*}}\n{content}\n\\end{{equation*}}'
        else:
            return f'\\begin{{equation*}}\n{content}\n\\end{{equation*}}'
    return re.sub(r'\$\$\s*(.*?)\s*\$\$', replace_math, text, flags=re.DOTALL)


def convert_md_to_tex(md_content):
    lines = md_content.split('\n')
    tex_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        title_match = re.match(r'^### (.+)$', line)
        if title_match:
            tex_lines.append(f'\\subsubsection*{{{title_match.group(1).strip()}}}')
            i += 1
            continue

        title_match = re.match(r'^## (.+)$', line)
        if title_match:
            tex_lines.append(f'\\subsection*{{{title_match.group(1).strip()}}}')
            i += 1
            continue

        title_match = re.match(r'^# (.+)$', line)
        if title_match:
            tex_lines.append(f'\\section*{{{title_match.group(1).strip()}}}')
            i += 1
            continue

        img_match = re.match(r'^!\[.*?\]\((.+?)\)(?:\{width=(.+?)\})?$', line)
        if img_match:
            path = img_match.group(1)
            width = img_match.group(2)
            tex_lines.append('\\begin{figure}[H]')
            if width:
                width_clean = width.strip()
                if width_clean.endswith('%'):
                    try:
                        num = float(width_clean[:-1]) / 100
                        tex_lines.append(f'\\includegraphics[width={num}\\textwidth]{{{path}}}')
                    except ValueError:
                        tex_lines.append(f'\\includegraphics[width={width}]{{{path}}}')
                elif width_clean.startswith('.') or width_clean.replace('.', '').isdigit():
                    try:
                        num = float(width_clean)
                        tex_lines.append(f'\\includegraphics[width={num}\\textwidth]{{{path}}}')
                    except ValueError:
                        tex_lines.append(f'\\includegraphics[width={width}]{{{path}}}')
                else:
                    tex_lines.append(f'\\includegraphics[width={width}]{{{path}}}')
            else:
                tex_lines.append(f'\\includegraphics{{{path}}}')
            tex_lines.append('\\end{figure}')
            i += 1
            continue

        if line.startswith('> '):
            tex_lines.append('\\begin{mdquote}')
            content = line[2:]
            content = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', content)
            content = process_math_in_quote(content)
            tex_lines.append(content)
            i += 1
            while i < len(lines) and lines[i].startswith('> '):
                content = lines[i][2:]
                content = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', content)
                content = process_math_in_quote(content)
                tex_lines.append(content)
                i += 1
            tex_lines.append('\\end{mdquote}')
            continue

        if '|' in line and line.strip().startswith('|') and not is_table_separator(line):
            # 保护公式内的 |
            protected_line = protect_math_bars(line)
            
            table_rows = []
            header_cells = [cell.strip() for cell in protected_line.split('|')[1:-1]]
            header_cells = [restore_math_bars(cell) for cell in header_cells]
            table_rows.append(header_cells)
            num_cols = len(header_cells)
            i += 1

            aligns = ['c'] * num_cols
            if i < len(lines) and is_table_separator(lines[i]):
                sep_cells = [cell.strip() for cell in lines[i].split('|')[1:-1]]
                for idx, cell in enumerate(sep_cells):
                    if idx >= num_cols:
                        break
                    if cell.startswith(':') and cell.endswith(':'):
                        aligns[idx] = 'c'
                    elif cell.startswith(':'):
                        aligns[idx] = 'l'
                    elif cell.endswith(':'):
                        aligns[idx] = 'r'
                    else:
                        aligns[idx] = 'c'
                i += 1

            while i < len(lines) and '|' in lines[i] and lines[i].strip().startswith('|'):
                if is_table_separator(lines[i]):
                    i += 1
                    continue
                protected_data_line = protect_math_bars(lines[i])
                cells = [cell.strip() for cell in protected_data_line.split('|')[1:-1]]
                cells = [restore_math_bars(cell) for cell in cells]
                if cells:
                    table_rows.append(cells)
                i += 1

            if table_rows:
                num_cols = len(table_rows[0])
                align_str = '|'.join(aligns[:num_cols])

                tex_lines.append('\\begin{table}[H]')
                tex_lines.append(f'\\begin{{tabular}}{{{align_str}}}')
                tex_lines.append('\\hline')

                header_cells_fixed = []
                for cell in table_rows[0]:
                    if re.match(r'^x_\d+$', cell):
                        header_cells_fixed.append(f'${cell}$')
                    else:
                        header_cells_fixed.append(cell)
                tex_lines.append(' & '.join(header_cells_fixed) + ' \\\\')
                tex_lines.append('\\hline')

                for row in table_rows[1:]:
                    tex_lines.append(' & '.join(row) + ' \\\\')

                tex_lines.append('\\hline')
                tex_lines.append('\\end{tabular}')
                tex_lines.append('\\end{table}')
            continue

        stripped = line.strip()
        if stripped.startswith('$$') and stripped.endswith('$$') and len(stripped) > 4:
            content = stripped[2:-2].strip()
            env_match = re.match(r'^\\begin\{([a-zA-Z]+[*]?)\}', content)
            if env_match:
                env_name = env_match.group(1)
                if env_name == 'aligned':
                    tex_lines.append('\\begin{equation*}')
                    tex_lines.append(content)
                    tex_lines.append('\\end{equation*}')
                elif env_name in ['align', 'align*']:
                    tex_lines.append(content)
                else:
                    tex_lines.append('\\begin{equation*}')
                    tex_lines.append(content)
                    tex_lines.append('\\end{equation*}')
            else:
                tex_lines.append('\\begin{equation*}')
                tex_lines.append(content)
                tex_lines.append('\\end{equation*}')
            i += 1
            continue

        if line.strip() == '$$':
            i += 1
            formula_lines = []
            while i < len(lines) and lines[i].strip() != '$$':
                formula_lines.append(lines[i])
                i += 1
            i += 1
            formula_content = '\n'.join(formula_lines).strip()
            env_match = re.search(r'^\\begin\{([a-zA-Z]+[*]?)\}', formula_content)
            if env_match:
                env_name = env_match.group(1)
                if env_name == 'aligned':
                    tex_lines.append('\\begin{equation*}')
                    tex_lines.append(formula_content)
                    tex_lines.append('\\end{equation*}')
                elif env_name in ['align', 'align*']:
                    tex_lines.append(formula_content)
                else:
                    tex_lines.append('\\begin{equation*}')
                    tex_lines.append(formula_content)
                    tex_lines.append('\\end{equation*}')
            else:
                tex_lines.append('\\begin{equation*}')
                tex_lines.append(formula_content)
                tex_lines.append('\\end{equation*}')
            continue

        line = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', line)
        tex_lines.append(line)
        i += 1

    return '\n'.join(tex_lines)


def md_to_tex(md_path: str, tex_path: str | None = None):
    md_file = Path(md_path)
    if not md_file.exists():
        raise FileNotFoundError(f"找不到文件: {md_file}")

    if tex_path is None:
        tex_file = md_file.with_suffix(".tex")
    else:
        tex_file = Path(tex_path)

    md_content = md_file.read_text(encoding="utf-8")
    body_content = convert_md_to_tex(md_content)
    tex_content = LATEX_HEADER + body_content + LATEX_FOOTER

    tex_file.write_text(tex_content, encoding="utf-8")
    print(f"✅ 已生成: {tex_file}")
    return str(tex_file)


def select_and_convert_mds():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    selected_files = filedialog.askopenfilenames(
        title='请选择要转换的 Markdown 文件',
        filetypes=[('Markdown 文件', '*.md'), ('所有文件', '*.*')]
    )

    if not selected_files:
        print('未选择任何文件，退出。')
        return []

    converted = []
    failed = []
    for md_path in selected_files:
        try:
            output = md_to_tex(md_path)
            converted.append(output)
        except Exception as e:
            print(f"❌ 转换失败: {md_path}，错误: {e}")
            failed.append((md_path, str(e)))

    print(f'\n转换完成，成功 {len(converted)} 个，失败 {len(failed)} 个。')
    return converted


if __name__ == "__main__":
    select_and_convert_mds()