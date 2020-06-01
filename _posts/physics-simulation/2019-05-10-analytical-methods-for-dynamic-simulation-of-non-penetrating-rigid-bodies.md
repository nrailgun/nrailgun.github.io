---
layout: post
title: "Analytical Methods for Dynamic Simulation of Non-penetrating Rigid Bodies"
categories: physics-simulation
date: 2019-05-10 00:00:00
---

﻿## Differential Equation Basics

ordinary differential equation (ODE):
$$
\dot x = f(x, t)
$$
where $\dot x$ is the derivative of $x$ with respect $t$.

euler's method:
$$
x(t_0 + h) = x_0 + h \dot x(t_0)
$$

2 problems of euler's method: inaccuracy and instability. runge-kutta's method is better.

## Particle System Dynamics

we define a scalar potential energy function
$$
E = \frac {k_s} 2 C^2
$$
where $C$ is a known behaviour (constraint) function.

since $E = \Delta xf$, the force on particle $x_i$ due to $C$ is
$$
f_i = -\frac {\partial E} {\partial x_i} = -k_s C \frac {\partial C} {\partial x_i}
$$
where $\frac {\partial C} {\partial x_i}$ is the jacobian matrix of $C$ with respect to $x_i$.

## Unconstrainted Rigid Body Dynamics

### rotation matrix and inertia

derivative of rotation matrix
$$
\dot R(t) = \omega(t)^* R(t) = \begin{bmatrix}
\omega(t) \times R(t)_1 & \omega(t) \times R(t)_2 & \omega(t) \times R(t)_3
\end{bmatrix}
$$
where $\omega(t)^* R(t)_i = \omega(t) \times R(t)_i$. but numerical error will build up so that $R(t)$ will no longer be precisely a rotation matrix.

convert body space inertia to world space inertia:
$$
I(t) = R(t) I_b R(t)^T \\
I^{-1}(t) = R \left( t \right) I_b^{-1} R \left( t \right)^T
$$
where $I_b$ is inertia in body space.

### equation of motion

define the state of rigid body as
$$
Y(t) = \begin{bmatrix} x(t) \\ R(t) \\ P(t) \\ L(t) \end{bmatrix}
$$
where $x$ is tranlation, $R$ is rotation matrix, $P$ is linear momentum, and $L$ is augular momentum. define the motion equation of rigid body as
$$
\frac d {dt} Y(t) = \frac d {dt} \begin{bmatrix} x(t) \\ R(t) \\ P(t) \\ L(t) \end{bmatrix}
= \begin{bmatrix} v(t) \\ \omega(t)^* R(t) \\ F(t) \\ \tau(t) \end{bmatrix}
$$
where $F$ is net force applied, $\tau$ is net torque applied.

### quaternion

a rotation of $\theta$ about a axis $u$ is represented by the unit quaternion
$$
q = \left[ \cos\left( \frac \theta 2 \right), \sin\left( \frac \theta 2 \right) u \right]
$$
with derivative
$$
\dot q = \frac {\omega(t) q(t)} 2
$$

check this [post](https://www.3dgep.com/understanding-quaternions/#Quaternion_Dot_Product) to better understand quaternion.

## Nonpenetration Constraints

### Colliding Contact

consider only vertex-face collsion and edge-edge contacts only.

$$
v_r = \hat n(t_0) \cdot \left( \dot p_a \left( t_0 \right) - \dot p_b \left( t_0 \right) \right)
$$

we prostulate a new vector quantity called impulse $J = \Delta t F = j \hat n(t_0)$, which has the units of momentum. applying an impulse produces an instantaneous change $\Delta v = \frac J M$ in the velocity (momentum) of a body. we compute $j$ by using empirical law for collisions.
$$
v_r^+ = -\beta v_r^- \\
\;\\
j = \frac {-\left( 1 + \beta \right) v_r^-}
{
\frac 1 {M_a} + \frac 1 {M_b}
+\hat n(t_0) \cdot \left(I_a^{-1} \left(t_0\right) \left( r_a \times \hat n \left(t_0\right) \right) \right) \times r_a
+\hat n(t_0) \cdot \left(I_b^{-1} \left(t_0\right) \left( r_b \times \hat n \left(t_0\right) \right) \right) \times r_b
}
$$
where $v_r^-$ and $v_r^+$ are relative velocity before and after applying impulse, $0 \le \beta \le 1$.

If we solve collision 1 by 1, the order of contact list may have effects on the simulation. There is a way compute impulses at more than 1 contact point at at time, but it's more complicated, and the idea will be describled below.

### Resting Contact

$$
d = \hat n_i \cdot ( p_a(t) - p_b(t) ) \\
\;\\
\ddot d = \hat n_i (p_a - p_b) + 2 \dot{\hat n_i} \cdot (\dot p_a - \dot p_b)
= \sum_{j=1}^n a_{ij} f_j + b_i
$$
where
$$
b_i =
\frac {F_a} {m_a} + (I_a^{-1} \tau_a) \times r_a + \omega_a \times (\omega_a \times r_a) +
(I_a^{-1} (L_a \times \omega_a)) \times r_a \\
+
\frac {F_b} {m_b} + (I_b^{-1} \tau_b) \times r_b + \omega_b \times (\omega_b \times r_b) +
(I_b^{-1} (L_b \times \omega_b)) \times r_b \\
+
2 \dot {\hat n_i} \cdot (\dot p_a - \dot p_b)
$$
and
$$
a_{ij} = \frac {\hat n_j} {m_a} + (I_a^{-1} (r_a \times \hat n_j)) \times r_a) -
\frac {\hat n_j} {m_b} + (I_b^{-1} (r_b \times \hat n_j)) \times r_b)
$$

then we formed a quadratic program equation system below, which is np-hard.
$$
\ddot d_i \ge 0 \\
f_i \ge 0 \\
f_i \ddot d_i = 0
$$

## FURTHER READINGS

- Physically based Modelling: Principals and Practice
- Analytical methods for dynamic simulation of non-penetrating rigid bodies
- Fast contact force computation for nonpenetrating rigid bodies
