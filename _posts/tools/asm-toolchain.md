可以参考 [The PC  Assembly Language](http://pacman128.github.io/static/pcasm-book-simplified-chinese.pdf) 作快速入门。

## 安装

NASM

```bash
apt-get install -y nasm
```

## 编译

NASM

```bash
nasm -f elf32 x.s
gcc -m32 -c main.c
gcc -m32 x.o main.o # a lot easier than using ld
```

nasm 增加 `-l $LISTFNAME` 可以在 `$LISTFNAME` 中输出汇编列表。注意其输出的地址不是运行时的地址。

## 截断与拓展

```assembly
mov ax, 0034h
mov cl, al
```

截断无符号数的规则是：为了能转换正确，所有需要移除的位都必须是 0。

截断有符号数的规则是：需要移除的位必须要么都是 1,要么都是 0。另外，没有移除的第一个比特位的值必须等于移除的位的第一位。

延展无符号数很简单，补 0 即可。

延展有符号数的规则是：必须扩展符号位。这就意味着所有的新位通过复制符号位得到。因为 FF 的符号位为 1，所以新的位必须全为 1，从而得到 FFFF。