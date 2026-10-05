## 2.2 Gaussian Process Models for Real-Valued Output

### 2.2.1 Introduction

> Nonsingular multivariate normal distributions have the advantage that it is easy to compute the conditional distribution of one (or several) of the $Y\left(\boldsymbol x_i\right)$ variables given the remaining $Y\left(\boldsymbol x_j\right)$.

Let $\boldsymbol Y\sim\mathcal N_p\left(\boldsymbol\mu,\boldsymbol\Sigma\right)$, where

$$
\boldsymbol Y=\begin{bmatrix}\boldsymbol Y_1\\\boldsymbol Y_2\end{bmatrix},\quad
\boldsymbol\mu=\begin{bmatrix}\boldsymbol\mu_1\\\boldsymbol\mu_2\end{bmatrix},\quad
\boldsymbol\Sigma=\begin{bmatrix}\boldsymbol\Sigma_{11}&\boldsymbol\Sigma_{12}\\
\boldsymbol\Sigma_{21}&\boldsymbol\Sigma_{22}\end{bmatrix}.
$$

Let $\boldsymbol\Sigma_{22}$ be the covariance matrix of $\boldsymbol Y_2$, and it is nonsingular.

Let $\boldsymbol Y_2=\boldsymbol y_2$, the condictional distribution of $\boldsymbol Y_1$ is still a multivariate normal distribution:

$$
\begin{aligned}
\boldsymbol Y_1\mid\boldsymbol Y_2&=\boldsymbol y_2\sim\mathcal N\left(\boldsymbol\mu_{1\mid2},\boldsymbol\Sigma_{1\mid2}\right),\text{ where}\\
\boldsymbol\mu_{1\mid2}&=\boldsymbol\mu_1+\boldsymbol\Sigma_{12}\boldsymbol\Sigma_{22}^{-1}\left(\boldsymbol y_2-\boldsymbol\mu_2\right),\\
\boldsymbol\Sigma_{1\mid2}&=\boldsymbol\Sigma_{11}-\boldsymbol\Sigma_{12}\boldsymbol\Sigma_{22}^{-1}\boldsymbol\Sigma_{21}.
\end{aligned}
$$

Hence, if we have known the distuibution of $\boldsymbol Y_1$, we can easily compute the distribution of $\boldsymbol Y_2$. So as $Y\left(\boldsymbol x_i\right)$ and $Y\left(\boldsymbol x_j\right)$.

### 2.2.2 Some Correlation Functions for GP Models

> *Example 2.2*. Arguably the simplest application of (2.2.6) is when $d=1$ and $f\left(w\right)$ is the uniform density over a symmetric interval which is taken to be $\left(-1/\xi,+1/\xi\right)$ for a given $\xi>0$. Thus the spectral density is $$f\left(w\right)=\begin{cases}\xi/2,&-1/\xi<w<1/\xi,\\0,&\text{otherwise}.\end{cases}$$ The corresponding correlation function is $$R\left(h\mid\xi\right)=\int_{-1/\xi}^{+1\xi}\frac\xi2\cos\left(hw\right)\mathrm dw=\begin{cases}\frac{\sin\left(h/\xi\right)}{h/\xi},&h\ne0,\\1,&h=0,\end{cases}$$ which has scale parameter $\xi$. Figure 2.5, which plots $R\left(h\mid\xi=1/4\pi\right)$ over $\left[-1,+1\right]$, shows that this correlation can be used to describe processes that have both positive and negative correlations.

The reason of emphasize "both positive and negative correlations" is that many popular correlation functions usually only have positive correlations. Such as

$$
R\left(h\right)=\exp\left(-\frac{\left|h\right|^2}{\xi^2}\right)\text{ and }R\left(h\right)=\exp\left(-\frac{\left|h\right|}{\xi}\right).
$$

Besides, $R\left(h\mid\xi\right)$ which have both positive and negative correlations means the plot of $R\left(h\mid\xi\right)$ acrossing $y=0$.

> The product of two valid correlation functions, $R_1\left(\cdot\right)$ and $R_2\left(\cdot\right)$, is a valid correlation function, but their sum is not (notice that $R_1\left(\boldsymbol0\right)+R_2\left(\boldsymbol0\right)=2$, which is not possible for a correlation function). Note, however, a convex combination of two valid correlation functions is a valid correlation function.

A convex combination means that a combination $R_{\mathrm{mix}}$ which seems like

$$
R_{\mathrm{mix}}=\alpha R_1\left(h\right)+\left(1-\alpha\right)R_2\left(h\right),\text{ where }\alpha\in\left[0,1\right].
$$

In the case above, $\alpha R_1\left(\boldsymbol0\right)+\left(1-\alpha\right)R_2\left(\boldsymbol0\right)=1$, which is still a valid correlation function.

> Calculation gives $$\begin{aligned}R\left(h\mid\xi\right)&=\int_{-\infty}^{+\infty}\cos\left(hw\right)\frac1{\sqrt{2\pi}\sqrt{2\xi}}\exp\left\{-w^2/\left(4\xi\right)\right\}\mathrm dw\\&=\exp{-\xi h^2},\quad h\in\mathbb R,\end{aligned}\tag{2.2.7}$$ which has rate parameter $\xi$.

> These are $$\exp\left\{-\left(h/\theta\right)^2\right\}=\rho^{h^2}=\rho_*^{Ch^2}=\exp\left\{-10^\tau h^2\right\}\tag{2.2.9}$$ where $C>0$ is a given constant (often $C=4$ in examples) with (valid) values of the parameters being $\theta>0$, $p\in\left(0,1\right)$, $p_*\in\left(0,1\right)$, and $\tau\in\left(-\infty,+\infty\right)$. In words, $\theta$ is the scale parameter version of (2.2.7), $\rho$ is the correlation between two inputs for which $\left|h\right|=1$, and $\rho_*$ is the the correlation between two inputs for which $\left|h\right|=1/\sqrt C$ (e.g., when $C=4$ and $d=1$, $\rho_*=\mathrm{Cor}\left[Y\left(0\right),Y\left(1/2\right)\right]$). Using simple algebra, the parameter defining any of these correlations can be expressed in terms of any of the other four parameters.

$\xi$ has the same dimension as $h$, and that is why it called the rate parameter, which means the rate of the attenuation of $R\left(h\mid\xi\right)$.

While $\theta$ has not the same dimension as $h$, and that is why it call the (general) scale parameter.

So-called simple algebra: let $\rho=\exp\left\{-1/\theta^2\right\}$, which means $R\left(\left|h\right|=1\right)$ (that is why the text claimed that "for which $\left|h\right|=1$"), then $\exp\left\{-\left(h/\theta\right)^2\right\}=\rho^{h^2}$. Similarly, let $\rho_*=\exp\left\{-1/\theta^2C\right\}$, which means $R\left(\left|h\right|=1/\sqrt C\right)$, then $\exp\left\{-\left(h/\theta\right)^2\right\}=\rho^{Ch^2}$. Besides, when $C=4$ and $d=1$, $\rho_*=\exp\left\{-\left(1/2\theta\right)^2\right\}=R\left(\left|h\right|=1/2\right)=R\left(\left|0-1/2\right|\right)=\mathrm{Cor}\left[Y\left(0\right),Y\left(1/2\right)\right]$.

## 3.2 BLUP and Minimum MSPE Predictors

### 3.2.2 Best MSPE Predictors

> Let $\widehat Y_0=\mathrm E\left[Y_0\mid\boldsymbol Y_\mathrm{tr}\right]$ and $Y_0^*=Y_0^*\left(\boldsymbol Y_\mathrm{tr}\right)$, then $$\begin{aligned}&\quad\;\mathrm E\left[\left(Y_0^*-\widehat Y_0\right)\left(\widehat Y_0-Y_0\right)\right]\\&=\mathrm E\left[\left(Y_0^*-\widehat Y_0\right)\mathrm E\left[\left(\widehat Y_0-Y_0\right)\mid\boldsymbol Y_\mathrm{tr}\right]\right]\\&=\mathrm E\left[\left(Y_0^*-\widehat Y_0\right)\left(\widehat Y_0-\mathrm E\left[Y_0\mid\boldsymbol Y_\mathrm{tr}\right]\right)\right]\\&=\mathrm E\left[\left(Y_0^*-\widehat Y_0\right)\times0\right]=0.\end{aligned}$$

The second line holds because the following properties:

**The law of total expectation**:

$$
\mathrm E\left[X\right]=\mathrm E\left[\mathrm E\left[X\mid\boldsymbol Y_\mathrm{tr}\right]\right];
$$

**The properity of conditional expection**: If random variable $Z$ is measured with respect to $\mathcal G$, then

$$
\mathrm E\left[ZW\mid\mathcal G\right]=Z\mathrm E\left[W\mid\mathcal G\right].
$$

Hence, we have

$$
\begin{aligned}
&\quad\;\mathrm E\left[\left(Y_0^*-\widehat Y_0\right)\left(\widehat Y_0-Y_0\right)\right]\\
&=\mathrm E\left[\mathrm E\left[\left(Y_0^*-\widehat Y_0\right)\left(\widehat Y_0-Y_0\right)\mid\boldsymbol Y_\mathrm{tr}\right]\right]\\
&=\mathrm E\left[\left(Y_0^*-\widehat Y_0\right)\mathrm E\left[\left(\widehat Y_0-Y_0\right)\mid\boldsymbol Y_\mathrm{tr}\right]\right].
\end{aligned}
$$

## 3.3 Empirical Best Linear Unbiased Prediction of Univariate Simulator Output

### 3.3.1 Introduction

> All except the "crossvalidation" estimator of $\boldsymbol\kappa$ require that the training data satisfy $$\left[\boldsymbol Y^\mathrm{tr}|\boldsymbol\beta,\sigma_Z^2,\boldsymbol\kappa\right]\sim\mathcal N_{n_s}\left(\boldsymbol F_\mathrm{tr}\boldsymbol\beta,\sigma_Z^2\boldsymbol R_\mathrm{tr}\right).$$

**Why should we except the "crossvalidation"?**

The essence of MLE, REML is to maximize the log-likelihood of the multivariate normal distribution, while crossvalidation is not. The reason is that the criterion of crossvalidation is **prediction loss criterion**, not probability density or likelihood.

### 6.3.4 Expected Improvement Algorithms for Optimization
