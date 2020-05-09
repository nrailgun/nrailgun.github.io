# 包围体

几种常见包围体：

- AABB
- Sphere
- OBB
- Sphere Sweep Volume

# 基本图元测试

## 最近点计算

### 点到面的最近点

$Q$ 到平面的投影 $R$ 可以通过如下式子求解，其中 $n$ 是平面法线，$P$ 是平面上任意一点。
$$
t = n \cdot \frac {Q - P} {n \cdot n} \\
R = Q - tn
$$
$t$ 可以理解为点到面的距离。如果平面通过 $n \cdot X =d$ 的形式给出，那么 $t = \frac {n \cdot Q - d} {n \cdot n}$。

### 点到线段的最近点

直线 $AB$ 上 $C$ 的最近点为 $D = A + t(B-A)$。
$$
D = A + t AB ,\; t = \frac{AC \cdot AB}{AB \cdot AB}
$$
距离 $CD \cdot CD$ 可以简化为：
$$
CD \cdot CD = AC \cdot AC - \frac{(AC \cdot AB)^2}{AB \cdot AB}
$$

### 点到 AABB 的最近点

$P$ 在 AABB $(c, h)$ 上的最近点 $Q$ 可以通过如下式子计算。
$$
Q_i = \min\left( \max \left(P_i, \left( c-h \right)_i \right), \left( c+h \right)_i \right), i \in [0, 1, 2]
$$

### 点到 OBB 的最近点

设定 $B$ 为中心点为 $C$ 的 OBB，OBB 中的点表示为 $S = C + au_0 + bu_1 + cu_2$。其中 ，$u_i, i \in [0, 1, 2]$ 分别为 $B$ 的 x，y，z 轴。要寻找点到 OBB 的最近点，可以先将点转换到 OBB 的局部坐标系中，将 OBB 作为 AABB 求解。3D 空间中的矩形（平面多边形）实际上是特殊的 $z = 0$ 的 OBB，计算方法是一样的。

### 点到三角形的最近点

**TODO**

### 点到四面体的最近点

可以遍历四面体 $ABCD$ 4 个面并检查距离面（三角形）的距离，并取最小值。

判断点 P 是否位于 $A$ 的 voronoi 区域：
$$
(P-A) \cdot (B-A) \le 0 \\
(P-A) \cdot (C-A) \le 0 \\
(P-A) \cdot (D-A) \le 0 \\
$$
判断点 $P$ 是否位于 $AB$ 的 voronoi 区域：
$$
(P-A) \cdot (B-A) \ge 0 \\
(P-B) \cdot (A-B) \ge 0 \\
(P-A) \cdot((B-A) \times n_{ABC}) \ge 0, n_{ABC} = (B-A)\times(C-A) \\
(P-A) \cdot (n_{ADB} \times (B-A)) \ge 0, n_{ADB} = (D-A)\times(B-A)
$$

### 点到凸多面体的最近点

对每个面进行检测虽然容易实现但是并不高效，层次结构和 GJK 算法可能更好。

### 两条直线间的最近点

对于包含两个顶点 $P_i, Q_i$ 的两条直线，相交点为 ：
$$
L_1(s) = P_1 + sd_1, d_1 = Q_1 - P_1 \\
L_2(t) = P_2 + td_2, d_2 = Q_2 - P_2
$$
线段 $L$ 垂直于线段 $P_iQ_i$，可得：
$$
s = \frac{bf-ce}{d} \\
t = \frac{af - bc}{d}
$$
其中 $r = P_1 - P_2$，$a = d_1 \cdot d_1$，$b = d_1 \cdot d_2$，$c = d_1 \cdot r$，$e = d_2 \cdot d_2$，$f = d_2 \cdot r$，$d = ae - b^2$。当 $d=0$，说明直线平行。注意：实际计算中，选取不合适的 $P_i, Q_i$ 会影响计算误差。

### 两条线段上的最近点

将线段延展为直线，如果最近点在线段上，那么可以直接应用。如果最近点在延长线上，可以截取至线段的最近端点处，并计算端点到另一条线段的距离。如果两点都位于延长线上，那么需要计算两次。

给定 $L_2$ 一点 $P_2 + td_2$，那么 $L_1$ 上最近点 $L_1(s)$ 的 $s$ 为：
$$
s = \frac{(P_2 + td_2 - P_1) \cdot d_1}{d_1 \cdot d_1}
$$
类似地，给定直线 $L_1$ 上一点 $P_1 + sd_1$，直线 $L_2$ 上最近点的 $s$ 为：
$$
t = \frac{(P_1 + td_1 - P_2) \cdot d_2}{d_2 \cdot d_2}
$$
对于 2D 平面上的两条线段，可以通过计算符号面积（Signed Area） $SA$ 检查 $CD$ 两点是否位于 $AB$ 的两侧，$AB$ 是否位于 $CD$ 两侧。注意符号面积具有 $SA(A, B, D) + SA(A,B,C) = SA(C,D,A) + SA(C,D,B)$ 的性质。
$$
t = SA(C, D, A) / (SA(C, D, A) - SA(C, D, B))
$$

### 线段和三角形最近点

 线段与三角形最近点计算涉及以下情况：

- 线段 $PQ$ 与三角形边 $AB$
- 线段 $PQ$ 与三角形边 $BC$
- 线段 $PQ$ 与三角形边 $CA$
- 线段端点 $P$ 与三角形平面（如果 $P$ 投影位于三角形 $ABC$ 内）
- 线段端点 $Q$ 与三角形平面（如果 $Q$ 投影位于三角形 $ABC$ 内）

以上述情况具有最小距离的点作为结果。

### 两个三角形之间最近点计算

对其中一个三角形的三条边，逐一进行线段-三角形最近点计算。

## 图元测试

与计算距离相比，图元测试应用并不广泛。一般只返回图元是否相交，而不包含相交位置以及方式。

### 分离轴测试

