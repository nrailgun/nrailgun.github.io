
# 前言

常用的物理实现 phyx 和寻路实现 recast/detour 默认不提供 golang 接口，如果使用 golang 编写可能需要考虑对接问题。目前在社区看到的反馈是 cgo 的运行效率不佳，我们需要先评估一下具体冲击。

# Cgo

Cgo 的使用非常简单，可以直接参考这两个文档：
- [GoDoc: Cgo](https://golang.org/cmd/cgo/)
- [GoDoc: C? Go? Cgo!](https://blog.golang.org/c-go-cgo)

由于 c++ 主要用于 cpu 密集计算（就像 phyx 和 recast/detour），因此我们使用 fibnacci 做benchmark。

我们先定义这个函数的 c 实现。

*fib.h*
```c
#include <inttypes.h>
uint64_t fib(uint8_t n);
```

*fib.c*
```c
#include <inttypes.h>
#include "fib.h"

uint64_t fib(uint8_t n) {
	uint8_t i = 0;
	uint64_t n1 = 0, n2 = 1, n3 = 0;

	if (n <= 1u)
		return n;

	for (i = 2; i <= n; i++) {
		n3 = n1 + n2;
		n1 = n2;
		n2 = n3;
	}
	return n3;
}
```

然后定义 benchmark，为了简便，使用内建的 benchmark。

*fib.go*
```go
package main

// #cgo CFLAGS: -O2
// #include "fib.h"
import "C"
import "fmt"

// 重复调用 c 函数。之所以 return 一个 sum，是为了防止 golang 编译器意外优化代码。
// 由于暂时没有找到文档说明 golang 编译器对于是否优化这种“无用”代码，所以使用返回
// 值来避免优化。
func runCFib(nRun int, maxI uint8) uint64 {
	var sum uint64
	for it := 0; it < nRun; it++ {
		var i uint8
		for i = 0; i < maxI; i++ {
			v, _ := C.fib(C.uint8_t(i))
			sum += uint64(v)
		}
	}
	return sum
}

// 除了语言，算法控制流完全一致。
func goFib(n uint8) uint64 {
	var (
		n1 uint64 = 0
		n2 uint64 = 1
		n3 uint64 = 0
	)

	if n <= 1 {
		return uint64(n)
	}

	var i uint8 = 0
	for i = 2; i <= n; i++ {
		n3 = n1 + n2
		n1 = n2
		n2 = n3
	}
	return n3
}

// 同上，阻止可能的优化。
func runGoFib(nRun int, maxI uint8) uint64 {
	var sum uint64
	for it := 0; it < nRun; it++ {
		var i uint8
		for i = 0; i < maxI; i++ {
			v := goFib(i)
			sum += v
		}
	}
	return sum
}

func main() {
}
```

*fib_test.go*
```go
package main

import (
	"testing"
)

func BenchmarkCFib(*testing.B) {
	runCFib(100000, 30)
}

func BenchmarkGoFib(*testing.B) {
	runGoFib(100000, 30)
}
```

Benchmark 结果如下。
```
go test -bench=.

goos: linux
goarch: amd64
BenchmarkCFib-4    	2000000000	         0.09 ns/op
BenchmarkGoFib-4   	2000000000	         0.01 ns/op
PASS
ok  	_/home/nr/workspace/go	1.931s
```
正如社区传言，cgo 的效率非常糟糕。

# 其他

Cgo 不能直接在 windows 上运行，因为默认只支持 gcc。对于 linux 服务器，这不是问题。

# 结论

一个可能的 cgo 如此迟钝的[解释](https://groups.google.com/forum/#!topic/golang-nuts/RTtMsgZi88Q)：
> 调用 c 函数会切换所有的寄存器。

我的理解是，这里的*所有寄存器*可能包括cr等寄存器，这就涉及了内存页/堆栈等问题，这些寄存器的操作都是非常缓慢的，可能经过几百个时钟周期。

在这个 ggrp 的讨论可以看到一个例子，也是 cgo 比 go 更慢的例子。
>Averaged time over 1,000,000 iterations
Go subroutine execution time (ns): 10.585000
Extern C execution time (ns): 161.750000 

询问了一下 HJH，他表示由于 c++ 动态依赖的问题，我们不使用 cgo。所以这个问题暂时不考虑，如果需要寻路和物理，需要另寻方案。
