# DACE

<div align="center">

<a href="https://github.com/wenje-ma/DACE">
  <img src="https://img.shields.io/badge/DACE-006E4C?style=for-the-badge&logo=bookstack&logoColor=white" alt="DACE"/>
  <img src="https://img.shields.io/badge/%E7%8A%B6%E6%80%81-%E6%A0%B8%E5%BF%83%E7%B2%BE%E8%AF%BB-00A878?style=for-the-badge&logo=verified&logoColor=white" alt="核心精读"/>
</a>

**The Design and Analysis of Computer Experiments** · T. J. Santner / B. J. Williams / W. I. Notz · Springer · 第2版 · 2026-09 开启

</div>

《The Design and Analysis of Computer Experiments》（第2版，Springer Series in Statistics, 2018）是计算机实验设计与分析的经典教材。本仓库**只读毕设必需的 GP 与 BO 理论核心**：GP 模型定义、后验推导、EI 与约束优化。其余章节不读。

## 📖 精读范围（必须）

| 小节 | 原书页码 | 内容 | 对毕设的作用 |
|---|---|---|---|
| **2.2.1** GP 定义 | p30–34 | 高斯过程定义、均值/协方差函数 | 代理模型起点 |
| **2.2.2** 相关函数 | p34–41 | 高斯/指数/幂指数/Matern 相关函数族 | 核的选择与参数 |
| **3.2** BLUP & MSPE | p68–76 | 条件后验均值/方差推导 | 手推后验的核心 |
| **3.3** EBLUP | p76–84 | ML/REML 超参数估计 | 实际建模必需 |
| **4.2** 共轭贝叶斯后验推断 | p117–128 | 后验分布的完整贝叶斯推断 | BO 的后验引擎（补 ED4DSE 分层贝叶斯推导） |
| **6.3.4** Expected Improvement | p216–225 | EI/EGO 定义与算法 | BO 核心 |
| **6.3.5** Constrained Global Optimization | p225–229 | 多输出约束优化 | 毕设主题（约束） |
| **6.4.2** Contour Estimation | p237–238 | 水平集/轮廓估计 | 主动学可行边界 |
| **8.2** KOH Model | p301–307 | Kennedy & O'Hagan 校准模型 | 多保真（Co-Kriging 源头） |

### ❌ 不读

2.3 非平稳、2.4 混合输入、2.5 多元输出、3.4/3.5、4.3、第5章、6.2/6.3.6/6.4 其余、第7章、8.3/8.4、附录 D/E（附录 B/C 作推导工具随用随查）

## 🗂 仓库结构

| 目录 | 内容 |
|---|---|
| `markdown/` | 原书 PDF 与转换文本、逐节笔记（Ch02-xx.md）、`figures/` 配图 |
| `代码/` | 逐节 R 复现（Ch02.ipynb 等）与数据（`data/`，RData） |
| `*.py` | 学习流水线脚本（PDF→txt、ipynb→md、md 合并/转 tex、图导出） |

## 🚀 进度

- [x] 2.1 介绍 + 例2.1（`markdown/Ch02-01.md`，图2.1 R 复现）
- [x] 2.2.1 GP 定义（`markdown/Ch02-02-01.md`）
- [x] 2.2.2 相关函数（`markdown/Ch02-02-02.md`，图2.2–2.8 R 复现）
- [x] 2.2.3 光滑性（`markdown/Ch02-02-03.md`，图2.9–2.10 R 复现）
- [x] 2.3.1–2.3.2、2.4（已读，超出必读范围，笔记在 `Ch02-03-xx.md`/`Ch02-04.md`）
- [ ] 3.2 BLUP/MSPE 推导 → 3.3 EBLUP → 4.2 共轭后验 → 6.3.4 EI → 6.3.5 约束优化 → 6.4.2 轮廓估计 → 8.2 KOH

## 🔗 关联

- [ED4DSE](https://github.com/wenje-ma/ED4DSE)：已完成的全书学习（GP 概览与试验设计全谱系），本仓库的理论上游
- 毕设方向2：约束昂贵黑箱 BO（见 graduation/思路历程）
