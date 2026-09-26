## 2.2 Gaussian Process Models for Real-Valued Output

### 2.2.1 Introduction

> Nonsingular multivariate normal distributions have the advantage that it is easy to compute the conditional distribution of one (or several) of the $Y(\boldsymbol x_i)$ variables given the remaining $Y(\boldsymbol x_j)$.

Let $\boldsymbol Y\sim\mathcal N_p(\boldsymbol\mu,\boldsymbol\Sigma)$, where

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
\boldsymbol Y_1\mid\boldsymbol Y_2&=\boldsymbol y_2\sim\mathcal N(\boldsymbol\mu_{1\mid2},\boldsymbol\Sigma_{1\mid2}),\text{ where}\\
\boldsymbol\mu_{1\mid2}&=\boldsymbol\mu_1+\boldsymbol\Sigma_{12}\boldsymbol\Sigma_{22}^{-1}(\boldsymbol y_2-\boldsymbol\mu_2),\\
\boldsymbol\Sigma_{1\mid2}&=\boldsymbol\Sigma_{11}-\boldsymbol\Sigma_{12}\boldsymbol\Sigma_{22}^{-1}\boldsymbol\Sigma_{21}.
\end{aligned}
$$

Hence, if we have known the distuibution of $\boldsymbol Y_1$, we can easily compute the distribution of $\boldsymbol Y_2$. So as $Y(\boldsymbol x_i)$ and $Y(\boldsymbol x_j)$.

### 2.2.2 Some Correlation Functions for GP Models

> *Example 2.2*. Arguably the simplest application of (2.2.6) is when $d=1$ and $f(w)$ is the uniform density over a symmetric interval which is taken to be $(-1/\xi,+1/\xi)$ for a given $\xi>0$. Thus the spectral density is $$f(w)=\begin{cases}\xi/2,&-1/\xi<w<1/\xi,\\0,&\text{otherwise}.\end{cases}$$ The corresponding correlation function is $$R(h\mid\xi)=\int_{-1/\xi}^{+1\xi}\frac\xi2\cos(hw)\mathrm dw=\begin{cases}\frac{\sin(h/\xi)}{h/\xi},&h\ne0,\\1,&h=0,\end{cases}$$ which has scale parameter $\xi$. Figure 2.5, which plots $R(h\mid\xi=1/4\pi)$ over $[-1,+1]$, shows that this correlation can be used to describe processes that have both positive and negative correlations.

The reason of emphasize "both positive and negative correlations" is that many popular correlation functions usually only have positive correlations. Such as

$$
R(h)=\exp\left(-\frac{|h|^2}{\xi^2}\right)\text{ and }R(h)=\exp\left(-\frac{|h|}{\xi}\right).
$$

Besides, $R(h\mid\xi)$ which have both positive and negative correlations means the plot of $R(h\mid\xi)$ acrossing $y=0$.

> The product of two valid correlation functions, $R_1(\cdot)$ and $R_2(\cdot)$, is a valid correlation function, but their sum is not (notice that $R_1(\boldsymbol0)+R_2(\boldsymbol0)=2$, which is not possible for a correlation function). Note, however, a convex combination of two valid correlation functions is a valid correlation function.

A convex combination means that a combination $R_{\mathrm{mix}}$ which seems like

$$
R_{\mathrm{mix}}=\alpha R_1(h)+(1-\alpha)R_2(h),\text{ where }\alpha\in[0,1].
$$

In the case above, $\alpha R_1(\boldsymbol0)+(1-\alpha)R_2(\boldsymbol0)=1$, which is still a valid correlation function.

> Calculation gives $$\begin{aligned}R(h\mid\xi)&=\int_{-\infty}^{+\infty}\cos(hw)\frac1{\sqrt{2\pi}\sqrt{2\xi}}\exp\{-w^2/(4\xi)\}\mathrm dw\\&=\exp{-\xi h^2},\quad h\in\mathbb R,\end{aligned}\tag{2.2.7}$$ which has rate parameter $\xi$.

> These are $$\exp\{-(h/\theta)^2\}=\rho^{h^2}=\rho_*^{Ch^2}=\exp\{-10^\tau h^2\}\tag{2.2.9}$$ where $C>0$ is a given constant (often $C=4$ in examples) with (valid) values of the parameters being $\theta>0$, $p\in(0,1)$, $p_*\in(0,1)$, and $\tau\in(-\infty,+\infty)$. In words, $\theta$ is the scale parameter version of (2.2.7), $\rho$ is the correlation between two inputs for which $|h|=1$, and $\rho_*$ is the the correlation between two inputs for which $|h|=1/\sqrt C$ (e.g., when $C=4$ and $d=1$, $\rho_*=\mathrm{Cor}[Y(0),Y(1/2)]$). Using simple algebra, the parameter defining any of these correlations can be expressed in terms of any of the other four parameters.

$\xi$ has the same dimension as $h$, and that is why it called the rate parameter, which means the rate of the attenuation of $R(h\mid\xi)$.

While $\theta$ has not the same dimension as $h$, and that is why it call the (general) scale parameter.

So-called simple algebra: let $\rho=\exp\{-1/\theta^2\}$, which means $R(|h|=1)$ (that is why the text claimed that "for which $|h|=1$"), then $\exp\{-(h/\theta)^2\}=\rho^{h^2}$. Similarly, let $\rho_*=\exp\{-1/\theta^2C\}$, which means $R(|h|=1/\sqrt C)$, then $\exp\{-(h/\theta)^2\}=\rho^{Ch^2}$. Besides, when $C=4$ and $d=1$, $\rho_*=\exp\{-(1/2\theta)^2\}=R(|h|=1/2)=R(|0-1/2|)=\mathrm{Cor}[Y(0),Y(1/2)]$.
