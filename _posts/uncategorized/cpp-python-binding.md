## Loading Shared Lib

```bash
g++ -c -Wall -Werror -fpic a.cc
g++ -c -Wall -Werror -fpic b.cc
g++ -shared -o liba.so a.o
g++ -shared -o libb.so b.o -L. -la
```

```python
import ctypes
liba = ctypes.CDLL('./a.so', mode=ctypes.RTDL_GLOBAL)
libb = ctypes.CDLL('./b.so')
```

如果 b.so 依赖 a.so，要注意 mode，否则出现 undefined symbol。

可以用 `ldd libb.so` 查看一个 lib 的 deps。但是 deps 是通过 g++ 编译时通过 `-l` 制定的，而漏掉这个选项并不影响 so 生成，所以如果有人比较粗心没写就会没头绪了。

## Call C Functions

Pretty straightforward.

```
arg = ctypes.c_int(0)
ret = liba.f(arg)
print(ret.value)
```

## Using C++ Class

WTF.

