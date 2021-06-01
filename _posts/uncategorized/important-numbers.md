## Important Numbers

```text
Latency Comparison Numbers (~2012)
----------------------------------
L1 cache reference                           0.5 ns
Branch mispredict                            5   ns
L2 cache reference                           7   ns                      14x L1 cache
Mutex lock/unlock                           25   ns
Main memory reference                      100   ns                      20x L2 cache, 200x L1 cache
Compress 1K bytes with Zippy             3,000   ns        3 us
Send 1K bytes over 1 Gbps network       10,000   ns       10 us
Read 4K randomly from SSD*             150,000   ns      150 us          ~1GB/sec SSD
Read 1 MB sequentially from memory     250,000   ns      250 us
Round trip within same datacenter      500,000   ns      500 us
Read 1 MB sequentially from SSD*     1,000,000   ns    1,000 us    1 ms  ~1GB/sec SSD, 4X memory
Disk seek                           10,000,000   ns   10,000 us   10 ms  20x datacenter roundtrip
Read 1 MB sequentially from disk    20,000,000   ns   20,000 us   20 ms  80x memory, 20X SSD
Send packet CA->Netherlands->CA    150,000,000   ns  150,000 us  150 ms

Notes
-----
1 ns = 10^-9 seconds
1 us = 10^-6 seconds = 1,000 ns
1 ms = 10^-3 seconds = 1,000 us = 1,000,000 ns

Credit
------
By Jeff Dean:               http://research.google.com/people/jeff/
Originally by Peter Norvig: http://norvig.com/21-days.html#answers

Contributions
-------------
'Humanized' comparison:  https://gist.github.com/hellerbarde/2843375
Visual comparison chart: http://i.imgur.com/k0t1e.png
```

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

