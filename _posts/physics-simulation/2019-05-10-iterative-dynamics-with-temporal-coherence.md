---
layout: post
mathjax: true
title: "Iterative Dynamics with Temporal Coherence"
categories: physics-simulation
date: 2019-05-10 00:00:00
---

﻿## Constrained Dynamics Model

### Kinematics

Position, quaternion, velocity and angular velocity of body:
$$
\dot x = v \\
\dot q = \frac {\omega * q} 2 \\
$$

$6n \times 1$ column vector $V$:
$$
V = \begin{bmatrix} v_1 \\ \omega_1 \\ \vdots \\ v_n \\ \omega_n \end{bmatrix}
$$
where $n$ is the number of rigid bodies in the system.

### Constraints

Single constraint $C_k(x_i, q_i, x_j, q_j) = 0$ are coolected in a $s \times 1$ column vector $C$, where $s$ is the number of constraints. 

By chain rule of differentiation and velocity constraints are guaranteed (assumed) to be linear, we have:
$$
\dot C = JV = 0
$$
where $J$ is the $s \times 6n$ jacobian.

### Constraint Forces

Reaction forces are collected in the $6n \times 1$ column vector
$$
F_c = \begin{bmatrix} f_{c_1} \\ \tau_{c_1} \\ \vdots \\ f_{c_n} \\ \tau_{c_n} \end{bmatrix}
= J^T \lambda
$$
where $\lambda$ is a vector aof $s$ undetermined multipliers.

### Computing the Jacobian

Take distance constraint $C_{\mathrm{dist}} = \frac 1 2 [(p_2 - p_1)^2 - L^2] = 0$ for example, we have
$$
\dot {C_{\mathrm{dist}}} = d \cdot (v_2 + \omega_2 \times r_2 - v_1 - \omega_1 \times r_1)
$$

By applying $A \cdot B \times C = B \cdot C \times A$ the velocities can be isolated.
$$
\dot {C_{\mathrm{dist}}} =
\begin{bmatrix}
	 ( -d^T &
	-(r_1 \times d)^T &
	d^T &
	(r_2 \times d)^T
\end{bmatrix}
 )  \begin{bmatrix} v_1 \\ \omega_1 \\ v_2 \\ \omega_2 \end{bmatrix}
$$

Taking adavantage of the sparsity of $J$, the paper also gives a simple faster algorithm for computing $\dot C = JV$ and $F_c = J^T \lambda$.

### Handling Inequality Constraints

For each constraint a lower and upper bound on $\lambda$ is specified as part of the constraint model.
$$
\lambda_i^- \leq \lambda_i \leq \lambda_i^+
$$

An equality constraint would specify that $(\lambda_i^- \lambda_i^+) = (-\infty, \infty)$.

### Constraint Bias

Constraint forces can be made to do work by adding a bias vector $\zeta$:
$$
JV = \zeta
$$

## Contact Model

### Normal Constraint

$$
C_n = (x_2 + r_2 - x_1 - r_1) \cdot n_1
\\
\dot{C_n} \approx J_n V =
\begin{bmatrix}
	-n^T &
	-(r_1 \times n)^T &
	n^T &
	(r_2 \times d)^T
\end{bmatrix}
\begin{bmatrix} v_1 \\ \omega_1 \\ v_2 \\ \omega_2 \end{bmatrix}
$$

### Handling Penetration

 A Baumgarte scheme is used to push the bodies apart when  they overlap. The velocity constraint is augmented with a feedback term proportional to the penetration depth.
$$
 J_n V = -\beta C_n
$$

Recalling that $\dot{C_n} \approx J_n V$ we have
$$
\dot{C_n} + \beta C_n = 0
$$
where $\beta$ is believed to have a bound of $\beta \leq \frac 1 {\Delta t}$ for smooth decay.

### Friction Constraint

Tangent constraints:
$$
\dot{C_{u_1}} = (v_2 + \omega_2 \times r_2 - v_1 - \omega_1 \times r_1) \cdot u_1 \\
\dot{C_{u_2}} = (v_2 + \omega_2 \times r_2 - v_1 - \omega_1 \times r_1) \cdot u_2
$$
where $u_1$ and $u_2$ are tangents of contact point satisfying $u_1 \times u_2 = n$. The Jacobian is found by inspection
$$
J_u V = \begin{bmatrix}
	-{u_1}^T    &    -(r_1 \times {u_1})^T    &    {u_1}^T    &    (r_2 \times {u_1})^T    \\
	-{u_2}^T    &    -(r_2 \times {u_2})^T    &    {u_2}^T    &    (r_2 \times {u_2})^T
\end{bmatrix}
\begin{bmatrix} v_1 \\ \omega_1 \\ v_2 \\ \omega_2 \end{bmatrix}
$$

Simplified friction model:
$$
-\mu m_c g \leq \lambda_{u_1} \leq \mu m_c g ,\, -\mu m_c g \leq \lambda_{u_2} \leq \mu m_c g
$$

Box stacking friction is unrealistic because lower boxes slide just as easily as upper boxes.

## Equations of Motion

Constrained equations of motion for $n$ bodies:
$$
M \dot V = F_c + F_{\mathrm{ext}} = J^T \lambda + F_{\mathrm{ext}}
\\
\dot C = JV = \zeta
$$

## Time Stepping

We have
$$
M(V^2 - V^1) = \Delta t (J^T \lambda + F_{\mathrm{ext}})
$$
with $V^t$ is the system velocity at time $t$, and $\dot V = \frac{V^2 - V^1}{\Delta t}$. By applying simple manipulations, we have
$$
J M^{-1} J^T \lambda =
\frac{JV^{2}}{\Delta t} - \frac{JV^{1}}{\Delta t} - J M^{-1} F_{\mathrm{ext}}
$$
or
$$
J B \lambda = \eta
$$
where $B = M^{-1} J^T$, and $\eta = \frac{\zeta}{\Delta t} - J \left( \frac{V^{1}}{\Delta t} - M^{-1} F_{\mathrm{ext}} \right)$. Once $\lambda$ is computed, equation $M(V^2 - V^1) = \Delta t (J^T \lambda + F_{\mathrm{ext}})$ is used to compute $V^2$.

## Iterative Solution

### Gauss-Seidel

Approximately solve $Ax=b$ given $x^0$.

- $x = x_0$
- for $j = 1$ to `max_iter` do
	- $\Delta x = \frac {b - Ax} { \mathrm{diag}(A) }$
	- $x := x + \Delta x$
- end for

where $\mathrm{diag}(A)$ is the diagonal vector of matrix $A$. Gauss-Seidel is better if $A$ is singular and sparse.

### Projected Gauss-Seidel

The PGS algorithm extends the basic gauss-seidel algorithm to handle bounds on the unknowns.

Approximately solve $JB\lambda=\eta$ given $\lambda^0$.

- $\lambda = \lambda_0$
- $a = B \lambda$
- $d = JB$
- for $j = 1$ to `max_iter` do
	- $\Delta \lambda = \frac {\eta - Ja} {d}$
	- update $\lambda$ with bound $\lambda = \max(\lambda^-, \min(\lambda^+, \lambda + \Delta \lambda)$
	- $a = B \lambda$
- end for

## Contact Caching

The idea is very simple: $\lambda$ is cached as $\lambda_0$ of next frame. Contact Model

