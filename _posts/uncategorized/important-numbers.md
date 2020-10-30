## Socket 传输

忽略 tcp / protocol 本身的 overhead，1000M 带宽 1s 可以传输：
$$
(1024 \times 1024 \times 1024) \div (4 \times 8) = 33,554,432
$$
最多大约 3 千万个 float。

## Python 2 Http 传递大包效率

python 2.7 `BaseHTTPServer.HTTPServer` 传递 381 MB post body 大约需要 0.8 秒。

## 内存间拷贝

```c++
#include <iostream>
#include <chrono>
#include <vector>
using namespace std;
using namespace chrono;

int main() {
	// MBP 2019, 2.6 GHz 6-core intel core i7.
  // copy 1K ints: 5   microseconds;
	// copy 1M ints: 3.6 milliseconds;
	// copy 1G ints: 3.7 seconds.
  const int N = 1024 * 1024 * 1024;
  const int NTEST = 10;
  vector<int> src(N), dst(N);
  srand(time(nullptr));
  for (int i = 0; i < N; i++)
    src[i] = rand();
  microseconds mean(0);
  for (int c = 0; c < NTEST; c++) {
    high_resolution_clock::time_point t1 = high_resolution_clock::now();
    for (int i = 0; i < N; i++)
      dst[i] = src[i];
    high_resolution_clock::time_point t2 = high_resolution_clock::now();
    if (c != 0)
      mean += duration_cast<microseconds>(t2 - t1);
  }
  cout << (mean / (NTEST - 1)).count() << endl;
  return 0;
}
```

