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

Value initialzation：

1. 数组初始化中提供 initializer 数量不足，
2. 定义 local static obj 没有 initializer，
3. `T()` 显式 value initialization。

会调用 default ctor。

---

虽然 *C++ Primer* 书中所写 catch exception by value，但是实际上应该 catch exception by ref，否则异常之类会发生 object slicing。

---

C++ 不能 copy array，所以不能将 array 作为返回值，只能返回 array 的指针。写法也怪异 `type (*function(parameters))[dimension]`。说实话 using 比较省事省心。

---

在不同的 scope 里面声明同名函数会导致 shadow 而不是 overload。

---

默认参数在声明中给定，并且不能重新声明，但是可以在 local scope shadow 掉 (= = ?)。

---

Aggregate class:

1. 全 public，
2. 没 ctor，
3. 没 in-class initializer，
4. 没虚函数，没基类。

可用 initializer list 初始化。

---

constexpr 函数的参数和返回值必须是 literal class。

Aggregate class 如果成员都是 literal 那么 就是 literal class。Non-aggregate class 如果：

1. 数据成员都是 literal，
2. 有一个 constexpr ctor，
3. 成员 in-class initializer 必须是 const expression 或者 constexpr。
4. 必须 default dctor。

---

 