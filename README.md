# DACE

<div align="center">

<a href="https://github.com/wenje-ma/DACE">
  <img src="https://img.shields.io/badge/DACE-006E4C?style=for-the-badge&logo=bookstack&logoColor=white" alt="DACE"/>
  <img src="https://img.shields.io/badge/%E7%8A%B6%E6%80%81-%E7%B2%BE%E8%AF%BB%E4%B8%AD-00A878?style=for-the-badge&logo=verified&logoColor=white" alt="精读中"/>
</a>

**The Design and Analysis of Computer Experiments** · T. J. Santner / B. J. Williams / W. I. Notz · Springer · 第2版 · 2026-09 开启

</div>

《The Design and Analysis of Computer Experiments》（第2版，Springer Series in Statistics, 2018）是计算机实验设计与分析的经典教材。本仓库**不是全书精读，而是定向精读**：只读与毕设方向2（约束昂贵黑箱贝叶斯优化 + 主动学可行边界 + 多保真）直接相关的章节，把 GP 补到"能推后验、能推采集函数"。

## 📖 精读范围

| 章节 | 内容 | 状态 |
|---|---|---|
| 第2章 Stochastic Process Models for Simulator Output | 高斯过程模型与相关函数（GP 建模基础） | 🔄 2.1 + 例2.1、2.2.1 已完成；2.2.2 起待读 |
| 第3章 Empirical Best Linear Unbiased Prediction | EBLUP 预测推导（条件后验均值/方差，采集函数推导的必要技能） | ⏳ 未开始 |
| 第6章 §6.3.4 Expected Improvement | EI 采集函数（贝叶斯优化核心） | ⏳ 未开始 |

## 🗂 仓库结构

| 目录 | 内容 |
|---|---|
| `markdown/` | 原书 PDF 与转换文本、逐节笔记（Ch02-xx.md）、`figures/` 配图 |
| `代码/` | 逐节 R 复现（Ch02.ipynb 等）与数据（`data/`，RData） |
| `*.py` | 学习流水线脚本（PDF→txt、ipynb→md、md 合并/转 tex、图导出） |

## 🚀 进度

- [x] 第2章 2.1 介绍 + 例2.1（笔记 `markdown/Ch02-01.md`，图2.1 R 复现 `代码/Ch02.ipynb`，4×4 英寸约定）
- [x] 第2章 2.2.1 介绍（`markdown/Ch02-02-01.md`，待提交）
- [ ] 第2章 2.2.2 相关函数 → 2.2.3 指定 GP → 第3章 EBLUP → 第6章 §6.3.4 EI

## 🔗 关联

- [ED4DSE](https://github.com/wenje-ma/ED4DSE)：已完成的全书学习（GP 概览与试验设计全谱系），本仓库的理论上游
- 毕设方向2：约束昂贵黑箱 BO（见 Graduation-Project/思路历程）
