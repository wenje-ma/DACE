# DACE 精读笔记（按 README 范围）

> 教材：《The Design and Analysis of Computer Experiments》，T. J. Santner / B. J. Williams / W. I. Notz，Springer，第 2 版
> 范围：严格按仓库 README「精读范围」整理的 9 个小节（2.2.1 / 2.2.2 / 3.2 / 3.3 / 4.2 / 6.3.4 / 6.3.5 / 6.4.2 / 8.2）。**习题全部忽略**。
> 定位：读本笔记等价于通读上述原文；公式、定义、性质、推导要点均已覆盖。
> 说明：本文用 $LaTeX$ 记数学公式；$\cdot^\top$ 表示转置；`tr` 下标=训练（training），`te`=测试（test）。

---

# 全书主线（先建立全局框架）

**计算机试验（computer experiment）与物理试验的本质区别：**
- 物理试验：观测带随机测量误差，重复试验可估计误差方差。
- 计算机试验（仿真器输出）：**确定性**。同一输入重复运行得到完全相同输出，没有测量噪声。

**因此建模目标不是"拟合带噪数据"，而是对确定性黑箱函数 $y(\boldsymbol{x})$ 构造插值元模型（surrogate / emulator），并量化预测不确定性。**

**核心模型（贯穿全书的回归 + 平稳高斯过程）：**
$$
Y(\boldsymbol{x}) = \sum_{j=1}^{p} f_j(\boldsymbol{x})\beta_j + Z(\boldsymbol{x}) = \boldsymbol{f}^\top(\boldsymbol{x})\boldsymbol{\beta} + Z(\boldsymbol{x}) \tag{2.2.3}
$$
- $\boldsymbol{f}^\top(\boldsymbol{x})\boldsymbol{\beta}$：均值项（回归趋势），刻画长期趋势；
- $Z(\boldsymbol{x})$：**零均值平稳高斯过程**，刻画对长期趋势的局部偏离（空间相关性）；
- 决定模型的是均值函数 $\mu(\cdot)$ 和协方差函数 $C(\cdot,\cdot)$。

**两条技术主线：**
1. **设计（Design）**：如何选输入点集 $\mathcal{X}=\{\boldsymbol{x}_1,\dots,\boldsymbol{x}_n\}$（第 5、6 章，本精读范围主要涉及 6.3.4/6.3.5/6.4.2 的序贯选点）。
2. **分析（Analysis）**：基于少量已跑仿真样本构造元模型并预测（第 2、3、4 章）。

**本笔记对应毕设作用**：GP 定义与相关函数是代理模型起点（2.2）；BLUP/MSPE 是手推后验核心（3.2）；EBLUP 的 ML/REML 是实际建模必需（3.3）；共轭贝叶斯后验是 BO 的后验引擎（4.2）；EI/EGO 是 BO 核心（6.3.4）；约束优化是毕设主题（6.3.5）；轮廓估计用于主动学可行边界（6.4.2）；KOH 是多保真/校准源头（8.2）。

---

# 2.2.1 GP 定义（p30–34）

## 为什么用高斯过程
- 计算试验文献中，最流行的函数模型是**高斯过程（Gaussian process, GP）**，亦称高斯随机函数模型；其解析可处理性使后验、预测都能闭式推导。
- GP 定义（Definition）：设 $\mathcal{X}$ 是 $\mathbb{R}^d$ 中具有正 $d$ 维体积的固定子集。$Y(\boldsymbol{x}),\ \boldsymbol{x}\in\mathcal{X}$ 是 GP，当且仅当对任意 $L\ge1$ 及任意 $\boldsymbol{x}_1,\dots,\boldsymbol{x}_L\in\mathcal{X}$，向量 $(Y(\boldsymbol{x}_1),\dots,Y(\boldsymbol{x}_L))$ 服从**多元正态分布**。
- 任何 GP 完全由其**均值函数** $\mu(\boldsymbol{x})\equiv E[Y(\boldsymbol{x})]$ 和**协方差函数**
$$
C(\boldsymbol{x}_1,\boldsymbol{x}_2)\equiv\mathrm{Cov}[Y(\boldsymbol{x}_1),Y(\boldsymbol{x}_2)] \tag{2.2.1}
$$
决定。

## 两个关键技术前提
1. **样本路径性质**：GP 由有限维分布定义，而连续性/可微性是"样本路径性质"（把 $y(\boldsymbol{x})=Y(\boldsymbol{x},\omega)$ 视为固定 $\omega$ 下 $\boldsymbol{x}$ 的函数）。Doob 引入**可分性（separability）**保证样本路径性质由有限维分布决定。本书默认所选用 GP 均可分。
2. **平稳性与遍历性**：训练数据 $y(\boldsymbol{x}_1),\dots,y(\boldsymbol{x}_n)$ 来自单个 $\omega$（单条函数曲线），而非多个随机变量的重复抽样。要从单个 $\omega$ 做有效的频率学派推断，需要**遍历性（ergodicity）**。**强平稳** GP 在温和条件下是遍历的，故全书限定讨论（强）平稳 GP。

## 平稳性定义
（强）平稳（Definition）：对任意 $\boldsymbol{h}\in\mathbb{R}^d$、任意 $L\ge1$、任意 $\boldsymbol{x}_1,\dots,\boldsymbol{x}_L\in\mathcal{X}$（且 $\boldsymbol{x}_1+\boldsymbol{h},\dots,\boldsymbol{x}_L+\boldsymbol{h}\in\mathcal{X}$），$(Y(\boldsymbol{x}_1),\dots,Y(\boldsymbol{x}_L))$ 与 $(Y(\boldsymbol{x}_1+\boldsymbol{h}),\dots,Y(\boldsymbol{x}_L+\boldsymbol{h}))$ 同分布。

对 GP 而言平稳等价于：对任意 $L\ge1$ 和 $\boldsymbol{x}_1,\dots,\boldsymbol{x}_L$，上述两组向量**均值向量相同且协方差矩阵相同**。推论：
- 对所有 $\boldsymbol{x}$，边际分布相同 ⇒ **均值、方差都是常数**；
- 协方差只依赖差值：$\mathrm{Cov}[Y(\boldsymbol{x}_1),Y(\boldsymbol{x}_2)]=C(\boldsymbol{x}_1-\boldsymbol{x}_2)$（(2.2.2)，此处 $C(\cdot)$ 即过程协方差函数）；
- $\mathrm{Var}[Y(\boldsymbol{x})]=C(0)$；相关系数
$$
\mathrm{Cor}[Y(\boldsymbol{x}_1),Y(\boldsymbol{x}_2)]=\frac{C(\boldsymbol{x}_1-\boldsymbol{x}_2)}{C(0)}.
$$
- 直观：任何"方向相同、间距相同"的两点对具有相同协方差。

## 平稳性条件与可加模型
- 平稳 GP $Y(\boldsymbol{x})$（协方差 $C(\boldsymbol{h})$）在 $C(\boldsymbol{h})\to0\ (\boldsymbol{h}\to\infty)$ 下是遍历的（下文所有相关函数均满足）。
- **各向同性（isotropic）**：协方差仅依赖欧氏距离 $\|\boldsymbol{x}_1-\boldsymbol{x}_2\|_2$。因仿真输入通常量纲不同，各向同性模型在仿真输出建模中少用。
- **二阶平稳**：只做均值、方差、协方差（(2.2.2)）假设，不做联合分布假设（非参数、仅矩假设）。

## 核心模型：回归 + 平稳 GP（非平稳化技巧）
为在保留平稳理论简便的同时增强建模能力，最简单的办法是让均值随 $\boldsymbol{x}$ 呈回归形式，残差仍为平稳 GP（即 (2.2.3)）：
$$
Y(\boldsymbol{x})=\boldsymbol{f}^\top(\boldsymbol{x})\boldsymbol{\beta}+Z(\boldsymbol{x}),\quad Z(\boldsymbol{x})\sim \text{零均值平稳GP}.
$$
直观：$\boldsymbol{f}^\top(\boldsymbol{x})\boldsymbol{\beta}$ 描述长期趋势，$Z(\boldsymbol{x})$ 建模局部偏离。该模型整体是非平稳的，但借平稳残差保留可解析性。（更一般的非平稳模型见 2.3，不在精读范围。）

---

# 2.2.2 相关函数（p34–41）

本节聚焦平稳零均值 $Z(\cdot)$，它完全由协方差函数 $C(\cdot)$ 决定。实践中更常分别指定**过程方差**与**过程相关函数**。

## 基本量
- 过程方差 $\sigma_Z^2\equiv C(0)$；过程相关函数 $R(\boldsymbol{h})=C(\boldsymbol{h})/\sigma_Z^2$（假设非退化 $\sigma_Z^2>0$）。
- 也可用**过程精度** $\lambda_Z=1/\sigma_Z^2$ 参数化。

## 有效相关函数必须满足的性质
设 $C(0)>0$：
1. $R(0)=1$（由定义）；
2. **对称性**：$C(\boldsymbol{h})=C(-\boldsymbol{h})$，$R(\boldsymbol{h})=R(-\boldsymbol{h})$ (2.2.4)（因 $\mathrm{Cov}[Y(x+h),Y(x)]=\mathrm{Cov}[Y(x),Y(x+h)]$）；
3. **正半定**：对任意 $L\ge1$、任意实数 $w_1,\dots,w_L$、任意 $\boldsymbol{x}_1,\dots,\boldsymbol{x}_L$，
$$
\sum_{i=1}^{L}\sum_{j=1}^{L} w_i w_j R(\boldsymbol{x}_i-\boldsymbol{x}_j)\ge 0. \tag{2.2.5}
$$
（左边是 $\sum_i w_i Y(\boldsymbol{x}_i)$ 的缩放方差。）若对非全零 $(w_1,\dots,w_L)$ 严格大于 0，则 $R$ 正定。

## 构造方法：Bochner 公式
仅满足上述性质仍无法系统构造相关函数。**Bochner (1955) 定理**：若 $f(\boldsymbol{w})$ 是 $\mathbb{R}^d$ 上的对称密度（$f(\boldsymbol{w})=f(-\boldsymbol{w})$），则
$$
R(\boldsymbol{h})=\int_{\mathbb{R}^d}\cos(\boldsymbol{h}^\top\boldsymbol{w})\,f(\boldsymbol{w})\,d\boldsymbol{w} \tag{2.2.6}
$$
是有效相关函数；$f(\boldsymbol{w})$ 称为 $R(\boldsymbol{h})$ 的**谱密度**。可验证满足 $R(0)=1$、对称性、正半定（正半定用 $\cos(a-b)=\cos a\cos b+\sin a\sin b$ 化平方和证明）。

**相关函数的运算规则：**
- 两个有效协方差函数之和、积仍是有效协方差函数（分别对应两个独立过程之和、两个独立零均值 GP 之积）。
- 两个有效相关函数之**积**是有效相关函数，但**和不是**（$R_1(0)+R_2(0)=2\ne1$）；相关函数的**凸组合**是有效相关函数。
- 由一维相关函数乘积构成的相关函数称为**可分离（separable）相关函数**（勿与 2.2.1 的过程可分性混淆）。

## 常用相关函数族（重点：按需选核）

### 例 2.3 高斯相关函数（Gaussian）
取谱密度为 $N(0,2\xi)$，得一维：
$$
R(h|\xi)=\exp\{-\xi h^2\},\ h\in\mathbb{R},\ \xi>0. \tag{2.2.7}
$$
$d$ 维可分离高斯族：
$$
R(\boldsymbol{h}|\boldsymbol{\xi})=\exp\left\{-\sum_{j=1}^{d}\xi_j h_j^2\right\},\ \boldsymbol{h}\in\mathbb{R}^d. \tag{2.2.8}
$$
**可分离高斯相关是计算机试验文献中最流行的相关模型。**

**等价的 4 种参数化**（文献常用，见 (2.2.9)）：
$$
\exp\left\{-\left(\frac{h}{\theta}\right)^2\right\}
=\rho^{h^2}
=\rho_\star^{C h^2}
=\exp\{-10^\tau h^2\}
$$
参数含义：$\theta$ 为尺度参数；$\rho$ 是 $|h|=1$ 时的相关；$\rho_\star$ 是 $|h|=1/\sqrt{C}$ 时的相关（常取 $C=4$）；$\tau\in(-\infty,\infty)$。选不同参数化是为了解释方便、贝叶斯先验设定、以及似然优化的数值性质。

### 例 2.4 幂指数相关族（Power Exponential）★
$$
R(h|\xi)=\exp\{-\xi|h|^p\},\ \xi>0,\ 0<p\le2. \tag{2.2.10}
$$
- $p=2$：高斯（见上）；
- $p=1$：指数相关，对应 **Ornstein–Uhlenbeck 过程**。
- **光滑性结论**：$0<p\le2$ 的所有幂指数相关都在原点连续，**只有高斯相关（$p=2$）在原点可导，且无穷次可导**。$p<2$ 时样本路径不可导。
- $d$ 维可分离版本：
$$
R(\boldsymbol{h}|\boldsymbol{\xi})=\exp\left\{-\sum_{j=1}^{d}\xi_j |h_j|^{p_j}\right\},\ \boldsymbol{h}\in\mathbb{R}^d. \tag{2.2.11}
$$

### 例 2.5 Matern 相关族
由 Bochner 公式取谱密度为 $t$ 分布（参数 $\nu>0,\psi>0$）得到双参数相关：
$$
R(h|(\nu,\psi))=\frac{1}{\Gamma(\nu)2^{\nu-1}}\left(\frac{2\sqrt{\nu}|h|}{\psi}\right)^\nu K_\nu\!\left(\frac{2\sqrt{\nu}|h|}{\psi}\right),
$$
$K_\nu$ 为 $\nu$ 阶修正 Bessel 函数，$\psi$ 为尺度参数，$\nu$ 控制光滑性。
- $\nu=1/2$ 时退化为 $e^{-\sqrt{2}|h|/\psi}$（幂指数 $p=1$）；
- $\nu\to\infty$ 时趋于 $e^{-(h/\psi)^2}$（高斯）。
- $d$ 维由一维 Matern 乘积构成，可带各维独立尺度 $\psi_i$ 与共同光滑参数 $\nu$。

### 例 2.6 三次（Cubic）相关族
$$
R(h|\psi)=\begin{cases}
1-6\left(\frac{h}{\psi}\right)^2+6\left(\frac{|h|}{\psi}\right)^3, & |h|\le\psi/2\\
2\left(1-\frac{|h|}{\psi}\right)^3, & \psi/2<|h|\le\psi\\
0, & |h|>\psi
\end{cases}\quad(\psi>0). \tag{2.2.12}
$$
- 分段三次多项式，处处有连续导数；**紧支撑**（$|x_1-x_2|>\psi$ 时 $R=0$），相关矩阵可有大量零元，便于稀疏矩阵求逆。
- 用 (2.2.12) 作 BLUP 会导致**三次样条插值预测器**。
- $d$ 维可分离版本 (2.2.13) 允许各维独立的相关截断距离 $\psi_j$。

### 例 2.7 Bohman 相关族
另一紧支撑相关函数：
$$
R(h|\psi)=\begin{cases}
\left(1-\frac{|h|}{\psi}\right)\cos\left(\frac{\pi|h|}{\psi}\right)+\frac{1}{\pi}\sin\left(\frac{\pi|h|}{\psi}\right), & |h|<\psi\\
0, & |h|\ge\psi
\end{cases}\quad(\psi>0). \tag{2.2.14}
$$

> **选核要点（对应 README "核的选择与参数"）**：高斯→最平滑、工程最常用；幂指数→通过 $p$ 控制光滑度；Matern→$\nu$ 独立控制光滑度（环境/空间统计常用）；三次/Bohman→紧支撑、稀疏计算。DACE 工具箱默认用幂指数族、固定 $p=2$，仅估计 $\boldsymbol{\theta}$。

---

# 3.2 BLUP 与最小 MSPE 预测（p68–76）

## 3.2.1 最佳线性无偏预测（BLUP）——通用框架
考虑预测随机变量 $Y_0$，训练数据 $Y_{tr}=(Y_1,\dots,Y_n)^\top$。预测器记 $\hat{Y}_0=\hat{Y}_0(Y_{tr})$。

**线性无偏预测器（LUP）**：形如 $\hat{Y}_0=a_0+\boldsymbol{a}^\top Y_{tr}$，且对给定分布族 $\mathcal{F}$ 中所有分布满足
$$
E[\hat{Y}_0]=E[Y_0],\quad \forall F\in\mathcal{F}. \tag{3.2.1}
$$
**均方预测误差（MSPE）**：
$$
\mathrm{MSPE}(\hat{Y}_0,F)\equiv E\left[(\hat{Y}_0-Y_0)^2\right]. \tag{3.2.2}
$$
**定义**：若 LUP $\hat{Y}_0$ 对 $\mathcal{F}$ 中所有 $F$ 的 MSPE 都不大于任何其他 LUP $Y_0^\star$，则称其为关于 $\mathcal{F}$ 的**最佳 LUP（BLUP）**。

### 例 3.1 位置参数模型
模型 $Y_i=\beta_0+\epsilon_i$（$i=0,\dots,n$），$\epsilon_i$ 零均值不相关、方差 $\sigma_\epsilon^2$。无偏性要求 $a_0+\beta_0\sum_i a_i=\beta_0$。MSPE $=\sigma_\epsilon^2(1+\sum_i a_i^2)\ge\sigma_\epsilon^2$，等式当且仅当 $a_0=\beta_0,\ a_1=\cdots=a_n=0$。故**唯一 BLUP 是 $\hat{Y}_0=\beta_0$**——BLUP 高度依赖 $\mathcal{F}$（本例随 $\beta_0$ 变）。

## 计算机试验场景的 BLUP（已知相关函数）
考虑模型 (3.1.1)，且**相关函数 $R(\cdot)$ 已知**。预测 $y(\boldsymbol{x}_{te})$。记 $\hat{y}(\boldsymbol{x}_{te})\equiv\hat{y}_{te}$，BLUP 为（Sect 3.6.1 证明）：
$$
\boxed{\hat{y}_{te}= \boldsymbol{f}_{te}^\top\hat{\boldsymbol{\beta}}+\boldsymbol{r}_{te}^\top R_{tr}^{-1}\left(Y_{tr}-F_{tr}\hat{\boldsymbol{\beta}}\right)} \tag{3.2.7}
$$
其中：
- $R_{tr}=\left(R(\boldsymbol{x}_i^{tr}-\boldsymbol{x}_j^{tr})\right)$：$n_s\times n_s$ 已知相关矩阵（训练点两两）；
- $F_{tr}$：$n_s\times p$ 已知设计矩阵，第 $i$ 行为 $\left(f_1(\boldsymbol{x}_i^{tr}),\dots,f_p(\boldsymbol{x}_i^{tr})\right)$；
- $\hat{\boldsymbol{\beta}}=\left(F_{tr}^\top R_{tr}^{-1}F_{tr}\right)^{-1}F_{tr}^\top R_{tr}^{-1}Y_{tr}$：**广义最小二乘（GLS）估计**；
- $\boldsymbol{f}_{te}^\top=\left(f_1(\boldsymbol{x}_{te}),\dots,f_p(\boldsymbol{x}_{te})\right)$：测试点回归向量；
- $\boldsymbol{r}_{te}^\top=\left(R(\boldsymbol{x}_{te}-\boldsymbol{x}_1^{tr}),\dots,R(\boldsymbol{x}_{te}-\boldsymbol{x}_{n_s}^{tr})\right)$：测试点与各训练点的相关向量。

**预测不确定性（MSPE，即预测方差）**：
$$
\boxed{s^2(\boldsymbol{x}_{te})=\sigma_Z^2\left\{1-\boldsymbol{r}_{te}^\top R_{tr}^{-1}\boldsymbol{r}_{te}+\boldsymbol{h}^\top Q^{-1}\boldsymbol{h}\right\}} \tag{3.2.8}
$$
其中 $\boldsymbol{h}=\boldsymbol{f}_{te}-F_{tr}^\top R_{tr}^{-1}\boldsymbol{r}_{te}$，$Q=F_{tr}^\top R_{tr}^{-1}F_{tr}$。已知相关结构时，(3.2.8) 只差一个未知标量 $\sigma_Z^2$。

> 实际应用限制：BLUP (3.2.7) 依赖相关结构，而相关结构通常未知；实际中用**估计的相关函数与过程方差**代入（→ 3.3 EBLUP）。

## 3.2.2 最小 MSPE 预测器（任意形式预测器）
**定义**：若 $\hat{Y}_0$ 对 $\mathcal{F}$ 中所有 $F$ 的 MSPE 都不大于任何其他（可为任意形式的）预测器 $Y_0^\star$，则称其为最小（最佳）MSPE 预测器。

**定理 3.1（预测基本定理）**：设 $(Y_0,Y_{tr})$ 有分布 $F$，则
$$
\hat{Y}_0=E[Y_0\mid Y_{tr}] \tag{3.2.9}
$$
是基于 $Y_{tr}$ 的最佳 MSPE 预测器。（证明：对任意竞争预测器 $Y_0^\star$，将 MSPE 拆成 $(Y_0^\star-\hat Y_0)+(\hat Y_0-Y_0)$，交叉项用迭代期望律等于 0。）

- 最佳 MSPE 预测器自动无偏（$E[\hat Y_0]=E[E[Y_0\mid Y_{tr}]]=E[Y_0]$）。
- **最佳 MSPE 是 BLUP 的强化**：预测器类从"线性"放宽到"任意"。
- 例 3.2 说明非线性预测器可以改进：当条件分布为均匀时，最佳预测器是 $Y_1^2/2$（非线性），其 MSPE（≈0.0167）略小于对应 BLUP（≈0.0181）。

### 例 3.3 GP 设置下的最小 MSPE 预测器
已知 $\boldsymbol{\beta},\sigma_Z^2,R(\cdot)$ 时，$Y_{te}$ 与 $Y_{tr}$ 的联合分布为多元正态：
$$
\begin{pmatrix}Y_{te}\\Y_{tr}\end{pmatrix}\sim N_{1+n_s}\!\left(\begin{pmatrix}\boldsymbol{f}_{te}^\top\\F_{tr}\end{pmatrix}\boldsymbol{\beta},\ \sigma_Z^2\begin{bmatrix}1 & \boldsymbol{r}_{te}^\top\\\boldsymbol{r}_{te} & R_{tr}\end{bmatrix}\right). \tag{3.2.13}
$$
由定理 3.1 与多元正态条件分布，**最佳 MSPE 预测器**为：
$$
\hat{y}_{te}=E[Y_{te}\mid Y_{tr}]=\boldsymbol{f}_{te}^\top\boldsymbol{\beta}+\boldsymbol{r}_{te}^\top R_{tr}^{-1}(Y_{tr}-F_{tr}\boldsymbol{\beta}) \tag{3.2.14}
$$
即 BLUP (3.2.7)（此处 $\boldsymbol{\beta}$ 已知）。

### 例 3.4 两层模型（$\boldsymbol{\beta}$ 有先验）
视 (3.2.13) 为给定 $\boldsymbol{\beta}$ 的条件分布（第一层），第二层给 $\boldsymbol{\beta}$ 先验 $[\boldsymbol{\beta}]$。则最佳 MSPE 预测器
$$
\hat{y}_{te}=E[Y_{te}\mid Y_{tr}]
=\boldsymbol{f}_{te}^\top E[\boldsymbol{\beta}\mid Y_{tr}]+\boldsymbol{r}_{te}^\top R_{tr}^{-1}\left(Y_{tr}-F_{tr}E[\boldsymbol{\beta}\mid Y_{tr}]\right).
$$
当取非信息先验 $[\boldsymbol{\beta}]\propto1$ 时，$[\boldsymbol{\beta}\mid Y_{tr}]\sim N_p\!\left(\hat{\boldsymbol{\beta}},\ \sigma_Z^2(F_{tr}^\top R_{tr}^{-1}F_{tr})^{-1}\right)$，其中 $\hat{\boldsymbol{\beta}}$ 为 GLS 估计，回到 BLUP (3.2.15)。**这为 4.2 的贝叶斯后验做了铺垫。**

## 3.2.3 BLUP 的性质（可直接验证）
1. **线性于训练数据**：将 $\hat{\boldsymbol{\beta}}$ 代入，(3.2.7) 化为 $\hat{y}_{te}=\boldsymbol{a}_\star^\top Y_{tr}$（(3.2.16)，线性组合）。
2. **无偏**：$E[\hat{y}_{te}]=\boldsymbol{f}_{te}^\top\boldsymbol{\beta}=E[Y(\boldsymbol{x}_{te})]$（(3.2.17)）。
3. **插值训练数据**：若 $\boldsymbol{x}_{te}=\boldsymbol{x}_i^{tr}$，则 $R_{tr}^{-1}\boldsymbol{r}_{te}=\boldsymbol{e}_i$（第 $i$ 个单位向量），于是修正项 $=\boldsymbol{e}_i^\top(Y_{tr}-F_{tr}\hat{\boldsymbol{\beta}})=Y(\boldsymbol{x}_i^{tr})-\boldsymbol{f}^\top(\boldsymbol{x}_i^{tr})\hat{\boldsymbol{\beta}}$，故 $\hat{y}(\boldsymbol{x}_{te})=Y(\boldsymbol{x}_i^{tr})$。**（确定性仿真 ⇒ 严格插值、采样点处预测方差为 0，与带噪回归不同。）**
4. **作为 $\boldsymbol{x}_{te}$ 的函数是"基函数"线性组合**（(3.2.18)）：
$$
\hat{y}(\boldsymbol{x}_{te})=\sum_{j=1}^{p}\hat\beta_j f_j(\boldsymbol{x}_{te})+\sum_{i=1}^{n_s} d_i R(\boldsymbol{x}_{te}-\boldsymbol{x}_i^{tr}),\quad \boldsymbol{d}=R_{tr}^{-1}(Y_{tr}-F_{tr}\hat{\boldsymbol{\beta}}).
$$
   - $\hat{y}$ 的**光滑性继承自相关函数 $R(\cdot)$**；靠近训练点时其行为取决于 $R(\cdot)$ 在原点的性态。

> **小结**：本节用两个经典准则（BLUP、最小 MSPE）给出了同一预测器 (3.2.7)。但它仅在"已知相关结构、受限预测器类"下最优。下一节解决相关结构未知的实证问题（EBLUP）。

---

# 3.3 实证 BLUP（EBLUP）：超参数估计（p76–84）

## 3.3.1 问题设置
预测 $y(\boldsymbol{x}_{te})$，训练数据 $(\boldsymbol{x}_i^{tr},y(\boldsymbol{x}_i^{tr}))$，模型为 (3.1.1)。假设**相关函数带未知参数**：$R(\cdot)=R(\cdot\mid\kappa)$。例如幂指数相关
$$
R(\boldsymbol{h})=\exp\left\{-\sum_{j=1}^{d}\xi_j|h_j|^{p_j}\right\}
$$
有 $d$ 个未知 rate（长度）参数 $\xi_1,\dots,\xi_d$ 和 $d$ 个未知 power 参数 $p_1,\dots,p_d$，故 $\kappa\equiv(\xi_1,\dots,\xi_d,p_1,\dots,p_d)$ 含 $2d$ 个未知量。$\boldsymbol{\beta},\sigma_Z^2$ 也未知。

**EBLUP 基本策略**：把 BLUP (3.2.7) 中的相关参数换成估计值：
$$
\boxed{\hat{y}(\boldsymbol{x}_{te})\equiv\hat{y}_{te}=\boldsymbol{f}_{te}^\top\hat{\boldsymbol{\beta}}+\hat{\boldsymbol{r}}_{te}^\top\hat{R}_{tr}^{-1}\left(Y_{tr}-F_{tr}\hat{\boldsymbol{\beta}}\right)} \tag{3.3.2}
$$
其中 $\hat{R}_{tr}=(R(\boldsymbol{x}_i^{tr}-\boldsymbol{x}_j^{tr}\mid\hat\kappa))$，$\hat{\boldsymbol{r}}_{te}=(R(\boldsymbol{x}_{te}-\boldsymbol{x}_i^{tr}\mid\hat\kappa))$，$\hat\kappa$ 为 $\kappa$ 的估计，$\hat{\boldsymbol{\beta}}$ 用 $\hat{R}_{tr}$ 代入的 GLS。

**重要注意事项**：
- EBLUP **不再是训练数据的线性函数**（因为 $\hat\kappa$ 一般非线性于 $Y_{tr}$），也不一定无偏（参见 Kackar & Harville 1984）。
- 用不同 $\kappa$ 估计法得到不同 EBLUP：**MLE-EBLUP、REML-EBLUP、XV-EBLUP、PMode-EBLUP**。
- 除交叉验证法外，其余方法要求数据满足 $[Y_{tr}\mid\boldsymbol{\beta},\sigma_Z^2,\kappa]\sim N_{n_s}(F_{tr}\boldsymbol{\beta},\sigma_Z^2 R_{tr})$。
- (3.3.2) 不需要 $\sigma_Z^2$，但量化预测不确定性需要 $\sigma_Z^2$ 的估计（见 4.2.8）。

## 3.3.2 极大似然 EBLUP（MLE-EBLUP）
用 $Y_{tr}$ 的多元正态假设。对数似然（去常数项）：
$$
\ell(\boldsymbol{\beta},\sigma_Z^2,\kappa)=-\frac12\left[n_s\ln(\sigma_Z^2)+\ln(\det R_{tr})+(\boldsymbol{y}_{tr}-F_{tr}\boldsymbol{\beta})^\top R_{tr}^{-1}(\boldsymbol{y}_{tr}-F_{tr}\boldsymbol{\beta})/\sigma_Z^2\right]. \tag{3.3.3}
$$
**给定 $\kappa$**：$\boldsymbol{\beta}$ 的 MLE 是 GLS 估计
$$
\hat{\boldsymbol{\beta}}=\left(F_{tr}^\top R_{tr}^{-1}F_{tr}\right)^{-1}F_{tr}^\top R_{tr}^{-1}\boldsymbol{y}_{tr} \tag{3.3.4}
$$
$\sigma_Z^2$ 的 MLE：
$$
\hat\sigma_Z^2=\frac{1}{n_s}\left(\boldsymbol{y}_{tr}-F_{tr}\hat{\boldsymbol{\beta}}\right)^\top R_{tr}^{-1}\left(\boldsymbol{y}_{tr}-F_{tr}\hat{\boldsymbol{\beta}}\right). \tag{3.3.5}
$$
**代回消去 $\boldsymbol{\beta},\sigma_Z^2$**，最大化的浓缩对数似然为：
$$
\ell(\hat{\boldsymbol{\beta}},\hat\sigma_Z^2,\kappa)=-\frac12\left[n_s\ln(\hat\sigma_Z^2(\kappa))+\ln(\det R_{tr}(\kappa))+n_s\right].
$$
**因此 MLE 选择 $\hat\kappa$ 最小化**：
$$
\boxed{n_s\ln(\hat\sigma_Z^2(\kappa))+\ln(\det R_{tr}(\kappa))} \tag{3.3.6}
$$
（$\hat\sigma_Z^2$ 由 (3.3.5) 定义，随 $\kappa$ 变化。）对应预测器为 **MLE-EBLUP**。

## 3.3.3 受限极大似然 EBLUP（REML-EBLUP）
REML（restricted/residual ML）由 Patterson & Thompson (1971) 提出，目的是得到比 MLE **偏差更小**的方差/协方差参数估计（也称 marginal ML）。REML 最大化 $Y_{tr}$ 的**一组极大线性无关线性组合**的似然，其中每个组合与均值 $F_{tr}\boldsymbol{\beta}$ 正交。

做法：设 $F_{tr}$ 满列秩 $p$，选 $(n_s-p)\times n_s$ 满行秩矩阵 $C$ 使 $CF_{tr}=0$。REML 估计 $\kappa$ 为线性变换数据
$$
W\equiv CY_{tr}\sim N\!\left(CF_{tr}\boldsymbol{\beta}=0,\ \sigma_Z^2 CR_{tr}(\kappa)C^\top\right)
$$
的似然最大化者。$W$ 比 $Y_{tr}$ 少 $p$ 个"观测"，但分布不含未知 $\boldsymbol{\beta}$。

### 例 3.5 简单情形
$Y_1,\dots,Y_n$ i.i.d. $N(\beta_0,\sigma^2)$。取 $W_1=Y_1-\bar Y,\dots,W_{n-1}=Y_{n-1}-\bar Y$，极大化 $W$ 的似然得到 $\hat\sigma^2=\sum_i(Y_i-\bar Y)^2/(n-1)$（无偏，除数 $n-1$），而 MLE 用 $n$（有偏）。这就是 REML 修正偏差的直观。

**一般结论**：REML 估计 $\kappa$ 与线性组合的选取无关（只要 $C$ 秩最大为 $n-p$）。REML 估计 $\sigma_Z^2$：
$$
\tilde\sigma_Z^2=\frac{n_s}{n_s-p}\hat\sigma_Z^2=\frac{1}{n_s-p}\left(\boldsymbol{y}_{tr}-F_{tr}\hat{\boldsymbol{\beta}}\right)^\top R_{tr}^{-1}(\kappa)\left(\boldsymbol{y}_{tr}-F_{tr}\hat{\boldsymbol{\beta}}\right), \tag{3.3.8}
$$
（$\hat\sigma_Z^2$ 是 MLE）。**REML 估计 $\kappa$ 最小化**：
$$
\boxed{(n_s-p)\ln(\tilde\sigma_Z^2)+\ln(\det R_{tr}(\kappa))+\ln\left(\det\left(F_{tr}^\top R_{tr}^{-1}(\kappa)F_{tr}\right)\right)} \tag{3.3.9}
$$
对应预测器为 **REML-EBLUP**。

## 3.3.4 交叉验证 EBLUP（XV-EBLUP）
交叉验证用留一法选参数。对 $i=1,\dots,n_s$，令 $\hat y_{-i}(\kappa)$ 为去掉 $(\boldsymbol{x}_i^{tr},y(\boldsymbol{x}_i^{tr}))$ 后、以 $\kappa$ 为真实参数时按 (3.3.2) 对 $y(\boldsymbol{x}_i^{tr})$ 的预测。**XV 估计 $\kappa$ 最小化经验 MSPE**：
$$
\mathrm{XV\text{-}PE}(\kappa)\equiv\sum_{i=1}^{n_s}\left(\hat y_{-i}(\kappa)-y(\boldsymbol{x}_i^{tr})\right)^2.
$$
对应预测器为 **XV-EBLUP**。更一般形式见 Golub et al. (1979)、Wahba (1980)。

## 3.3.5 后验众数 EBLUP（PMode-EBLUP）
动机：最佳 MSPE 预测器是 $E[Y(\boldsymbol{x}_{te})\mid Y_{tr}]$，贝叶斯下可写
$$
E[Y(\boldsymbol{x}_{te})\mid Y_{tr}]=E\left[E[Y(\boldsymbol{x}_{te})\mid Y_{tr},\kappa]\mid Y_{tr}\right], \tag{3.3.10}
$$
内层是 $\kappa$ 的函数，外层对后验 $[\kappa\mid Y_{tr}]$ 取期望。$[\kappa\mid Y_{tr}]$ 一般无闭式。一个简单近似是取 $\hat\kappa$ 为 $[\kappa\mid Y_{tr}]$ 的众数，预测用
$$
E[Y(\boldsymbol{x}_{te})\mid Y_{tr},\hat\kappa], \tag{3.3.11}
$$
（视 $[\kappa\mid Y_{tr}]$ 退化在众数处）。后验众数 $\hat\kappa$ 最大化
$$
[\kappa\mid Y_{tr}]\propto[Y_{tr}\mid\kappa][\kappa].
$$
对应预测器为 **PMode-EBLUP**。注意：相关参数上给不当的无信息先验可能导致不当后验（Berger et al. 2001 对各类各向同性相关函数证明）；该书给出一个后验为正当的默认先验。

## 3.3.6 示例（MLE/REML 应用工作流）
以"烟羽升至火源上方 5 ft 所需时间"为例，4 个输入（热损失分数、火源高度、房间高度、房间面积）。用 40 个 Sobol 序列点作训练。REML-EBLUP 用常数均值、高斯相关
$$
\mathrm{Cor}[Y(\boldsymbol{x}_1),Y(\boldsymbol{x}_2)]=\exp\left\{-\sum_{j=1}^{d}\xi_j(x_{1,j}-x_{2,j})^2\right\}, \tag{3.3.12}
$$
拟合得 $\hat\beta_0=49.57,\ \hat\sigma_Z^2=397.29$ 及 $\hat\xi_j$。
**实际注意**：各输入量纲不同，直接解释 $\xi_j$ 有问题；应将每个输入归一化到 $[0,1]$（$\boldsymbol{x}_{i,j}^s=(\boldsymbol{x}_{i,j}-\min_j)/(\max_j-\min_j)$）后再解读 $\xi_j$（归一化后其倒数大致对应有效相关长度）。

> **工作流总括**：选空间填充设计 → 跑仿真 → 用 MLE/REML 估 $\kappa,\sigma_Z^2$（数值优化浓缩似然 (3.3.6)/(3.3.9)）→ 代入 BLUP 得预测与 MSPE → 交叉验证诊断。

---

# 4.2 共轭贝叶斯模型的推断（p117–128）

本节做**完整贝叶斯推断**：对回归+平稳 GP 模型 (4.1.1)，在回归系数 $\boldsymbol{\beta}$ 未知、过程精度 $\lambda_Z$ 与相关结构已知（$\vartheta=\boldsymbol{\beta}$）时，给出后验 $[\boldsymbol{\beta}\mid Y_{tr}]$ 与预测分布 $[Y_{te}\mid Y_{tr}]$ 的闭式。

## 设定与两种 $\boldsymbol{\beta}$ 先验
两层分层模型，顶层（第一层）：
$$
\begin{pmatrix}Y_{te}\\Y_{tr}\end{pmatrix}\Bigg|\boldsymbol{\beta}\sim N_{n_e+n_s}\!\left(\begin{pmatrix}F_{te}\\F_{tr}\end{pmatrix}\boldsymbol{\beta},\ \lambda_Z^{-1}\begin{bmatrix}R_{te} & R_{te,tr}\\R_{te,tr}^\top & R_{tr}\end{bmatrix}\right),
$$
$\boldsymbol{\beta}$ 未知，$\lambda_Z$ 与所有相关已知。$F_{te}$ 为测试点回归矩阵（$n_e$ 个测试点）。

两种先验：
- **Case (a) 信息先验**：$[\boldsymbol{\beta}]\sim N_p\!\left(\boldsymbol{b}_\beta,\lambda_\beta^{-1}V_\beta\right)$（$V_\beta$ 正定、$\boldsymbol{b}_\beta\in\mathbb{R}^p$、$\lambda_\beta>0$ 均已知）；
- **Case (b) 非信息先验**：$\pi(\boldsymbol{\beta})\propto1$（可视为 Case (a) 先验精度 $\lambda_\beta\to0$ 的极限）。

## 定理 4.1（共轭后验与预测分布）

### Case (a)（信息先验）
**$\boldsymbol{\beta}$ 的后验**：
$$
[\boldsymbol{\beta}\mid Y_{tr}=\boldsymbol{y}_{tr}]\sim N_p(\boldsymbol{\mu}_{\beta\mid tr},\Sigma_{\beta\mid tr})
$$
$$
\boldsymbol{\mu}_{\beta\mid tr}=\left(\lambda_Z F_{tr}^\top R_{tr}^{-1}F_{tr}+\lambda_\beta V_\beta^{-1}\right)^{-1}\left(\lambda_Z F_{tr}^\top R_{tr}^{-1}\boldsymbol{y}_{tr}+\lambda_\beta V_\beta^{-1}\boldsymbol{b}_\beta\right), \tag{4.2.1}
$$
$$
\Sigma_{\beta\mid tr}=\left(\lambda_Z F_{tr}^\top R_{tr}^{-1}F_{tr}+\lambda_\beta V_\beta^{-1}\right)^{-1}. \tag{4.2.2}
$$

**预测分布**：
$$
[Y_{te}\mid Y_{tr}=\boldsymbol{y}_{tr}]\sim N_{n_e}(\boldsymbol{\mu}_{te\mid tr},\Sigma_{te\mid tr}), \tag{4.2.3}
$$
均值：
$$
\boldsymbol{\mu}_{te\mid tr}=F_{te}\boldsymbol{\mu}_{\beta\mid tr}+R_{te,tr}R_{tr}^{-1}\left(\boldsymbol{y}_{tr}-F_{tr}\boldsymbol{\mu}_{\beta\mid tr}\right), \tag{4.2.4}
$$
协方差：
$$
\Sigma_{te\mid tr}=\lambda_Z^{-1}\left\{R_{te}-\left(F_{te}\ R_{te,tr}\right)\begin{bmatrix}-\frac{\lambda_\beta}{\lambda_Z}V_\beta^{-1} & F_{tr}^\top\\F_{tr} & R_{tr}\end{bmatrix}^{-1}\begin{pmatrix}F_{te}^\top\\R_{te,tr}^\top\end{pmatrix}\right\}. \tag{4.2.5}
$$

### Case (b)（非信息先验 $\pi(\boldsymbol{\beta})\propto1$）
**$\boldsymbol{\beta}$ 的后验**：
$$
[\boldsymbol{\beta}\mid Y_{tr}]\sim N_p\!\left(\hat{\boldsymbol{\beta}}\equiv\left(F_{tr}^\top R_{tr}^{-1}F_{tr}\right)^{-1}F_{tr}^\top R_{tr}^{-1}\boldsymbol{y}_{tr},\ \lambda_Z^{-1}\left(F_{tr}^\top R_{tr}^{-1}F_{tr}\right)^{-1}\right),
$$
即后验均值恰为 **GLS/BLUP 的 $\hat{\boldsymbol{\beta}}$**。

**预测分布** (4.2.6)：均值由 (4.2.4) 把 $\boldsymbol{\mu}_{\beta\mid tr}$ 换成 $\hat{\boldsymbol{\beta}}$；协方差由 (4.2.5) 把 $\frac{\lambda_\beta}{\lambda_Z}V_\beta^{-1}$ 换成 $p\times p$ 零矩阵。

> 证明只需在 (4.1.2) 的一般策略下做积分的直接计算（见 4.4）。

## 4.2.1.1 关于 $\boldsymbol{\beta}$ 的后验推断
Case (a) 后验均值**只依赖比值 $\lambda_\beta/\lambda_Z$**：
$$
\boldsymbol{\mu}_{\beta\mid tr}=\left(F_{tr}^\top R_{tr}^{-1}F_{tr}+V_\beta^{-1}\lambda_\beta/\lambda_Z\right)^{-1}\left(F_{tr}^\top R_{tr}^{-1}F_{tr}\hat{\boldsymbol{\beta}}+V_\beta^{-1}\boldsymbol{b}_\beta\,\lambda_\beta/\lambda_Z\right).
$$
当 $\lambda_\beta=\lambda_Z$ 时进一步简化为**矩阵凸组合**：
$$
\boldsymbol{\mu}_{\beta\mid tr}=\Omega\hat{\boldsymbol{\beta}}+(I_p-\Omega)\boldsymbol{b}_\beta, \tag{4.2.7}
$$
其中 $\Omega=\left(F_{tr}^\top R_{tr}^{-1}F_{tr}+V_\beta^{-1}\right)^{-1}F_{tr}^\top R_{tr}^{-1}F_{tr}$——后验均值是 BLUP $\hat{\boldsymbol{\beta}}$ 与先验均值 $\boldsymbol{b}_\beta$ 的加权平均（权重由数据信息与先验信息的"信息量"决定）。
后验协方差 $\Sigma_{\beta\mid tr}$ 依赖 $\lambda_Z$ 与 $\lambda_\beta$（或比值）。

## 4.2.1.2 单测试点 $x_{te}$ 的预测推断
单点情形下，预测均值与方差：

**两种先验下预测均值都**：线性于 $Y_{tr}$、是 $Y(\boldsymbol{x}_{te})$ 的无偏预测、**插值训练数据**。其形式（把 $R(\cdot)$ 与回归函数当"基函数"）：
$$
\mu_{te\mid tr}(\boldsymbol{x}_{te})=\sum_{j=1}^{p}f_j(\boldsymbol{x}_{te})\mu_{\beta\mid tr,j}+\sum_{i=1}^{n_s}d_i R(\boldsymbol{x}_{te}-\boldsymbol{x}_i^{tr}),
$$
光滑性继承自 $R(\cdot)$ 与 $\{f_j\}$。插值证明：当 $\boldsymbol{x}_{te}=\boldsymbol{x}_i^{tr}$ 时 $R_{tr}^{-1}\boldsymbol{r}_{te}=\boldsymbol{e}_i$，于是 $\mu_{te\mid tr}=f^\top(\boldsymbol{x}_i^{tr})\mu_{\beta\mid tr}+(Y_i-f^\top(\boldsymbol{x}_i^{tr})\mu_{\beta\mid tr})=Y_i$。

**预测方差**：
- Case (b)：与 BLUP 方差 (3.2.8) 一致：
$$
\sigma_{te\mid tr}^2(\boldsymbol{x}_{te})=\lambda_Z^{-1}\left\{1-\boldsymbol{r}_{te}^\top R_{tr}^{-1}\boldsymbol{r}_{te}+\boldsymbol{h}^\top\left(F_{tr}^\top R_{tr}^{-1}F_{tr}\right)^{-1}\boldsymbol{h}\right\},\quad \boldsymbol{h}=\boldsymbol{f}_{te}-F_{tr}^\top R_{tr}^{-1}\boldsymbol{r}_{te}. \tag{4.2.8}
$$
- Case (a)：形式类似，用 $Q=F_{tr}^\top R_{tr}^{-1}F_{tr}+\frac{\lambda_\beta}{\lambda_Z}V_\beta^{-1}$ 替换 (4.2.11)，得到 (4.2.9)/(4.2.10)：
$$
\sigma_{te\mid tr}^2(\boldsymbol{x}_{te})=\lambda_Z^{-1}\left\{1-\boldsymbol{r}_{te}^\top R_{tr}^{-1}\boldsymbol{r}_{te}+\boldsymbol{h}^\top Q^{-1}\boldsymbol{h}\right\}.
$$
- **在训练点处后验方差为 0**（$\boldsymbol{x}_{te}=\boldsymbol{x}_i^{tr}$ 时 $r_{te}^\top R_{tr}^{-1}=\boldsymbol{e}_i^\top$、$f_{te}=f(\boldsymbol{x}_i^{tr})$，代入得 0）——因为确定性仿真无测量误差，训练点函数值已知。

**预测区间**：条件分布标准化后
$$
\frac{Y(\boldsymbol{x}_{te})-\mu_{te\mid tr}(\boldsymbol{x}_{te})}{\sigma_{te\mid tr}(\boldsymbol{x}_{te})}\sim N(0,1) \tag{4.2.12}
$$
给出逐点后验预测区间：
$$
P\left\{Y(\boldsymbol{x}_{te})\in\mu_{te\mid tr}(\boldsymbol{x}_{te})\pm\sigma_{te\mid tr}(\boldsymbol{x}_{te})z_{\alpha/2}\mid Y_{tr}\right\}=1-\alpha.
$$
当 $\boldsymbol{x}_{te}\in(a,b)$ 变化时，$\mu_{te\mid tr}\pm\sigma_{te\mid tr}z_{\alpha/2}$ 构成 $y(\boldsymbol{x}_{te})$ 的**逐点 $100(1-\alpha)\%$ 预测带**。

### 例 4.1 阻尼正弦曲线
$y(x)=e^{-1.4x}\cos(7\pi x/2)$，$0<x<1$，7 个训练点。模型 $[Y(x)\mid\beta_0]=\beta_0+Z(x)$，$R(h)=\exp\{-10h^2\}$。Case (a) 取 $\beta_0\sim N(b_{te},\lambda_\beta^{-1})$。预测均值 (4.2.13)：
$$
\mu_{te\mid tr}(\boldsymbol{x}_{te})=\mu_{\beta\mid tr}+\boldsymbol{r}_{te}^\top R_{tr}^{-1}\left(\boldsymbol{y}_{tr}-\boldsymbol{1}_{n_s}\mu_{\beta\mid tr}\right),
$$
其中 $\mu_{\beta\mid tr}$ 为 (4.2.1) 的标量版。**图示表明先验精度 $\lambda_\beta$ 越大，预测均值越被拉向先验均值 $b_{te}$**（$\lambda_\beta=0$ 蓝、$\lambda_\beta=10$ 红、$\lambda_\beta=100$ 绿），量化了先验信息对后验预测的影响。

> **对 BO 的作用**：4.2 给出贝叶斯后验的闭式预测均值/方差，正是贝叶斯优化中"后验引擎"的完整形式；ED4DSE 的分层贝叶斯推导在此补齐。

---

# 6.3.4 期望改进算法（EI / EGO，p216–225）

前文准则往往难以/无法实现，本节给出**可实现但启发式**的全局优化算法，目标：求未知函数 $y_1(\boldsymbol{x})$ 在 $\mathcal{X}$ 上的全局最小点 $\boldsymbol{x}_{\min}\in\arg\min_{\boldsymbol{x}\in\mathcal{X}}y_1(\boldsymbol{x})$。

## 6.3.4.1 Schonlau & Jones 期望改进算法（EGO）
**框架**：Schonlau et al. (1998) 与 Jones et al. (1998) 提出序贯设计策略，即**高效全局优化（EGO）算法**：每阶段加一个输入点。初始化：在空间填充设计（如 maximin 距离 LHD）上算 $n$ 个点，获得 $y_1(\cdot)$ 的初始信息（这 $n$ 次运行即训练数据）。

**模型与后验**：对 $y_1(\cdot)$ 用 (3.1.1) 形式的高斯先验（过程方差 $\sigma_1^2$，回归参数 $\boldsymbol{\beta}$ 取均匀先验）。$\sigma_1^2$ 已知时，
$$
[Y_1(\boldsymbol{x}_0)\mid Y_1^n=\boldsymbol{y}_1^n]\sim N\left(\hat y_1(\boldsymbol{x}_0),\ s_1^2(\boldsymbol{x}_0)\right), \tag{6.3.3}
$$
$\hat y_1$ 是 BLUP (3.2.7)，预测方差
$$
s_1^2(\boldsymbol{x}_0)=\sigma_1^2\left\{1-\boldsymbol{r}_0^\top R^{-1}\boldsymbol{r}_0+\boldsymbol{h}_0^\top(F^\top R^{-1}F)^{-1}\boldsymbol{h}_0\right\},\quad \boldsymbol{h}_0=\boldsymbol{f}_0-F^\top R^{-1}\boldsymbol{r}_0. \tag{6.3.4}
$$
实践中相关参数与 $\sigma_1^2$ 用 MLE/REML 估计（见 3.3.2）。

**改进（Improvement）定义**：设当前 $n$ 次运行已得最小输出 $y_{\min}^n=\min_{i=1,\dots,n}y_1(\boldsymbol{x}_i)$。对候选点 $\boldsymbol{x}$，相对当前最小已知值的改进为：
$$
\text{Improvement at } \boldsymbol{x}=\begin{cases}y_{\min}^n-y_1(\boldsymbol{x}), & y_{\min}^n-y_1(\boldsymbol{x})>0\\0, & y_{\min}^n-y_1(\boldsymbol{x})\le0\end{cases}. \tag{6.3.5}
$$
$y_1(\boldsymbol{x})$ 未知，故用其后验定义**概率型改进函数**：
$$
I_n(\boldsymbol{x})=\begin{cases}y_{\min}^n-Y_1(\boldsymbol{x}), & y_{\min}^n-Y_1(\boldsymbol{x})>0\\0, & y_{\min}^n-Y_1(\boldsymbol{x})\le0\end{cases},\ \boldsymbol{x}\in\mathcal{X}. \tag{6.3.6}
$$

### 例 6.1 直觉
对 $x_1,x_2,x_3$ 画出 $[y_{\min}^n-Y_1(\boldsymbol{x})\mid Y_1^n]$ 的后验密度：
- $x_1$：密度集中在正值 ⇒ $y_1(x_1)$ 很可能低于 $y_{\min}^n$，是好的探索点；
- $x_2$：密度集中在负值 ⇒ 不理想；
- $x_3$：尾部重、正区间支撑大 ⇒ 也可取。尾部重源于 $x_3$ 处 MSPE $s_1^2(x_3)$ 大；在 $x_3$ 采样可降低其 MSPE。**一般地，$s_1(\boldsymbol{x})$ 大的点可产生大的期望改进。**

**期望改进的闭式**：对 $x\in D_n$（训练点），$E[I_n(\boldsymbol{x})\mid Y_1^n]=0$（重复算已采样点无益）。对 $x\notin D_n$：
$$
\boxed{E[I_n(\boldsymbol{x})\mid Y_1^n]=(y_{\min}^n-\hat y_1(\boldsymbol{x}))\Phi\!\left(\frac{y_{\min}^n-\hat y_1(\boldsymbol{x})}{s_1(\boldsymbol{x})}\right)+s_1(\boldsymbol{x})\,\varphi\!\left(\frac{y_{\min}^n-\hat y_1(\boldsymbol{x})}{s_1(\boldsymbol{x})}\right)} \tag{6.3.7}
$$
$\Phi,\varphi$ 为标准正态分布函数/密度。
**由 (6.3.7) 可见 EI 大当且仅当**：
- 预测值远低于当前最优，$\hat y_1(\boldsymbol{x})\ll y_{\min}^n$（**局部搜索**项），或
- 对 $y_1(\boldsymbol{x})$ 的不确定性大，$s_1(\boldsymbol{x})$ 相对 $|y_{\min}^n-\hat y_1(\boldsymbol{x})|$ 大（**全局搜索**项）。

**EGO 算法（更新规则）**：从空间填充设计出发，给定绝对容差 $\epsilon_a$：
1. 若 $\max_{\boldsymbol{x}\in\mathcal{X}}E[I_n(\boldsymbol{x})\mid Y_1^n]<\epsilon_a$：停止，取 $\hat{\boldsymbol{x}}_{\min}$ 为 (6.3.8) 中使 $y_1(\boldsymbol{x}_i)$ 最小的训练点（或用 EBLUP 在 $\mathcal{X}$ 上最小化来预测 $\boldsymbol{x}_{\min}$）；
2. 否则选 $\boldsymbol{x}_{n+1}=\arg\max_{\boldsymbol{x}\in\mathcal{X}}E[I_n(\boldsymbol{x})\mid Y_1^n]$；令 $D_{n+1}=D_n\cup\{\boldsymbol{x}_{n+1}\}$，$Y_1^{n+1}=((Y_1^n)^\top,y_1(\boldsymbol{x}_{n+1}))^\top$，$n\gets n+1$，重复。

**参数估计与实现**：Jones/Schonlau 用幂指数相关 (2.2.11)，每个输入一个 range 一个 smoothness 参数，MLE 估计；每步后可选更新相关参数（更新代价高，尤其大设计）。
**批处理（batch）**：Schonlau 提供每阶段加多个点（$q$ 个 iterate）的变体——加完 $q$ 个后更新相关参数；建议每步更新 $s_1(\boldsymbol{x})$ 系数，但不更新 $(y_{\min}^n-\hat y_1)/s_1$ 项，以强制避开所有已采样点。
**收敛**：$\mathcal{X}$ 有限、$\epsilon_a$（或 $\epsilon_r$）=0 时 EGO 收敛到全局最小。

**改进的推广（$g$-改进）**：把改进 (6.3.6) 换成
$$
I_n^g(\boldsymbol{x})=\begin{cases}(y_{\min}^n-Y_1(\boldsymbol{x}))^g, & Y_1(\boldsymbol{x})<y_{\min}^n\\0, & \text{otherwise}\end{cases},\ g\in\{0,1,2,\dots\}.
$$
$g$ 越大搜索越偏全局（对尾部更大权重）。停止准则用 $E[I_n(\cdot)\mid Y_1^n]^{1/g}$，使容差 $\epsilon_a,\epsilon_r$ 对不同 $g$ 近似同义。Schonlau 给出 $E[I_n^g(\boldsymbol{x})\mid Y_1^n]$ 的递推式。

### 例 6.2 EGO 用于 Branin 函数
Branin：$\boldsymbol{x}\in[-5,10]\times[0,15]$，三个全局最小 $y(\pi,2.275)=y(3\pi,2.475)=y(-\pi,12.275)=0.39789$。EGO 用 21 个 maximin LHD 起点，SPACE 包序贯加了 12 点后停止（共 33 点）。加点分阶段：红（探索高不确定区）→ 橙（两全局最小附近局部搜索）→ 绿（三个全局最小附近，但 EI 峰值几乎不再下降）。最终 $\hat{\boldsymbol{x}}_{\min}=(3.14042,2.27273)$，$y(\hat{\boldsymbol{x}}_{\min})=0.39790$，相对误差约 $2.5\times10^{-5}$。

## 6.3.4.2 Picheny 期望分位数改进（EQI）——随机仿真器
EGO 假设输出确定；对**随机仿真器** $y_1(\cdot)$，同设计重复运行输出不同，$y_{\min}^n$ 也不再确定。为此给 GP 先验加**独立零均值高斯白噪声（nugget 效应）**：
$$
\tilde Y_1(\boldsymbol{x})=Y_1(\boldsymbol{x})+\varepsilon_1(\boldsymbol{x}),\quad C_1(\boldsymbol{x}_1,\boldsymbol{x}_2)=\sigma_Z^2 R_1(\boldsymbol{x}_1,\boldsymbol{x}_2)+\tau^2 I\{\boldsymbol{x}_1=\boldsymbol{x}_2\}.
$$
nugget 放松 GP 的精确插值性（随机仿真需要）。$\tau^2$ 可随运行变；Picheny 假设 $\tau^2$ 未知但在 $\mathcal{X}$ 上齐次，与其余参数一并估计。

Picheny et al. (2013) 提议最小化预测分布的 $\beta$-分位数 $q_n(\boldsymbol{x})=\hat y_1(\boldsymbol{x})+\Phi^{-1}(\beta)s_1(\boldsymbol{x})$。当前 $D_n$ 上最小值 $q_{\min}^n=\min\{q_n(\boldsymbol{x}_1),\dots,q_n(\boldsymbol{x}_n)\}$（给定数据确定）。定义分位数改进函数 $I_n^Q(\boldsymbol{x})=\max\{0,\ q_{\min}^n-Q_{n+1}(\boldsymbol{x})\}$（$Q_{n+1}$ 为含未来输出的随机 $\beta$-分位数），其期望（EQI）：
$$
E[I_n^Q(\boldsymbol{x})\mid\tilde Y_1^n]=\left(q_{\min}^n-\hat y_Q(\boldsymbol{x})\right)\Phi\!\left(\frac{q_{\min}^n-\hat y_Q(\boldsymbol{x})}{s_Q(\boldsymbol{x})}\right)+s_Q(\boldsymbol{x})\,\varphi\!\left(\frac{q_{\min}^n-\hat y_Q(\boldsymbol{x})}{s_Q(\boldsymbol{x})}\right),
$$
$\{\hat y_Q,s_Q\}$ 为 $[Q_{n+1}(\boldsymbol{x})\mid\tilde Y_1^n]$ 的均值/标准差。选 $\boldsymbol{x}_{n+1}$ 最大化 EQI，直至 EQI 足够小或预算 $N$ 耗尽。
- 首项局部（偏好 $\hat y_Q\ll q_{\min}^n$），次项全局（$s_Q$ 大）；选 $\beta\ge0.5$。
- 计算 EQI 需指定未来输出的 nugget；Picheny 建议设为 $\tau^2/(N-n)$（还剩 $N-n$ 次运行）。EQI 初始全局探索、预算将尽转局部。
- 若无 nugget（确定性），EQI 退化为 EGO。

## 6.3.4.3 Williams 环境变量均值优化
Williams et al. (2000) 把 EI 推广到同时含**控制输入 $\boldsymbol{x}_c$** 与**环境输入 $\boldsymbol{x}_e$** 的输入设置，目标：找控制输入使 $y_1(\boldsymbol{x}_c,\boldsymbol{x}_e)$ 对环境输入支撑点的均值 $\mu_1(\boldsymbol{x}_c)=\sum_j w_j y_1(\boldsymbol{x}_c,\boldsymbol{x}_{e,j})$ 最小（$\{w_j\}$ 为支撑点权重）。设 $\mathcal{X}=\mathcal{X}_c\times\mathcal{X}_e$，环境变量取 $n_e$ 个支撑点。

$\mu_1(\boldsymbol{x}_c)$ 继承先验 $M_1(\boldsymbol{x}_c)\equiv\sum_j w_j Y_1(\boldsymbol{x}_c,\boldsymbol{x}_{e,j})$。改进定义基于 $\mu_{\min}^n=\min_i\mu_1(\boldsymbol{x}_{c,i})$，但 $\mu_{\min}^n$ **永远不能直接算出**（因 $\mu_1(\cdot)$ 未知），故用 $M_{\min}^n=\min_i M_1(\boldsymbol{x}_{c,i})$ 的（后）验推断预测 $\mu_{\min}^n$——EI 估计比 Schonlau/Jones 更难。

**算法步骤**：① 初始设计 $D_n$ 并算输出；② 估相关参数（MLE/REML 或贝叶斯后验众数）；③ 选 $\boldsymbol{x}_{c,n+1}\in\arg\max_{\boldsymbol{x}_c}E[I_n(\boldsymbol{x}_c)\mid Y_1^n]$；④ 给定 $\boldsymbol{x}_{c,n+1}$，选 $\boldsymbol{x}_{e,n+1}$ 最小化给定 $Y_1^n$ 的预测 MSPE（有闭式）；⑤ 停止判断：是则以 $M_1(\cdot)$ 条件均值的全局最小预测为解；否则 $D_{n+1}=D_n\cup\{(\boldsymbol{x}_{c,n+1},\boldsymbol{x}_{e,n+1})\}$、算 $y_1$、$n\gets n+1$、回步骤②。
- 相关参数估计可能极耗时；建议初始迭代频繁更新、后期降低更新频率。
- 步骤③的 EI 无闭式（因 $M_{\min}^n$ 未知），Williams 给出蒙特卡洛近似；步骤④的 MSPE 有闭式。
- 因每阶段重估相关参数，最大 EI 序列**不必单调下降**；停止准则基于相对历史的一组"小"最大 EI（如跟踪移动平均与极差，达到相对初值的阈值，建议连续两次满足）。

---

# 6.3.5 约束全局优化（p225–229）★毕设主题

## Schonlau 概率型约束 EI
Schonlau et al. (1998) 基于 EI 求解约束优化。标记输出为 $y_1(\cdot),\dots,y_{k+1}(\cdot)$（$m=k+1$）。目标：在 $k$ 个约束 $l_i\le y_i(\boldsymbol{x})\le u_i\ (i=2,\dots,k+1)$ 下最小化 $y_1(\boldsymbol{x})$。要求每个输入处都计算所有输出。设 $(Y_1(\boldsymbol{x}),\dots,Y_{k+1}(\boldsymbol{x}))$ 为 $(y_1,\dots,y_{k+1})$ 的随机过程模型。

**约束改进函数**：
$$
I_{c,n}^g(\boldsymbol{x})=\begin{cases}(y_{\min}^n-Y_1(\boldsymbol{x}))^g, & Y_1(\boldsymbol{x})<y_{\min}^n\ \text{且}\ l_i\le Y_i(\boldsymbol{x})\le u_i,\ i=2,\dots,k+1\\0, & \text{otherwise}\end{cases}. \tag{6.3.9}
$$
**任何约束违规 → 改进为 0。**

**独立假设下的条件期望**：假设目标与约束过程**相互独立**，则约束条件期望改进分解为
$$
E\left[I_{c,n}^g(\boldsymbol{x})\mid Y_1^n,\dots,Y_{k+1}^n\right]
=E\left[I_n^g(\boldsymbol{x})\mid Y_1^n\right]\times P\left[l_2\le Y_2(\boldsymbol{x})\le u_2\mid Y_2^n\right]\times\cdots\times P\left[l_{k+1}\le Y_{k+1}(\boldsymbol{x})\le u_{k+1}\mid Y_{k+1}^n\right],
$$
其中给定观测 $Y_i^n$，$Y_i(\boldsymbol{x})$ 的条件分布是高斯（即 (6.3.3) 的类比）。于是**目标 EI × 各约束满足概率**，可闭式计算。

## Gramacy 增广拉格朗日 EI
Gramacy et al. (2016) 由增广拉格朗日数值优化框架提出约束 EI。目标：在 $k$ 个约束 $y_i(\boldsymbol{x})\le0\ (i=2,\dots,k+1)$ 下最小化 $y_1(\boldsymbol{x})$，通过最小化**增广拉格朗日**
$$
L_A(\boldsymbol{x};\boldsymbol{\lambda},\rho)=y_1(\boldsymbol{x})+\sum_{i=1}^{k}\lambda_i y_{i+1}(\boldsymbol{x})+\frac{1}{2\rho}\sum_{i=1}^{k}\max\{0,y_{i+1}(\boldsymbol{x})\}^2,
$$
$\rho>0$ 为惩罚参数，$\lambda_i\ge0$ 为 Lagrange 乘子。

**迭代**：给定 $(\rho_{j-1},\boldsymbol{\lambda}_{j-1})$，解子问题
$$
\min_{\boldsymbol{x}}\{L_A(\boldsymbol{x};\boldsymbol{\lambda}_{j-1},\rho_{j-1}):\boldsymbol{x}\in\mathcal{X}\} \tag{6.3.10}
$$
得候选解 $\boldsymbol{x}_j$；然后更新
$$
\lambda_i^j=\max\left\{0,\ \lambda_i^{j-1}+\frac{1}{\rho_{j-1}}y_{i+1}(\boldsymbol{x}_j)\right\},\quad
\rho^j=\begin{cases}\rho^{j-1}, & y_{i+1}(\boldsymbol{x}_j)\le0\ \forall i\\\frac{1}{2}\rho^{j-1}, & \text{otherwise}\end{cases},
$$
直至用户停止准则。直接算目标/约束代价过高，故把 EGO 用到 $L_A$ 上。

**对 $L_A$ 的过程表示**：给定 $(\boldsymbol{\lambda},\rho)$，
$$
Y(\boldsymbol{x})=Y_1(\boldsymbol{x})+\sum_{i=1}^{k}\lambda_i Y_{i+1}(\boldsymbol{x})+\frac{1}{2\rho}\sum_{i=1}^{k}\max\{0,Y_{i+1}(\boldsymbol{x})\}^2. \tag{6.3.11}
$$
可用 EI (6.3.7)（以 $Y(\cdot)$ 代替 $Y_1(\cdot)$）。**局限**：因含平方和 max 运算，$L_A(\cdot)$ 非平稳，直接 EGO 需要非平稳 GP。

**推荐做法（Gramacy）**：分别对 $Y_1(\cdot),\dots,Y_{k+1}(\cdot)$ 建独立 GP，基于 (6.3.6) 用蒙特卡洛估计 EI。已算 $n$ 个输入、得 $Y_1^n,\dots,Y_{k+1}^n$ 及对应 $L_A$ 求值 $Y^n$。从联合分布
$$
[Y_1(\boldsymbol{x}),\dots,Y_{k+1}(\boldsymbol{x})\mid \boldsymbol{y}_1^n,\dots,\boldsymbol{y}_{k+1}^n]=\prod_{i=1}^{k+1}[Y_i(\boldsymbol{x})\mid Y_i^n=\boldsymbol{y}_i^n]
$$
（等号因过程相互独立）采 $N$ 个样本 $Y_i^j(\boldsymbol{x})$（$i=1,\dots,k+1;\ j=1,\dots,N$）。令 $y_{\min}^n$ 为增广拉格朗日在 $D_n$ 上的最小观测值，EI 估计为
$$
\hat E[I_n(\boldsymbol{x})\mid \boldsymbol{y}_1^n,\dots,\boldsymbol{y}_{k+1}^n]=\frac1N\sum_{j=1}^{N}\left(y_{\min}^n-Y^j(\boldsymbol{x})\right)I\left\{Y^j(\boldsymbol{x})<y_{\min}^n\right\},
$$
其中 $Y^j(\boldsymbol{x})=Y_1^j(\boldsymbol{x})+\sum_i\lambda_i Y_{i+1}^j(\boldsymbol{x})+\frac1{2\rho}\sum_i\max\{0,Y_{i+1}^j(\boldsymbol{x})\}^2$。用其关于 $\boldsymbol{x}$ 的最大化代替子问题 (6.3.10)。

**扩展到相关约束**：两种方法都可扩展处理相关的约束函数，需有效互相关结构（见 2.5）。代价是建模/计算负担上升，收益是更灵活、找约束最优更高效。

**Williams et al. (2010) 相关目标/约束**：单一约束函数，目标 $\min_{\boldsymbol{x}_c}\mu_1(\boldsymbol{x}_c)$ 且 $\mu_2(\boldsymbol{x}_c)\le B$（$\mu_i$ 为对环境输入分布的均值）。把 $(y_1,y_2)$ 建模为双变量空间自回归过程（(2.5.7)）。改进函数为 (6.3.9) 的修改
$$
I_{c,n}(\boldsymbol{x})=\begin{cases}M_{\min}^{n\star}-M_1(\boldsymbol{x}_c), & M_1(\boldsymbol{x}_c)<M_{\min}^{n\star}\ \text{且}\ M_2^{0.05}(\boldsymbol{x}_c)\le B\\0, & \text{otherwise}\end{cases},
$$
其中 $M_2^{0.05}(\boldsymbol{x}_c)$ 是 $M_2(\boldsymbol{x}_c)$ 分布的 0.05 分位数，$M_{\min}^{n\star}=\min\{M_1(\boldsymbol{x}_{c,i}):1\le i\le n\ \text{且}\ M_2^{0.05}(\boldsymbol{x}_{c,i})\le B\}$——**仅当 $x_{c,i}$ 有强证据满足约束时才计入 $M_1$ 最小值的计算**，以提高找到"约束成立处 $\mu_1$ 全局最小"的几率。算法类似 6.3.4；停止后用 $M_1(\cdot),M_2(\cdot)$ 的 EBLUP 求解约束优化预测约束最优点。可自然扩展到下界或双侧约束。

> **对毕设（约束昂贵黑箱 BO）**：核心思想是"目标 EI × 约束满足概率"，或增广拉格朗日 + 独立 GP 的蒙特卡洛 EI；毕设可直接在此框架上引入多保真。

---

# 6.4.2 轮廓估计（Contour Estimation，p237–238）

Ranjan et al. (2008) 目标：确定 $y(\boldsymbol{x})$ 的轮廓（水平集）
$$
\{\boldsymbol{x}\in\mathcal{X}: y(\boldsymbol{x})=a\}, \tag{6.4.1}
$$
$a$ 为用户给定常数。用 $n$ 个训练输出 $\boldsymbol{y}^n$，设
$$
\hat y(\boldsymbol{x}_0)=\hat\beta+\hat{\boldsymbol{r}}_0^\top\hat R^{-1}\left(\boldsymbol{y}^n-\boldsymbol{1}_n\hat\beta\right) \tag{6.4.2}
$$
为 $y(\boldsymbol{x}_0)$ 的 MLE-EBLUP，预测方差（常数均值、$p=1$ 情形）
$$
s^2(\boldsymbol{x}_0)=\hat\sigma_Z^2\left(1-\hat{\boldsymbol{r}}_0^\top\hat R^{-1}\hat{\boldsymbol{r}}_0+\frac{(1-\boldsymbol{1}_n^\top\hat R^{-1}\hat{\boldsymbol{r}}_0)^2}{\boldsymbol{1}_n^\top\hat R^{-1}\boldsymbol{1}_n}\right),
$$
$\hat\beta$ 为 GLS 估计、$\hat{\boldsymbol{r}}_0$ 为 $x_0$ 与训练点的估计相关向量、$\hat R$ 为 $Y^n$ 相关矩阵估计、$\boldsymbol{1}_n$ 为 $n$ 维全 1 向量、$\hat\sigma_Z^2$ 为 MLE（见 (3.2.7)(3.2.8)）。

**理论改进函数**（Ranjan）：
$$
i(\boldsymbol{x})=\alpha^2 s^2(\boldsymbol{x})-\min\left\{(y(\boldsymbol{x})-a)^2,\ \alpha^2 s^2(\boldsymbol{x})\right\}
=\begin{cases}\alpha^2 s^2(\boldsymbol{x})-(y(\boldsymbol{x})-a)^2, & y(\boldsymbol{x})\in(a-\alpha s(\boldsymbol{x}),\ a+\alpha s(\boldsymbol{x}))\\0, & \text{otherwise}\end{cases}, \tag{6.4.3}
$$
$\alpha>0$ 为调节序贯更新方法的常数。最大可能改进为 $\alpha^2 s^2(\boldsymbol{x})$。**置信区间解释**：当区间 $y(\boldsymbol{x})\pm\alpha s(\boldsymbol{x})$ 包含 $a$ 时发生改进。

**概率型改进**：把 $y(\boldsymbol{x})$ 换成 $Y(\boldsymbol{x})$ 得 $I(\boldsymbol{x})$。利用 $[Y(\boldsymbol{x})\mid Y^n]\approx N(\hat y(\boldsymbol{x}),s^2(\boldsymbol{x}))$，Ranjan 采用 Method 1 期望改进作为质量指标：
$$
E[I(Y(\boldsymbol{x}))\mid Y^n]=\left[(\alpha s(\boldsymbol{x}))^2-(\hat y(\boldsymbol{x})-a)^2\right]\left[\Phi\!\left(\frac{a-\hat y(\boldsymbol{x})}{s(\boldsymbol{x})}+\alpha\right)-\Phi\!\left(\frac{a-\hat y(\boldsymbol{x})}{s(\boldsymbol{x})}-\alpha\right)\right]
$$
$$
+2(\hat y(\boldsymbol{x})-a)s^2(\boldsymbol{x})\left[\varphi\!\left(\frac{a-\hat y(\boldsymbol{x})}{s(\boldsymbol{x})}+\alpha\right)-\varphi\!\left(\frac{a-\hat y(\boldsymbol{x})}{s(\boldsymbol{x})}-\alpha\right)\right]
-\int_{a-\alpha s(\boldsymbol{x})}^{a+\alpha s(\boldsymbol{x})}(y-\hat y(\boldsymbol{x}))^2\,\varphi\!\left(\frac{y-\hat y(\boldsymbol{x})}{s(\boldsymbol{x})}\right)dy, \tag{6.4.4}
$$
$\Phi,\varphi$ 为标准正态分布函数/密度。

**性质**：
- 期望改进 (6.4.4) 同时含**局部搜索**与**全局搜索**成分；
- 常数 $\alpha$ 决定搜索局部 vs 全局程度：**$\alpha$ 越大越全局**；
- 最大改进发生在 $\hat y(\boldsymbol{x}^*)$ 接近 $a$ 且 $s(\boldsymbol{x}^*)$ 大的点 $\boldsymbol{x}^*$；
- 算法序贯加点时：靠近真实轮廓处加点（局部）+ 偶在高不确定区域加点（全局）。

> **对毕设（主动学可行边界）**：轮廓估计即主动学习水平集/约束边界，可作为"约束满足概率"的主动采样实现。

---

# 8.2 KOH 校准模型（Kennedy & O'Hagan，p301–307）★多保真源头

## 8.2.1 引言
描述 **Kennedy & O'Hagan (2001) 校准模型（KOH）**及若干统计推断方法。后续 8.3 采用 Higdon et al. (2004/2008) 的全贝叶斯版本。含一个解析例（说明方法与模型误用的警示）和真实数据例。

## 8.2.2 KOH 模型
**前提**：物理试验与仿真器对该系统的输出都可用。每个输入分两类：
- **控制输入（control inputs）**：研究者可设定；物理试验（完全随机化）的所有输入都是控制变量；
- **校准输入（calibration inputs/参数）**：物理常数（生长率、材料属性等），未知不完全；仿真器需要指定。

**记号（表 8.1）**：$n$ 次物理试验（控制输入 $\boldsymbol{x}_1^p,\dots,\boldsymbol{x}_n^p\in\mathbb{R}^d$，观测 $y^p(\boldsymbol{x}_i^p)$，常称 field data）；$m$ 次仿真器运行，输入 $(\boldsymbol{x}_1^s,\boldsymbol{t}_1),\dots,(\boldsymbol{x}_m^s,\boldsymbol{t}_m)$，$\boldsymbol{x}^s\in\mathbb{R}^d$ 为控制部分、$\boldsymbol{t}\in\mathbb{R}^q$ 为校准部分，输出 $y^s(\boldsymbol{x}^s,\boldsymbol{t})$。$\boldsymbol{x}^p$ 与 $\boldsymbol{x}^s$ 表示同一组控制变量。

**KOH 两个重要特征**：
1. 允许**不完美仿真器**：即使用"真"校准参数，仿真输出也可偏离物理试验均值；
2. 假设仿真器足够准确、专家可对校准参数给出一致于物理系统的先验——即**贝叶斯**，先验基于专家对未知模型参数与未知校准参数的意见。

**两层分层贝叶斯模型**：连接仿真器运行与物理观测，与第 4 章两层模型类似。

**仿真器模型**：$y^s(\boldsymbol{x}^s,\boldsymbol{t})$ 条件地视为来自平稳 GP $Y^s(\boldsymbol{x},\boldsymbol{t})$，均值 $\beta_0$、过程精度 $\lambda_s$、$m\times m$ 相关矩阵 $R_s$，其中高斯相关
$$
R_s\left((\boldsymbol{x}_1,\boldsymbol{t}_1),(\boldsymbol{x}_2,\boldsymbol{t}_2)\right)=\prod_{k=1}^{d}(\rho_k^x)^{(x_{1,k}-x_{2,k})^2}\prod_{\ell=1}^{q}(\rho_\ell^t)^{(t_{1,\ell}-t_{2,\ell})^2} \tag{8.2.1}
$$
$\boldsymbol{\rho}^x=(\rho_1^x,\dots,\rho_d^x)$、$\boldsymbol{\rho}^t=(\rho_1^t,\dots,\rho_q^t)$ 为相关参数。即
$$
[Y^s(\boldsymbol{x}^s,\boldsymbol{t})\mid\beta_0,\lambda_s,\boldsymbol{\rho}^x,\boldsymbol{\rho}^t]\sim GP\!\left(\beta_0,\ \lambda_s,\ (\boldsymbol{\rho}^x,\boldsymbol{\rho}^t)\right). \tag{8.2.2}
$$
可推广到一般回归均值 $E[Y^s\mid\cdot]=\sum_j f_j(\boldsymbol{x}^s,\boldsymbol{t})\beta_j=\boldsymbol{f}^\top(\boldsymbol{x}^s,\boldsymbol{t})\boldsymbol{\beta}$（(8.2.3)，非平稳但无新理论）。实践中常先标准化仿真数据为样本零均值后假设 $Y^s$ 均值为 0；相关函数 (8.2.1) 可用 (2.2.9) 的等价参数化（但并非所有形式都便于设先验）。

**物理观测模型**：$y^p(\boldsymbol{x}_1^p),\dots,y^p(\boldsymbol{x}_n^p)$ 条件地服从回归模型
$$
Y^p(\boldsymbol{x}_i^p)=\mu(\boldsymbol{x}_i^p)+\epsilon(\boldsymbol{x}_i^p),\ i=1,\dots,n, \tag{8.2.4}
$$
给定 $\mu(\boldsymbol{x}^p)$ 与 $\lambda_\epsilon>0$。$\mu(\boldsymbol{x}^p)$ 为物理系统在控制变量 $\boldsymbol{x}^p$ 处的均值响应；$\epsilon(\boldsymbol{x}_1^p),\dots,\epsilon(\boldsymbol{x}_n^p)$ 为独立 $N(0,\sigma_\epsilon^2)$ 测量误差（精度 $\lambda_\epsilon\equiv1/\sigma_\epsilon^2$）。相对通常回归，(8.2.4) 的增强是 $\mu(\boldsymbol{x}^p)$ 的**形式非参数、未指定**。

**偏差（bias/discrepancy）函数**：KOH 通过偏差函数间接给 $\mu(\boldsymbol{x}^p)$ 一个 GP 先验。设 $\boldsymbol{\theta}$ 为物理系统中校准参数的"真值"（有先验分布；某些应用中真值随试验变，取分布均值作 $\boldsymbol{\theta}$）。记 $\Theta$ 为赋有贝叶斯先验或目标分布的随机向量。定义**仿真器偏差**
$$
\delta(\boldsymbol{x}^p)\equiv\mu(\boldsymbol{x}^p)-y^s(\boldsymbol{x}^p,\boldsymbol{\theta}), \tag{8.2.5}
$$
即在真校准参数下运行仿真器的误差。

**完整参数集**：$\Omega=(\boldsymbol{\beta},\boldsymbol{\lambda},\boldsymbol{\rho},\Theta)$，其中 $\boldsymbol{\lambda}=(\lambda_s,\lambda_\epsilon,\lambda_\delta)^\top$、$\boldsymbol{\rho}=(\boldsymbol{\rho}^x,\boldsymbol{\rho}^t,\boldsymbol{\rho}^\delta)$，$\lambda_\delta>0$、$\boldsymbol{\rho}^\delta=(\rho_1^\delta,\dots,\rho_d^\delta)\in(0,1]^d$。

**偏差函数先验**：条件给定 $\Omega$，
$$
[\Delta(\boldsymbol{x})\mid\Omega]\sim GP\!\left(0,\lambda_\delta,\boldsymbol{\rho}^\delta\right),
$$
$\Delta(\boldsymbol{x})$ 有 $n\times n$ 相关矩阵 $R_\delta$，$(i,j)$ 元
$$
R_\delta(\boldsymbol{x}_i^p,\boldsymbol{x}_j^p)=\prod_{\ell=1}^{d}(\rho_\ell^\delta)^{(x_{i,\ell}^p-x_{j,\ell}^p)^2}. \tag{8.2.6}
$$
$\Delta(\boldsymbol{x})$ 条件独立于 $Y^s(\boldsymbol{x},\Theta)$ 与测量误差 $\epsilon(\boldsymbol{x})$。故给定 $\Omega$，$\mu(\boldsymbol{x}^p)=\delta(\boldsymbol{x}^p)+y^s(\boldsymbol{x}^p,\boldsymbol{\theta})$ 是过程
$$
M(\boldsymbol{x}^p)=\Delta(\boldsymbol{x}^p)+Y^s(\boldsymbol{x}^p,\Theta)
$$
的实现（独立 GP 之和仍为 GP）。类似地
$$
Y^p(\boldsymbol{x}^p)=M(\boldsymbol{x}^p)+\epsilon(\boldsymbol{x}^p)=\Delta(\boldsymbol{x}^p)+Y^s(\boldsymbol{x}^p,\Theta)+\epsilon(\boldsymbol{x}^p) \tag{8.2.7}
$$
是 GP 与独立测量误差之和。

> **KOH 模型核心三件套**：仿真器 GP $Y^s$ + 偏差 GP $\Delta$ + 测量误差 $\epsilon$，物理观测 = 三者之和；未知校准参数 $\Theta$ 有先验。这就是**多保真/校准（Co-Kriging 源头）**的统计基础。

## 8.2.2.1 校准参数的不同视角（使用警示）
- 有些仿真器用简化物理/生物模型构建，专家关于 $\boldsymbol{\theta}$ 的知识未必准确描述参数在简化仿真器中的作用；
- 机制型仿真器的未知参数（如材料属性）虽诱人作校准参数，但**难以/无法给先验分布**（至多给范围）；数值调参参数同理；
- 这类情形应定义 $\boldsymbol{\theta}$ 为目标值，即最小化 $y^s(\boldsymbol{x},\boldsymbol{\theta})$ 与 $\mu(\boldsymbol{x})$ 或 $y^p(\boldsymbol{x})$ 差异度量的值（engineering validation）。相关统计文献：Cox et al. (2001)、Tuo & Wu (2016)、Plumlee (2017)；Han et al. (2009b) 处理部分元素有专家先验、其余按度量选取的情形。

### 例 8.1 简单解析例
单控制变量 $x\in[-5,5]$、实值校准参数 $t$。$n=5$ 次物理观测来自 $Y^p(x)=\mu(x)+\epsilon(x)$，$\mu(x)=0.1x^2-x+0.4$，$\epsilon$ i.i.d. $N(0,0.8^2)$（$\lambda_\epsilon=1/0.8^2$）。物理数据（表 8.2）偏离 $\mu(x)$ 明显。$m=15$ 次仿真运行用
$$
y^s(x,t)=t-1.3x,\quad t\in[-5,5],
$$
直线 $y^s$ 在控制范围上可粗略近似二次 $\mu(x)$。该例演示形式化贝叶斯校准流程、说明偏差函数先验参数的影响、以及用错误先验信息时贝叶斯方法的后果。

> **小结（8.2）**：KOH 通过"仿真器 GP + 偏差 GP + 测量噪声 + 校准参数先验"把物理观测与仿真输出联合建模，从而既能校准未知参数、又能量化偏差与不确定性；是多保真代理（Co-Kriging）与基于模型的校准的基石。

---

# 精读范围速查表（对应 README）

| 小节 | 页码 | 核心内容 | 关键公式/结论 |
|---|---|---|---|
| 2.2.1 | 30–34 | GP 定义、均值/协方差、平稳性、回归+GP 模型 | (2.2.3) |
| 2.2.2 | 34–41 | 相关函数性质、Bochner、高斯/幂指数/Matern/三次/Bohman | (2.2.6)–(2.2.14) |
| 3.2 | 68–76 | BLUP & MSPE，条件后验均值/方差 | (3.2.7),(3.2.8) |
| 3.3 | 76–84 | EBLUP：ML/REML/CV/后验众数 | (3.3.2),(3.3.6),(3.3.9) |
| 4.2 | 117–128 | 共轭贝叶斯后验 $[\beta\mid Y_{tr}]$ 与预测分布 | (4.2.1)–(4.2.12) |
| 6.3.4 | 216–225 | EI/EGO、EQI、环境变量均值优化 | (6.3.7) |
| 6.3.5 | 225–229 | 约束全局优化：目标 EI×约束概率、增广拉格朗日 | (6.3.9),蒙特卡洛 EI |
| 6.4.2 | 237–238 | 轮廓/水平集估计，主动学可行边界 | (6.4.3),(6.4.4) |
| 8.2 | 301–307 | KOH 校准模型：仿真 GP+偏差 GP+噪声 | (8.2.1)–(8.2.7) |

# 阅读建议
- **先读 2.2.1→2.2.2** 打基础（GP 是什么、核怎么选）；
- **再读 3.2→3.3**（BLUP 怎么推、超参数怎么估）——这是"手推后验"的核心；
- **然后 4.2**（完整贝叶斯后验，BO 引擎）；
- **6.3.4→6.3.5** 是 BO/约束优化主线（对应毕设主题）；
- **6.4.2** 与 **8.2** 分别对应可行边界主动学与多保真/校准源头。
- 做毕设时建议对照 ED4DSE（已完成的全书学习）与本笔记交叉使用；代码可参考仓库 `markdown/` 计划中的逐节 R 复现与 `代码/`（README 结构，尚未生成）。
