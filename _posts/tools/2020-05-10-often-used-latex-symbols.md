---
layout: post
title: "Often Used LaTeX Symbols"
categories: tools
date: 2020-05-10 00:00:00
---

﻿## Matrix
```tex
\begin{bmatrix}
    a & \cdots & b \\
    \vdots & \ddots & \vdots \\
    c & \cdots & d
\end{bmatrix}
```
$$
\begin{bmatrix}
    a & \cdots & b \\
    \vdots & \ddots & \vdots \\
    c & \cdots & d
\end{bmatrix}
$$

Besides `pmatrix`, `Bmatrix`, and `vmatrix` works as well. Use `smallmatrix` for inline matrix.

## Aligned
```c
\begin{align}
a + b & = c \\
    & = \sin(x)
\end{align}
```
$$
\begin{align}
a + b & = c \\
    & = \sin(x)
\end{align}
$$

## Cases
```tex
f(n) = \begin{cases}
    \frac n 2 & \text{$n$ is even} \\
    \frac {n - 1} 2 & \text{otherwise}
\end{cases}
```
$$
f(n) = \begin{cases}
    \frac n 2 & \text{$n$ is even} \\
    \frac {n - 1} 2 & \text{otherwise}
\end{cases}
$$

## Arrays
```tex
\begin{array}{l|rc}
    n & \text{name} & \text{age} \\
    1 & \text{John} & 18 \\
    1 & \text{A} & 17
\end{array}
```
$$
\begin{array}{l|rc}
    n & \text{name} & \text{age} \\
    1 & \text{John} & 18 \\
    1 & \text{A} & 17
\end{array}
$$

## Sum of equations
```tex
\left\{ \begin{array}{rcl}
    x + y & = & 10 \\
    y & = & 0
\end{array} \right.
```
$$
\left\{ \begin{array}{rcl}
    x + y & = & 10 \\
    y & = & 0
\end{array} \right.
$$

## Iff
```
\begin{array}{cl}
    & A(x) + 1 = e^{-1} \\
    \iff & f_x = 0 \\
    \iff & g_x \ne 0
\end{array}
```
$$
\begin{array}{cl}
    & A(x) + 1 = e^{-1} \\
    \iff & f_x = 0 \\
    \iff & g_x \ne 0
\end{array}
$$

## New command
```c
\newcommand{\aboutthesame}[2]{\mathcal #1 \cong \mathcal #2}
\aboutthesame A B
```
$$
\newcommand{\aboutthesame}[2]{\mathcal #1 \cong \mathcal #2}
\aboutthesame A B
$$

I Love It, :).
