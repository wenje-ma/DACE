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
