---
layout: post
title: "C 语言返回值截断"
categories: uncategorized
date: 2019-05-10 00:00:00
---

﻿

现在有代码一份，请猜测输出？
```C
// file: main.c

#include <stdio.h>
#include <stdlib.h>

unsigned char nr_sum(unsigned char a[], int len)
{
	int i, sum = 0;

	for (i = 0; i < len; i++) {
		sum += a[i];
	}
	return sum;
}

int main(int argc, char *argv[])
{
	unsigned char ucs[] = {
		5, -5
	};

	int rv = nr_sum(ucs, 2);
	printf("%d\n", rv);
	
	return EXIT_SUCCESS;
}
```
档案很简单，明显是 0，毫无亮点。

另一份代码：
```c
// file: math.c

#include <stdio.h>

unsigned char nr_sum(unsigned char a[], int len)
{
	int i, sum = 0;

	for (i = 0; i < len; i++) {
		sum += a[i];
	}

	return sum;
}
```
```c
// file: main.c

#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
	unsigned char ucs[] = {
		5, -5
	};

	int rv = nr_sum(ucs, 2);
	printf("%d\n", rv);
	
	return EXIT_SUCCESS;
}
```
欢迎猜答案！只是简单把函数换一个地方放而已呀，并无大碍。答案是 0...， 就有鬼了....答案是 256～

为了向后兼容，C 没有禁止 implicit declaration，而对于那些没有 declaration 的函数，C 默认返回是 `int`。第一份代码由于写在同一个文件，不需要声明，没发生问题。第二个文件，忘记声明，假设返回 `int`。结果倒霉的函数真的返回的是 `int`，所以没有被（如同我期望般）截断。

检查生成的汇编：
```asm
	.file	"math.c"
	.section	.rodata
.LC0:
	.string	"nr_sum %d\n"
	.text
	.globl	nr_sum
	.type	nr_sum, @function
nr_sum:
.LFB0:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	subq	$32, %rsp
	movq	%rdi, -24(%rbp)
	movl	%esi, -28(%rbp)
	movl	$0, -4(%rbp)
	movl	$0, -8(%rbp)
	jmp	.L2
.L3:
	movl	-8(%rbp), %eax
	movslq	%eax, %rdx
	movq	-24(%rbp), %rax
	addq	%rdx, %rax
	movzbl	(%rax), %eax
	movzbl	%al, %eax
	addl	%eax, -4(%rbp)
	addl	$1, -8(%rbp)
.L2:
	movl	-8(%rbp), %eax
	cmpl	-28(%rbp), %eax
	jl	.L3
	movl	-4(%rbp), %eax
	movl	%eax, %esi
	movl	$.LC0, %edi
	movl	$0, %eax
	call	printf
	movl	-4(%rbp), %eax
	leave
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE0:
	.size	nr_sum, .-nr_sum
	.ident	"GCC: (Ubuntu 4.8.4-2ubuntu1~14.04) 4.8.4"
	.section	.note.GNU-stack,"",@progbits
```
`movl	-4(%rbp), %eax` 返回值放在 32 bit 长度的寄存器里面，没有截断就回传。这是真的坑爹。

顺便贴一下出问题的代码：
```c
static
mp_fp_struct_t *mp_lookup_fp_struct_at(uint32_t phys, size_t len)
{
	uint8_t *a, *end, *p;
	int rv;

	a = p2v(phys);
	end = a + len;
	for (p = a; p < end; p += sizeof(mp_fp_struct_t)) {
		if (!memcmp(p, "_MP_", 4)) {
			rv = sum_uc(p, sizeof(mp_fp_struct_t));
			printf("return value %d\n", rv);
			if (!rv)
				return (mp_fp_struct_t *) p;
		}
	}
	return NULL;
}
```
我不幸地忘记 include `sum_uc` 所在的头文件了。所以 `sum_uc` 总是返回 `int`.... 经过被坑了一个晚上的惨痛经历，我决定打开警告选项：
```bash
gcc -Wall kernel/mp.c
```
