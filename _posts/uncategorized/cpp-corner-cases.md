负数的 div 和 mod 的符号曾经没有明确定义，C++11 做出了明确要求。

> except for the obscure case where $-m$ overflows, $(-m)/n$ and $m/(-n)$ are always equal to $-(m/n)$, $m\%(-n)$ is equal to $m\%n$, and $(-m)\%n$ is equal to $-(m\%n)$.

---

`*p++` 等价于 `*(p++)`。

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

众所周知，持有容器类型的 iterator，在容器插入、删除时迭代器会失效。实际上，指针、引用也是同样的。比如 vector resize 的时候，之前持有的指针都成为了野指针，引用都成为了非法引用。

```c++
class A {
public:
    int i;
    A() : i(0xDEADBEEF) {
    }
};
void foo(int i, A &a) {
    a.i = i; // invalid ref
}
int main(int argc, char* argv[]) {
    vector<A> as;
    vector<thread> ts;
    for (int i = 0; i < 10; i++) {
        as.push_back(A());
        ts.emplace_back(thread(foo, i, ref(as[i]));); // 引用已经失效
    }
    for (int i = 0; i < 10; i++)
        ts[i].join();
    for (int i = 0; i < 10; i++)
        cout << as[i].i << endl;
    return EXIT_SUCCESS;
}
```

---

New operator `A *a = new A(...)` 会做 2 件事情：

1. 通过 operator new 申请内存，可以重载 `void *::operator new(size_t)` 或者 `void *A::operator(size_t)`。
2. 通过 placement new `new (a) A(...)` 初始化对象，可以重载 `void *operator new(size_t, void *)` 或者 `void *A::operator new(size_t, void *)`。

---

```c++
#include <iostream>
#include <future>
#include <thread>
 
int main() {
    // 通过 async 返回 future 是最抽象的方式。
    std::future<int> f2 = std::async(std::launch::async, []{ return 8; });
    
    // async 其实是开了线程，传了一个 packaged_task。
    std::packaged_task<int()> task([]{ return 7; });
    std::future<int> f1 = task.get_future();
    std::thread t(std::move(task));
 
    // 更细节：packaged_task 其实创建了一个与 future 绑定的 promise，在函数返回时给 promise set_value，然后
    // future 可以等待结果。
    std::promise<int> p;
    std::future<int> f3 = p.get_future();
    std::thread( [&p]{ p.set_value_at_thread_exit(9); }).detach();
 
    std::cout << "Waiting..." << std::flush;
    f1.wait();
    f2.wait();
    f3.wait();
    std::cout << f1.get() << ' ' << f2.get() << ' ' << f3.get() << endl;
    t.join();
}
```

---

C++11 的 `chrono` 还是比较方便的，不过接口比较拗口。

```c++
int main() {
	chrono::time_point<chrono::steady_clock> t1 = chrono::steady_clock::now();
	chrono::time_point<chrono::steady_clock> t2 = chrono::steady_clock::now();
	chrono::milliseconds d = chrono::duration_cast<chrono::milliseconds>(t2 - t1);
	chrono::steady_clock::rep c = d.count(); // long long
	cout << c << endl;
	return EXIT_SUCCESS;
}
```

---

Template 现在也支持变长模板。

```c++
template <typename T>
void foo(T t) {
	cout << t << endl;
}

template <typename T, typename ...Args>
void foo(T t, Args... args) {
	cout << t << endl;
	foo(args...);
}
```

---

`T &&` 是右值引用，同时也是所谓 *forwarding reference*，可以被 forwarding，保持参数传递过程中的类型。

```c++
struct A {
    A(int&& n) { std::cout << "rvalue overload, n=" << n << "\n"; }
    A(int& n)  { std::cout << "lvalue overload, n=" << n << "\n"; }
};
 
class B {
public:
    template<class T1, class T2, class T3>
    B(T1&& t1, T2&& t2, T3&& t3) :
        a1_{std::forward<T1>(t1)},
        a2_{std::forward<T2>(t2)},
        a3_{std::forward<T3>(t3)}
    {}
private:
    A a1_, a2_, a3_;
};
 
template<class T, class U>
std::unique_ptr<T> make_unique1(U&& u) {
    return std::unique_ptr<T>(new T(std::forward<U>(u)));
}
 
template<class T, class... U>
std::unique_ptr<T> make_unique2(U&&... u) {
    return std::unique_ptr<T>(new T(std::forward<U>(u)...));
}
 
int main() {
    auto p1 = make_unique1<A>(2); // rvalue
    int i = 1;
    auto p2 = make_unique1<A>(i); // lvalue
 
    std::cout << "B\n";
    auto t = make_unique2<B>(2, i, 3);
}
```

---

C style casting 虽然同时具有多种语义，不过熟悉了之后还好。C++ 把 casting 拆成了 4 种。

`static_cast`：

`dynamic_cast`：

`const_cast`：

`reinterpret_cast`：

---

1. 将一个类型 `A` 的 lval 传递给模板 rref 参数（`T &&`），推断 `T` 为 `A &`，而不是 `A`。
2. `A& &`，`A & &&`，和 `A&& &` 都折叠成 `A&`。
3. `A&& &&` 折叠成 `A&&`。

---

