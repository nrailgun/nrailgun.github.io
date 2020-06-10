---
layout: post
title: "C++ 奇怪角落复习笔记"
categories: uncategorized
date: 2020-06-10 00:00:00
---

---

负数的 div 和 mod 的符号曾经没有明确定义，C++11 做出了明确要求。

> except for the obscure case where $-m$ overflows, $(-m)/n$ and $m/(-n)$ are always equal to $-(m/n)$, $m\%(-n)$ is equal to
> $m\%n$, and $(-m)\%n$ is equal to $-(m\%n)$.

---

`*p++` 等价于 `*(p++)`，迷惑。

---

Unsigned type 的 right shift 补位是 implementation depending。

---

Integral promotion: `bool`, `char`, `signed char`, `unsigned char`, `short`, and `unsigned short` are promoted to `int` if all possible values of that type fit in an int. Otherwise, the value is promoted to `unsigned int`. The larger char types (`wchar_t`, `char16_t`, and `char32_t`) are promoted to the smallest type of `int`, `unsigned int`, `long`, `unsigned long`, `long long`, or `unsigned long long` in which all possible values of that character type fit.

---

If any operand is an unsigned type, the type to which the operands are converted depends on the relative sizes of the integral types on the
machine.

如果整型提升得到了相同类型，那么无需继续转型。如果符号不同：

1. 如果无符号类型更大，那么有符号转无符号，
2. 如果有符号类型更大，
   1. 可以容纳所有无符号类型值，那么无符号转有符号（如果 long 大于 unsigned int，那么 unsigned int 转 long）。
   2. 无法容纳所有无符号类型值，那么有符号转无符号（如果 long 小于等于 unsigned int，那么 long 转 unsigned int）。

讲道理，显式转型不好吗？不要没事找事。

---

