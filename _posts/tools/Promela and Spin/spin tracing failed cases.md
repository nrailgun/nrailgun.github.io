随机测试可能找到失败 case，但是并不能保证状态空间完全搜索，而且不能复现。

## 产生检测器

通过设置 spin 参数产生一系列文件，通过编译 `pan.c` 产生检测器。
```bash
spin -a maxF.pml
gcc -o pan pan.c
```

运行检测器即可遍历状态空间。如果存在错误，检测器会提示错误：

>nr@nr-lab ~/Downloads % ./a.out 
>hint: this search is more efficient if pan.c is compiled -DSAFETY
>pan:1: assertion violated (max==( ((a>b)) ? (a) : (b) )) (at depth 2)
>pan: wrote maxF.pml.trail

并产生记录错误的文件 `maxF.pml.trail`。

## 追踪、复现错误

*注意：请在 pml 文件所在文件夹进行检测和复现。*

spin 可以读取当前文件夹下的 `maxF.pml.trail` 进行错误复现：
```
spin -t maxF.pml
```

如果你希望输出更多的信息，避免瞎了狗眼，可以考虑一下参数 `-p` 和 `-l`。指定 `-p` 输出运行的指令，`-l` 输出每次对于局部变量的写操作。
```
spin -t -p -l maxF.pml
```