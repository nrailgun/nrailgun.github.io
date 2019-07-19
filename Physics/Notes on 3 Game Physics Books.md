本文是 *Physics for Game Developer**Game Physics Engine Development*，与 *Game Physics 2nd edition* by *David Eberly* 的读书笔记。部分为 *Physics for Game Developer* 的简单笔记，部分为 *Game Physics Engine Development* 的代码 Cyclone 的剖析，最后是 *Game Physics 2nd rly* 的摘录。

# Physics for Game Developer

## 第1章 基本概念

### 质心与转动惯量

质心（center of mass）：
$$
C_g = \frac
{ \sum \left( C_g^{(i)} m_i \right) }
{ \sum m_i }
$$

转动惯量（Moment of Inertia）极为难算，实际可以使用基本形状逼近。基本形状对于自身中心轴（通过物体质心）的转动惯量可以在高校教科书找到。

$$
I = \int r^2 \; dm
$$

平行轴定理：$I = I_o + md^2$，如果两个坐标系坐标轴平行。

### 牛顿第二定律

牛顿运动3定律：
1. 惯性；
2. $F = ma$；
3. 反作用力。

动量（momentum）$G = mv$。

力矩：支点与力作用方向相垂直的距离的乘积就称为力矩（例如杠杆）。标量。

扭矩、转矩：转动的力矩。若将转轴中心看成支点，在转动的物体圆周上的作用力和转轴中心与作用力方向垂直的距离的乘积就称为转矩。

对于物体质心，力矩如下，$r$ 是 F 到物体质心的垂直距离向量。
$$
M_{cg} = r \times F
$$

### 惯性张量

$$
r = xi + yj + zk
$$
$$
\omega = \omega_x i + \omega_y j + \omega_z k
$$

角动量：
$$
H_{cg} = \int \left(r \times \left(r \times \omega \right) \right) dm = I \omega
$$

中文书此处排版有错误，好似标量，其实惯性张量 $I$ 应为矩阵。
$$
I = \begin{bmatrix}
+I_{xx} & -I_{xy} & -I_{xz} \\
-I_{yx} & +I_{yy} & -I_{yz} \\
-I_{zx} & -I_{zy} & +I_{zz} \\
\end{bmatrix}
$$

转动惯量：
$$
I_{xx} = \int{y^2 + z^2}{dm},\;
I_{yy} = \int{x^2 + z^2}{dm},\;
I_{zz} = \int{x^2 + y^2}{dm}
$$
惯性积：
$$
I_{xy} = I_{yx} = \int (xy) dm,\;
I_{xz} = I_{zx} = \int (xz) dm,\;
I_{yz} = I_{zy} = \int (yz) dm
$$

惯性积也满足平行轴定理：
$$
I_{xy} = I_{o(xy)} + m d_x d_y
$$


## 第2章 运动学

在 3d 空间上（右手定则）：

$$
v = \omega \times r
$$
$$
H = r \times m (\omega \times r)
$$
$$
a_t = \alpha \times r
$$
$$
a_n = \omega \times \left( \omega \times r \right)
$$


## 第3章 作用力

力产生线性加速度，而力矩产生旋转加速度，力矩是 $N-m$。

力矩：
$$
M = r \times F
$$
r 是力 F 的 contact 点到质心的距离。


## 第4章 动力学

$$
M = I \alpha = \frac {\Delta H} {\Delta t}
$$
$$ 是力矩总和，I 是转动惯量，a 是角加速度，H 是角动量，t 是时间。


## 第5章 碰撞

### 冲击

Linear impulse
$$
\int_{t-}^{t+} F \; dt = m(v_+ - v_-)
$$

Angular impulse
$$
\int_{t-}^{t+} M \; dt = I(\omega_+ - \omega_-)
$$

线性动能：
$$
{KE}_{\mathrm{linear}} = \frac {m v^2} 2
$$

角动能：
$$
{KE}_{\mathrm{angular}} = \frac {I \omega^2} 2
$$

撞击的作用线垂直于碰撞接触面。
- 物体速度沿着作用线，称为“直接碰撞（direct impact）”。
- 物体速度不沿着作用线，称为“倾斜碰撞（oblique impact）”。
- 作用线通过质心，称为“中心碰撞（central impact）”。

此处翻译版少了 $|v|$ 符号。

### 线性冲击

由：
$$
|J| = m_1 (|v_{1+}| - |v_{1-}|)
$$
$$
|-J| = m_2 (|v_{2+}| - |v_{2-}|)
$$
$$
e = -\frac
{ (|v_{1+}| - |v_{2+}|) }
{ (|v_{1-}| - |v_{2-}|) }
$$

得：
$$
|J| = -\frac
{ (|v_1| - |v_2|) (e + 1) }
{ \frac 1 {m_1} + \frac 1 {m_2} }
$$
$$
v_{1+} = v_{1-} + \frac { |J| n } {m_1}
$$
$$
v_{2+} = v_{2-} - \frac { |J| n } {m_2}
$$

### 角冲击

定义：
$$
v_p = v_g + ( \omega \times r )
$$

由：

$$
v_{1g+} + ( \omega_{1+} \times r_1 )=\frac J {m_1} + v_{1g-} + (\omega_{1-} \times r_1)
$$

$$v_{2g+} + ( \omega_{2+} \times r_2 )=\frac {-J} {m_2} + v_{2g-} + (\omega_{2-} \times r_2)$$

$$(r_1 \times J) = I_1 (w_{1+} - w_{1-})$$

$$(r_2 \times -J) = I_2 (w_{2+} - w_{2-})$$

得：
$$
|J| = -\frac
{ \left( v_2 - v_2 \right) n }
{
    \frac 1 {m_1} + \frac 1 {m_2}
    + n \left( \frac {r_1 \times n} {I_1} \right) \times r_1
    + n \left( \frac {r_2 \times n} {I_2} \right) \times r_2
}
$$
$$
v_{1+} = v_{1-} + \frac {|J|n} {m_1}
$$
$$
v_{2+} = v_{2-} - \frac { |J| n } {m_2}
$$
$$
\omega_{1+} = \omega_{1-} + \frac {r_1 \times |J| n} {I_1}
$$
$$
\omega_{2+} = \omega_{2-} - \frac {r_2 \times |J| n} {I_2}
$$


## 第7章 实时模拟

改良欧拉法：
$$
k_1 = (\Delta t) \, y'(t, y)
$$
$$
k_2 = (\Delta t) \, y'(t + \Delta t, y + k_1)
$$
$$
y(t + \Delta t) = y(t) + \frac {k_1 + k_2} 2
$$


## 第8-9章

给出了简化的碰撞例子。


## 第11章 3D刚体仿真中的转动

quaternion
$$
\mathrm q = \left[ \cos \left( \frac \theta 2 \right), \sin \left( \frac \theta 2 \right) u \right]
$$

grassmann product of quaternions
$$
\rm q \rm p = \left[
n_q n_p - v_q \cdot v_p,
n_q v_p + n_p v_q + (v_q \times v_p)
\right]
$$

rotation
$$
\rm v' = rot(q, v) = q v q^{*}, \; q^* = \left[ n, -v \right]
$$

integration
$$
\rm \frac {dq} {dt} = \frac 1 2 \omega q
$$

[此处](https://www.3dgep.com/understanding-quaternions/#Quaternion_Dot_Product)给出了更好的 quaternion 的解释，强烈建议读一下。


## 第12章

给出了简化的 quaternion 旋转例子。


## 第13章

通过模拟弹簧来实现**连接**，模拟锁链与绳子。通过在恰当的位置添加弹簧，可以模拟转动**约束**。

弹簧，r 是弹簧静止长度，L 是拉伸长度。
$$
F_s = k_s (r - L)
$$

阻尼器，$v_r$ 是相对速度。
$$
F_d = -k_d v_r
$$


## 第15-19章

具体物理模型，具体问题具体探讨，略过。19 章讨论碰撞反馈，值得看一下。


# Game Physics Engine Development


## 代码示例：Cyclone

Cyclone 是《游戏物理引擎开发》一书的源代码示例，本身并非一个强健的引擎，但是非常简单，有很强的参考意义。游戏物理引擎不是物理模拟器，所以有一些物理计算，看上去无法理解，其实并非现实物理规律而是伪造的障眼法。

本节摘取 bigballistic demo 分析代码。此处不会太过于介绍碰撞检测算法，因为该书并不深入讨论碰撞检测，只是给出了一些简单的示例。详细碰撞检测算
法应参考《实时碰撞检测》。

### update

- app ctor
    - new rigid bodies, collision detector, collision resolver
    - filling values, nothing new.

- `update()`
    - `updateObjects()`
    - `generateContacts()`
    - `resolver.resolveContacts()`

### integrate

- `updateObjects()`
    - `primitive.body.integrate()`
        - update velocity and rotation
        - drag
        - update position and orientation
        - `calculateDerivedData()`
            - normalize orientation
            - update transforma matrix for body
            - update inertia in world coord
        - clear force and torque
    - `primitive.calculateInternals()`
        - set transform matrix for primitive

Cyclone 的重力是直接设计成加速度的（`body.acceleration`），然后加上 force / torque 算出 `body.lastFrameAcceleration` 才是合力下加速度，这两者的区别在命名上比较难以凸显。

### generate contacts

- `generateContacts()`
    - create collision plane (not a rigid body / primitive)
    - collision data reset
        - empty collisions
        - fill coefficients
    - for each box
        - return no memory for collision
        - `CollisionDetector::boxAndHalfSpace(box, plane)`
        - for each ammo
            - `CollisionDetector::boxAndSphere(box, shot)`

书中并没有使用 GJK 或是类似算法，而是直接自己编写了 non-general 的算法，仅用于示例。

- `CollisionDetector::boxAndHalfSpace()`
    - early check `IntersectionTest::boxAndHalfSpace()`
    - for each box vertex `vertexPos`
        - check if vertex collides plane
        - new `Contact`
            - contact point
            - contact normal
            - contact penetration
            - contact bodies

- `CollisionDetector::boxAndSphere()`
    - similar to `CollisionDetector::boxAndHalfSpace()`
    - early check if intersect
    - check if closest point of sphere intersect
    - new `Contact`
        - contact point
        - contact normal
        - contact penetration
        - contact bodies

### resolve contacts

- `ContactResolver::resolveContacts`
    - `PrepareContacts()`
    - `adjustPositions()`
    - `adjustVelocities()`

- `PrepareContacts()`
    - for each contact
        - `contact.calculateInternals()`
            - `contact.calculateContactBasis()` form contact coord
            - set body `relativeContactPosition`
            - `contactVelocity` in contact coord: $v + \omega \times r + a \Delta t$, ignoring x component.
            - `desiredDeltaVelocity`: $r a \Delta t$ x component, r for restitution.

在碰撞反馈之前先处理重叠（overlap / penetration）的问题，否则会有“失真感”。一般在质心相对方向上互相避让，这样比较失真，所以旋转刚体做障眼法。

此处 $a * n + m^{-1}$ 粗看很费解，考虑 $|F|t \, (a * n)$ 得到速率，而 $|F|t \, m^{-1}$ 也得到速率。

所谓的 angular move direction 并非很准确的说法，简单而言方向与角变化（`angularChange`）相同，但是模不同。再次注意，此处也不是物理规律，因为真实世界并没有所谓“碰撞后瞬间调整位置”，只有形变/弹力/摩擦力。所以不需要太纠结其物理意义。角的大小需要让 contact normal 方向上的投影大小正好即可。

- `adjustPositions()`
    - repeat for `positionIterations` times
    - find contact with biggest penetration
    - wake up bodies
    - `linearChange, angularChange = contact.applyPositionChange()`
        - for 2 bodies
            - get body inertia in world coord
            - `totalInertia =` $\left( I^{-1} (r \times F) \times r * n \right) + m^{-1} = a * n + m^{-1}$
        - for 2 bodies
            - split penetration into scalar `linearMove` and `angularMove` (with `totalInertia`).
            - limit angular move to an upper bound if too big.
            - angular move "direction" $r \times n$
            - linear move along `contactNormal` for `linearMove` unit
            - set pos and orientation
            - `body.calculateDerivedData()`
    - for each `contact`
        - for 2 `contact.body`s
            - for 2 `body`s
                - `deltaPos =` $x = v \Delta t = \omega \Delta t \times r$
                - penetration += `deltaPos` projection on contact normal

在解除了 overlap 之后，计算新的 velocity。

- `adjustVelocities()`
    - repeat for `velocityIteration` times
    - find contact with biggest closing velocity (`desiredVelocity`)
    - wake up bodies
    - `contact.applyVelocityChange()`
        - calculate impulse contacr coord
        - calculate velocity / angular velocity change
        - update velocity / angular velocity
    - for each `contact`
        - for 2 `contact.body`s
            - for 2 `body`s
                - `deltaVel =` $\Delta v = \alpha \Delta t \times r$
                - `contactVelocity` += `deltaVel` in contact coord
                - `contact.calculateDesiredDeltaVelocity`

`desiredVelocity = contact.calculateDesiredDeltaVelocity` 计算反弹后理应的闭合速度变化量，通过它寻找下一个反弹速度最大的刚体，并调整速度，本身不用于刚体运动。


# Game Physics

This article is the note I took while reading the book *Game Physics* by *David Eberly*.

## APPENDIX A

### Linear Systems

to solve

$$
\begin{bmatrix} \epsilon & 1 \\ 1 & 2 \end{bmatrix} x = \begin{bmatrix} 1 \\ -1 \end{bmatrix}
$$

by gaussian elimination, you might produce

$$
\begin{bmatrix} 1 & \frac 1 \epsilon \\ 0 & 2 - \frac 1 \epsilon \end{bmatrix} x = \begin{bmatrix} \frac 1 \epsilon \\ -1 - \frac 1 \epsilon \end{bmatrix}
$$

if $\epsilon$ is nearly $0$, $\frac 1 \epsilon$ is very large, which is error proning, due to cpu floating arithmetic error (***TODO***: more details). the solution is searching pivot with greatest magnitude.

### Matrices

construction of inverses: row reducing $\left[ A | I \right]$ to $\left[ I | A^{-1} \right]$.

lu decomposition: $A = LU' = LDU$.
1. if $A$ is invertible, then its LDU decomposition is unique,
2. if $A$ is symmetric, then $U$ in LDU must satisfy $U = L^T$.

### Vectors Spaces

span of $|A|$:

$$
\mathrm{Span}|A| = \left\{ \sum_{k=1}^{|A|} c_kx_k: c_k \in \mathbb{R}, x_k \in A \right\}
$$

$x \in \mathrm{Span}|A|$ has unique representation $x = \sum a_i x_i$, values of $a_i$ are called coefficients of $x$  with respect to $A$.

$$
\mathrm{Rank}(A) = \mathrm{Rank}(A^T)
$$

$$
\mathrm{dim}( \mathbb R ^n ) = n = \mathrm{cardinality}
$$

products:
- dot product
- cross product
- triple scalar product
- triple vector product

orthogonal complement

$$
U^\perp = \left\{ x \in \mathbb R^n: x \cdot y = 0 \; \forall y \in U \right\}
$$

kernel of $n \times m$ matrix $A$

$$
\mathrm{Kernel}(A) = \left\{ x \in \mathbb R^m: Ax = 0 \right\}
$$

$$
\mathrm{dim} \left( \mathrm{Kernel} \left( A \right) \right) = m - \mathrm{Rank}(A)
$$

range of $A = \left[ a_1 | \dots | a_m \right]$

$$
\mathrm{Range}(A)
= \mathrm{Span} \left[ a_1 | \dots | a_m \right]
= \mathrm{Span} \left[ a_{k_1} | \dots | a_{k_r} \right]
= \mathrm{Range}(\tilde A) 
$$

$$
\mathrm{dim} \left( \mathrm{Range} \left( A \right) \right) = \mathrm{Rank}(A)
$$

where $k_i$ is pivot position of $U =EA$.

fundamental theorem of linear algebra:
- $\mathrm{kernel}(A) = \mathrm{range}(A^T)^\perp$ (the only one you need to remember)
- $\mathrm{kernel}(A)^\perp = \mathrm{range}(A^T)$
- $\mathrm{kernel}(A^T) = \mathrm{range}(A)^\perp$
- $\mathrm{kernel}(A^T)^\perp = \mathrm{range}(A)$

if $b$ of $Ax = b$ is not in range of $A$, solution of $x$ does not exist. trying to find closest x that minimizes $|Ax - b|^2$ is called least square problem. the normal equation corresponding is given below.

$$
A^TAx = A^Tb
$$

### Advanced Topics

determinant is property of square matrix.

$$
A =\begin{bmatrix}
	a_{11} & a_{12} & a_{13} \\
	a_{21} & a_{22} & a_{23} \\
	a_{31} & a_{32} & a_{33}
\end{bmatrix}
$$

$$
\mathrm{det}\left( A \right) =
a_{11}(a_{22}a_{33} - a_{23}a_{32}) - a_{12}(a_{23}a_{31} - a_{21}a_{33}) + a_{13}(a_{21}a_{32} - a_{22}a_{31})
$$

## APPENDIX C

l'hopital's rule: if $f(x)$ and $g(x)$ are differentiable at $x=c$ and $g'(x) \neq 0$

$$
\lim_{x \to c} \frac {f(x)}{g(x)} = \frac {f'(x)}{g'(x)}
$$

the directional derivative at $x$ in the direction $u$ is

$$
u \cdot \nabla f(x) = \sum_{i=1}^n u_i \frac {\partial f}{\partial x_i}
$$

approximations of differences

$$
F'(x) = \frac {F(x+h) - F(x)} {h} + O(h)
$$

$$
F''(x) = \frac {F(x+2h) - 2F(x+h) + F(x)} {h^2} + O(h)
$$

## CHAPTER 11

this chapter is a brief summary of ordinary differential equations (ODE).

let $y$ be a dependent variable and $x$ an independent variable, and $y = f(x)$ is an unknown function of $x$. the equation of the form

$$
F(x, y, y', y'', \dots, y^{(n)}) = 0
$$

is called (implicit) ordinary differential equation.

| classification | general form |
|:-:|--|
| explicit | $$y^{(n)} = F(x, y, y', y'', \dots, y^{(n-1)})$$ |
| autonomous | $$F(y, y', y'', \dots, y^{(n)}) = 0$$ |
| linear | $$y^{(n)} = \sum_{i=0}^{n-1} a_i(x) y^{(i)} + r(x)$$ |
| homogenous (linear) | $$y^{(n)} = \sum_{i=0}^{n-1} a_i(x) y^{(i)}$$ |

in practice closed form $y^{n}(x)$ might not exist or too hard to obtain, you have to use numerical methods.

## CHAPTER 13

- euler's method
- runge-kutta methods
- and etc

## CHAPTER 2

chapter 2 introduces basic math and physics knowledges.

## CHAPTER 3

you got to understand: *Physics is just a model*.  a more romantic way to explain is: nature does not has a goal. if you can't understand, you might want to watch this [video](https://www.youtube.com/watch?v=dPxhTiiq-1A).

position $x$ is parameterized by $q$, we have lagrangian equation of motion:

$$
F_q = F \cdot \frac {dx}{dq}
$$

$$
F_q = \frac d {dt} \left(
\frac {\partial \frac {m |\dot x|^2} 2} {\partial \dot q }
\right) - \frac {\partial \frac {m |\dot x|^2} 2}{\partial q}
$$

scalar value $F_q$ is referred as a generalized force. the next thing you need to do is solving these constraint differential equations.

## CHAPTER 4

chapter 4 is on the topic of deformable (non-rigid) body motion. i'm not saying that it's not important, but i'm more interested in rigid body motion currently. so i'll leave it for later.

## CHAPTER 6

### example: bouncing sphere

hard coded collision detection.
prevent penetrations by pulling rigid bodies away in collision normal direction, which looks not so *naturely*.

the response force is calculated with
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

note that the following property is also applied
$$
n \cdot (\omega \times r) = \omega \cdot (r \times n)
$$

### unconstrained motion

old school rigidbody ( newton 2nd law, and differential equations).

### acceleration based constrained motion

only vertex/face and edge/edge collisions are taken into consideration. check:

- *Physically based Modelling: Principals and Practice*
- *Analytical methods for dynamic simulation of non-penetrating rigid bodies*

for more details.

### velocity base constrained motion

check:

- *Iterative Dynamics with Temporal Coherence*

for more details.

